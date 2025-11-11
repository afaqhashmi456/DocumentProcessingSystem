from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional
from pathlib import Path

class Settings(BaseSettings):
    openai_api_key: str = ""
    openai_model: str = "gpt-4o-mini"
    openai_temperature_extraction: float = 0.1
    openai_temperature_summary: float = 0.3
    openai_max_retries: int = 3
    
    ocr_provider: str = "google"
    google_credentials_json: str = ""
    tesseract_dpi: int = 300
    tesseract_psm: int = 6
    tesseract_oem: int = 3
    
    max_file_size: int = 10485760 
    upload_dir: str = "uploads"
    allowed_extensions: list[str] = [".pdf"]
    
    csv_path: str = "../Extracted Data.csv"
    excel_path: str = "../Extracted Data.xlsx"
    csv_columns: list[str] = [
        "First name", "Middle name", "Last name", "Date created",
        "DOC #", "Facility name", "Address", "Unit",
        "AI Summary", "Raw text"
    ]
    
    api_title: str = "Document Processing API"
    api_description: str = "OCR and AI-powered document extraction system"
    api_version: str = "1.0.0"
    cors_origins: str = "http://localhost:5173"
    host: str = "0.0.0.0"
    port: int = 8000
    
    image_contrast_factor: float = 2.0
    image_sharpness_factor: float = 1.5
    image_brightness_factor: float = 1.1
    
    log_level: str = "INFO"
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )
    
    def validate_settings(self) -> tuple[bool, list[str]]:
        errors = []
        
        if not self.openai_api_key or self.openai_api_key == "placeholder-key":
            errors.append("OpenAI API key not configured (AI features will be unavailable)")
        
        if self.max_file_size < 1024 * 1024:
            errors.append(f"MAX_FILE_SIZE too small: {self.max_file_size} bytes")
        
        csv_file = Path(self.csv_path)
        if not csv_file.parent.exists():
            errors.append(f"CSV directory does not exist: {csv_file.parent}")
        
        return len(errors) == 0, errors

settings = Settings()

is_valid, errors = settings.validate_settings()
if not is_valid:
    import logging
    logger = logging.getLogger(__name__)
    for error in errors:
        logger.warning(f"Configuration warning: {error}")
