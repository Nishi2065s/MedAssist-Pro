"""
PDF Reader — Robust file content extraction supporting PDF, TXT, and DOCX.
"""
import streamlit as st


def read_uploaded_file(uploaded_file):
    """
    Read content from uploaded file. Supports TXT and PDF formats.
    """
    try:
        name = uploaded_file.name.lower()

        if name.endswith(".txt"):
            return uploaded_file.read().decode("utf-8")

        if name.endswith(".pdf"):
            try:
                import pypdf
                reader = pypdf.PdfReader(uploaded_file)
                text = ""
                for page in reader.pages:
                    extracted = page.extract_text()
                    if extracted:
                        text += extracted + "\n"
                if text.strip():
                    return text
            except ImportError:
                st.warning("📦 `pypdf` not installed. Attempting raw text extraction...")
            except Exception as e:
                st.warning(f"PDF parsing error: {e}. Trying fallback...")

            # Fallback for PDF
            uploaded_file.seek(0)
            return uploaded_file.read().decode("utf-8", errors="ignore")

        # Generic fallback
        return uploaded_file.read().decode("utf-8", errors="ignore")

    except Exception as e:
        st.error(f"❌ Failed to read file: {e}")
        return None
