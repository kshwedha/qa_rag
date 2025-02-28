import psycopg2
from psycopg2.extras import execute_values, RealDictCursor
import uuid
from db.database import get_db_connection

class EmbeddingModel:
    """Model for embedding operations in the database"""
    
    def __init__(self):
        pass
    
    def create_chunks(self, doc_id, chunks, embeddings):
        """Store document chunks and their embeddings
        
        Args:
            doc_id (str): Document ID
            chunks (list): List of text chunks
            embeddings (list): List of embedding vectors
            
        Returns:
            bool: True if successful, False otherwise
        """
        if len(chunks) != len(embeddings):
            print("Error: Number of chunks and embeddings must match")
            return False
        
        conn = None
        try:
            conn = get_db_connection()
            
            # Prepare data for batch insert
            chunk_data = []
            for i, (chunk, embedding) in enumerate(zip(chunks, embeddings)):
                chunk_id = str(uuid.uuid4())
                chunk_data.append((chunk_id, doc_id, i, chunk, embedding.tolist()))
            
            with conn.cursor() as cur:
                execute_values(
                    cur,
                    "INSERT INTO chunks (chunk_id, doc_id, chunk_index, text_content, embedding) VALUES %s",
                    chunk_data,
                    template="(%s, %s, %s, %s, %s)"
                )
            
            conn.commit()
            return True
        except Exception as e:
            if conn:
                conn.rollback()
            print(f"Error storing chunks: {e}")
            return False
        finally:
            if conn:
                conn.close()
    
    def search_similar(self, embedding, top_k=5, doc_id=None):
        """Search for chunks similar to the given embedding
        
        Args:
            embedding (list): Query embedding vector
            top_k (int): Number of results to return
            doc_id (str, optional): Limit search to specific document
            
        Returns:
            list: List of dictionaries with chunk text, document title, and similarity score
        """
        conn = None
        try:
            conn = get_db_connection()
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                if doc_id:
                    # Search only within the specified document
                    cur.execute("""
                        SELECT c.chunk_id, c.text_content, d.doc_id, d.title, 
                               1 - (c.embedding <=> %s) as similarity
                        FROM chunks c
                        JOIN documents d ON c.doc_id = d.doc_id
                        WHERE d.doc_id = %s
                        ORDER BY c.embedding <=> %s
                        LIMIT %s;
                    """, (embedding, doc_id, embedding, top_k))
                else:
                    # Search across all documents
                    cur.execute("""
                        SELECT c.chunk_id, c.text_content, d.doc_id, d.title, 
                               1 - (c.embedding <=> %s) as similarity
                        FROM chunks c
                        JOIN documents d ON c.doc_id = d.doc_id
                        ORDER BY c.embedding <=> %s
                        LIMIT %s;
                    """, (embedding, embedding, top_k))
                
                results = cur.fetchall()
            
            return [dict(result) for result in results]
        except Exception as e:
            print(f"Error searching similar chunks: {e}")
            return []
        finally:
            if conn:
                conn.close()
    
    def delete_by_document(self, doc_id):
        """Delete all chunks for a document
        
        Args:
            doc_id (str): Document ID
            
        Returns:
            bool: True if successful, False otherwise
        """
        conn = None
        try:
            conn = get_db_connection()
            with conn.cursor() as cur:
                cur.execute("DELETE FROM chunks WHERE doc_id = %s", (doc_id,))
            conn.commit()
            return True
        except Exception as e:
            if conn:
                conn.rollback()
            print(f"Error deleting chunks: {e}")
            return False
        finally:
            if conn:
                conn.close()