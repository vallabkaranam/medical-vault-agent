import os
import json
from typing import List, Dict
    StandardizationResult, VaccineRecord, VaccineStatus, VaccineName, ComplianceStandard,
    TranscriptionResult, TranslationResult, LanguageCode
)

def perform_standardization(standard: str, extracted_vaccines: List[Dict]) -> StandardizationResult:
    """
    Shared helper to standardize extracted vaccines against a compliance standard.
    """
    # Define required vaccines per standard
    required_vaccines_map = {
        "us_cdc": {VaccineName.MMR, VaccineName.TETANUS, VaccineName.HEPATITIS_B},
        "cornell_tech": {VaccineName.MMR, VaccineName.TETANUS, VaccineName.HEPATITIS_B, 
                       VaccineName.MENINGOCOCCAL, VaccineName.TB_TEST},
        "uk_nhs": {VaccineName.MMR, VaccineName.TETANUS, VaccineName.MENINGOCOCCAL},
        "canada_health": {VaccineName.MMR, VaccineName.TETANUS, VaccineName.HEPATITIS_B, VaccineName.VARICELLA}
    }
    
    # Helper map for common variations if AI misses exact Enum match
    name_mapping = {
        "MMR II": VaccineName.MMR,
        "Measles Mumps Rubella": VaccineName.MMR,
        "Td": VaccineName.TETANUS,
        "DTap": VaccineName.TDAP,
        "Varicella Zoster": VaccineName.VARICELLA,
        "Chicken Pox": VaccineName.VARICELLA,
        "Meningitis": VaccineName.MENINGOCOCCAL,
        "PPD": VaccineName.TB_TEST,
        "Mantoux": VaccineName.TB_TEST
    }

    vaccine_records = []
    for vax in extracted_vaccines:
        v_name_str = vax.get("vaccine_name", "")
        
        # Try direct Enum match
        try:
            v_name_enum = VaccineName(v_name_str)
        except ValueError:
            # Try mapping
            v_name_enum = name_mapping.get(v_name_str)
            
            # If still not found, try case-insensitive match against Enum values
            if not v_name_enum:
                for member in VaccineName:
                    if member.value.lower() == v_name_str.lower():
                        v_name_enum = member
                        break
            
            # If still not found, map to OTHER
            if not v_name_enum:
                v_name_enum = VaccineName.OTHER

        vaccine_records.append(
            VaccineRecord(
                vaccine_name=v_name_enum,
                date=vax.get("date", ""),
                status=VaccineStatus.COMPLIANT,
                original_text=vax.get("original_text", ""),
                translated_text=vax.get("original_text"), # Fallback
                lot_number=vax.get("lot_number"),
                provider=vax.get("provider")
            )
        )
    
    # Calculate compliance
    extracted_names = {r.vaccine_name for r in vaccine_records}
    required = required_vaccines_map.get(standard, set())
    missing = list(required - extracted_names)
    is_compliant = len(missing) == 0
    
    # Handle standard enum conversion safely
    try:
        std_enum = ComplianceStandard(standard)
    except ValueError:
        # Fallback to US CDC if invalid standard string passed
        std_enum = ComplianceStandard.US_CDC

    return StandardizationResult(
        standard=std_enum,
        is_compliant=is_compliant,
        records=vaccine_records,
        missing_vaccines=missing,
        compliance_notes=f"Validated against {standard.upper()} requirements. " +
                        (f"Missing: {', '.join([v.value for v in missing])}" if missing else "All required vaccines present.")
    )

