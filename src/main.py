import logging
import argparse
from modules.google_ai_commands import process_embeddings, carregar_modelos, prompt_request
from modules.files import import_embeddings_from_csv, get_csv_file_path
from modules.database import initialize_database, insert_vector, recreate_tables
from modules.metrics import MetricsDashboard

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


if __name__ == "__main__":

    parser = argparse.ArgumentParser(description="IA com RAG.")
    parser.add_argument('--import-csv', action='store_true', help='Importar embeddings de um arquivo CSV')
    parser.add_argument('--recreate-tables', action='store_true', help='Recriar tabelas no banco de dados')
    parser.add_argument('--rag-prompt', action='store_true', help='Prompt para RAG')
    parser.add_argument('--load-models', action='store_true', help='Carregar modelos do Google Generative AI')
    parser.add_argument('--print-metrics', action='store_true', help='Imprimir métricas de desempenho')
    parser.add_argument('--generate-embeddings', type=str, choices=['db', 'file'], help='Gerar embeddings a partir de um arquivo')
    args = parser.parse_args()
    
    if args.import_csv:
        initialize_database()
        csv_file_path = get_csv_file_path()
        import_embeddings_from_csv(csv_file_path, insert_vector)
    if args.recreate_tables:
        recreate_tables()
    if args.rag_prompt:
        initialize_database()
        prompt_request()
    if args.load_models:
        carregar_modelos()
    if args.print_metrics:
        metrics = MetricsDashboard()
        metrics.print_dashboard()
    if args.generate_embeddings and args.generate_embeddings in ["db", "file"]:
        initialize_database()
        process_embeddings(args.generate_embeddings)

