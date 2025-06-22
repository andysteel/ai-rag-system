import numpy as np
import time
import logging
import google.generativeai as genai
import os
from config.settings import config
from modules.files import FileExtractorFactory, save_embedding_to_csv, get_csv_file_path, get_cache_file_path
from modules.database import query_embedding, insert_vector
from modules.utils import Emojis
from modules.cache import EmbeddingCache
from modules.metrics import metrics, track_time, MetricsDashboard

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configure com sua API Key
genai.configure(api_key=config.google_api_key)

# Inicializar o cache
cache = EmbeddingCache(cache_dir=get_cache_file_path())

dash = MetricsDashboard()

# chunk_size=1536, chunk_overlap=153 config para gemini
def split_text(text, chunk_size=config.embedding.chunk_size, chunk_overlap=config.embedding.chunk_overlap):
    """Divide o texto em chunks com sobreposição."""
    chunks = []
    start = 0
    while start < len(text):
        end = start + chunk_size
        chunks.append(text[start:end])
        start += chunk_size - chunk_overlap
        if end >= len(text):
            break
    return chunks

@track_time('processing_time')
def process_embeddings(generate_type):
    path_to_file = input("Digite o caminho do arquivo (ex: resources/files/some-file.pdf): ")
    if not path_to_file:
        logger.error(f"{Emojis.ERROR.value} Nenhum caminho de arquivo fornecido.")
        return
    if not os.path.exists(path_to_file):
        logger.error(f"{Emojis.ERROR.value} O arquivo {path_to_file} não existe.")
        return
    logger.info(f"{Emojis.INFO.value} Iniciando o processamento do arquivo: {path_to_file}")

    extracted_text = FileExtractorFactory.create_extractor(path_to_file).extract_text()

    text_chunks = split_text(extracted_text)
    logger.info(f"{Emojis.INFO.value} Número de chunks: {len(text_chunks)}")

    embeddings = generate_embeddings(text_chunks)
    file_name = os.path.basename(path_to_file)
    if embeddings:
        logger.info(f"{Emojis.INFO.value} Número de embeddings gerados: {len(embeddings)}")
        csv_file_path = get_csv_file_path()

        for i, (chunk, embedding) in enumerate(zip(text_chunks, embeddings)):

            if generate_type == "file":
                save_embedding_to_csv(i+1, chunk, embedding, source=file_name, csv_file_path=csv_file_path)
            elif generate_type == "db":
                insert_vector(str().join(map(str, embedding)), chunk, description=file_name)
    else:
        logger.error(f"{Emojis.ERROR.value} Falha ao gerar embeddings.")

    metrics.increment('files_processed')
    logger.info(f"{Emojis.SUCCESS.value} Processamento concluído.")
    dash.save_metrics_to_file()

def generate_embeddings(texts, model_name=config.embedding.model_name, wait_time=config.embedding.rate_limit_delay, range_limit=config.embedding.batch_size):
    """Gera embeddings para uma lista de textos."""
    try:
        all_embeddings = []
        
        # Processa a lista em chunks de 5
        for i in range(0, len(texts), range_limit):
            # Cria lista secundária da posição i até i+5 (ou final da lista)
            chunk = texts[i:i+range_limit]
            logger.info(f"{Emojis.LOADING.value} Processando chunk {i//range_limit + 1}: posições {i} até {min(i+(range_limit - 1), len(texts)-1)}")
            logger.info(f"{Emojis.INFO.value} Tamanho do chunk: {len(chunk)}")

            chunk_in_cache = False
            for text in chunk:
                cached_embedding = cache.get(text, model_name)

                if cached_embedding is not None:
                    print(f"{Emojis.INFO.value} Usando embedding do cache.")
                    all_embeddings.append([cached_embedding])
                    chunk_in_cache = True

            if chunk_in_cache == False:
                time.sleep(wait_time)  # Pausa maior entre chunks
                result = genai.embed_content(
                        model=model_name,
                        content=chunk, 
                        task_type="RETRIEVAL_DOCUMENT",
                        output_dimensionality=config.database.embedding_dimension
                    )
                metrics.increment('api_calls')

                cache.set_batch(chunk, model_name, [np.array(embedding) for embedding in result['embedding']])
                for embedding in result['embedding']:
                    all_embeddings.append([np.array(embedding)])

            logger.info(f"{Emojis.INFO.value} Chunk processado. Total de embeddings até agora: {len(all_embeddings)}")

        logger.info(f"{Emojis.INFO.value} Total de embeddings gerados: {len(all_embeddings)}")

        return all_embeddings
    except Exception as e:
        logger.error(f"{Emojis.ERROR.value} Erro ao gerar embeddings: {e}")
        return None

