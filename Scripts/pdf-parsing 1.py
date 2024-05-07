import camelot
from PyPDF2 import PdfReader

def extract_text_and_tables(pdf_path):
    # Initialize lists to store extracted text and tables
    text_content = []
    tables = []

    # Open the PDF file
    pdf = PdfReader(pdf_path)
    pdf_reader = pdf.pages

    # Extract text from each page
    for page in pdf_reader:
        text = page.extract_text()
        text_content.append(text)

    # Extract tables from the PDF file using camelot
    tables_from_pdf = camelot.read_pdf(pdf_path, pages='all') # type: ignore

    # Append the extracted tables to the tables list
    for table in tables_from_pdf:
        tables.append(table.df)

    return text_content, tables

def save_text_to_file(text_content, pdf_name):
    # Generate the file name
    txt_file_name = pdf_name.replace('.pdf', '_text.txt')

    # Write the extracted text to a text file
    with open(txt_file_name, 'w') as file:
        for text in text_content:
            file.write(text)
            file.write('\n\n')

# Paths to the PDF files
pdf_paths = [
    "sample-level-i-questions.pdf",
    "sample-level-II-itemset-questions.pdf",
    "sample-level-III-itemset-questions.pdf"
]

# Iterate over each PDF file
for pdf_path in pdf_paths:
    print(f"Processing {pdf_path}...")
    # Extract text and tables from the PDF file
    text_content, tables = extract_text_and_tables(pdf_path)

    # Save the extracted text to a text file
    save_text_to_file(text_content, pdf_path)
    print(f"Text content saved to {pdf_path.replace('.pdf', '_text.txt')}")

    # Print the extracted tables (assuming multiple tables are present)
    for i, table in enumerate(tables, start=1):
        print(f"Table {i}:")
        print(table)

    print("All text files and tables saved successfully!")
