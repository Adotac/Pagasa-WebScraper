import pdfplumber

pdf_path = r'dataset\pdfs\pagasa-25-TC21\PAGASA_25-TC21_Uwan_TCB#05.pdf'

with pdfplumber.open(pdf_path) as pdf:
    print(f"Total pages: {len(pdf.pages)}\n")
    print("="*80)
    for i, page in enumerate(pdf.pages):
        print(f"\n\nPAGE {i+1}")
        print("="*80)
        text = page.extract_text()
        print(text)
        print("\n" + "-"*80)
