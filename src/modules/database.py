import sqlite3
import sqlite_vec
import logging
from config.settings import config
from modules.files import get_database_path

# Logger configuration
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

db = None  # Variável global para a conexão com o banco de dados
    
def get_database_connection():
    """Obtém a conexão com o banco de dados."""
    global db
    if db is None:
        db_path = get_database_path()
        db = sqlite3.connect(db_path)
    return db

def initialize_database():
    """
    Inicializa o banco de dados e cria as tabelas necessárias.
    """
    enable_extensions()
    create_tables()

def enable_extensions():
    """
    Habilita as extensões necessárias para o banco de dados.
    """
    global db
    db = get_database_connection()
    db.enable_load_extension(True)
    sqlite_vec.load(db)
    db.enable_load_extension(False)

def create_tables():
    db.execute(
        f"""
        CREATE VIRTUAL TABLE IF NOT EXISTS vectors
        USING vec0(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            embedding float[{config.database.embedding_dimension}],
        )
        """
    )
    db.execute(
        """
        CREATE TABLE IF NOT EXISTS metadata(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            content TEXT NOT NULL,
            description TEXT,
            vector_id INTEGER NOT NULL UNIQUE,
            FOREIGN KEY (vector_id) REFERENCES vectors(id) ON DELETE CASCADE
        )
        """
    )
    db.commit()

def recreate_tables():
    """Recria as tabelas com as dimensões corretas"""

    # Re-enable extensions
    enable_extensions()
    
    # Drop existing tables
    db.execute("DROP TABLE IF EXISTS metadata")
    db.execute("DROP TABLE IF EXISTS vectors")
    db.commit()
    
    # Recreate with correct dimensions
    create_tables()

def insert_vector(vector, content, description=None):

    cursor = db.cursor()
    cursor.execute(
        "INSERT INTO vectors (embedding) VALUES (?)",
        (vector,)  # Convert numpy array to bytes for storage
    )
    vector_id = cursor.lastrowid
    cursor.execute(
        "INSERT INTO metadata (content, description, vector_id) VALUES (?, ?, ?)",
        (content, description, vector_id)
    )
    db.commit()
    return vector_id

def query_embedding(query: str, embedding):

    # Sqlite cursor *DOES NOT* support context manager
    cursor = db.cursor()
    cursor.execute(
      """
      SELECT 
          mtd.content,
          mtd.description
      FROM vectors vct
      JOIN metadata mtd ON vct.id = mtd.vector_id
      WHERE vct.embedding MATCH ? AND k = 10
      ORDER BY distance
      """,
      (embedding,))
    results = cursor.fetchall()
    cursor.close()
    return results