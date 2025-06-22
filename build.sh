#!/bin/bash
# filepath: build.sh

echo "🚀 Iniciando build do executável..."

# Verificar se sqlite_vec está instalado
python -c "import sqlite_vec; print('✅ sqlite_vec encontrado')" || {
    echo "❌ sqlite_vec não encontrado. Instalando..."
    pip install sqlite_vec
}

# Instalar dependências de build
pip install pyinstaller

# Limpar builds anteriores
rm -rf build/ dist/ *.spec

# Obter caminho do sqlite_vec
SQLITE_VEC_PATH=$(python -c "import sqlite_vec; print(sqlite_vec.__path__[0])")

echo "📦 Incluindo sqlite_vec de: $SQLITE_VEC_PATH"

# Criar executável
pyinstaller \
    --onefile \
    --name="rag-system" \
    --add-data="src/config:config" \
    --add-data="src/modules:modules" \
    --add-data="resources:resources" \
    --add-binary="$SQLITE_VEC_PATH:sqlite_vec" \
    --hidden-import=google.generativeai \
    --hidden-import=PyPDF2 \
    --hidden-import=markdown \
    --hidden-import=bs4 \
    --hidden-import=numpy \
    --hidden-import=sqlite3 \
    --hidden-import=sqlite_vec \
    --clean \
    src/main.py

echo "✅ Build concluído!"
echo "📁 Executável disponível em: dist/rag-system"
echo "🧪 Testando..."
./dist/rag-system --load-models