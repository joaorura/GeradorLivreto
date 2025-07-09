import os
import glob
import argparse
import tempfile
from PIL import Image, ImageDraw
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.utils import ImageReader
import re

try:
    from pdf2image import convert_from_path
    PDF2IMAGE_AVAILABLE = True
except ImportError:
    PDF2IMAGE_AVAILABLE = False
    print("Aviso: pdf2image não está instalado. Suporte a PDF não disponível.")

def extrair_paginas_pdf(pdf_path, dpi=300):
    """Extrai todas as páginas de um PDF como imagens"""
    if not PDF2IMAGE_AVAILABLE:
        print("Erro: pdf2image não está instalado. Instale com: pip install pdf2image")
        return []
    
    try:
        print(f"Extraindo páginas do PDF: {pdf_path}")
        # Converte PDF para imagens com alta resolução
        imagens = convert_from_path(pdf_path, dpi=dpi)
        
        # Salva temporariamente as imagens
        temp_dir = tempfile.mkdtemp()
        caminhos_imagens = []
        
        for i, imagem in enumerate(imagens):
            # Salva como PNG com numeração
            caminho_temp = os.path.join(temp_dir, f"pagina_{i+1:02d}.png")
            imagem.save(caminho_temp, 'PNG')
            caminhos_imagens.append(caminho_temp)
        
        print(f"Extraídas {len(caminhos_imagens)} páginas do PDF")
        return caminhos_imagens, temp_dir
        
    except Exception as e:
        print(f"Erro ao extrair páginas do PDF: {e}")
        return [], None

def encontrar_imagens_png(diretorio):
    """Encontra todas as imagens PNG indexadas no diretório"""
    padrao = os.path.join(diretorio, "*.png")
    imagens = glob.glob(padrao)
    
    # Filtra apenas imagens com padrão de indexação (-01, -02, etc.)
    imagens_indexadas = []
    for img in imagens:
        nome_arquivo = os.path.basename(img)
        if re.search(r'-\d+\.png$', nome_arquivo):
            imagens_indexadas.append(img)
    
    # Ordena por número de índice
    def extrair_numero(nome_arquivo):
        match = re.search(r'-(\d+)\.png$', nome_arquivo)
        return int(match.group(1)) if match else 0
    
    imagens_indexadas.sort(key=lambda x: extrair_numero(os.path.basename(x)))
    
    return imagens_indexadas

def combinar_imagens(imagem1_path, imagem2_path):
    """Combina duas imagens lado a lado preservando resolução original"""
    try:
        img1 = Image.open(imagem1_path)
        img2 = Image.open(imagem2_path)
        
        # Mantém as imagens em sua resolução original
        # Apenas ajusta a altura para que ambas tenham a mesma altura
        altura_max = max(img1.height, img2.height)
        
        # Redimensiona apenas se necessário para alinhar alturas
        if img1.height != altura_max:
            razao = altura_max / img1.height
            nova_largura = int(img1.width * razao)
            img1 = img1.resize((nova_largura, altura_max), Image.Resampling.LANCZOS)
        
        if img2.height != altura_max:
            razao = altura_max / img2.height
            nova_largura = int(img2.width * razao)
            img2 = img2.resize((nova_largura, altura_max), Image.Resampling.LANCZOS)
        
        # Cria uma nova imagem combinada preservando resolução
        largura_combinada = img1.width + img2.width
        altura_combinada = altura_max
        
        imagem_combinada = Image.new('RGB', (largura_combinada, altura_combinada), 'white')
        imagem_combinada.paste(img1, (0, 0))
        imagem_combinada.paste(img2, (img1.width, 0))
        
        return imagem_combinada
        
    except Exception as e:
        print(f"Erro ao combinar imagens: {e}")
        return None

