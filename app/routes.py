from flask import Blueprint, render_template, request, jsonify
from app.rag_service import build_index_if_needed, ask_question, ingest_uploaded_file, list_documents

bp = Blueprint('main', __name__)


@bp.route('/')
def index():
    documents = list_documents()
    return render_template('index.html', documents=documents)


@bp.route('/ask', methods=['POST'])
def ask():
    payload = request.get_json(silent=True) or {}
    question = (payload.get('question') or '').strip()

    if not question:
        return jsonify({'answer': 'Please enter a question.', 'sources': []}), 400

    build_index_if_needed()
    answer = ask_question(question)
    return jsonify(answer)


@bp.route('/upload', methods=['POST'])
def upload_document():
    file = request.files.get('file')
    if not file or not file.filename:
        return jsonify({'error': 'No file selected.'}), 400

    try:
        result = ingest_uploaded_file(file)
        return jsonify(result)
    except Exception as exc:  # pragma: no cover
        return jsonify({'error': f'Upload failed: {exc}'}), 500
