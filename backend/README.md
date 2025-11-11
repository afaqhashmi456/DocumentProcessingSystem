# Document Processing API - Backend

FastAPI backend for OCR and AI-powered document extraction system.

## Overview

This backend service processes handwritten prison mail PDFs using:
- **Google Cloud Vision API** (RECOMMENDED) or **Tesseract OCR** for text extraction
  - Google Vision: 90%+ accuracy on handwriting, commercial API
  - Tesseract: ~30% accuracy on handwriting, free but limited
- **OpenAI GPT-4** for intelligent data extraction and summarization
- **Pandas** for CSV data storage

> ⚠️ **For handwritten documents, Google Vision API is STRONGLY RECOMMENDED.**  
> See [GOOGLE_VISION_SETUP.md](./GOOGLE_VISION_SETUP.md)

## Architecture

```
app/
├── api/           # API routes
├── services/      # Business logic services
├── models/        # Pydantic schemas
└── config/        # Configuration management
```

## Services

### PDFProcessor
- Converts PDF pages to images
- Enhances images for better OCR (grayscale, contrast, sharpness)
- Handles multi-page documents

### OCRService
- **Primary**: Google Vision API (best for handwriting, 90%+ accuracy)
- **Fallback**: Tesseract OCR (free but limited for handwriting, ~30% accuracy)
- Batch processes multiple pages
- Automatic fallback if Google Vision unavailable
- Provides confidence scoring

### AIService
- Extracts structured data (names, DOC#, facility, address)
- Generates concise summaries
- Includes retry logic and error handling

### StorageService
- Appends data to CSV with file locking
- Validates data before saving
- Handles concurrent writes safely

## Setup

### 1. Install Dependencies

```bash
cd backend

python3 -m venv venv
source venv/bin/activate

pip install -r requirements.txt
```

### 2. Install System Dependencies

**Required - PDF Processing** (pdf2image requires poppler):

**macOS:**
```bash
brew install poppler
```

**Ubuntu/Debian:**
```bash
sudo apt-get install poppler-utils
```

**Windows:**
Download poppler from: https://github.com/oschwartz10612/poppler-windows/releases/

---

**Optional - Tesseract OCR** (if not using Google Vision):

**macOS:**
```bash
brew install tesseract
```

**Ubuntu/Debian:**
```bash
sudo apt-get install tesseract-ocr
```

**Windows:**
Download from: https://github.com/UB-Mannheim/tesseract/wiki

### 3. Configure Environment

Create `.env` file (see `env.example`):

```env
# OCR Configuration (choose provider)
OCR_PROVIDER=google  # "google" (recommended) or "tesseract" (fallback)

# Google Vision API (for OCR_PROVIDER=google)
GOOGLE_CREDENTIALS_JSON=/path/to/google-vision-key.json

# OpenAI API
OPENAI_API_KEY=your_openai_api_key
OPENAI_MODEL=gpt-4o-mini

# Data Storage
CSV_PATH=/Users/mac/Downloads/assessment/Extracted Data.csv

# Server Config
UPLOAD_DIR=uploads
MAX_FILE_SIZE=10485760
CORS_ORIGINS=http://localhost:5173
```

**📖 Google Vision Setup**: See [GOOGLE_VISION_SETUP.md](./GOOGLE_VISION_SETUP.md) for complete instructions on:
- Creating Google Cloud project
- Enabling Vision API
- Getting credentials
- Configuration options
- Cost considerations (~$0 for assessment, ~$4.50/mo for 1k letters)

### 4. Run Server

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

python -m app.main
```

Server will start at: http://localhost:8000

## API Endpoints

### GET /
Root endpoint with API information

### GET /api/health
Health check endpoint

**Response:**
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "timestamp": "2024-11-11T10:00:00"
}
```

### POST /api/process
Process PDF documents

**Request:**
- Content-Type: multipart/form-data
- Body: Multiple PDF files

**Response:**
```json
{
  "total_files": 3,
  "processed": 3,
  "failed": 0,
  "results": [
    {
      "filename": "document.pdf",
      "success": true,
      "data": {
        "first_name": "John",
        "middle_name": "A",
        "last_name": "Doe",
        "date_created": "2024-11-11",
        "doc_number": "123456",
        "facility_name": "State Prison",
        "address": "123 Prison Rd, City, ST 12345",
        "unit": "B-Wing",
        "ai_summary": "Request for legal assistance...",
        "raw_text": "Full OCR text..."
      },
      "error": null,
      "processing_time": 15.2
    }
  ]
}
```

## Testing

### Test with curl

```bash

curl http://localhost:8000/api/health

curl -X POST http://localhost:8000/api/process \
  -F "files=@document1.pdf" \
  -F "files=@document2.pdf"
```

### Test with Postman

1. Create POST request to `http://localhost:8000/api/process`
2. Set Body type to `form-data`
3. Add key `files` with type `File`
4. Select multiple PDF files
5. Send request

## Logging

Logs are output to console with format:
```
2024-11-11 10:00:00 - service_name - INFO - Message
```

Adjust log level in `app/main.py`:
```python
logging.basicConfig(level=logging.DEBUG)
```

## Error Handling

The API returns appropriate HTTP status codes:
- 200: Success
- 400: Bad request (invalid file type, size exceeded)
- 500: Internal server error

Error responses include:
```json
{
  "error": "Error type",
  "message": "Detailed message",
  "details": {...}
}
```

## Performance Considerations

- **PDF Processing**: ~2-5 seconds per page
- **OCR**: ~3-8 seconds per page
- **AI Extraction**: ~2-4 seconds per document
- **Total**: ~10-30 seconds per multi-page document

Tips for optimization:
- Use appropriate DPI (300 recommended)
- Process files in parallel when possible
- Implement caching for repeated requests
- Monitor API rate limits (Google Vision, OpenAI)

## Production Deployment

See main README.md for deployment instructions.
