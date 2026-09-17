import json
import os
import re
from typing import List, Dict, Any

import numpy as np
from sentence_transformers import SentenceTransformer
from pypdf import PdfReader

DATA_DIR = os.path.join(os.path.dirname(__file__), '..', 'data')
DOCUMENT_DIR = os.path.join(DATA_DIR, 'documents')
UPLOAD_DIR = os.path.join(DATA_DIR, 'uploads')
INDEX_PATH = os.path.join(DATA_DIR, 'knowledge_index.json')

EMBEDDING_MODEL = 'sentence-transformers/all-MiniLM-L6-v2'


def _ensure_directories():
    os.makedirs(DOCUMENT_DIR, exist_ok=True)
    os.makedirs(UPLOAD_DIR, exist_ok=True)
    os.makedirs(DATA_DIR, exist_ok=True)


def _chunk_text(text: str, chunk_size: int = 600, overlap: int = 150) -> List[str]:
    if not text or not text.strip():
        return []

    cleaned = re.sub(r'\s+', ' ', text).strip()
    sentences = re.split(r'(?<=[.!?])\s+', cleaned)
    chunks: List[str] = []
    current = ''

    for sentence in sentences:
        if not sentence.strip():
            continue
        if len(current) + len(sentence) <= chunk_size:
            current = f'{current} {sentence}'.strip()
        else:
            if current:
                chunks.append(current)
            current = sentence[:chunk_size]

        if len(current) > chunk_size:
            chunks.append(current[:chunk_size])
            current = current[chunk_size - overlap:]

    if current:
        chunks.append(current)

    return [chunk.strip() for chunk in chunks if chunk.strip()]


def _read_file_text(file_path: str) -> str:
    ext = os.path.splitext(file_path)[1].lower()
    if ext == '.txt':
        with open(file_path, 'r', encoding='utf-8') as handle:
            return handle.read()
    if ext == '.pdf':
        reader = PdfReader(file_path)
        pages = [page.extract_text() or '' for page in reader.pages]
        return '\n'.join(pages)
    raise ValueError(f'Unsupported file type: {ext}')


def _load_file_chunks(file_path: str) -> List[Dict[str, str]]:
    text = _read_file_text(file_path)
    chunks = _chunk_text(text)
    return [{'source': os.path.basename(file_path), 'text': chunk} for chunk in chunks]


def _save_index(index_data: List[Dict[str, Any]]):
    with open(INDEX_PATH, 'w', encoding='utf-8') as handle:
        json.dump(index_data, handle, ensure_ascii=False, indent=2)


def _load_index() -> List[Dict[str, Any]]:
    if not os.path.exists(INDEX_PATH):
        return []
    with open(INDEX_PATH, 'r', encoding='utf-8') as handle:
        try:
            return json.load(handle)
        except json.JSONDecodeError:
            return []


def _encode_texts(model: SentenceTransformer, texts: List[str]) -> np.ndarray:
    embeddings = model.encode(texts, convert_to_numpy=True, normalize_embeddings=True)
    return np.asarray(embeddings, dtype=np.float32)


def _compute_similarity(query_vector: np.ndarray, stored_vectors: np.ndarray) -> np.ndarray:
    if stored_vectors.size == 0:
        return np.array([], dtype=np.float32)
    norms = np.linalg.norm(stored_vectors, axis=1)
    norms[norms == 0] = 1
    scores = stored_vectors @ query_vector / (norms * np.linalg.norm(query_vector))
    return scores.astype(np.float32)


def build_index_if_needed() -> List[Dict[str, Any]]:
    _ensure_directories()
    index = []

    for file_name in sorted(os.listdir(DOCUMENT_DIR)):
        if file_name.startswith('.'):
            continue
        full_path = os.path.join(DOCUMENT_DIR, file_name)
        if os.path.isfile(full_path):
            index.extend(_load_file_chunks(full_path))

    for file_name in sorted(os.listdir(UPLOAD_DIR)):
        if file_name.startswith('.'):
            continue
        full_path = os.path.join(UPLOAD_DIR, file_name)
        if os.path.isfile(full_path):
            index.extend(_load_file_chunks(full_path))

    if not index:
        _save_index([])
        return []

    model = SentenceTransformer(EMBEDDING_MODEL)
    texts = [item['text'] for item in index]
    embeddings = _encode_texts(model, texts)

    stored = []
    for item, vector in zip(index, embeddings):
        stored.append({
            'source': item['source'],
            'text': item['text'],
            'embedding': vector.tolist(),
        })
    _save_index(stored)
    return stored


def ask_question(question: str) -> Dict[str, Any]:
    index = _load_index()
    if not index:
        return {
            'answer': 'No knowledge has been indexed yet. Add a document or upload a text/PDF file first.',
            'sources': []
        }

    model = SentenceTransformer(EMBEDDING_MODEL)
    query_vector = model.encode([question], convert_to_numpy=True, normalize_embeddings=True)[0]
    stored_vectors = np.asarray([np.asarray(item['embedding'], dtype=np.float32) for item in index], dtype=np.float32)
    scores = _compute_similarity(query_vector, stored_vectors)
    top_indices = np.argsort(scores)[::-1][:4]

    matched_docs = []
    for idx in top_indices:
        item = index[int(idx)]
        matched_docs.append({
            'source': item.get('source', 'unknown'),
            'text': item.get('text', ''),
            'score': float(scores[int(idx)])
        })

    answer_text = '\n\n'.join(doc['text'] for doc in matched_docs if doc['score'] > 0.0) or 'No confident match was found.'
    return {
        'answer': 'Based on the available knowledge, here is the most relevant answer:\n\n' + answer_text[:1500],
        'sources': [
            {'source': doc['source'], 'content': doc['text'][:400]}
            for doc in matched_docs
        ]
    }


def list_documents() -> List[str]:
    _ensure_directories()
    docs = []
    for directory in [DOCUMENT_DIR, UPLOAD_DIR]:
        for file_name in sorted(os.listdir(directory)):
            if not file_name.startswith('.') and os.path.isfile(os.path.join(directory, file_name)):
                docs.append(file_name)
    return sorted(set(docs))


def ingest_uploaded_file(file_obj) -> Dict[str, Any]:
    _ensure_directories()
    safe_name = os.path.basename(file_obj.filename).replace('..', '')
    if not safe_name:
        raise ValueError('File name is empty.')

    path = os.path.join(UPLOAD_DIR, safe_name)
    file_obj.save(path)

    new_chunks = _load_file_chunks(path)
    existing = _load_index()
    updated = existing + new_chunks

    model = SentenceTransformer(EMBEDDING_MODEL)
    embeddings = _encode_texts(model, [chunk['text'] for chunk in updated])
    final_index = []
    for item, vector in zip(updated, embeddings):
        final_index.append({
            'source': item['source'],
            'text': item['text'],
            'embedding': vector.tolist(),
        })

    _save_index(final_index)
    return {'message': f'Uploaded and indexed: {safe_name}', 'source': safe_name}
