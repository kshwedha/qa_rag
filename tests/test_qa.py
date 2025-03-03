import unittest
from unittest.mock import patch, MagicMock
from io import BytesIO
from datetime import datetime
from services.qa_service import QuestionAnsweringService


class TestQuestionAnsweringService(unittest.TestCase):
    
    def setUp(self):
        # Mocking the document model, embedding model, and QA pipeline
        self.mock_document_model = MagicMock()
        self.mock_embedding_model = MagicMock()
        self.mock_qa_pipeline = MagicMock()
        
        self.qa_service = QuestionAnsweringService(
            document_model=self.mock_document_model,
            embedding_model=self.mock_embedding_model,
            qa_model_name="deepset/roberta-base-squad2",
            embedding_model_name="sentence-transformers/all-MiniLM-L6-v2"
        )
        
        self.test_pdf_path = "./uploads/manual-testing.pdf"
        self.test_metadata = {"author": "me"}
        self.test_question = "What is Quality?"
        
    @patch("PyPDF2.PdfReader")
    def test_process_pdf_success(self, MockPdfReader):
        """Test successful PDF processing"""
        mock_pdf_reader = MagicMock()
        mock_pdf_reader.pages = [MagicMock(extract_text=MagicMock(return_value="This is a test PDF."))]
        MockPdfReader.return_value = mock_pdf_reader
        
        # Mock the create method to return a mock document ID
        self.mock_document_model.create.return_value = "12345"
        
        # Mock embedding model to return mock embeddings
        self.mock_embedding_model.create_chunks.return_value = True
        self.mock_embedding_model.search_similar.return_value = [{"text_content": "Test chunk", "doc_id": "12345"}]
        
        # Call the method
        result = self.qa_service.process_pdf(self.test_pdf_path, self.test_metadata)
        
        # Assertions
        self.assertEqual(result, "12345")
        self.mock_document_model.create.assert_called_once_with(
            "manual-testing.pdf", self.test_pdf_path, self.test_metadata
        )
        self.mock_embedding_model.create_chunks.assert_called_once()
    
    @patch("PyPDF2.PdfReader")
    def test_process_pdf_file_not_found(self, MockPdfReader):
        """Test PDF processing when the file is not found"""
        self.mock_document_model.create.return_value = None
        
        result = self.qa_service.process_pdf("non_existing_file.pdf")
        
        self.assertIsNone(result)
    
    def test_create_chunks(self):
        """Test chunk creation logic"""
        text = "This is a test sentence. This is another sentence. Yet another sentence."
        chunks = self.qa_service._create_chunks(text)
        
        self.assertGreater(len(chunks), 0)
        self.assertTrue(any("This is a test sentence." in chunk for chunk in chunks))

    
    @patch("transformers.pipeline")
    def test_answer_question(self, mock_qa_pipeline):
        """Test answering a question based on the document"""
        # Mock the QA pipeline to return a fake result
        mock_qa_pipeline.return_value = {"answer": "identify the defects and provide quality product to end user"}
        
        # Mock embedding model's search_similar method
        self.mock_embedding_model.search_similar.return_value = [{"text_content": "identify the defects and provide quality product to end user", "doc_id": "12345", "title": "manual-testing", "similarity": 0.36}]
        
        # Call the method
        result = self.qa_service.answer_question(self.test_question, doc_id="12345", top_k=1)
        
        # Assertions
        self.assertIn(result["answer"], "identify the defects and provide quality product to end user")
    
    @patch("transformers.pipeline")
    def test_answer_question_no_relevant_chunks(self, mock_qa_pipeline):
        """Test answering a question when no relevant chunks are found"""
        self.mock_embedding_model.search_similar.return_value = []
        
        # Call the method
        result = self.qa_service.answer_question(self.test_question)
        
        # Assertions
        self.assertEqual(result["answer"], "No relevant information found.")
        self.assertEqual(result["confidence"], 0)
        self.assertEqual(result["context"], "")
        self.assertEqual(result["sources"], [])

if __name__ == "__main__":
    unittest.main()
