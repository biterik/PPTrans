#!/usr/bin/env python3
"""
Test alternative translation approaches to bypass the googletrans API issues
"""

def test_direct_requests_translation():
    """Test using direct requests to Google Translate"""
    import requests
    import json
    from urllib.parse import quote
    
    def translate_with_requests(text, source='de', target='en'):
        """Translate using direct HTTP requests to Google Translate"""
        try:
            # URL encode the text
            encoded_text = quote(text)
            
            # Google Translate URL (this is the public interface)
            url = f"https://translate.googleapis.com/translate_a/single"
            params = {
                'client': 'gtx',
                'sl': source,
                'tl': target,
                'dt': 't',
                'q': text
            }
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
            }
            
            response = requests.get(url, params=params, headers=headers, timeout=10)
            
            if response.status_code == 200:
                result = response.json()
                
                # Extract translation from the response
                if result and isinstance(result, list) and len(result) > 0:
                    translations = result[0]
                    if isinstance(translations, list) and len(translations) > 0:
                        translated_text = translations[0][0]
                        return translated_text
            
            return None
            
        except Exception as e:
            print(f"Request translation failed: {e}")
            return None
    
    # Test translations
    test_texts = [
        "Hallo Welt",
        "Guten Tag",
        "Wie geht es dir?",
        "STUDIEREN AM CAMPUS SCHWÄBISCH HALL"
    ]
    
    print("=== Testing Direct Requests Translation ===")
    successful_translations = 0
    
    for text in test_texts:
        result = translate_with_requests(text)
        if result and result != text:
            print(f"✅ '{text}' → '{result}'")
            successful_translations += 1
        else:
            print(f"❌ '{text}' → Failed or no change")
    
    return successful_translations > 0

def test_alternative_googletrans():
    """Test alternative googletrans usage patterns"""
    try:
        from googletrans import Translator
        import time
        
        print("\n=== Testing Alternative googletrans Patterns ===")
        
        # Try different initialization methods
        translators_to_try = [
            Translator(),
            Translator(service_urls=['translate.google.com']),
            Translator(service_urls=['translate.google.co.kr']),
        ]
        
        test_text = "Hallo Welt"
        successful_translations = 0
        
        for i, translator in enumerate(translators_to_try):
            try:
                print(f"Trying translator {i+1}...")
                result = translator.translate(test_text, src='de', dest='en')
                
                # Try multiple extraction methods
                extracted_text = None
                
                if hasattr(result, 'text') and result.text:
                    extracted_text = result.text
                elif isinstance(result, str):
                    extracted_text = result
                elif hasattr(result, '__dict__'):
                    # Try to find text in the object attributes
                    for attr_name in ['text', 'translatedText', 'translation']:
                        if hasattr(result, attr_name):
                            attr_value = getattr(result, attr_name)
                            if isinstance(attr_value, str) and attr_value.strip():
                                extracted_text = attr_value
                                break
                
                if extracted_text and extracted_text.strip() and extracted_text != test_text:
                    print(f"✅ Translator {i+1}: '{test_text}' → '{extracted_text}'")
                    successful_translations += 1
                else:
                    print(f"❌ Translator {i+1}: Failed to extract valid translation")
                    
            except Exception as e:
                print(f"❌ Translator {i+1}: Error - {e}")
            
            # Small delay between attempts
            time.sleep(0.5)
        
        return successful_translations > 0
        
    except ImportError:
        print("googletrans not available")
        return False

def test_manual_translation_mapping():
    """Test a manual translation mapping for common terms"""
    
    print("\n=== Testing Manual Translation Mapping ===")
    
    # Common German-English translations for academic/university context
    manual_translations = {
        'STUDIEREN': 'STUDYING',
        'CAMPUS': 'CAMPUS',
        'HALL': 'HALL',
        'Informationsveranstaltung': 'Information Event',
        'Themenschwerpunkte': 'Main Topics',
        'Hochschul Account': 'University Account',
        'Netzzugang': 'Network Access',
        'WLAN': 'WIFI',
        'VPN': 'VPN',
        'Drucken': 'Printing',
        'Scannen': 'Scanning',
        'Kopieren': 'Copying',
        'Software für Studierende': 'Software for Students',
        'Termine': 'Appointments',
        'Ansprechpartner': 'Contact Person',
        'Raum': 'Room',
        'Praktisches Studiensemester': 'Practical Study Semester',
        'Ausland': 'Abroad',
        'Partnerhochschulen': 'Partner Universities',
        'Studieren im Ausland': 'Studying Abroad'
    }
    
    def translate_with_mapping(text):
        """Simple translation using word mapping"""
        translated = text
        for german, english in manual_translations.items():
            if german.lower() in text.lower():
                translated = translated.replace(german, english)
        return translated
    
    test_texts = [
        'STUDIEREN AM CAMPUS SCHWÄBISCH HALL',
        'Informationsveranstaltung des Rechenzentrums',
        'Software für Studierende',
        'Praktisches Studiensemester im Ausland'
    ]
    
    successful_translations = 0
    for text in test_texts:
        result = translate_with_mapping(text)
        if result != text:
            print(f"✅ '{text}' → '{result}'")
            successful_translations += 1
        else:
            print(f"→ '{text}' (no mapping available)")
    
    return successful_translations > 0

def main():
    """Test all alternative translation methods"""
    print("Alternative Translation Methods Test")
    print("=" * 50)
    
    methods_working = []
    
    # Test direct requests
    if test_direct_requests_translation():
        methods_working.append("Direct HTTP Requests")
    
    # Test alternative googletrans patterns
    if test_alternative_googletrans():
        methods_working.append("Alternative googletrans")
    
    # Test manual mapping
    if test_manual_translation_mapping():
        methods_working.append("Manual Translation Mapping")
    
    print("\n" + "=" * 50)
    print("🔍 Results Summary:")
    
    if methods_working:
        print(f"✅ Working methods: {', '.join(methods_working)}")
        print("\nRecommendation: Implement the most reliable working method")
    else:
        print("❌ No translation methods are currently working")
        print("This suggests a broader issue with Google Translate access")
    
    print("\nNext steps:")
    print("1. Try the working method(s) above")
    print("2. Consider using a different translation service (DeepL, Azure, etc.)")
    print("3. For now, focus on fixing the PowerPoint text application issue")

if __name__ == "__main__":
    main()
