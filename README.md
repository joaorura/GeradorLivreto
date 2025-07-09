# Combinador de Imagens PNG e PDF

Este script combina imagens PNG indexadas ou páginas de PDF em um novo PDF, organizando-as em páginas seguindo um padrão específico.

## Funcionalidades

- Combina imagens PNG lado a lado preservando a resolução original
- **NOVO**: Extrai páginas de PDF e as combina em novo PDF
- Organiza as imagens em páginas seguindo padrão específico
- Suporta diferentes quantidades de imagens com lógica adaptativa
- Gera PDF em alta qualidade (300 DPI)

## Instalação

1. Clone ou baixe este repositório
2. Instale as dependências:

```bash
pip install -r requirements.txt
```

**Nota**: Para suporte a PDFs, você também precisa do Poppler:
- **Windows**: Baixe de https://github.com/oschwartz10612/poppler-windows/releases
- **Linux**: `sudo apt-get install poppler-utils`
- **macOS**: `brew install poppler`

### Solução de Problemas

**Erro na instalação do reportlab no Windows:**
```bash
# Tente instalar apenas binários pré-compilados:
pip install reportlab --only-binary=all

# Ou use a versão simplificada:
pip install -r requirements-simple.txt
```

**Erro de compilação:**
```bash
# Instale o Visual Studio Build Tools ou use:
pip install --upgrade pip setuptools wheel
pip install -r requirements-simple.txt
```

## Uso

### Processar Diretório com Imagens PNG

```bash
python main.py --input "caminho/para/diretorio"
```

### Processar Arquivo PDF

```bash
python main.py --input "arquivo.pdf"
```

### Uso com Parâmetros

```bash
python main.py --input "caminho/ou/arquivo.pdf" --output "meu_arquivo.pdf" --tamanho "A6"
```

ou usando as versões curtas:

```bash
python main.py -i "caminho/ou/arquivo.pdf" -o "meu_arquivo.pdf" -t "A6"
```

### Exemplos de Tamanhos

```bash
# Usar A6 (padrão) - resultado final será A4
python main.py -i "meus_manuais" -t "A6"

# Usar A5 - resultado final será A3
python main.py -i "meus_manuais" -t "A5"

# Usar tamanho customizado (300x400 pontos) - resultado final será 600x800 pontos
python main.py -i "meus_manuais" -t "300,400"
```

### Parâmetros

- `--input`, `-i`: **OBRIGATÓRIO** - Caminho para diretório com imagens PNG ou arquivo PDF
- `--output`, `-o`: Nome do arquivo PDF de saída (opcional, padrão: "combinado.pdf")
- `--tamanho`, `-t`: Tamanho de cada grupo (opcional, padrão: "A6")
  - Tamanhos padrão: A6, A5, A4, A3, letter, legal
  - Tamanho customizado: formato "largura,altura" em pontos (ex: "300,400")
  - O resultado final será 4x o tamanho especificado (ex: A6 → A4)

## Tipos de Entrada

### 1. Diretório com Imagens PNG
- Procura por imagens PNG com padrão de indexação no nome do arquivo
- Exemplo: `imagem-01.png`, `imagem-02.png`, `imagem-03.png`, etc.
- As imagens são ordenadas numericamente pelo índice

### 2. Arquivo PDF
- Extrai cada página do PDF como uma imagem
- Processa as páginas na ordem original do PDF
- Requer `pdf2image` e `poppler` instalados

## Sistema de Tamanhos

O script permite especificar o tamanho de cada grupo de imagens. O resultado final será sempre 4x o tamanho especificado:

- **A6** (padrão) → Página final: **A4**
- **A5** → Página final: **A3**
- **A4** → Página final: **A2**
- **A3** → Página final: **A1**
- **letter** → Página final: 2x letter
- **legal** → Página final: 2x legal
- **Customizado** → Página final: 2x o tamanho especificado

### Como funciona:
- Cada grupo contém 2 imagens lado a lado
- Cada página contém 2 grupos (2x2 = 4 imagens por página)
- O tamanho da página final é sempre 2x2 = 4x o tamanho de cada grupo

## Padrão de Organização

### Para múltiplos de 8 imagens (8, 16, 24, etc.):
- Todas as páginas ficam completas com 2 pares de imagens cada

### Para não múltiplos de 8 (12, 20, etc.):
- Primeiras páginas: completas com 2 pares
- Últimas páginas: 1 par cada

### Exemplo com 12 imagens:
- Página 1: 6-7, 4-9
- Página 2: 5-8, 3-10
- Página 3: 2-11
- Página 4: 1-12

## Dependências

- Python 3.7+
- Pillow (PIL)
- ReportLab
- pdf2image (para suporte a PDFs)
- Poppler (para pdf2image funcionar)

## Exemplo de Execução

```bash
# Instalar dependências
pip install -r requirements.txt

# Processar diretório com imagens
python main.py -i "meus_manuais" -o "manual_final.pdf"

# Processar arquivo PDF
python main.py -i "documento.pdf" -o "documento_combinado.pdf"

# Processar apenas com input (usa nome padrão para saída e tamanho A6)
python main.py -i "meus_manuais"

# Processar com tamanho específico
python main.py -i "meus_manuais" -t "A5"
```

## Saída

O script gera um arquivo PDF com as imagens combinadas, organizadas conforme o padrão especificado. O arquivo é salvo no diretório atual com o nome especificado (ou `combinado.pdf` por padrão).

## Notas

- Para PDFs, o script cria arquivos temporários que são automaticamente removidos após o processamento
- A resolução de extração de PDFs é de 300 DPI para manter alta qualidade
- Se `pdf2image` não estiver instalado, o script ainda funciona para diretórios com imagens PNG 