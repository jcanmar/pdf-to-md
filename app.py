import io
import re

import fitz
import streamlit as st
from docx import Document


st.set_page_config(page_title="PDF to Markdown / Word", page_icon="📄")

st.title("📄 PDF → Markdown / Word")
st.write("Sube un PDF digital y descarga el contenido en `.md` o `.docx`.")


def clean_text(text: str) -> str:
    text = text.replace("\x00", "")
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def pdf_to_markdown(file_bytes: bytes) -> str:
    doc = fitz.open(stream=file_bytes, filetype="pdf")
    output = []

    for page_number, page in enumerate(doc, start=1):
        text = page.get_text("text")
        text = clean_text(text)

        if text:
            output.append(f"\n\n<!-- Página {page_number} -->\n\n")
            output.append(text)

    return "\n".join(output).strip()


def markdown_to_word(markdown_text: str) -> bytes:
    document = Document()

    for line in markdown_text.splitlines():
        line = line.strip()

        if not line:
            document.add_paragraph()
        elif line.startswith("# "):
            document.add_heading(line.replace("# ", "", 1), level=1)
        elif line.startswith("## "):
            document.add_heading(line.replace("## ", "", 1), level=2)
        elif line.startswith("### "):
            document.add_heading(line.replace("### ", "", 1), level=3)
        elif line.startswith("- "):
            document.add_paragraph(line.replace("- ", "", 1), style="List Bullet")
        elif line.startswith("* "):
            document.add_paragraph(line.replace("* ", "", 1), style="List Bullet")
        elif re.match(r"^\d+\.\s+", line):
            document.add_paragraph(re.sub(r"^\d+\.\s+", "", line), style="List Number")
        elif line.startswith("<!-- Página"):
            page_text = line.replace("<!--", "").replace("-->", "").strip()
            document.add_paragraph(page_text)
        else:
            document.add_paragraph(line)

    buffer = io.BytesIO()
    document.save(buffer)
    buffer.seek(0)
    return buffer.getvalue()


uploaded_file = st.file_uploader("Sube tu PDF", type=["pdf"])

if uploaded_file is not None:
    file_bytes = uploaded_file.read()
    markdown_text = pdf_to_markdown(file_bytes)

    base_name = uploaded_file.name.rsplit(".", 1)[0]
    word_bytes = markdown_to_word(markdown_text)

    st.subheader("Vista previa")
    st.text_area("Contenido extraído", markdown_text[:5000], height=300)

    col1, col2 = st.columns(2)

    with col1:
        st.download_button(
            label="📥 Descargar Markdown (.md)",
            data=markdown_text,
            file_name=f"{base_name}.md",
            mime="text/markdown",
        )

    with col2:
        st.download_button(
            label="📥 Descargar Word (.docx)",
            data=word_bytes,
            file_name=f"{base_name}.docx",
            mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        )
