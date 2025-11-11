# Document Processing System

AI-powered OCR system for processing handwritten prison mail PDFs with intelligent data extraction.

## 🎯 Overview

This full-stack application processes handwritten documents using:
- **Frontend**: Vue 3 + TypeScript + Tailwind CSS
- **Backend**: FastAPI + Python
- **OCR**: Google Cloud Vision API (90%+ accuracy) or Tesseract (fallback)
- **AI**: OpenAI GPT-4 for intelligent data extraction
- **Export**: CSV and Excel formats

## 📋 Table of Contents

- [Architecture](#architecture)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
  - [Backend Setup](#backend-setup)
  - [Frontend Setup](#frontend-setup)
  - [Google Vision API Setup](#google-vision-api-setup)
- [Configuration](#configuration)
- [Running the Application](#running-the-application)
- [API Documentation](#api-documentation)
- [Features](#features)
- [Deployment](#deployment)
- [Troubleshooting](#troubleshooting)

## 🏗️ Architecture

```
assessment/
├── backend/                 # FastAPI Python backend
│   ├── app/
│   │   ├── api/            # API routes
│   │   ├── services/       # Business logic (OCR, AI, Storage)
│   │   ├── models/         # Pydantic schemas
│   │   └── config/         # Configuration management
│   ├── google-vision-key.json  # Google Cloud credentials (create this)
│   └── requirements.txt
├── frontend/                # Vue 3 TypeScript frontend
│   ├── src/
│   │   ├── components/     # Vue components
│   │   ├── services/       # API client
│   │   ├── types/          # TypeScript types
│   │   └── utils/          # Utilities
│   └── package.json
└── README.md               # This file
```

## ✅ Prerequisites

### Required Software
- **Python 3.8+** - Backend runtime
- **Node.js 16+** - Frontend runtime
- **npm** or **yarn** - Package manager
- **Poppler** - PDF processing (required)

### API Keys
- **OpenAI API Key** - For AI-powered data extraction
- **Google Cloud Service Account** - For Vision API OCR (recommended)

## 🚀 Installation

### Backend Setup

#### 1. Navigate to Backend Directory
```bash
cd backend
```

#### 2. Create Virtual Environment
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

#### 3. Install Python Dependencies
```bash
pip install -r requirements.txt
```

#### 4. Install System Dependencies

**Poppler (Required for PDF processing):**

**macOS:**
```bash
brew install poppler
```

**Ubuntu/Debian:**
```bash
sudo apt-get install poppler-utils
```

**Windows:**
Download from: https://github.com/oschwartz10612/poppler-windows/releases/

---

**Tesseract OCR (Optional - if not using Google Vision):**

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

### Frontend Setup

#### 1. Navigate to Frontend Directory
```bash
cd frontend
```

#### 2. Install Node Dependencies
```bash
npm install
```

### Google Vision API Setup

#### 🔑 Step 1: Create Google Cloud Project

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Click **"Select a project"** → **"New Project"**
3. Enter project name (e.g., "document-processing")
4. Click **"Create"**

#### 📦 Step 2: Enable Vision API

1. In the Cloud Console, go to **"APIs & Services"** → **"Library"**
2. Search for **"Cloud Vision API"**
3. Click on it and click **"Enable"**

#### 🔐 Step 3: Create Service Account

1. Go to **"APIs & Services"** → **"Credentials"**
2. Click **"Create Credentials"** → **"Service Account"**
3. Enter a name (e.g., "vision-ocr-service")
4. Click **"Create and Continue"**
5. Select role: **"Project"** → **"Editor"** (or **"Cloud Vision API User"** for minimum permissions)
6. Click **"Continue"** → **"Done"**

#### 📥 Step 4: Download Credentials JSON

1. In **"Credentials"** page, find your service account
2. Click on the service account email
3. Go to **"Keys"** tab
4. Click **"Add Key"** → **"Create new key"**
5. Select **"JSON"** format
6. Click **"Create"** - A JSON file will download

#### 📝 Step 5: Create `google-vision-key.json`

1. In the `backend/` directory, create a file named `google-vision-key.json`
2. Copy the contents of the downloaded JSON file
3. The file should have this structure:

```json
{
  "type": "service_account",
  "project_id": "your-project-id",
  "private_key_id": "your-private-key-id",
  "private_key": "-----BEGIN PRIVATE KEY-----\nYOUR_PRIVATE_KEY\n-----END PRIVATE KEY-----\n",
  "client_email": "your-service-account@your-project.iam.gserviceaccount.com",
  "client_id": "your-client-id",
  "auth_uri": "https://accounts.google.com/o/oauth2/auth",
  "token_uri": "https://oauth2.googleapis.com/token",
  "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
  "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/your-service-account%40your-project.iam.gserviceaccount.com",
  "universe_domain": "googleapis.com"
}
```

**⚠️ Security Note:** 
- This file contains sensitive credentials - **NEVER commit it to git**
- It's already in `.gitignore`
- Keep it secure and private

#### 💰 Cost Considerations

Google Vision API pricing (as of 2024):
- **Free tier**: 1,000 units/month
- **After free tier**: ~$1.50 per 1,000 images
- **For 1,000 letters/month**: ~$4.50/month
- **For this assessment**: Likely free (under 1,000 images)

## ⚙️ Configuration

### Backend Configuration

Create a `.env` file in the `backend/` directory:

```env
# OCR Configuration
OCR_PROVIDER=google  # "google" (recommended) or "tesseract" (fallback)

# Google Vision API
GOOGLE_CREDENTIALS_JSON=google-vision-key.json

# OpenAI API
OPENAI_API_KEY=your_openai_api_key_here
OPENAI_MODEL=gpt-4o-mini

# Data Storage
CSV_PATH=../Extracted Data.csv

# Server Config
UPLOAD_DIR=uploads
MAX_FILE_SIZE=10485760  # 10MB
CORS_ORIGINS=http://localhost:5173
```

**Required Environment Variables:**
- `OPENAI_API_KEY` - Get from https://platform.openai.com/api-keys
- `GOOGLE_CREDENTIALS_JSON` - Path to your Google Vision credentials file

### Frontend Configuration

The frontend is pre-configured to connect to `http://localhost:8000`. 

If you need to change the backend URL, edit `frontend/src/services/api.ts`:

```typescript
const API_BASE_URL = 'http://localhost:8000'
```

## 🎮 Running the Application

### Start Backend Server

```bash
cd backend
source venv/bin/activate  # On Windows: venv\Scripts\activate
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Backend will be available at: **http://localhost:8000**

### Start Frontend Server

In a new terminal:

```bash
cd frontend
npm run dev
```

Frontend will be available at: **http://localhost:5173**

### Access the Application

Open your browser and navigate to: **http://localhost:5173**

## 📚 API Documentation

### Base URL
```
http://localhost:8000
```

### Endpoints

#### GET `/`
Root endpoint with API information

#### GET `/api/health`
Health check endpoint

**Response:**
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "timestamp": "2024-11-11T10:00:00"
}
```

#### POST `/api/process`
Process PDF documents

**Request:**
- Content-Type: `multipart/form-data`
- Body: Multiple PDF files (field name: `files`)

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

### Testing with curl

```bash
# Health check
curl http://localhost:8000/api/health

# Process documents
curl -X POST http://localhost:8000/api/process \
  -F "files=@document1.pdf" \
  -F "files=@document2.pdf"
```

## ✨ Features

### Frontend Features
- ✅ **Drag & Drop File Upload** - Intuitive file selection
- ✅ **Multi-file Processing** - Batch document processing
- ✅ **Real-time Status Updates** - Live progress indicators
- ✅ **Interactive Results Table** - Expandable rows with details
- ✅ **Data Export** - Download as CSV or Excel (.xlsx)
- ✅ **Error Handling** - Comprehensive error messages
- ✅ **Responsive Design** - Mobile-friendly interface
- ✅ **Type Safety** - Full TypeScript integration

### Backend Features
- ✅ **High-Accuracy OCR** - 90%+ accuracy with Google Vision
- ✅ **AI Data Extraction** - GPT-4 powered intelligent extraction
- ✅ **Multi-page Support** - Process complex documents
- ✅ **Automatic Fallback** - Tesseract OCR backup
- ✅ **Concurrent Processing** - Handle multiple files
- ✅ **Data Validation** - Ensure data integrity
- ✅ **Comprehensive Logging** - Track all operations

## 🏢 Deployment

### Backend Deployment

**Option 1: Heroku**
```bash
# Install Heroku CLI
heroku create your-app-name
heroku config:set OPENAI_API_KEY=your_key
heroku config:set GOOGLE_CREDENTIALS_JSON="$(cat google-vision-key.json)"
git push heroku main
```

**Option 2: Docker**
```dockerfile
FROM python:3.9
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Frontend Deployment

**Build for production:**
```bash
cd frontend
npm run build
```

**Deploy to:**
- **Vercel**: `vercel deploy`
- **Netlify**: Drag `dist/` folder to Netlify
- **Static hosting**: Upload `dist/` contents

## 🐛 Troubleshooting

### Backend Issues

**"Poppler not found"**
```bash
# Install poppler (see Installation section)
brew install poppler  # macOS
```

**"Google credentials not found"**
- Ensure `google-vision-key.json` exists in `backend/` directory
- Check `.env` file has correct `GOOGLE_CREDENTIALS_JSON` path
- Verify JSON file structure is correct

**"OpenAI API error"**
- Check your API key is valid
- Ensure you have credits in your OpenAI account
- Verify `OPENAI_API_KEY` in `.env` file

### Frontend Issues

**"Cannot connect to backend"**
- Ensure backend is running on port 8000
- Check CORS settings in backend `.env`
- Verify API URL in `src/services/api.ts`

**"Module not found"**
```bash
cd frontend
rm -rf node_modules package-lock.json
npm install
```

### Performance Issues

**Processing is slow:**
- Google Vision: ~3-8 seconds per page (normal)
- Check your internet connection
- Monitor API rate limits
- Consider processing fewer files at once

## 📊 Performance Metrics

- **PDF Processing**: ~2-5 seconds per page
- **OCR (Google Vision)**: ~3-8 seconds per page
- **AI Extraction**: ~2-4 seconds per document
- **Total**: ~10-30 seconds per multi-page document

## 🔒 Security Best Practices

1. **Never commit credentials:**
   - `google-vision-key.json` ✅ in `.gitignore`
   - `.env` file ✅ in `.gitignore`

2. **Rotate API keys regularly:**
   - OpenAI API keys
   - Google Cloud service accounts

3. **Use environment variables:**
   - Never hardcode sensitive data
   - Use `.env` files for local development
   - Use platform secrets for production

4. **Restrict API access:**
   - Set up CORS properly
   - Use API key restrictions in Google Cloud
   - Implement rate limiting

## 📝 Tech Stack

### Frontend
- **Vue 3.5.13** - Progressive JavaScript framework
- **TypeScript 5.9.3** - Type safety
- **Vite 6.0.3** - Build tool and dev server
- **Tailwind CSS 3.4.1** - Utility-first CSS
- **Axios 1.13.2** - HTTP client
- **XLSX 0.18.5** - Excel export

### Backend
- **FastAPI** - Modern Python web framework
- **Python 3.8+** - Programming language
- **Google Cloud Vision** - OCR service
- **OpenAI GPT-4** - AI extraction
- **Pandas** - Data processing
- **pdf2image** - PDF conversion
- **Pillow** - Image processing

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📄 License

This project is for assessment purposes.

## 💬 Support

For issues or questions:
1. Check the troubleshooting section
2. Review the API documentation
3. Verify all dependencies are installed
4. Check backend and frontend logs

---

**Built with ❤️ using Vue 3, FastAPI, Google Vision AI, and OpenAI GPT-4**

