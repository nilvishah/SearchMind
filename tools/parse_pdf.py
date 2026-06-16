# tools/parse_pdf.py
import fitz  # PyMuPDF
import requests
import tempfile
import os

def parse_pdf(source: str) -> dict:
    """
    Extract text from a PDF file or URL.
    source can be a local file path or a URL ending in .pdf
    """
    try:
        if source.startswith("http"):
            headers = {"User-Agent": "Mozilla/5.0"}
            response = requests.get(source, headers=headers, timeout=15)
            response.raise_for_status()

            with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as f:
                f.write(response.content)
                tmp_path = f.name
        else:
            tmp_path = source

        doc = fitz.open(tmp_path)
        full_text = ""
        page_count = len(doc)  # ← moved here, BEFORE close
        for page in doc:
            full_text += page.get_text()
        doc.close()

        if source.startswith("http"):
            os.unlink(tmp_path)

        full_text = full_text[:3000].strip()

        return {
            "source": source,
            "content": full_text,
            "pages": page_count
        }

    except Exception as e:
        return {
            "source": source,
            "content": f"Failed to parse PDF: {str(e)}",
            "pages": 0
        }