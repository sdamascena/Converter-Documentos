from pathlib import Path
from io import BytesIO
import streamlit as st
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from PyPDF2 import PdfReader, PdfWriter
from utilidades import pegar_dados_pdf


def exibir_menu_marca_dagua(coluna):
    """Exibe o menu para adicionar uma marca d'água com texto sobre todas as páginas de um PDF."""
    with coluna:
        st.markdown("""
        # Adicionar marca d'água com texto

        Digite o texto e selecione um PDF para aplicar a marca d'água:
        """)

        texto_marca = st.text_input("Digite o texto da marca d'água", value="Confidencial")
        arquivo_pdf = st.file_uploader("Selecione o arquivo PDF...", type="pdf")

        if arquivo_pdf and texto_marca.strip():
            if st.button("Clique para processar o arquivo PDF...", use_container_width=True):
                marca_pdf = gerar_pdf_com_texto(texto_marca)
                dados_pdf = aplicar_marca_dagua_texto(arquivo_pdf, marca_pdf)
                nome_arquivo = f"{Path(arquivo_pdf.name).stem}_com_marca.pdf"
                st.download_button(
                    "Clique para baixar o PDF com marca d'água...",
                    data=dados_pdf,
                    file_name=nome_arquivo,
                    mime="application/pdf",
                    use_container_width=True
                )


def gerar_pdf_com_texto(texto):
    """Gera um PDF com texto da marca d’água espalhado na página."""
    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter

    c.setFont("Helvetica", 30)
    c.setFillGray(0.6, 0.2)

    step_x = 200
    step_y = 150

    for x in range(0, int(width) + step_x, step_x):
        for y in range(0, int(height) + step_y, step_y):
            c.saveState()
            c.translate(x, y)
            c.rotate(45)
            c.drawCentredString(0, 0, texto)
            c.restoreState()

    c.showPage()
    c.save()
    buffer.seek(0)
    return buffer


def aplicar_marca_dagua_texto(arquivo_pdf, marca_pdf_buffer):
    """Aplica a marca d'água em cada página do PDF original usando PyPDF2."""
    leitor_pdf = PdfReader(arquivo_pdf)
    marca_pdf = PdfReader(marca_pdf_buffer)
    pagina_marca = marca_pdf.pages[0]

    escritor = PdfWriter()
    for pagina in leitor_pdf.pages:
        pagina.merge_page(pagina_marca)  # PyPDF2 não tem transformações, apenas merge simples
        escritor.add_page(pagina)

    buffer = BytesIO()
    escritor.write(buffer)
    buffer.seek(0)
    return buffer.read()
