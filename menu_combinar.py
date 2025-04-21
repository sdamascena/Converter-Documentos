import pdfkit
from PyPDF2 import PdfReader, PdfWriter
from projeto_pdf_excel.caminhos import PASTA_DADOS, PASTA_ASSETS, PASTA_OUTPUT
from projeto_pdf_excel.formatacao_de_dados import pegar_template_renderizado

CONFIG = {
    'mes_referencia': '2023-02',
    'pasta_dados': PASTA_DADOS,
    'arquivo_excel': 'dados.xlsx',
    'pasta_assets': PASTA_ASSETS,
    'arquivo_template': 'template.jinja',
    'arquivo_css': 'style.css',
    'pasta_output': PASTA_OUTPUT,
    'arquivo_layout': 'layout_relatorio.pdf'
}


def main(
        mes_referencia,
        pasta_dados,
        arquivo_excel,
        pasta_assets,
        arquivo_template,
        arquivo_css,
        pasta_output,
        arquivo_layout,
) -> None:
    print('Iniciando geração de relatório...')
    pasta_output.mkdir(exist_ok=True, parents=True)

    string_html = pegar_template_renderizado(
        mes_referencia=mes_referencia,
        pasta_dados=pasta_dados,
        arquivo_excel=arquivo_excel,
        pasta_assets=pasta_assets,
        arquivo_template=arquivo_template,
        arquivo_css=arquivo_css,
    )
    caminho_relatorio = gerar_relatorio(
        string_html=string_html,
        mes_referencia=mes_referencia,
        pasta_output=pasta_output,
    )

    caminho_layout = pasta_assets / arquivo_layout
    adicionar_layout_a_relatorio(caminho_relatorio=caminho_relatorio, caminho_layout=caminho_layout)
    print(f'Relatório gerado no caminho: {caminho_relatorio}')


def gerar_relatorio(string_html, mes_referencia, pasta_output):
    nome_relatorio = f'Relatório Mensal - {mes_referencia}.pdf'
    caminho_relatorio = pasta_output / nome_relatorio
    pdfkit.from_string(string_html, output_path=str(caminho_relatorio))
    return caminho_relatorio


def adicionar_layout_a_relatorio(caminho_relatorio, caminho_layout):
    layout_pdf = PdfReader(caminho_layout).pages[0]
    pdf = PdfWriter()
    with open(caminho_relatorio, "rb") as f:
        relatorio = PdfReader(f)
        for page in relatorio.pages:
            page.merge_page(layout_pdf)
            pdf.add_page(page)
    with open(caminho_relatorio, "wb") as f_out:
        pdf.write(f_out)


if __name__ == '__main__':
    main(**CONFIG)
