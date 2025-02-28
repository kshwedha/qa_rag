# models/document.py
import psycopg2
from psycopg2.extras import RealDictCursor
import json
from datetime import datetime
import uuid
from db.database import get_db_connection

class DocumentModel:
    """Model for document operations in the database"""
    
    def __init__(self):
        pass
        
    def create(self, title, file_path, metadata=None):
        """Create a new document record
        
        Args:
            title (str): Document title
            file_path (str): Path to the stored document
            metadata (dict): Optional metadata
            
        Returns:
            str: Document ID if successful, None otherwise
        """
        doc_id = str(uuid.uuid4())
        conn = None
        try:
            conn = get_db_connection()
            with conn.cursor() as cur:
                cur.execute(
                    "INSERT INTO documents (doc_id, title, file_path, date_added, metadata) VALUES (%s, %s, %s, %s, %s)",
                    (doc_id, title, file_path, datetime.now(), json.dumps(metadata or {}))
                )
            conn.commit()
            return doc_id
        except Exception as e:
            if conn:
                conn.rollback()
            print(f"Error creating document: {e}")
            return None
        finally:
            if conn:
                conn.close()
    
    def get_by_id(self, doc_id):
        """Get document by ID
        
        Args:
            doc_id (str): Document ID
            
        Returns:
            dict: Document details or None if not found
        """
        conn = None
        try:
            conn = get_db_connection()
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute(
                    "SELECT doc_id, title, file_path, date_added, metadata FROM documents WHERE doc_id = %s",
                    (doc_id,)
                )
                document = cur.fetchone()
            return dict(document) if document else None
        except Exception as e:
            print(f"Error retrieving document: {e}")
            return None
        finally:
            if conn:
                conn.close()
    
    def list_all(self):
        """List all documents
        
        Returns:
            list: List of document dictionaries
        """
        conn = None
        try:
            conn = get_db_connection()
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute(
                    "SELECT doc_id, title, file_path, date_added FROM documents ORDER BY date_added DESC"
                )
                documents = cur.fetchall()
            return [dict(doc) for doc in documents]
        except Exception as e:
            print(f"Error listing documents: {e}")
            return []
        finally:
            if conn:
                conn.close()
    
    def delete(self, doc_id):
        """Delete document by ID
        
        Args:
            doc_id (str): Document ID
            
        Returns:
            bool: True if successful, False otherwise
        """
        conn = None
        try:
            conn = get_db_connection()
            with conn.cursor() as cur:
                cur.execute("DELETE FROM documents WHERE doc_id = %s", (doc_id,))
                rows_deleted = cur.rowcount
            conn.commit()
            return rows_deleted > 0
        except Exception as e:
            if conn:
                conn.rollback()
            print(f"Error deleting document: {e}")
            return False
        finally:
            if conn:
                conn.close()