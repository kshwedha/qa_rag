import os
import re
import numpy as np
from PyPDF2 import PdfReader
from custom_logger import logger
from transformers import pipeline
from sentence_transformers import SentenceTransformer
from custom_logger import logger
# import ollama, openai

class QuestionAnsweringService:
    """Service for PDF processing and question answering"""
    
    def __init__(self, document_model, embedding_model, qa_model_name, embedding_model_name):
        """
        Initialize the QA service
        
        Args:
            document_model: Model for document operations
            embedding_model: Model for embedding operations
            qa_model_name (str): Hugging Face QA model name
            embedding_model_name (str): Sentence transformer model name
        """
        self.document_model = document_model
        self.embedding_model = embedding_model
        
        # Load NLP models
        logger.info(f"Loading QA model: {qa_model_name}")
        self.qa_pipeline = pipeline('question-answering', model=qa_model_name)
        
        logger.info(f"Loading embedding model: {embedding_model_name}")
        self.sentence_transformer = SentenceTransformer(embedding_model_name)
        
        # Configuration
        self.chunk_size = 250
        self.overlap = 50
    
    def process_pdf(self, pdf_path, metadata=None):
        """
        Process a PDF file and store its chunks and embeddings
        
        Args:
            pdf_path (str): Path to the PDF file
            metadata (dict): Optional metadata
            
        Returns:
            str: Document ID if successful, None otherwise
        """
        if not os.path.exists(pdf_path):
            logger.info(f"Error: File {pdf_path} not found")
            return None
            
        try:
            logger.info(f"Processing PDF: {pdf_path}")
            reader = PdfReader(pdf_path)
            
            # Extract text from PDF
            logger.info("extracting pdf text")
            full_text = ""
            for page in reader.pages:
                text = page.extract_text()
                if text:
                    full_text += text + " "
            
            full_text = re.sub(r'\s+', ' ', full_text).strip()
            
            if not full_text:
                logger.info("Error: No text content extracted from PDF")
                return None
            
            # Create document record
            logger.info("creating doc record")
            title = os.path.basename(pdf_path)
            doc_id = self.document_model.create(title, pdf_path, metadata)
            
            if not doc_id:
                logger.info("Error: Failed to create document record")
                return None
            
            # Generate chunks
            logger.info("creating chunks")
            chunks = self._create_chunks(full_text)
            if not chunks:
                logger.info("Error: Failed to create text chunks")
                self.document_model.delete(doc_id)
                return None
            
            # Create embeddings for chunks
            logger.info("Create embeddings for chunks")
            embeddings = self.sentence_transformer.encode(chunks)
            
            # Store chunks and embeddings
            logger.info("Store chunks and embeddings")
            if not self.embedding_model.create_chunks(doc_id, chunks, embeddings):
                logger.info("Error: Failed to store chunks and embeddings")
                self.document_model.delete(doc_id)
                return None
            
            logger.info(f"PDF processed and stored successfully. Document ID: {doc_id}")
            return doc_id
            
        except Exception as e:
            logger.info(f"Error processing PDF: {e}")
            return None
    
    def _create_chunks(self, text):
        """Split text into overlapping chunks for embedding"""
        chunks = []
        start = 0
        text_len = len(text)
        
        while start < text_len:
            end = min(start + self.chunk_size, text_len)
            
            # If we're not at the end, try to end at a sentence boundary
            if end < text_len:
                sentence_end = max(text.rfind(". ", start, end), 
                                text.rfind("? ", start, end),
                                text.rfind("! ", start, end))
                
                if sentence_end > start + self.chunk_size // 2:
                    end = sentence_end + 1
                else:
                    space = text.rfind(" ", start, end)
                    if space > start + self.chunk_size // 2:
                        end = space

            chunks.append(text[start:end].strip())
            start += (end - start) - self.overlap
            if start+self.overlap == end:
                break
        return chunks
    
    def answer_question(self, question, doc_id=None, top_k=5):
        """
        Answer a question using stored document embeddings
        
        Args:
            question (str): Question to answer
            doc_id (str, optional): Limit search to specific document
            top_k (int): Number of relevant chunks to consider
            
        Returns:
            dict: Answer with metadata
        """
        # Get question embedding
        logger.info("reading question.")
        logger.info(f"question: {question}")
        logger.info(f"doc id: {doc_id}")
        question_embedding = self.sentence_transformer.encode(question)
        
        # Search for similar chunks
        similar_chunks = self.embedding_model.search_similar(
            embedding=question_embedding,
            top_k=top_k,
            doc_id=doc_id
        )
        
        if not similar_chunks:
            return {
                "answer": "No relevant information found.",
                "confidence": 0,
                "context": "",
                "sources": []
            }
        
        # Combine chunks to create context
        context = " ".join([chunk["text_content"] for chunk in similar_chunks])

        # Track which documents the answer came from
        source_docs = []
        for chunk in similar_chunks:
            if chunk["doc_id"] not in [doc["id"] for doc in source_docs]:
                source_docs.append({
                    "id": chunk["doc_id"],
                    "title": chunk["title"],
                    "similarity": float(chunk["similarity"])
                })
        
        # Sort sources by similarity
        source_docs.sort(key=lambda x: x["similarity"], reverse=True)
        
        return self.generate_answer_pipeline(question, context, source_docs)
        # if os.environ.get("GENERAL"):
            # logger.info("generating answer via general.")
            # return self.generate_answer_pipeline(question, context, source_docs)
        # logger.info("generating answer via model.")
        # return self.generate_answer_model(question, context, source_docs)
    
    def generate_answer_pipeline(self, question, context, source_docs):
        # Use QA model to find answer in context
        qa_result = self.qa_pipeline(question=question, context=context)
        
        return {
            "answer": qa_result["answer"],
            "confidence": float(qa_result["score"]),
            "context": context,
            "sources": source_docs
        }

    # def generate_answer_model(self, question, context, source_docs):
    #     prompt = f"Using the following context, answer the question:\n\nContext: {context}\n\nQuestion: {question}\n\nAnswer:"
    #     if os.environ.get("ollama", False):
    #         response = ollama.chat(model=os.environ.get("ollama_model"), messages=[{"role": "user", "content": prompt}])
    #     else:
    #         response = openai.ChatCompletion.create(model=os.environ.get("gpt_model"), messages=[{"role": "user", "content": prompt}])
    #     return {
    #         "answer": response["choices"][0]["message"]["content"],
    #         "confidence": float("inf"),
    #         "context": context,
    #         "sources": source_docs
    #     }