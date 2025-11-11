import io
import logging
from typing import List
from pdf2image import convert_from_bytes
from PIL import Image, ImageEnhance, ImageFilter
logger = logging.getLogger(__name__)

class PDFProcessor:

    def __init__(self, dpi: int = 300, contrast: float = 2.0, sharpness: float = 1.5, brightness: float = 1.1):
        self.dpi = dpi
        self.contrast = contrast
        self.sharpness = sharpness
        self.brightness = brightness
        logger.info(f"PDFProcessor initialized with DPI: {dpi}, Contrast: {contrast}, Sharpness: {sharpness}")
    
    def extract_images(self, pdf_bytes: bytes) -> List[bytes]:
        try:
            logger.info("Converting PDF to images...")
            
            images = convert_from_bytes(
                pdf_bytes,
                dpi=self.dpi,
                fmt='PNG'
            )
            
            logger.info(f"Extracted {len(images)} pages from PDF")
          
            processed_images = []
            for idx, img in enumerate(images):
                logger.debug(f"Processing page {idx + 1}/{len(images)}")
                
                enhanced_img = self.enhance_image(img)
                
                img_bytes = self._image_to_bytes(enhanced_img)
                processed_images.append(img_bytes)
            
            logger.info(f"Successfully processed {len(processed_images)} images")
            return processed_images
            
        except Exception as e:
            logger.error(f"Failed to extract images from PDF: {str(e)}")
            raise Exception(f"PDF processing failed: {str(e)}")
    
    def enhance_image(self, img: Image.Image) -> Image.Image:
        try:
            if img.mode != 'L':
                img = img.convert('L')
                logger.debug("Converted image to grayscale")

            enhancer = ImageEnhance.Contrast(img)
            img = enhancer.enhance(self.contrast)
            logger.debug(f"Enhanced contrast: {self.contrast}x")

            enhancer = ImageEnhance.Sharpness(img)
            img = enhancer.enhance(self.sharpness)
            logger.debug(f"Enhanced sharpness: {self.sharpness}x")

            enhancer = ImageEnhance.Brightness(img)
            img = enhancer.enhance(self.brightness)
            logger.debug(f"Enhanced brightness: {self.brightness}x")
            
            return img
            
        except Exception as e:
            logger.error(f"Image enhancement failed: {str(e)}")
            return img
    
    def _image_to_bytes(self, img: Image.Image, format: str = 'PNG') -> bytes:
        img_byte_arr = io.BytesIO()
        img.save(img_byte_arr, format=format)
        img_byte_arr.seek(0)
        return img_byte_arr.getvalue()
    
    def validate_pdf(self, pdf_bytes: bytes, max_size: int) -> tuple[bool, str]:
        if len(pdf_bytes) > max_size:
            size_mb = len(pdf_bytes) / (1024 * 1024)
            max_mb = max_size / (1024 * 1024)
            return False, f"File too large: {size_mb:.2f}MB (max: {max_mb:.2f}MB)"

        if not pdf_bytes.startswith(b'%PDF'):
            return False, "Invalid PDF file format"
        
        return True, ""

