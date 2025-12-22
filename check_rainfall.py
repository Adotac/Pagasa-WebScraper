import pdfplumber
import json

# Check PAGASA_22-TC08_Henry_TCA#04.pdf
pdf_path = 'dataset/pdfs/pagasa-22-TC08/PAGASA_22-TC08_Henry_TCA#04.pdf'
with pdfplumber.open(pdf_path) as pdf:
    for i, page in enumerate(pdf.pages[:3]):
        text = page.extract_text() or ""
        if 'hazard' in text.lower():
            idx = text.lower().find('hazard')
            print(f"Page {i+1}:")
            print(text[idx:idx+1500])
            print("\n" + "="*80 + "\n")
            break

# Check annotation
print("\nAnnotation data:")
with open('dataset/pdfs_annotation/PAGASA_22-TC08_Henry_TCA#04.json') as f:
    anno = json.load(f)
    print("rainfall_warning_tags2:")
    print(json.dumps(anno['rainfall_warning_tags2'], indent=2))
