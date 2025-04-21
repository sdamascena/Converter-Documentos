from pathlib import Path
from io import BytesIO
import streamlit as st
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
import pypdf
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
    """Gera um PDF com várias repetições do texto da marca d’água em grade."""
    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter

    c.setFont("Helvetica", 30)
    c.setFillGray(0.6, 0.2)  # tom de cinza + transparência

    step_x = 200  # espaço horizontal entre marcas
    step_y = 150  # espaço vertical entre marcas

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
    """Aplica a marca d'água de texto em cada página do PDF original."""
    leitor_pdf = pypdf.PdfReader(arquivo_pdf)
    marca_pdf = pypdf.PdfReader(marca_pdf_buffer)
    pagina_marca = marca_pdf.pages[0]

    escritor = pypdf.PdfWriter()

    for pagina in leitor_pdf.pages:
        escala_x = pagina.mediabox.width / pagina_marca.mediabox.width
        escala_y = pagina.mediabox.height / pagina_marca.mediabox.height
        escala = min(escala_x, escala_y)

        largura_marca = pagina_marca.mediabox.width * escala
        altura_marca = pagina_marca.mediabox.height * escala

        desloc_x = (pagina.mediabox.width - largura_marca) / 2
        desloc_y = (pagina.mediabox.height - altura_marca) / 2

        transf = pypdf.Transformation().scale(escala).translate(tx=desloc_x, ty=desloc_y)
        pagina.merge_transformed_page(pagina_marca, transf, over=True)
        escritor.add_page(pagina)

    buffer = BytesIO()
    escritor.write(buffer)
    buffer.seek(0)
    return buffer.read()