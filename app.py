import io
import re
import fitz
import streamlit as st


st.set_page_config(page_title="PDF to Markdown", page_icon="📄")

st.title("📄 PDF → Markdown")
st.write("Sube un PDF digital y descarga el contenido en formato `.md`.")

uploaded_file = st.file_uploader("Sube tu PDF", type=["pdf"])


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

        output.append(f"\n\n## Página {page_number}\n\n{text}")

    return "\n".join(output).strip()


if uploaded_file is not None:
    file_bytes = uploaded_file.read()

    try:
        markdown = pdf_to_markdown(file_bytes)

        if not markdown:
            st.warning("No se ha extraído texto. Puede que el PDF sea escaneado y necesite OCR.")
        else:
            st.success("Conversión completada.")

            st.text_area("Vista previa", markdown[:6000], height=350)

            output_filename = uploaded_file.name.rsplit(".", 1)[0] + ".md"

            st.download_button(
                label="Descargar archivo .md",
                data=markdown.encode("utf-8"),
                file_name=output_filename,
                mime="text/markdown",
            )

    except Exception as e:
        st.error(f"Error procesando el PDF: {e}")
