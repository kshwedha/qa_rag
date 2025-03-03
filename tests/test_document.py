import unittest
from unittest.mock import patch, ANY, MagicMock
from models.document import DocumentModel
from datetime import datetime
import json


class TestDocumentModel(unittest.TestCase):
    
    def setUp(self):
        """Setup the test environment"""
        self.document_model = DocumentModel()
        self.test_doc_id = "12345"
        self.test_title = "Test Document"
        self.test_file_path = "./uploads/manual-testing.pdf"
        self.test_metadata = {"author": "Test Author"}
    
    @patch('models.document.get_db_connection')
    def test_create(self, mock_get_db_connection):
        """Test the create method"""
        # Mock the database connection and cursor
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_get_db_connection.return_value = mock_conn
        mock_conn.cursor.return_value.__enter__.return_value = mock_cursor
        
        # Simulate a successful insert
        mock_cursor.execute.return_value = None
        mock_conn.commit.return_value = None
        
        doc_id = self.document_model.create(
            self.test_title, self.test_file_path, self.test_metadata
        )
        
        # Verify the result and the mock interactions
        self.assertIsNotNone(doc_id)
        mock_cursor.execute.assert_called_once_with(
            "INSERT INTO documents (doc_id, title, file_path, date_added, metadata) VALUES (%s, %s, %s, %s, %s)",
            (doc_id, self.test_title, self.test_file_path, ANY, json.dumps(self.test_metadata))
        )
        mock_conn.commit.assert_called_once()

    @patch('models.document.get_db_connection')
    def test_get_by_id(self, mock_get_db_connection):
        """Test the get_by_id method"""
        # Mock the database connection and cursor
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_get_db_connection.return_value = mock_conn
        mock_conn.cursor.return_value.__enter__.return_value = mock_cursor
        
        # Simulate a successful fetch
        mock_cursor.fetchone.return_value = {
            'doc_id': self.test_doc_id,
            'title': self.test_title,
            'file_path': self.test_file_path,
            'date_added': datetime.now(),
            'metadata': json.dumps(self.test_metadata)
        }
        
        document = self.document_model.get_by_id(self.test_doc_id)
        
        # Verify the result and the mock interactions
        self.assertEqual(document['doc_id'], self.test_doc_id)
        mock_cursor.execute.assert_called_once_with(
            "SELECT doc_id, title, file_path, date_added, metadata FROM documents WHERE doc_id = %s",
            (self.test_doc_id,)
        )
        
    @patch('models.document.get_db_connection')
    def test_list_all(self, mock_get_db_connection):
        """Test the list_all method"""
        # Mock the database connection and cursor
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_get_db_connection.return_value = mock_conn
        mock_conn.cursor.return_value.__enter__.return_value = mock_cursor
        
        # Simulate a successful fetch of documents
        mock_cursor.fetchall.return_value = [{
            'doc_id': self.test_doc_id,
            'title': self.test_title,
            'file_path': self.test_file_path,
            'date_added': datetime.now()
        }]
        
        documents = self.document_model.list_all()
        
        # Verify the result and the mock interactions
        self.assertEqual(len(documents), 1)
        self.assertEqual(documents[0]['doc_id'], self.test_doc_id)
        mock_cursor.execute.assert_called_once_with(
            "SELECT doc_id, title, file_path, date_added FROM documents ORDER BY date_added DESC"
        )
        
    @patch('models.document.get_db_connection')
    def test_delete(self, mock_get_db_connection):
        """Test the delete method"""
        # Mock the database connection and cursor
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_get_db_connection.return_value = mock_conn
        mock_conn.cursor.return_value.__enter__.return_value = mock_cursor
        
        # Simulate a successful delete
        mock_cursor.rowcount = 1
        mock_conn.commit.return_value = None
        
        result = self.document_model.delete(self.test_doc_id)
        
        # Verify the result and the mock interactions
        self.assertTrue(result)
        mock_cursor.execute.assert_called_once_with(
            "DELETE FROM documents WHERE doc_id = %s", (self.test_doc_id,)
        )
        mock_conn.commit.assert_called_once()

    @patch('models.document.get_db_connection')
    def test_delete_not_found(self, mock_get_db_connection):
        """Test delete method when document does not exist"""
        # Mock the database connection and cursor
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_get_db_connection.return_value = mock_conn
        mock_conn.cursor.return_value.__enter__.return_value = mock_cursor
        
        # Simulate a document not found
        mock_cursor.rowcount = 0
        
        result = self.document_model.delete(self.test_doc_id)
        
        # Verify the result and the mock interactions
        self.assertFalse(result)
        mock_cursor.execute.assert_called_once_with(
            "DELETE FROM documents WHERE doc_id = %s", (self.test_doc_id,)
        )
        mock_conn.commit.assert_called_once()


if __name__ == '__main__':
    unittest.main()