def check_embedding_dimensions(text="test", model_name="text-embedding-004"):
    """Verifica a dimensão dos embeddings do modelo atual"""
    try:
        result = genai.embed_content(
            model=model_name,
            content=[text],
            task_type="RETRIEVAL_DOCUMENT"
        )
        metrics.increment('api_calls')
        embedding = np.array(result['embedding'])
        logger.info(f"{Emojis.INFO.value} Dimensões do embedding: {embedding.shape}")
    except Exception as e:
        logger.error(f"{Emojis.ERROR.value} Erro ao verificar dimensões: {e}")
        return None

def get_embedding(text, model_name="text-embedding-004"):
    """Gera um embedding para um único texto."""
    try:
        result = genai.embed_content(
            model=model_name,
            content=[text],
            task_type="RETRIEVAL_QUERY",
            output_dimensionality=config.database.embedding_dimension
        )
        metrics.increment('api_calls')
        return np.array(result['embedding'])
    except Exception as e:
        print(f"{Emojis.ERROR.value} Erro ao gerar embedding: {e}")
        return None

def carregar_modelos():
    print("Modelos disponíveis:")

    for model in genai.list_models():
        # Imprime o nome (identificador) do modelo
        print(f"- Nome: {model.name}")

        # Imprime o nome de exibição (mais legível)
        print(f"  Nome de Exibição: {model.display_name}")

        # Imprime a descrição
        print(f"  Descrição: {model.description[:80]}...") # Imprime os primeiros 80 caracteres

        # Imprime os métodos de geração suportados (ex: 'generateContent', 'embedContent')
        print(f"  Suporta: {model.supported_generation_methods}")

        if "embedContent" in model.supported_generation_methods:
            print(f"  Dimensão do Embedding: {model.output_dimensionality if hasattr(model, 'output_dimensionality') else 'N/A'}")

        print("-" * 20)
    metrics.increment('api_calls')


def prompt_request():
    print("✨IA com RAG ✨")
    print("⭐" * 30)
    ia_name = input(f"{Emojis.QUESTION.value} Qual o nome da sua IA?: ")
    if not ia_name:
        print(f"{Emojis.ERROR.value} Nenhum nome fornecido.")
        exit(1)
    print(f"{Emojis.ROBOT.value} Olá, eu sou {ia_name}! Estou aqui para responder às suas perguntas usando RAG (Retrieval-Augmented Generation).\n")
    text = input(f"{Emojis.QUESTION.value} Digite sua pergunta: ")
    if not text:
        print(f"{Emojis.ERROR.value} Nenhuma pergunta fornecida.")
        exit(1)

    while text != "sair":
        print(f"{Emojis.LOADING.value * 3} Processando sua pergunta...")
        processar_pergunta(text, ia_name)
        text = input(f"{Emojis.QUESTION.value} Digite sua pergunta (ou 'sair' para encerrar): ")

    print(f"{Emojis.STAR.value} Que pena, volte sempre! {Emojis.STAR.value}")

def processar_pergunta(text, ia_name):

    cached_embedding = cache.get(text, config.embedding.model_name)

    embedding = None
    if cached_embedding is not None:
        print(f"{Emojis.INFO.value} Usando embedding do cache.")
        embedding = cached_embedding
    else:
        embedding = get_embedding(text)
        cache.set(text, config.embedding.model_name, embedding)

    context = query_embedding(text, str(embedding[0]))

    rag_prompt = f"""
    Use o seguinte contexto para responder à pergunta. Se a resposta não estiver no contexto, diga que não sabe.

    Contexto: {context}

    Pergunta: {text}
    """

    model = genai.GenerativeModel(config.gen_ai_model)

    response = model.generate_content(rag_prompt)
    print(f"{Emojis.ROBOT.value} {ia_name} : {response.candidates[0].content.parts[0].text}\n")