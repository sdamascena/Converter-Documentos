import io
import tempfile
import pandas as pd
from pathlib import Path
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.lib.utils import ImageReader
from reportlab.lib import colors
from reportlab.platypus import Table, TableStyle, SimpleDocTemplate, Paragraph, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet
import streamlit as st

def exibir_menu_relatorio(coluna):
    with coluna:
        st.markdown("""
            # Conversor Inteligente de Excel para PDF

            Transforme seus dados Excel em relatórios PDF com estilo:
        """)
        arquivo_excel = st.file_uploader(
            "Selecione o arquivo Excel...",
            type='xlsx',
            accept_multiple_files=False,
        )

        titulo_relatorio = st.text_input("Título do relatório (ex: Relatório Financeiro)", value="Relatório Personalizado")
        logotipo = st.file_uploader("Selecione um logotipo (opcional)", type=['png', 'jpg', 'jpeg'])

        clicou_processar = st.button(
            "Converter para PDF",
            disabled=not arquivo_excel,
            use_container_width=True,
        )

        if clicou_processar:
            logotipo_path = None
            if logotipo:
                temp_logo = tempfile.NamedTemporaryFile(delete=False, suffix=".png")
                temp_logo.write(logotipo.read())
                temp_logo.flush()
                logotipo_path = temp_logo.name

            dados_pdf = converter_excel_para_pdf(arquivo_excel, logotipo_path, titulo_relatorio)
            st.download_button(
                "📄 Baixar PDF Gerado",
                data=dados_pdf,
                file_name="relatorio_convertido.pdf",
                mime="application/pdf",
                use_container_width=True,
            )

def converter_excel_para_pdf(arquivo_excel, logotipo_path=None, titulo=""):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, leftMargin=1.5*cm, rightMargin=1.5*cm, topMargin=3.5*cm, bottomMargin=2*cm)
    elements = []
    styles = getSampleStyleSheet()

    excel = pd.read_excel(arquivo_excel, sheet_name=None)

    for nome_aba, df in excel.items():
        if logotipo_path:
            try:
                img = Image(logotipo_path, width=3*cm, height=1.5*cm)
                elements.append(img)
            except Exception as e:
                print(f"Erro ao carregar logotipo: {e}")

        titulo_completo = f"<b>{titulo} - {nome_aba}</b>" if titulo else f"<b>{nome_aba}</b>"
        elements.append(Paragraph(titulo_completo, styles['Title']))
        elements.append(Spacer(1, 12))

        data = [df.columns.tolist()] + df.astype(str).values.tolist()
        table = Table(data, repeatRows=1)
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#f0f0f0")),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.HexColor("#000000")),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('BACKGROUND', (0, 1), (-1, -1), colors.white)
        ]))

        elements.append(table)
        elements.append(Spacer(1, 24))

    doc.build(elements)
    buffer.seek(0)
    return buffer.read()