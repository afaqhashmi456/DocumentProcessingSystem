import json
import logging
import time
from typing import Optional
from openai import OpenAI
from openai import RateLimitError, APIError

logger = logging.getLogger(__name__)


class AIService:
    def __init__(self, api_key: str, model: str = "gpt-4o-mini", 
                 temperature_extraction: float = 0.1, temperature_summary: float = 0.3):
        try:
            self.client = OpenAI(api_key=api_key)
            self.model = model
            self.temperature_extraction = temperature_extraction
            self.temperature_summary = temperature_summary
            logger.info(f"AIService initialized with model: {model} (extraction temp: {temperature_extraction}, summary temp: {temperature_summary})")
            
        except Exception as e:
            logger.error(f"Failed to initialize AI service: {str(e)}")
            raise Exception(f"AI service initialization failed: {str(e)}")
    
    def extract_structured_data(self, raw_text: str, max_retries: int = 3) -> dict:
        prompt = f"""You are extracting INMATE (sender) information from a PRISON LETTER. The inmate is writing TO someone outside prison.

🔍 CRITICAL - CROSS-REFERENCE MULTIPLE SOURCES:
You will find sender information in 3 places: ENVELOPE (PAGE 1), LETTER BODY, and SIGNATURE. Cross-reference ALL sources for accuracy.

📝 EXTRACTION STRATEGY (IN ORDER OF PRIORITY):

**FOR NAMES:**
1. **CHECK ENVELOPE FIRST** (PAGE 1, usually printed/cleaner):
   - Look for "Name:" or "Inmate Name:" field
   - Example: "Name: Ivan Sanchez" or "Name_Ivan Sanchez"
   - Envelope names are usually MORE ACCURATE (printed, not handwritten)

2. **CHECK LETTER BODY** (middle pages):
   - Look for "Hello my name is [Name]"
   - Look for "My legal name is [Name]" or "I go by [Name]"
   - These are usually clear statements

3. **CHECK SIGNATURE AREA** (last, may have handwriting errors):
   - Near "Sincerely", "Thank you", etc.
   - If signature name DIFFERS from envelope/body, PREFER envelope/body
   - Handwritten signatures often have OCR errors

**CROSS-REFERENCE RULE:**
- If envelope says "Ivan Sanchez" but signature says "Fan Sanching" → USE "Ivan Sanchez" (envelope is cleaner)
- If all sources agree → high confidence
- If sources differ → prefer: Envelope > Letter Body > Signature

**FOR DOC NUMBER:**

⚠️ CRITICAL: Extract the VALUE, NOT the label!
- ❌ DON'T extract: "CDCR#:", "IDOC #", "DOC#", "Register Number"
- ✅ DO extract: The actual number that follows

1. **SEARCH MULTIPLE LOCATIONS** (in priority order):
   
   a) **ENVELOPE** - Look for patterns:
      - "CDCR #A12345" → extract "A12345" (not "CDCR #")
      - "CDCR#: BK8702" → extract "BK8702" (not "CDCR#:")
      - "IDOC #101241" → extract "101241" (not "IDOC #")
      - "Register Number 180738" → extract "180738" (not "Register Number")
      
   b) **TOP OF LETTER PAGES** - Look for standalone codes:
      - Often appears in top-right corner
      - Format: Letter+Numbers or just numbers
      - Example: "BK8702" standalone at top
      
   c) **SIGNATURE AREA** - Near sender's name at bottom
   
2. **DOC NUMBER FORMATS BY STATE**:
   - California CDCR: 1-2 Letters + 4-5 digits (e.g., "BK8702", "A32203")
   - Idaho IDOC: 6 digits (e.g., "101241", "180738")
   - Colorado: 6 digits (e.g., "180738")
   
3. **VALIDATION RULES**:
   - ❌ If result contains ":", "#", or spaces → you extracted the LABEL, not VALUE
   - ❌ If result is just text like "CDCR" or "IDOC" → wrong, find the number
   - ✅ Valid formats: "BK8702", "A32203", "101241", "180738"
   - ✅ Should be alphanumeric code matching state patterns above

4. **FALLBACK STRATEGY**:
   - If envelope shows "CDCR#:" but no number after it
   - Search top of page 2 for standalone code matching CDCR format
   - Check near inmate name on any page
   - Look for 6-digit or letter+digit combinations

**FOR UNIT:**
1. **CHECK ENVELOPE** for:
   - "Bldg/Bed: B4-217" → extract "B4-217"
   - "Unit: ABC-123" → extract "ABC-123"
   - "ISCI-F-B-14-B" → extract "F-B-14-B"
   - "Building 4, Bed 217" → extract "4-217"
   
2. **RECOGNIZE UNIT PATTERNS:**
   - "Bldg/Bed" = Building/Bed number = UNIT
   - Format: Letter-Letter-Number-Letter (e.g., "F-B-14-B")
   - Format: Number-Number (e.g., "B4-217" or "34-217")
   - Even if OCR garbled (e.g., "34-217" might be "B4-217")

**FOR FACILITY & ADDRESS:**
- Check envelope return address (top-left, PAGE 1)
- Prison address = P.O. Box format
- Facility name often appears with "Department of Corrections"

🎯 EXTRACT THESE FIELDS:
- **firstName**: Cross-reference envelope, body, signature (prefer envelope if different)
- **middleName**: Middle name/initial if present (null if not found)
- **lastName**: Cross-reference envelope, body, signature (prefer envelope if different)
- **docNumber**: FULL alphanumeric code (e.g., "A32203" not just "203")
- **facilityName**: Full prison name
- **address**: Prison P.O. Box address
- **unit**: Building/bed/unit code from envelope (check "Bldg/Bed" field)

⚠️ CRITICAL RULES TO AVOID ERRORS:
❌ **NEVER** use recipient addresses (street addresses like "500 Westover Dr", "Hustle 2.0", etc.)
❌ **NEVER** prioritize signature over envelope when names differ (envelope is cleaner!)
❌ **NEVER** truncate DOC numbers (keep letter prefixes: "A32203" not "203")
❌ **NEVER** extract field LABELS as values ("CDCR#:", "IDOC #", "Register Number" are LABELS!)
❌ **NEVER** ignore "Bldg/Bed" fields (that's the unit!)
❌ **NEVER** use facility name as DOC number
❌ **NEVER** extract DOC# with symbols like ":", "#" in it (those are part of labels)
✅ **ALWAYS** cross-reference envelope + body + signature
✅ **ALWAYS** prefer envelope names (printed text) over signature (handwritten)
✅ **ALWAYS** extract FULL DOC numbers with any letter prefixes
✅ **ALWAYS** validate DOC# format: should be alphanumeric WITHOUT ":", "#", "CDCR", "IDOC" text
✅ **ALWAYS** check for "Bldg/Bed", "Building", "Unit" for unit extraction
✅ **ALWAYS** use P.O. Box addresses (prisons), not street addresses (recipients)
✅ **ALWAYS** search multiple pages if DOC# incomplete on envelope (check top of letter pages)

🔍 QUALITY CHECKS:
- Does the name in envelope match signature? If not, use envelope.
- Is the DOC number complete? (Check for letter prefixes)
- Does DOC number contain ":", "#", "CDCR", "IDOC" text? If YES → you extracted the LABEL, not the value! Search again!
- Is DOC number a valid alphanumeric code? Examples: "BK8702", "A32203", "101241"
- Did you check the "Bldg/Bed" field on envelope for unit?
- Did you check top of letter pages for DOC# if envelope incomplete?
- Does first name look like it could be a last name? (e.g., "Stevens" is a last name)

📋 COMMON ERRORS TO WATCH FOR:
- "Ivan" misread as "Fan" (I→F) → check envelope
- "Sanchez" misread as "Sanching" (z→ng) → check envelope  
- "B4" misread as "34" (B→3) → check context
- "A32" misread as "ANZ" → look for letter+digit pattern
- "CDCR#:" extracted instead of actual number → this is a LABEL! Find the VALUE!
- DOC# truncated on envelope → search top of letter pages for complete number

Return ONLY this JSON:
{{
    "firstName": "string",
    "middleName": "string or null",
    "lastName": "string",
    "docNumber": "string",
    "facilityName": "string",
    "address": "string",
    "unit": "string or null"
}}

OCR Text:
{raw_text}

JSON Response:"""

        for attempt in range(max_retries):
            try:
                logger.info(f"Extracting structured data (attempt {attempt + 1}/{max_retries})")
                
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {
                            "role": "system",
                            "content": "You are a precise data extraction system. Return only valid JSON, no explanations."
                        },
                        {
                            "role": "user",
                            "content": prompt
                        }
                    ],
                    temperature=self.temperature_extraction,
                    max_tokens=500,
                    response_format={"type": "json_object"}
                )
                
                result_text = response.choices[0].message.content.strip()
                logger.debug(f"GPT-4 extraction response: {result_text}")
                
                extracted_data = json.loads(result_text)
                
                required_fields = ['firstName', 'lastName', 'docNumber', 'facilityName', 'address']
                for field in required_fields:
                    if not extracted_data.get(field):
                        logger.warning(f"Missing required field: {field}")
                        extracted_data[field] = "Unknown"
                
                logger.info("Successfully extracted structured data")
                return extracted_data
                
            except RateLimitError as e:
                logger.warning(f"Rate limit hit, waiting before retry: {str(e)}")
                if attempt < max_retries - 1:
                    time.sleep(2 ** attempt)
                    continue
                raise
                
            except json.JSONDecodeError as e:
                logger.error(f"Failed to parse JSON response: {str(e)}")
                if attempt < max_retries - 1:
                    time.sleep(1)
                    continue
                raise Exception("Failed to extract valid JSON from AI response")
                
            except Exception as e:
                logger.error(f"Extraction failed: {str(e)}")
                if attempt < max_retries - 1:
                    time.sleep(1)
                    continue
                raise
        
        raise Exception("Failed to extract data after maximum retries")
    
    def generate_summary(self, raw_text: str, max_retries: int = 3) -> str:
        prompt = f"""Summarize this prison letter in 1-2 sentences. Focus on the main message, request, or purpose of the letter.

Letter content:
{raw_text[:3000]}

Summary (1-2 sentences):"""

        for attempt in range(max_retries):
            try:
                logger.info(f"Generating summary (attempt {attempt + 1}/{max_retries})")
                
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {
                            "role": "system",
                            "content": "You are a professional summarizer. Create brief, clear summaries."
                        },
                        {
                            "role": "user",
                            "content": prompt
                        }
                    ],
                    temperature=self.temperature_summary,
                    max_tokens=150
                )
                
                summary = response.choices[0].message.content.strip()

                if not summary or len(summary) < 10:
                    logger.warning("Generated summary too short, retrying...")
                    if attempt < max_retries - 1:
                        continue
                    summary = "Letter content could not be summarized effectively."
                
                logger.info(f"Successfully generated summary ({len(summary)} chars)")
                return summary
                
            except RateLimitError as e:
                logger.warning(f"Rate limit hit, waiting before retry: {str(e)}")
                if attempt < max_retries - 1:
                    time.sleep(2 ** attempt)
                    continue
                raise
                
            except Exception as e:
                logger.error(f"Summarization failed: {str(e)}")
                if attempt < max_retries - 1:
                    time.sleep(1)
                    continue
                raise
        
        raise Exception("Failed to generate summary after maximum retries")
    
    def process_document_text(self, raw_text: str) -> dict:
        try:
            logger.info("Starting complete AI processing")
          
            extracted_data = self.extract_structured_data(raw_text)
            
            summary = self.generate_summary(raw_text)
            
            result = {
                **extracted_data,
                'summary': summary
            }
            
            logger.info("Complete AI processing finished successfully")
            return result
            
        except Exception as e:
            logger.error(f"AI processing failed: {str(e)}")
            raise Exception(f"AI processing failed: {str(e)}")

