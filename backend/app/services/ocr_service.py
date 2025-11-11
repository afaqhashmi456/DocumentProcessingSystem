import logging
from typing import List, Optional
import pytesseract
from PIL import Image
import io
import json
import os

logger = logging.getLogger(__name__)


class OCRService:
    def __init__(self, provider: str = "google", google_credentials: str = ""):
        self.provider = provider.lower()
        self.google_client = None
        
        if self.provider == "google":
            try:
                from google.cloud import vision
 
                if google_credentials:
                    if os.path.isfile(google_credentials):
                        os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = google_credentials
                        logger.info(f"Using Google credentials from file: {google_credentials}")
                    else:
                        try:
                            json.loads(google_credentials)
                            import tempfile
                            with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
                                f.write(google_credentials)
                                os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = f.name
                            logger.info("Using Google credentials from JSON string")
                        except json.JSONDecodeError:
                            logger.warning("Invalid Google credentials format, attempting default auth")
                
                self.google_client = vision.ImageAnnotatorClient()
                logger.info("Google Vision API initialized successfully")
                
            except ImportError:
                logger.error("google-cloud-vision not installed. Install with: pip install google-cloud-vision")
                logger.warning("Falling back to Tesseract")
                self.provider = "tesseract"
            except Exception as e:
                logger.error(f"Failed to initialize Google Vision: {str(e)}")
                logger.warning("Falling back to Tesseract")
                self.provider = "tesseract"
        
        if self.provider == "tesseract":
            try:
                pytesseract.get_tesseract_version()
                logger.info("Tesseract OCR initialized successfully")
                
            except Exception as e:
                logger.warning(f"Tesseract not found: {str(e)}")
                logger.warning("Install with: brew install tesseract (macOS) or apt-get install tesseract-ocr (Linux)")
    
    def extract_handwriting(self, image_bytes: bytes) -> str:
        if self.provider == "google" and self.google_client:
            return self._extract_with_google(image_bytes)
        else:
            return self._extract_with_tesseract(image_bytes)
    
    def _extract_with_google(self, image_bytes: bytes) -> str:
        try:
            from google.cloud import vision

            image = vision.Image(content=image_bytes)
            
            response = self.google_client.document_text_detection(image=image)
            
            if response.error.message:
                raise Exception(f"Google Vision API error: {response.error.message}")
            
            text = response.full_text_annotation.text if response.full_text_annotation else ""
            
            logger.debug(f"Google Vision extracted {len(text)} characters")
            
            return text.strip()
            
        except Exception as e:
            logger.error(f"Google Vision extraction failed: {str(e)}")
            raise Exception(f"Text extraction failed: {str(e)}")
    
    def _extract_with_tesseract(self, image_bytes: bytes) -> str:
        try:
            image = Image.open(io.BytesIO(image_bytes))
            
            custom_config = r'--oem 3 --psm 6'
            
            text = pytesseract.image_to_string(image, config=custom_config)
            
            logger.debug(f"Tesseract extracted {len(text)} characters")
            
            return text.strip()
            
        except pytesseract.TesseractNotFoundError:
            logger.error("Tesseract is not installed or not in PATH")
            raise Exception(
                "Tesseract OCR is not installed. "
                "Install with: brew install tesseract (macOS) or "
                "apt-get install tesseract-ocr (Linux)"
            )
        except Exception as e:
            logger.error(f"Tesseract extraction failed: {str(e)}")
            raise Exception(f"Text extraction failed: {str(e)}")
    
    def batch_process(self, images: List[bytes]) -> str:
        all_text = []
        
        for idx, image_bytes in enumerate(images):
            logger.info(f"Processing image {idx + 1}/{len(images)}")
            
            try:
                text = self.extract_handwriting(image_bytes)
                
                if text.strip():
                    page_text = f"--- PAGE {idx + 1} ---\n{text}"
                    all_text.append(page_text)
                else:
                    logger.warning(f"No text found on page {idx + 1}")
                    
            except Exception as e:
                logger.error(f"Failed to process page {idx + 1}: {str(e)}")
                all_text.append(f"--- PAGE {idx + 1} ---\n[ERROR: Could not extract text]")
        
        combined_text = "\n\n".join(all_text)
        
        logger.info(f"Batch processing complete: {len(all_text)} pages processed")
        logger.info(f"Total extracted text length: {len(combined_text)} characters")
        
        return combined_text
    
    def extract_with_confidence(self, image_bytes: bytes) -> dict:
        try:
            image = Image.open(io.BytesIO(image_bytes))
            
            data = pytesseract.image_to_data(image, output_type=pytesseract.Output.DICT)
            
            words = []
            confidences = []
            
            for i, text in enumerate(data['text']):
                if text.strip():
                    words.append(text)
                    conf = int(data['conf'][i])
                    if conf > 0:
                        confidences.append(conf)
            
            full_text = ' '.join(words)
            avg_confidence = sum(confidences) / len(confidences) if confidences else 0
            
            result = {
                'text': full_text,
                'confidence': avg_confidence / 100,
                'word_count': len(words)
            }
            
            logger.info(f"Extracted {len(words)} words with {avg_confidence:.1f}% confidence")
            
            return result
            
        except Exception as e:
            logger.error(f"Confidence extraction failed: {str(e)}")
            raise Exception(f"Confidence extraction failed: {str(e)}")
