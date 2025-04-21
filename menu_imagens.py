import tempfile
from pathlib import Path

from PyPDF2 import PdfReader, PdfWriter

import streamlit as st
from PIL import Image

from utilidades import pegar_dados_pdf


def exibir_menu_imagens(coluna):
    """Exibe o menu para gerar um arquivo PDF contendo múltiplas imagens, uma por página."""
    with coluna:
        st.markdown(
            """
        # Imagens para PDF

        Selecione as imagens para gerar um arquivo PDF com elas:
        """
        )

        imagens = st.file_uploader(
            label="Selecione as imagens que irão para o arquivo PDF...",
            type=['png', 'jpg', 'jpeg'],
            accept_multiple_files=True,
        )

        botoes_desativados = not imagens

        clicou_processar = st.button(
            'Clique para processar o arquivo PDF...',
            disabled=botoes_desativados,
            use_container_width=True,
        )
        if clicou_processar:
            dados_pdf = gerar_arquivo_pdf_com_imagens(imagens)
            nome_arquivo = 'imagens.pdf'
            st.download_button(
                'Clique para baixar o arquivo PDF resultante...',
                type='primary',
                data=dados_pdf,
                file_name=nome_arquivo,
                mime='application/pdf',
                use_container_width=True,
            )


def gerar_arquivo_pdf_com_imagens(imagens):
    imagens_pillow = []
    for imagem in imagens:
        dados_imagem = Image.open(imagem)
        if dados_imagem.mode == 'RGBA':
            dados_imagem = remover_canal_transparencia(imagem=imagem)
        else:
            dados_imagem = dados_imagem.convert('RGB')
        imagens_pillow.append(dados_imagem)

    primeira_imagem = imagens_pillow[0]
    demais_imagens = imagens_pillow[1:]

    with tempfile.TemporaryDirectory() as tempdir:
        nome_arquivo = Path(tempdir) / 'temp.pdf'
        primeira_imagem.save(nome_arquivo, save_all=True, append_images=demais_imagens)

        leitor = PdfReader(nome_arquivo)
        escritor = PdfWriter()

        for pagina in leitor.pages:
            escritor.add_page(pagina)

        dados_pdf = pegar_dados_pdf(escritor=escritor)
        return dados_pdf


def remover_canal_transparencia(imagem):
    imagem_rgba = Image.open(imagem)
    imagem_rgb = Image.new('RGB', imagem_rgba.size, (255, 255, 255))
    imagem_rgb.paste(imagem_rgba, mask=imagem_rgba.split()[3])
    return imagem_rgb
