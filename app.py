import os
import uuid
from flask import Flask, request, jsonify
from werkzeug.utils import secure_filename
from models.document import DocumentModel
from models.embedding import EmbeddingModel
from services.qa_service import QuestionAnsweringService
from flask_limiter.util import get_remote_address
from flask_limiter import Limiter
from custom_logger import logger

app = Flask(__name__)
app.config.from_object('config.Config')

limiter = Limiter(
    app,
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"]
)

# Create upload folder if it doesn't exist
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Initialize services
document_model = DocumentModel()
embedding_model = EmbeddingModel()
qa_service = QuestionAnsweringService(
    document_model=document_model,
    embedding_model=embedding_model,
    qa_model_name=app.config['QA_MODEL'],
    embedding_model_name=app.config['EMBEDDING_MODEL']
)

@app.route('/api/documents', methods=['POST'])
@limiter.limit("10 per minute")
def upload_document():
    """Upload and process a PDF document"""
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    
    if file and file.filename.lower().endswith('.pdf'):
        # Save the uploaded file
        filename = secure_filename(file.filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)
        
        # Process the PDF
        metadata = request.form.get('metadata', '{}')
        doc_id = qa_service.process_pdf(file_path, metadata)
        
        if doc_id:
            logger.info("Document saved.")
            return jsonify({
                'message': 'Document uploaded and processed successfully',
                'document_id': doc_id
            }), 201
        else:
            logger.error("Failed to save document.")
            return jsonify({'error': 'Failed to process document'}), 500
    
    return jsonify({'error': 'File must be a PDF'}), 400

@app.route('/api/documents', methods=['GET'])
def list_documents():
    """List all documents"""
    documents = document_model.list_all()
    logger.info("listing documents")
    return jsonify({'documents': documents}), 200

@app.route('/api/documents/<doc_id>', methods=['GET'])
def get_document(doc_id):
    """Get document details"""
    document = document_model.get_by_id(doc_id)
    if document:
        logger.info(f"returning document {doc_id}")
        return jsonify({'document': document}), 200
    logger.error("error: doc not found")
    return jsonify({'error': 'Document not found'}), 404

@app.route('/api/documents/<doc_id>', methods=['DELETE'])
def delete_document(doc_id):
    """Delete a document"""
    if document_model.delete(doc_id):
        logger.info(f"document {doc_id} deleted.")
        return jsonify({'message': 'Document deleted successfully'}), 200
    logger.error("error deleting document.")
    return jsonify({'error': 'Failed to delete document or document not found'}), 404

@app.route('/api/question', methods=['POST'])
def answer_question():
    """Answer a question based on document knowledge"""
    data = request.json
    if not data or 'question' not in data:
        return jsonify({'error': 'Question is required'}), 400
    
    question = data['question']
    doc_id = data.get('document_id')  # Optional: limit to specific document
    top_k = data.get('top_k', 5)
    
    answer = qa_service.answer_question(question, doc_id, top_k)
    return jsonify(answer), 200

if __name__ == '__main__':
    app.run(debug=app.config['DEBUG'], host=app.config['HOST'], port=app.config['PORT'])