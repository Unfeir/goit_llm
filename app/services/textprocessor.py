from PyPDF2 import PdfReader

# https://pypdf2.readthedocs.io/en/3.0.0/search.html?q=async&check_keywords=yes&area=default
def get_txt_from_pdf(file: str) -> str:
    # creating a pdf reader object
    reader = PdfReader(file)
    text = ''

    for page in range(len(reader.pages)):
        text += reader.pages[page].extract_text()

    return text
    