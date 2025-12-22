from typhoon_extraction_ml import TyphoonBulletinExtractor
import json

# Test extraction
print('Testing extraction without ML dependencies...')
extractor = TyphoonBulletinExtractor()
result = extractor.extract_from_pdf('dataset/pdfs/pagasa-25-TC21/PAGASA_25-TC21_Uwan_TCB#05.pdf')

# Verify all fields exist
required_fields = [
    'typhoon_location_text', 'typhoon_movement', 'typhoon_windspeed', 'updated_datetime',
    'signal_warning_tags1', 'signal_warning_tags2', 'signal_warning_tags3', 
    'signal_warning_tags4', 'signal_warning_tags5',
    'rainfall_warning_tags1', 'rainfall_warning_tags2', 'rainfall_warning_tags3'
]

print('\nField verification:')
all_present = True
for field in required_fields:
    if field in result:
        print(f'  ✓ {field}')
    else:
        print(f'  ✗ {field} MISSING')
        all_present = False

if all_present:
    print('\n✓ All required fields present!')
    print('\nSample extraction:')
    print(f'  Location: {result["typhoon_location_text"][:60]}...')
    print(f'  Movement: {result["typhoon_movement"]}')
    print(f'  DateTime: {result["updated_datetime"]}')
else:
    print('\n✗ Some fields missing!')
