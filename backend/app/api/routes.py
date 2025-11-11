import asyncio
import logging
import time
import json
from typing import List
from fastapi import APIRouter, HTTPException, File, UploadFile, status
from fastapi.responses import StreamingResponse
from datetime import datetime
from app.models.schemas import  HealthResponse, DocumentData, FileProcessResult
from app.services.ocr_service import OCRService
from app.services.ai_service import AIService
from app.services.pdf_processor import PDFProcessor
from app.config.settings import settings
from app.services.storage_service import StorageService

logger = logging.getLogger(__name__)

router = APIRouter()

pdf_processor = PDFProcessor(
    dpi=settings.tesseract_dpi,
    contrast=settings.image_contrast_factor,
    sharpness=settings.image_sharpness_factor,
    brightness=settings.image_brightness_factor
)

storage_service = StorageService(
    csv_path=settings.csv_path,
    excel_path=settings.excel_path
)

_ocr_service = None
_ai_service = None

def get_ocr_service():
    global _ocr_service
    if _ocr_service is None:
        try:
            _ocr_service = OCRService(
                provider=settings.ocr_provider,
                google_credentials=settings.google_credentials_json
            )
            logger.info(f"OCR service initialized successfully with provider: {settings.ocr_provider}")
        except Exception as e:
            logger.error(f"Failed to initialize OCR service: {str(e)}")
            raise HTTPException(status_code=503, detail=f"OCR service initialization failed: {str(e)}")
    return _ocr_service

def get_ai_service():
    global _ai_service
    if _ai_service is None:
        try:
            logger.info(f"Initializing AI service with model: {settings.openai_model}")

            if not settings.openai_api_key or settings.openai_api_key == "placeholder-key":
                raise ValueError("OpenAI API key not configured")
            
            if settings.openai_api_key.strip() == "":
                raise ValueError("OpenAI API key is empty")
            
            _ai_service = AIService(
                api_key=settings.openai_api_key.strip(),
                model=settings.openai_model,
                temperature_extraction=settings.openai_temperature_extraction,
                temperature_summary=settings.openai_temperature_summary
            )
            logger.info(f"Ai service initialized successfully with provider: {settings.ocr_provider}")
        except Exception as e:
            logger.error(f"Failed to initialize AI service: {str(e)}")
            raise HTTPException(status_code=503, detail=f"AI service initialization failed: {str(e)}")
    return _ai_service


@router.get("/health", response_model=HealthResponse)
async def health_check():
    ocr_available = False
    if settings.ocr_provider == "google":
        try: 
           from google.cloud import vision
           ocr_available = bool(settings.google_credentials_json)
        except ImportError:
            logger.warning("google-cloud-vision not installed. Install with: pip install google-cloud-vision")
            ocr_available = False
    else:
        try:
            import pytesseract
            pytesseract.get_tesseract_version()
            ocr_available = True
        except:
            logger.warning("pytesseract not installed. Install with: pip install pytesseract")
            ocr_available = False
    ai_available = bool(settings.openai_api_key and settings.openai_api_key != "placeholder-key")

    status = "healthy" if(ocr_available and ai_available) else "degraded"
    logger.info(f"Health check completed. OCR available: {ocr_available}, AI available: {ai_available}, status: {status}")

    return HealthCheckResponse(status=status, ocr_available=ocr_available, ai_available=ai_available)

