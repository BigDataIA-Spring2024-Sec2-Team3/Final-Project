import os
import PyPDF2
import tabula

def extract_text_and_tables(pdf_path):
    # Initialize lists to store extracted text and tables
    text_content = []
    tables = []
    
    # Open the PDF file
    with open(pdf_path, 'rb') as file:
        # Create a PDF reader object
        pdf_reader = PyPDF2.PdfReader(file)
        
        # Extract text from each page
        for page_num in range(len(pdf_reader.pages)):
            page = pdf_reader.pages[page_num]
            text_content.append(page.extract_text())
            
            # Extract tables from each page using tabula-py
            page_tables = tabula.read_pdf(pdf_path, pages=page_num+1, multiple_tables=True)
            if page_tables:
                tables.extend(page_tables)
    
    return text_content, tables

def save_text_to_file(text_content, pdf_name):
    # Generate the file name
    txt_file_name = pdf_name.replace('.pdf', '_text.txt')
    
    # Write the extracted text to a text file
    with open(txt_file_name, 'w') as file:
        for text in text_content:
            file.write(text)
            file.write('\n\n')

def main():
    # Path to the data folder
    data_folder = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'data'))

    # Iterate over each file in the data folder
    for filename in os.listdir(data_folder):
        if filename.endswith(".pdf"):
            pdf_path = os.path.join(data_folder, filename)
            print(f"Processing {pdf_path}...")
            # Extract text and tables from the PDF file
            text_content, _ = extract_text_and_tables(pdf_path)
            
            # Save the extracted text to a text file
            save_text_to_file(text_content, pdf_path)
            print(f"Text content saved to {pdf_path.replace('.pdf', '_text.txt')}")

    print("All text files saved successfully!")

if __name__ == "__main__":
    main()