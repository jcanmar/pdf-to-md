import io
import re

import fitz
import streamlit as st
from docx import Document


st.set_page_config(
    page_title="PDF → Markdown / Word",
    page_icon="📄",
)

st.title("📄 PDF → Markdown / Word")
st.write(
    "Sube un PDF digital y descarga el contenido en formato Markdown (.md) o Word (.docx)."
)


def clean_text(text):
    text = text.replace("\x00", "")
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def pdf_to_markdown(file_bytes):
    doc = fitz.open(stream=file_bytes, filetype="pdf")

    output = []

    for page_num, page in enumerate(doc, start=1):
        text = page.get_text()

        text = clean_text(text)

        if not text:
            continue

        output.append(f"\n# Página {page_num}\n")
        output.append(text)

    return "\n\n".join(output)


def markdown_to_word(markdown_text):
    document = Document()

    for line in markdown_text.splitlines():
        line = line.strip()

        if not line:
            document.add_paragraph()
            continue

        if line.startswith("# "):
            document.add_heading(line[2:], level=1)

        elif line.startswith("## "):
            document.add_heading(line[3:], level=2)

        elif line.startswith("### "):
            document.add_heading(line[4:], level=3)

        elif line.startswith("- "):
            document.add_paragraph(
                line[2:],
                style="List Bullet"
            )

        else:
            document.add_paragraph(line)

    buffer = io.BytesIO()
    document.save(buffer)
    buffer.seek(0)

    return buffer.getvalue()


uploaded_file = st.file_uploader(
    "Selecciona un PDF",
    type=["pdf"]
)

if uploaded_file:

    pdf_bytes = uploaded_file.read()

    markdown_text = pdf_to_markdown(pdf_bytes)

    st.subheader("Vista previa")

    st.text_area(
        "Contenido extraído",
        markdown_text[:10000],
        height=350
    )

    word_bytes = markdown_to_word(markdown_text)

    base_name = uploaded_file.name.rsplit(".", 1)[0]

    col1, col2 = st.columns(2)

    with col1:
        st.download_button(
            "📥 Descargar Markdown (.md)",
            markdown_text,
            file_name=f"{base_name}.md",
            mime="text/markdown",
        )

    with col2:
        st.download_button(
            "📥 Descargar Word (.docx)",
            word_bytes,
            file_name=f"{base_name}.docx",
            mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        )
