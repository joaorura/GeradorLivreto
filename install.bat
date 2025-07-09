@echo off
echo Instalando dependencias do Combinador de PDF...
echo.

echo Atualizando pip, setuptools e wheel...
pip install --upgrade pip setuptools wheel

echo.
echo Tentando instalar dependencias principais...
pip install -r requirements.txt

if %errorlevel% neq 0 (
    echo.
    echo Erro na instalacao. Tentando metodo alternativo...
    pip install reportlab --only-binary=all
    pip install Pillow pdf2image
)

echo.
echo Instalacao concluida!
echo.
echo Para usar o script:
echo python main.py -i "caminho/para/diretorio" -o "saida.pdf"
echo.
pause 