@router.post("/process")
async def process_documents_stream(files: List[UploadFile] = File(...)):
    logger.info(f"Received {len(files)} files for processing")
    
    if not files:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No files provided"
        )
    
    async def generate_progress():
        results = []
        successful = 0
        failed = 0
        total_files = len(files)
        
        for index, file in enumerate(files, start=1):
            progress_data = {
                "type": "progress",
                "current": index,
                "total": total_files,
                "filename": file.filename,
                "percentage": int(((index - 1) / total_files) * 100)
            }
            yield json.dumps(progress_data) + "\n"
            await asyncio.sleep(0)
            
            file_result = await process_single_file(file)
            results.append(file_result)
            
            if file_result.success:
                successful += 1
            else:
                failed += 1
            
            result_data = {
                "type": "result",
                "result": {
                    "filename": file_result.filename,
                    "success": file_result.success,
                    "data": file_result.data.model_dump() if file_result.data else None,
                    "error": file_result.error,
                    "processing_time": file_result.processing_time
                }
            }
            yield json.dumps(result_data) + "\n"
            await asyncio.sleep(0)
        
        logger.info(f"Processing complete: {successful} succeeded, {failed} failed")
        
        complete_data = {
            "type": "complete",
            "summary": {
                "total_files": total_files,
                "processed": successful,
                "failed": failed,
                "results": [
                    {
                        "filename": r.filename,
                        "success": r.success,
                        "data": r.data.model_dump() if r.data else None,
                        "error": r.error,
                        "processing_time": r.processing_time
                    }
                    for r in results
                ]
            }
        }
        yield json.dumps(complete_data) + "\n"
    
    return StreamingResponse(
        generate_progress(),
        media_type="application/x-ndjson",
        headers={
            "Cache-Control": "no-cache, no-transform",
            "X-Accel-Buffering": "no",
            "Content-Type": "application/x-ndjson; charset=utf-8",
            "Transfer-Encoding": "chunked"
        }
    )


async def process_single_file(file: UploadFile) -> FileProcessResult:
    start_time = time.time()
    filename = file.filename
    
    logger.info(f"Processing file: {filename}")
    
    try:
        if not filename.lower().endswith('.pdf'):
            raise ValueError("Only PDF files are allowed")
        
        pdf_bytes = await file.read()
        
        is_valid, error_msg = pdf_processor.validate_pdf(pdf_bytes, settings.max_file_size)
        if not is_valid:
            raise ValueError(error_msg)
        
        logger.info(f"{filename}: PDF validation passed")
        
        images = pdf_processor.extract_images(pdf_bytes)
        logger.info(f"{filename}: Extracted {len(images)} images")
        
        ocr_service = get_ocr_service()
        raw_text = ocr_service.batch_process(images)
        
        if not raw_text or len(raw_text.strip()) < 10:
            raise ValueError("No text could be extracted from the document")
        
        logger.info(f"{filename}: Extracted {len(raw_text)} characters of text")
        
        ai_service = get_ai_service()
        extracted_data = ai_service.extract_structured_data(raw_text)
        logger.info(f"{filename}: Structured data extracted")
        
        summary = ai_service.generate_summary(raw_text)
        logger.info(f"{filename}: Summary generated")
        
        document_data = DocumentData(
            first_name=extracted_data.get('firstName', 'Unknown'),
            middle_name=extracted_data.get('middleName'),
            last_name=extracted_data.get('lastName', 'Unknown'),
            date_created=datetime.now().strftime('%Y-%m-%d'),
            doc_number=extracted_data.get('docNumber', 'Unknown'),
            facility_name=extracted_data.get('facilityName', 'Unknown'),
            address=extracted_data.get('address', 'Unknown'),
            unit=extracted_data.get('unit'),
            ai_summary=summary,
            raw_text=raw_text
        )
        
        storage_service.append_to_csv({
            'firstName': document_data.first_name,
            'middleName': document_data.middle_name,
            'lastName': document_data.last_name,
            'dateCreated': document_data.date_created,
            'docNumber': document_data.doc_number,
            'facilityName': document_data.facility_name,
            'address': document_data.address,
            'unit': document_data.unit,
            'aiSummary': document_data.ai_summary,
            'rawText': document_data.raw_text
        })
        
        logger.info(f"{filename}: Data saved to CSV")
        
        processing_time = time.time() - start_time
        logger.info(f"{filename}: Processing complete in {processing_time:.2f}s")
        
        return FileProcessResult(
            filename=filename,
            success=True,
            data=document_data,
            error=None,
            processing_time=processing_time
        )
        
    except HTTPException as e:
        processing_time = time.time() - start_time
        error_msg = e.detail
        
        logger.error(f"{filename}: Processing failed - {error_msg}")
        
        return FileProcessResult(
            filename=filename,
            success=False,
            data=None,
            error=error_msg,
            processing_time=processing_time
        )
    except Exception as e:
        processing_time = time.time() - start_time
        error_msg = str(e)
        
        logger.error(f"{filename}: Processing failed - {error_msg}")
        
        return FileProcessResult(
            filename=filename,
            success=False,
            data=None,
            error=error_msg,
            processing_time=processing_time
        )