def criar_pdf_com_imagens(imagens_combinadas, output_path="output.pdf"):
    """Cria um PDF com as imagens combinadas em alta qualidade (300 DPI)"""
    try:
        largura_pagina = 595.276
        altura_pagina = 841.890
        margem = 50
        largura_disponivel = largura_pagina - 2 * margem
        altura_disponivel = altura_pagina - 2 * margem
        grupos_por_pagina = 2
        c = canvas.Canvas(output_path, pagesize=(largura_pagina, altura_pagina))
        
        total = len(imagens_combinadas)
        # Calcula quantas imagens foram usadas para criar os grupos
        # Cada grupo = 2 imagens, então total_grupos * 2 = total_imagens_originais
        total_imagens_originais = total * 2
        
        # Se o número de imagens é múltiplo de 8, todas as páginas devem ser completas
        # Se não é múltiplo de 8, os últimos grupos ficam separados
        if total_imagens_originais % 8 == 0:
            # Múltiplo de 8: todas as páginas completas
            i = 0
            while i < total:
                imagens_pagina = imagens_combinadas[i:i+grupos_por_pagina]
                altura_imagem = altura_disponivel / len(imagens_pagina)
                y_atual = altura_pagina - margem
                for j, img_combinada in enumerate(imagens_pagina):
                    largura_img, altura_img = img_combinada.size
                    largura_img_pts = largura_img * 72 / 300
                    altura_img_pts = altura_img * 72 / 300
                    razao = min(largura_disponivel / largura_img_pts, altura_imagem / altura_img_pts)
                    nova_largura_pts = largura_img_pts * razao
                    nova_altura_pts = altura_img_pts * razao
                    x_pos = margem + (largura_disponivel - nova_largura_pts) / 2
                    y_pos = y_atual - nova_altura_pts
                    temp_path = f"temp_img_{i}_{j}.png"
                    nova_largura_px = int(nova_largura_pts * 300 / 72)
                    nova_altura_px = int(nova_altura_pts * 300 / 72)
                    img_redim = img_combinada.resize((nova_largura_px, nova_altura_px), Image.Resampling.LANCZOS)
                    img_redim.save(temp_path, 'PNG', optimize=False, quality=100)
                    c.drawImage(temp_path, x_pos, y_pos, nova_largura_pts, nova_altura_pts)
                    os.remove(temp_path)
                    y_atual = y_pos
                c.showPage()
                i += grupos_por_pagina
        else:
            # Não múltiplo de 8: últimos grupos ficam separados
            i = 0
            while i < total:
                # Se restam 2 ou 1 grupos, cada um vai para uma página separada
                if total - i <= 2:
                    for j in range(i, total):
                        imagens_pagina = [imagens_combinadas[j]]
                        altura_imagem = altura_disponivel
                        y_atual = altura_pagina - margem
                        for k, img_combinada in enumerate(imagens_pagina):
                            largura_img, altura_img = img_combinada.size
                            largura_img_pts = largura_img * 72 / 300
                            altura_img_pts = altura_img * 72 / 300
                            razao = min(largura_disponivel / largura_img_pts, altura_imagem / altura_img_pts)
                            nova_largura_pts = largura_img_pts * razao
                            nova_altura_pts = altura_img_pts * razao
                            x_pos = margem + (largura_disponivel - nova_largura_pts) / 2
                            y_pos = y_atual - nova_altura_pts
                            temp_path = f"temp_img_{j}_{k}.png"
                            nova_largura_px = int(nova_largura_pts * 300 / 72)
                            nova_altura_px = int(nova_altura_pts * 300 / 72)
                            img_redim = img_combinada.resize((nova_largura_px, nova_altura_px), Image.Resampling.LANCZOS)
                            img_redim.save(temp_path, 'PNG', optimize=False, quality=100)
                            c.drawImage(temp_path, x_pos, y_pos, nova_largura_pts, nova_altura_pts)
                            os.remove(temp_path)
                            y_atual = y_pos
                        c.showPage()
                    break
                else:
                    imagens_pagina = imagens_combinadas[i:i+grupos_por_pagina]
                    altura_imagem = altura_disponivel / len(imagens_pagina)
                    y_atual = altura_pagina - margem
                    for j, img_combinada in enumerate(imagens_pagina):
                        largura_img, altura_img = img_combinada.size
                        largura_img_pts = largura_img * 72 / 300
                        altura_img_pts = altura_img * 72 / 300
                        razao = min(largura_disponivel / largura_img_pts, altura_imagem / altura_img_pts)
                        nova_largura_pts = largura_img_pts * razao
                        nova_altura_pts = altura_img_pts * razao
                        x_pos = margem + (largura_disponivel - nova_largura_pts) / 2
                        y_pos = y_atual - nova_altura_pts
                        temp_path = f"temp_img_{i}_{j}.png"
                        nova_largura_px = int(nova_largura_pts * 300 / 72)
                        nova_altura_px = int(nova_altura_pts * 300 / 72)
                        img_redim = img_combinada.resize((nova_largura_px, nova_altura_px), Image.Resampling.LANCZOS)
                        img_redim.save(temp_path, 'PNG', optimize=False, quality=100)
                        c.drawImage(temp_path, x_pos, y_pos, nova_largura_pts, nova_altura_pts)
                        os.remove(temp_path)
                        y_atual = y_pos
                    c.showPage()
                    i += grupos_por_pagina
        
        c.save()
        print(f"PDF criado com sucesso: {output_path}")
    except Exception as e:
        print(f"Erro ao criar PDF: {e}")

