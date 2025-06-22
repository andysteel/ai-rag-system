import PyPDF2
import markdown
from bs4 import BeautifulSoup
import logging
import os
import csv
import tempfile
import sys
from modules.utils import Emojis

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class FileExtractorFactory:
    """Factory class to create file extractors based on file type."""
    
    @staticmethod
    def create_extractor(file_path):
        if file_path.endswith('.pdf'):
            return PDFExtractor(file_path)
        elif file_path.endswith('.md'):
            return MarkdownExtractor(file_path)
        else:
            raise ValueError("Unsupported file type. Only .pdf and .md files are supported.")

class FileExtractor:

    def __init__(self, file_path):
        self.file_path = file_path

    def extract_text(file_path):
        pass


class PDFExtractor(FileExtractor):
    def extract_text(self):
        """
        Extracts text from a PDF file.

        Returns:
            str: The extracted text from the PDF.
        """
        text = ""
        if not self.file_path.endswith('.pdf'):
            logger.error(f"{Emojis.ERROR.value} Arquivo não é um PDF: {self.file_path}")
            raise ValueError("O arquivo fornecido não é um PDF.")
        try:
            with open(self.file_path, "rb") as file:
                reader = PyPDF2.PdfReader(file)
                for page in reader.pages:
                    text += page.extract_text() or ""
                return text.strip()
        except FileNotFoundError:
            logger.error(f"{Emojis.ERROR.value} Arquivo não encontrado: {self.file_path}")
            raise
        except PyPDF2.errors.PdfReadError as e:
            logger.error(f"{Emojis.ERROR.value} Erro ao ler o PDF: {e}")
            raise e
        except Exception as e:
            logger.error(f"{Emojis.ERROR.value} Erro ao extrair texto do PDF: {e}")
            raise e

class MarkdownExtractor(FileExtractor):
    def extract_text(self):
        """
        Extracts text from a Markdown file.

        Returns:
            str: The extracted text from the Markdown file.
        """
        try:
            with open(self.file_path, "r", encoding="utf-8") as file:
                md_content = file.read()
                html_content = markdown.markdown(md_content)
                soup = BeautifulSoup(html_content, "html.parser")
                return soup.get_text(separator="\n", strip=True)
            
        except FileNotFoundError:
            logger.error(f"{Emojis.ERROR.value} Arquivo não encontrado: {self.file_path}")
            raise
        except UnicodeDecodeError:
            logger.error(f"{Emojis.ERROR.value} Erro de decodificação ao ler o arquivo: {self.file_path}")
            raise
        except Exception as e:
            logger.error(f"{Emojis.ERROR.value} Erro ao extrair texto do Markdown: {e}")
            raise e
        

def save_embedding_to_csv(index, chunk, embedding, source, csv_file_path):
    """Save embedding data to CSV file."""
    with open(csv_file_path, 'a') as f:
        clean_chunk = chunk.replace(',', ' ')
        clean_chunk = clean_chunk.replace('\n', ' ')
        clean_chunk = clean_chunk.replace('"', '""')  # Escape quotes for CSV
        
        embedding_str = ','.join(map(str, embedding))
        f.write(f"\"{index}\",\"{clean_chunk}\",\"{embedding_str}\",\"{source}\"\n")

def import_embeddings_from_csv(file_path, insert_vector):
    """Import embeddings from a CSV file."""
    with open(file_path, 'r') as f:
        try:
            reader = csv.reader(f)
            for row in reader:
                index, content, embedding, source = row

                vector_id = insert_vector(embedding, content, source)
                logger.info(f"{Emojis.INFO.value} Chunk {index} inserido com ID: {vector_id}")

            logger.info(f"{Emojis.SUCCESS.value} Importação de embeddings concluída.")
            os.remove(file_path)
        except csv.Error as e:
            logger.error(f"{Emojis.ERROR.value} Erro ao ler o CSV: {e}")
            raise e
        except Exception as e:
            logger.error(f"{Emojis.ERROR.value} Erro ao importar embeddings do CSV: {e}")
            raise e

def get_csv_file_path():
    """Get the path to the CSV file for embeddings."""
    csv_dir = "resources/files"
    if getattr(sys, 'frozen', False):
        # Executável - usar caminho absoluto
        app_data_dir = os.path.join(tempfile.gettempdir(), 'local-rag-embeddings')
        os.makedirs(app_data_dir, exist_ok=True)
        csv_file_path = os.path.join(app_data_dir, 'embeddings.csv')
        logger.info(f"{Emojis.INFO.value} Executável detectado. CSV em: {csv_file_path}")
    else:
        # Desenvolvimento - usar caminho relativo
        os.makedirs(csv_dir, exist_ok=True)
        csv_file_path = os.path.join(csv_dir, 'embeddings.csv')
        logger.info(f"{Emojis.INFO.value} Modo desenvolvimento. CSV em: {csv_file_path}")

    return csv_file_path

def get_cache_file_path():
    """Get the path to the cache file for embeddings."""
    cache_dir = "resources/files"
    if getattr(sys, 'frozen', False):
        # Executável - usar caminho absoluto
        app_data_dir = os.path.join(tempfile.gettempdir(), 'local-rag-embeddings')
        os.makedirs(app_data_dir, exist_ok=True)
        cache_file_path = os.path.join(app_data_dir, 'embeddings_cache')
        logger.info(f"{Emojis.INFO.value} Executável detectado. Cache em: {cache_file_path}")
    else:
        # Desenvolvimento - usar caminho relativo
        os.makedirs(cache_dir, exist_ok=True)
        cache_file_path = os.path.join(cache_dir, 'embeddings_cache')
        logger.info(f"{Emojis.INFO.value} Modo desenvolvimento. Cache em: {cache_file_path}")

    return cache_file_path

def get_metrics_file_path():
    """Get the path to the metrics file."""
    metrics_dir = "resources/files"
    if getattr(sys, 'frozen', False):
        # Executável - usar caminho absoluto
        app_data_dir = os.path.join(tempfile.gettempdir(), 'local-rag-embeddings')
        os.makedirs(app_data_dir, exist_ok=True)
        metrics_file_path = os.path.join(app_data_dir, 'metrics.json')
        logger.info(f"{Emojis.INFO.value} Executável detectado. Metrics em: {metrics_file_path}")
    else:
        # Desenvolvimento - usar caminho relativo
        os.makedirs(metrics_dir, exist_ok=True)
        os.makedirs(metrics_dir, exist_ok=True)
        metrics_file_path = os.path.join(metrics_dir, 'metrics.json')
        logger.info(f"{Emojis.INFO.value} Modo desenvolvimento. Metrics em: {metrics_file_path}")

    return metrics_file_path

def get_database_path():
    """
    Retorna o caminho correto do banco de dados baseado no ambiente.
    """
    if getattr(sys, 'frozen', False):
        # Executável PyInstaller
        # Usar diretório temporário do usuário para o banco
        app_data_dir = os.path.join(tempfile.gettempdir(), 'local-rag-embeddings')
        os.makedirs(app_data_dir, exist_ok=True)
        db_path = os.path.join(app_data_dir, 'local_rag_database.db')
        logger.info(f"{Emojis.INFO.value} Executável detectado. DB em: {db_path}")
        return db_path
    else:
        # Desenvolvimento - usar caminho relativo
        db_dir = "resources/db"
        os.makedirs(db_dir, exist_ok=True)
        db_path = os.path.join(db_dir, "my_database.db")
        logger.info(f"{Emojis.INFO.value} Modo desenvolvimento. DB em: {db_path}")
        return db_path