async def analyze_image_with_ai(file_bytes: bytes, openai_api_key: str) -> dict:
    """
    Shared helper to send image to OpenAI Vision API and extract data.
    Returns the raw JSON response from the AI.
    """
    # CHECK FOR MOCK MODE TO SAVE COSTS
    if os.getenv("MOCK_AI", "false").lower() == "true":
        print("🔮 USING MOCK AI RESPONSE (Cost Saving Mode)")
        import asyncio
        await asyncio.sleep(2.0) # Simulate network delay for "magical" feel
        return {
            "raw_text": "MOCK DATA: MMR Vaccine - 05/15/2023, Lot: ABC123, Provider: University Health Center\n"
                        "Tdap - 11/20/2023, Lot: GSK-456, Provider: Walgreens",
            "detected_language": "en",
            "confidence": 0.98,
            "translation": {
                "original_text": "",
                "translated_text": "",
                "confidence": 1.0
            },
            "structured_data": {
                "dates": ["2023-05-15", "2023-11-20"],
                "vaccines": ["MMR", "Tdap"],
                "lot_numbers": ["ABC123", "GSK-456"]
            },
            "extracted_vaccines": [
                {
                    "vaccine_name": "MMR",
                    "date": "2023-05-15",
                    "original_text": "MMR Vaccine - 05/15/2023",
                    "lot_number": "ABC123",
                    "provider": "University Health Center"
                },
                {
                    "vaccine_name": "Tdap",
                    "date": "2023-11-20",
                    "original_text": "Tdap - 11/20/2023",
                    "lot_number": "GSK-456",
                    "provider": "Walgreens"
                }
            ]
        }

    from openai import OpenAI
    import base64
    
    client = OpenAI(api_key=openai_api_key)
    
    # Encode image
    base64_image = base64.b64encode(file_bytes).decode('utf-8')
    
    system_prompt = """You are a medical document OCR and extraction expert. 
    Your task is to analyze a vaccination record image and extract structured data.
    
    Perform the following steps:
    1. TRANSCRIPTION: Extract all visible text.
    2. LANGUAGE DETECTION: Detect the primary language.
    3. TRANSLATION: If not English, provide an English translation of the key medical text.
    4. EXTRACTION: Extract vaccine records into a structured list.
    
    For each vaccine record, try to normalize the 'vaccine_name' to one of these standard values if possible:
    MMR, Measles, Mumps, Rubella, Tetanus, Diphtheria, Pertussis, Tdap, Hepatitis A, Hepatitis B, 
    Varicella, Meningococcal, COVID-19, Influenza, HPV, Polio, TB Test.
    If it doesn't match, use the raw name.
    
    Return ONLY a JSON object with this structure:
    {
        "raw_text": "full extracted text...",
        "detected_language": "en" (or "es", "fr", etc.),
        "confidence": 0.95,
        "translation": {
            "original_text": "...",
            "translated_text": "...",
            "confidence": 1.0
        },
        "structured_data": {
            "dates": ["YYYY-MM-DD", ...],
            "vaccines": ["Name1", "Name2"],
            "lot_numbers": ["..."]
        },
        "extracted_vaccines": [
            {
                "vaccine_name": "Standardized Or Raw Name",
                "date": "YYYY-MM-DD",
                "original_text": "Line from doc",
                "lot_number": "...",
                "provider": "..."
            }
        ]
    }
    """
    
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {
                "role": "system",
                "content": system_prompt
            },
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": "Analyze this vaccination record."},
                    {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}}
                ]
            }
        ],
        response_format={"type": "json_object"},
        temperature=0.0
    )
    
    return json.loads(response.choices[0].message.content)

def process_ai_result(data: dict) -> tuple[TranscriptionResult, TranslationResult, List[Dict]]:
    """
    Shared helper to convert raw AI JSON into typed Pydantic models for the pipeline stages.
    Returns: (transcription, translation, extracted_vaccines)
    """
    # Stage 1: Transcription
    transcription = TranscriptionResult(
        raw_text=data.get("raw_text", ""),
        detected_language=LanguageCode(data.get("detected_language", "en")) if data.get("detected_language") in [l.value for l in LanguageCode] else LanguageCode.UNKNOWN,
        confidence=data.get("confidence", 0.0),
        structured_data=data.get("structured_data", {})
    )
    
    # Stage 2: Translation
    trans_data = data.get("translation", {})
    translation = TranslationResult(
        original_text=trans_data.get("original_text", transcription.raw_text),
        translated_text=trans_data.get("translated_text", transcription.raw_text),
        source_language=transcription.detected_language,
        target_language=LanguageCode.ENGLISH,
        translation_confidence=trans_data.get("confidence", 1.0)
    )
    
    # Extracted Vaccines (Raw)
    extracted_vaccines = data.get("extracted_vaccines", [])
    
    return transcription, translation, extracted_vaccines
