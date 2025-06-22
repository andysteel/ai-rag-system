# 🤖 AI RAG System

## 📖 Visão Geral
Este projeto é um sistema RAG (Retrieval-Augmented Generation) completo que utiliza a API do Google Generative AI para gerar embeddings de documentos e responder perguntas baseadas no conteúdo indexado. O sistema é otimizado com cache, métricas de performance e suporte para múltiplos formatos de arquivo.

## ✨ Principais Features

### 📄 Processamento de Documentos
- **PDF**: Extração de texto usando PyPDF2
- **Markdown**: Conversão para HTML e extração de texto limpo
- **Chunking inteligente**: Divisão de documentos em chunks com sobreposição configurável

### 🧠 Geração de Embeddings
- **Google Generative AI**: Integração com modelos text-embedding-004
- **Cache inteligente**: Sistema de cache para evitar recálculos desnecessários
- **Rate limiting**: Controle automático de requisições para respeitar limites da API
- **Batch processing**: Processamento em lotes para otimizar performance

### 🗄️ Armazenamento de Dados
- **SQLite com sqlite-vec**: Banco vetorial para busca semântica eficiente
- **Exportação CSV**: Backup e intercâmbio de embeddings
- **Gerenciamento de cache**: Sistema de cache persistente

### 🎯 Sistema RAG
- **Busca semântica**: Encontra conteúdo relevante baseado na similaridade
- **IA conversacional**: Interface interativa para fazer perguntas
- **Contexto personalizado**: Respostas baseadas no conteúdo indexado

### 📊 Monitoramento
- **Métricas de performance**: Acompanhamento de API calls, tempo de processamento
- **Dashboard**: Visualização de estatísticas de uso
- **Logging detalhado**: Sistema de logs com emojis para melhor legibilidade

## 🛠️ Instalação

### Pré-requisitos
- Python 3.8+
- Conta Google AI Platform
- Git

### 1️⃣ Clone o repositório
```bash
git clone https://github.com/andysteel/ai-rag-system.git
cd ai-rag-system
```

### 2️⃣ Crie um ambiente virtual python
```bash
python -m venv .venv
```

### 3️⃣ Ative o ambiente virtual
```bash
$ source venv/bin/activate
```

### 4️⃣ Instale as dependências
```bash
pip install -r requirements.txt
```

### 5️⃣ Configure a API Key
```bash
export GOOGLE_AI_API="sua_api_key_aqui"
```

### 6️⃣ Inicialize o banco de dados
```bash
python src/main.py --recreate-tables
```

## 🚀 Como Usar

### 📚 Processar um documento e gerar embeddings
```bash
# Salvar embeddings diretamente no banco
python src/main.py --generate-embeddings db

# Ou salvar em arquivo CSV primeiro
python src/main.py --generate-embeddings file
```

### 💬 Fazer perguntas com RAG
```bash
python src/main.py --rag-prompt
```

### 📥 Importar embeddings de CSV
```bash
python src/main.py --import-csv
```

### 🔍 Verificar modelos disponíveis
```bash
python src/main.py --load-models
```

### 📊 Visualizar métricas
```bash
python src/main.py --print-metrics
```

## 🏗️ Build do Executável

### 🐧 Linux/Mac
```bash
chmod +x build.sh
./build.sh
```

### 🪟 Windows
```bash
# Instalar dependências de build
pip install pyinstaller

# Criar executável
pyinstaller --onefile --name="rag-system" src/main.py
```

O executável será gerado em `dist/rag-system` e incluirá todas as dependências necessárias.

## 📁 Estrutura do Projeto
```
ai-rag-system/
├── 📂 src/
│   ├── 🐍 main.py                 # Ponto de entrada principal
│   ├── 📂 modules/
│   │   ├── 🤖 google_ai_commands.py  # Comandos da API Google AI
│   │   ├── 📄 files.py               # Processamento de arquivos
│   │   ├── 🗄️ database.py            # Operações do banco vetorial
│   │   ├── 💾 cache.py               # Sistema de cache
│   │   ├── 📊 metrics.py             # Métricas e dashboard
│   │   └── 🛠️ utils.py               # Utilitários gerais
│   └── 📂 config/
│       └── ⚙️ settings.py            # Configurações do sistema
├── 📂 resources/
│   ├── 📂 db/                     # Banco de dados SQLite
│   └── 📂 files/                  # Cache e arquivos temporários
├── 🏗️ build.sh                    # Script de build
├── 📋 requirements.txt            # Dependências Python
└── 📖 README.md                   # Este arquivo
```

## ⚙️ Configuração Avançada

### 🎛️ Parâmetros configuráveis em `src/config/settings.py`:
- **Chunk size**: Tamanho dos pedaços de texto
- **Chunk overlap**: Sobreposição entre chunks
- **Batch size**: Tamanho dos lotes para API
- **Rate limiting**: Delay entre requisições
- **Embedding dimensions**: Dimensões dos vetores

### 📝 Exemplo de uso programático:
```python
from modules.google_ai_commands import get_embedding
from modules.database import query_embedding

# Gerar embedding para uma pergunta
question = "Como funciona o machine learning?"
embedding = get_embedding(question)

# Buscar conteúdo similar
results = query_embedding(question, str(embedding[0]))
print(results)
```

## 🎯 Casos de Uso

- **📚 Base de conhecimento**: Indexe documentos da empresa para consultas rápidas
- **🎓 Assistente educacional**: Crie chatbots baseados em material didático
- **📋 Análise de documentos**: Encontre informações específicas em grandes volumes de texto
- **🔍 Sistema de busca**: Implemente busca semântica em seu conteúdo

## 🤝 Contribuição

Contribuições são bem-vindas! Por favor:

1. 🍴 Faça um fork do projeto
2. 🌿 Crie uma branch para sua feature
3. 💻 Implemente suas mudanças
4. ✅ Adicione testes se necessário
5. 📨 Envie um pull request

## 📄 Licença

Este projeto está licenciado sob a Licença MIT. Consulte o arquivo LICENSE para mais detalhes.

## 🆘 Suporte

Se encontrar problemas ou tiver dúvidas:

- 🐛 Abra uma issue no GitHub
- 📧 Entre em contato: andersoninfonet@gmail.com
- 📖 Consulte a documentação da [Google AI API](https://ai.google.dev/)

---

⭐ Se este projeto foi útil para você, considere dar uma estrela no GitHub!