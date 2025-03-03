import unittest
import json
from unittest.mock import patch, MagicMock
from app import app
from services.qa_service import QuestionAnsweringService
from models.document import DocumentModel
from flask import Flask


class FlaskAppTestCase(unittest.TestCase):
    def setUp(self):
        """Set up the Flask test client"""
        self.app = app.test_client()
        self.app.testing = True

        # Mocking the database and services to avoid hitting real DBs or external services
        self.mock_document_model = MagicMock(spec=DocumentModel)
        self.mock_embedding_model = MagicMock()
        self.mock_qa_service = MagicMock(spec=QuestionAnsweringService)

        app.config['UPLOAD_FOLDER'] = './uploads'  # Set a temp folder for uploads

    @patch('services.qa_service.QuestionAnsweringService', return_value=MagicMock())
    @patch('models.document.DocumentModel', return_value=MagicMock())
    def test_upload_document(self, mock_document, mock_qa_service):
        """Test uploading a document"""
        # Create a mock file for the test
        data = {
            'file': (open('./uploads/manual-testing.pdf', 'rb'), 'manual-testing.pdf'),
            'metadata': '{"title": "Test Document"}'
        }

        with self.app as client:
            response = client.post('/api/documents', data=data, content_type='multipart/form-data')

        self.assertEqual(response.status_code, 201)
        self.assertIn('Document uploaded and processed successfully', response.json['message'])

    @patch('models.document.DocumentModel.list_all', return_value=[{'id': '1', 'title': 'Test Doc'}])
    def test_list_documents(self, mock_list_all):
        """Test listing all documents"""
        response = self.app.get('/api/documents')
        self.assertEqual(response.status_code, 200)
        self.assertIn('documents', response.json)
        self.assertEqual(len(response.json['documents']), 1)

    @patch('models.document.DocumentModel.get_by_id', return_value={'id': '1', 'title': 'Test Doc'})
    def test_get_document(self, mock_get_by_id):
        """Test retrieving a specific document"""
        response = self.app.get('/api/documents/1')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json['document']['id'], '1')

    @patch('models.document.DocumentModel.delete', return_value=True)
    def test_delete_document(self, mock_delete):
        """Test deleting a document"""
        response = self.app.delete('/api/documents/1')
        self.assertEqual(response.status_code, 200)
        self.assertIn('Document deleted successfully', response.json['message'])

    @patch('services.qa_service.QuestionAnsweringService.answer_question', return_value={'answer': 'Test answer'})
    def test_answer_question(self, mock_answer_question):
        """Test answering a question"""
        data = {
            'question': 'What is Quality?',
            'document_id': '1',
            'top_k': 5
        }
        response = self.app.post('/api/question', json=data)
        self.assertEqual(response.status_code, 200)
        self.assertIn('answer', response.json)
        self.assertEqual(response.json['answer'], 'Test answer')

    @patch('services.qa_service.QuestionAnsweringService.answer_question', return_value={'answer': 'Test answer'})
    def test_answer_question_missing_field(self, mock_answer_question):
        """Test error when question is missing"""
        data = {}
        response = self.app.post('/api/question', json=data)
        self.assertEqual(response.status_code, 400)
        self.assertIn('Question is required', response.json['error'])


if __name__ == '__main__':
    unittest.main()
