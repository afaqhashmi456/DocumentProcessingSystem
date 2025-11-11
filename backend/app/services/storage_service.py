import os
import logging
import pandas as pd
import fcntl
from typing import Dict, Optional
from datetime import datetime
from pathlib import Path

logger = logging.getLogger(__name__)

class StorageService:
    CSV_COLUMNS = [
        'First name',
        'Middle name',
        'Last name',
        'Date created',
        'DOC #',
        'Facility name',
        'Address',
        'Unit',
        'AI Summary',
        'Raw text'
    ]
    
    def __init__(self, csv_path: str, excel_path: Optional[str] = None):
        self.csv_path = csv_path
        self.excel_path = excel_path
        
        self._ensure_csv_exists()
        
        if self.excel_path:
            self._ensure_excel_exists()
            logger.info(f"StorageService initialized with CSV: {csv_path} and Excel: {excel_path}")
        else:
            logger.info(f"StorageService initialized with CSV: {csv_path}")
    
    def _ensure_csv_exists(self):
        if not os.path.exists(self.csv_path):
            logger.info(f"CSV file not found, creating: {self.csv_path}")
            
            Path(self.csv_path).parent.mkdir(parents=True, exist_ok=True)
            
            df = pd.DataFrame(columns=self.CSV_COLUMNS)
            df.to_csv(self.csv_path, index=False)
            logger.info("CSV file created with headers")
        else:
            logger.debug("CSV file already exists")
    
    def _ensure_excel_exists(self):
        if not os.path.exists(self.excel_path):
            logger.info(f"Excel file not found, creating: {self.excel_path}")
            
            Path(self.excel_path).parent.mkdir(parents=True, exist_ok=True)
            
            df = pd.DataFrame(columns=self.CSV_COLUMNS)
            df.to_excel(self.excel_path, index=False, engine='openpyxl')
            logger.info("Excel file created with headers")
        else:
            logger.debug("Excel file already exists")
    
    def append_to_csv(self, data: Dict) -> None:
        try:
            logger.info("Preparing to append data to storage")
            
            if not self._validate_data(data):
                raise ValueError("Data validation failed")
            
            row_data = {
                'First name': data.get('firstName', ''),
                'Middle name': data.get('middleName', ''),
                'Last name': data.get('lastName', ''),
                'Date created': data.get('dateCreated') or datetime.now().strftime('%Y-%m-%d'),
                'DOC #': data.get('docNumber', ''),
                'Facility name': data.get('facilityName', ''),
                'Address': data.get('address', ''),
                'Unit': data.get('unit', ''),
                'AI Summary': data.get('aiSummary', ''),
                'Raw text': data.get('rawText', '')
            }
            
            with open(self.csv_path, 'r+') as f:
                fcntl.flock(f.fileno(), fcntl.LOCK_EX)
                
                try:
                    df = pd.read_csv(self.csv_path)
                    
                    new_row_df = pd.DataFrame([row_data])
                    df = pd.concat([df, new_row_df], ignore_index=True)
                    
                    f.seek(0)
                    f.truncate()
                    df.to_csv(f, index=False)
                    
                    logger.info("Successfully appended data to CSV")
                    
                finally:
                    fcntl.flock(f.fileno(), fcntl.LOCK_UN)
            
            if self.excel_path:
                self._append_to_excel(row_data)
            
        except Exception as e:
            logger.error(f"Failed to save to storage: {str(e)}")
            raise Exception(f"Storage save failed: {str(e)}")
    
    def _append_to_excel(self, row_data: Dict) -> None:
        try:
            df = pd.read_excel(self.excel_path, engine='openpyxl')
 
            new_row_df = pd.DataFrame([row_data])
            df = pd.concat([df, new_row_df], ignore_index=True)
            
            df.to_excel(self.excel_path, index=False, engine='openpyxl')
            
            logger.info("Successfully appended data to Excel")
            
        except Exception as e:
            logger.error(f"Failed to save to Excel: {str(e)}")
            raise Exception(f"Excel save failed: {str(e)}")
    
    def _validate_data(self, data: Dict) -> bool:
        required_fields = ['firstName', 'lastName', 'docNumber', 'facilityName', 'address']
        
        for field in required_fields:
            if not data.get(field):
                logger.error(f"Missing required field: {field}")
                return False
        
        if len(data.get('firstName', '')) > 100:
            logger.error("First name too long")
            return False
        
        if len(data.get('lastName', '')) > 100:
            logger.error("Last name too long")
            return False
        
        if len(data.get('docNumber', '')) > 50:
            logger.error("DOC number too long")
            return False
        
        logger.debug("Data validation passed")
        return True
    
    def read_csv(self) -> pd.DataFrame:
        try:
            df = pd.read_csv(self.csv_path)
            logger.info(f"Read CSV: {len(df)} rows")
            return df
        except Exception as e:
            logger.error(f"Failed to read CSV: {str(e)}")
            raise
    
    def get_record_count(self) -> int:
        try:
            df = pd.read_csv(self.csv_path)
            return len(df)
        except Exception:
            return 0
    
    def backup_csv(self, backup_path: Optional[str] = None) -> str:
        try:
            if not backup_path:
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                backup_path = f"{self.csv_path}.backup_{timestamp}"
            
            df = pd.read_csv(self.csv_path)
            df.to_csv(backup_path, index=False)
            
            logger.info(f"Created CSV backup: {backup_path}")
            return backup_path
            
        except Exception as e:
            logger.error(f"Backup failed: {str(e)}")
            raise

