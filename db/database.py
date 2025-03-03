import psycopg2
from psycopg2.extras import execute_values
from config import Config
from custom_logger import logger

def get_db_connection():
    """Create a new database connection"""
    return psycopg2.connect(
        host=Config.DB_HOST,
        port=Config.DB_PORT,
        dbname=Config.DB_NAME,
        user=Config.DB_USER,
        password=Config.DB_PASSWORD
    )

def initialize_database():
    """Initialize database schema if it doesn't exist"""
    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            # Enable vector extension
            cur.execute("CREATE EXTENSION IF NOT EXISTS vector;")
            
            # Create documents table
            cur.execute("""
                CREATE TABLE IF NOT EXISTS documents (
                    doc_id UUID PRIMARY KEY,
                    title TEXT NOT NULL,
                    file_path TEXT,
                    date_added TIMESTAMP,
                    metadata JSONB
                );
            """)

            cur.execute("CREATE EXTENSION IF NOT EXISTS vector;")
            
            # Get embedding dimension from config
            embedding_dim = 1536  # Default for all-MiniLM-L6-v2
            
            # Create chunks table with vector support
            cur.execute(f"""
                CREATE TABLE IF NOT EXISTS chunks (
                    chunk_id UUID PRIMARY KEY,
                    doc_id UUID REFERENCES documents(doc_id) ON DELETE CASCADE,
                    chunk_index INTEGER,
                    text_content TEXT NOT NULL,
                    embedding vector({embedding_dim}),
                    UNIQUE (doc_id, chunk_index)
                );
            """)
            
            # Create index for faster similarity search
            cur.execute(f"""
                CREATE INDEX IF NOT EXISTS chunks_embedding_idx ON chunks 
                USING ivfflat (embedding vector_cosine_ops) WITH (lists = 100);
            """)
            
        conn.commit()
        logger.info("Database initialized successfully")
    except Exception as e:
        conn.rollback()
        logger.info(f"Error initializing database: {e}")
    finally:
        conn.close()