def main(input_path, output_file=None):
    # Se não foi fornecido arquivo de saída, usa o padrão
    if output_file is None:
        output_file = "combinado.pdf"
    
    # Verifica se o caminho existe
    if not os.path.exists(input_path):
        print(f"Erro: O caminho '{input_path}' não existe!")
        return
    
    # Detecta se é um PDF ou diretório
    if input_path.lower().endswith('.pdf'):
        # É um PDF - extrai as páginas
        if not PDF2IMAGE_AVAILABLE:
            print("Erro: Para processar PDFs, instale pdf2image: pip install pdf2image")
            return
        
        caminhos_imagens, temp_dir = extrair_paginas_pdf(input_path)
        if not caminhos_imagens:
            print("Erro: Não foi possível extrair páginas do PDF!")
            return
        
        # Usa as imagens extraídas
        imagens = caminhos_imagens
        usar_temp_dir = True
        
    else:
        # É um diretório - procura por imagens PNG
        imagens = encontrar_imagens_png(input_path)
        temp_dir = None
        usar_temp_dir = False
    
    if not imagens:
        print("Nenhuma imagem encontrada!")
        return
    
    print(f"Encontradas {len(imagens)} imagens:")
    for img in imagens:
        print(f"  - {os.path.basename(img)}")
    
    # Nova lógica: 2 pares por página (4 imagens por página). Se sobrar menos de 4 imagens, cada par vai para uma página separada.
    imagens_combinadas = []
    n = len(imagens)
    print(f"Gerando grupos para {n} imagens...")

    # Monta os pares conforme o padrão desejado
    pares = [
        (5, 6), (3, 8),  # Página 1
        (4, 7), (2, 9),  # Página 2
        (1, 10),         # Página 3
        (0, 11)          # Página 4
    ] if n == 12 else []

    # Generalização para qualquer n >= 4
    if not pares:
        left = 0
        right = n - 1
        pares_temp = []
        while left < right:
            pares_temp.append((left, right))
            left += 1
            right -= 1
        pares = pares_temp

    # Verifica se é múltiplo de 8 para determinar o comportamento
    eh_multiplo_de_8 = n % 8 == 0

    # Agrupa os pares em páginas de 2 pares (4 imagens)
    grupos_por_pagina = 2
    i = 0
    while i < len(pares):
        # Se restam menos de 2 pares E não é múltiplo de 8, cada um vai para uma página separada
        if len(pares) - i <= 2 and not eh_multiplo_de_8:
            for j in range(i, len(pares)):
                idx1, idx2 = pares[j]
                img_combinada = combinar_imagens(imagens[idx1], imagens[idx2])
                if img_combinada:
                    imagens_combinadas.append(img_combinada)
                    print(f"Grupo {len(imagens_combinadas)}: {os.path.basename(imagens[idx1])} + {os.path.basename(imagens[idx2])} (página separada)")
            break
        else:
            # Página completa com 2 pares (ou múltiplo de 8)
            for j in range(min(grupos_por_pagina, len(pares) - i)):
                idx1, idx2 = pares[i + j]
                img_combinada = combinar_imagens(imagens[idx1], imagens[idx2])
                if img_combinada:
                    imagens_combinadas.append(img_combinada)
                    print(f"Grupo {len(imagens_combinadas)}: {os.path.basename(imagens[idx1])} + {os.path.basename(imagens[idx2])}")
            i += grupos_por_pagina
    
    # Cria o PDF
    if imagens_combinadas:
        criar_pdf_com_imagens(imagens_combinadas, output_file)
        
        # Limpa arquivos temporários se necessário
        if usar_temp_dir and temp_dir:
            try:
                import shutil
                shutil.rmtree(temp_dir)
                print(f"Arquivos temporários removidos: {temp_dir}")
            except Exception as e:
                print(f"Aviso: Não foi possível remover arquivos temporários: {e}")
    else:
        print("Nenhuma imagem foi combinada com sucesso!")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Combina imagens PNG indexadas ou páginas de PDF em um novo PDF')
    parser.add_argument('--input', '-i', required=True,
                       help='Caminho para o diretório com imagens PNG ou arquivo PDF')
    parser.add_argument('--output', '-o', 
                       help='Nome do arquivo PDF de saída (padrão: "combinado.pdf")')
    
    args = parser.parse_args()
    
    # Executa o script
    main(args.input, args.output)
