import io
import pypdf
import docx


class DocumentParser:
    """
    Utility service to extract clean text from uploaded .txt, .pdf, and .docx documents.
    """

    @staticmethod
    def parse_txt(file_bytes: bytes) -> str:
        """
        Parses standard plain text document byte buffers.
        """
        try:
            return file_bytes.decode("utf-8")
        except UnicodeDecodeError:
            # Fallback to latin-1 encoding if UTF-8 fails
            return file_bytes.decode("latin-1")

    @staticmethod
    def parse_pdf(file_bytes: bytes) -> str:
        """
        Extracts raw text content from PDF file streams using pypdf.
        """
        pdf_file = io.BytesIO(file_bytes)
        reader = pypdf.PdfReader(pdf_file)
        
        extracted_pages = []
        for page in reader.pages:
            text = page.extract_text()
            if text:
                extracted_pages.append(text)
                
        return "\n".join(extracted_pages)

    @staticmethod
    def parse_docx(file_bytes: bytes) -> str:
        """
        Extracts raw text content from Microsoft Word DOCX files.
        """
        docx_file = io.BytesIO(file_bytes)
        doc = docx.Document(docx_file)
        
        paragraphs = [p.text for p in doc.paragraphs if p.text]
        return "\n".join(paragraphs)

    @classmethod
    def extract_text(cls, filename: str, file_bytes: bytes) -> str:
        """
        Detects file extension and routes to appropriate parser method.
        """
        ext = filename.split(".")[-1].lower()
        
        if ext == "txt":
            return cls.parse_txt(file_bytes)
        elif ext == "pdf":
            return cls.parse_pdf(file_bytes)
        elif ext == "docx":
            return cls.parse_docx(file_bytes)
        else:
            raise ValueError(f"Unsupported file format: {ext}. Only txt, pdf, docx allowed.")
