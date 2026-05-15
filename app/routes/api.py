import logging
import os
import re
import uuid
from datetime import datetime
from typing import Any, Dict, List

from flask import Blueprint, current_app, jsonify, request
from werkzeug.utils import secure_filename

from ..core.ai import CollegeAI
from ..core.storage import (
    KNOWLEDGE_FILE,
    LOCATIONS_FILE,
    UPLOAD_DIR,
    ensure_data_dir,
    read_json_file,
    write_json_file,
)


api_bp = Blueprint('api', __name__)
logger = logging.getLogger(__name__)


def _ai() -> CollegeAI:
    return current_app.extensions['ai_assistant']  # type: ignore


def _require_admin(req: Any) -> bool:
    token = req.headers.get('X-Admin-Token') or req.args.get('admin_token')
    return token == current_app.config.get('ADMIN_TOKEN', 'changeme')


# Chat
@api_bp.post('/chat')
def chat():
    try:
        data = request.get_json() or {}
        message = str(data.get('message') or '').strip()
        if not message:
            return jsonify({'error': 'Message is required'}), 400
        result = _ai().get_response_with_meta(message)
        return jsonify({'reply': result['text'], 'source': result.get('source'), 'timestamp': datetime.now().isoformat(), 'status': 'success'})
    except Exception as e:
        logger.exception("Error in chat endpoint")
        return jsonify({'error': 'Internal server error'}), 500


# Knowledge CRUD
@api_bp.get('/knowledge')
def get_knowledge():
    try:
        built_in = list(_ai().knowledge_base.keys())
        admin_entries = _ai().admin_knowledge
        return jsonify({'built_in_categories': built_in, 'admin_entries': admin_entries, 'status': 'success'})
    except Exception:
        logger.exception('Error getting knowledge')
        return jsonify({'error': 'Failed to get knowledge'}), 500


@api_bp.post('/knowledge')
def add_knowledge():
    if not _require_admin(request):
        return jsonify({'error': 'Unauthorized'}), 401
    try:
        body = request.get_json() or {}
        keywords = body.get('keywords') or []
        responses = body.get('responses') or ([] if body.get('response') is None else [body.get('response')])
        title = body.get('title') or 'Custom'
        if not isinstance(keywords, list) or not keywords:
            return jsonify({'error': 'keywords must be a non-empty array'}), 400
        if not isinstance(responses, list) or not responses:
            return jsonify({'error': 'responses must be a non-empty array'}), 400
        entry = {
            'id': str(uuid.uuid4()),
            'title': str(title),
            'keywords': [str(k).lower() for k in keywords],
            'responses': [str(r) for r in responses],
            'created_at': datetime.now().isoformat()
        }
        entries = _ai().admin_knowledge.copy()
        entries.append(entry)
        if not write_json_file(KNOWLEDGE_FILE, {"entries": entries}):
            return jsonify({'error': 'Failed to save entry'}), 500
        _ai().admin_knowledge = entries
        return jsonify({'entry': entry, 'status': 'success'})
    except Exception:
        logger.exception('Error adding knowledge')
        return jsonify({'error': 'Failed to add knowledge'}), 500


@api_bp.put('/knowledge/<entry_id>')
def update_knowledge(entry_id: str):
    if not _require_admin(request):
        return jsonify({'error': 'Unauthorized'}), 401
    try:
        body = request.get_json() or {}
        entries = _ai().admin_knowledge.copy()
        found = None
        for e in entries:
            if e.get('id') == entry_id:
                found = e
                break
        if not found:
            return jsonify({'error': 'Entry not found'}), 404
        if 'title' in body:
            found['title'] = str(body['title'])
        if 'keywords' in body and isinstance(body['keywords'], list) and body['keywords']:
            found['keywords'] = [str(k).lower() for k in body['keywords']]
        if 'responses' in body and isinstance(body['responses'], list) and body['responses']:
            found['responses'] = [str(r) for r in body['responses']]
        if not write_json_file(KNOWLEDGE_FILE, {"entries": entries}):
            return jsonify({'error': 'Failed to save entry'}), 500
        _ai().admin_knowledge = entries
        return jsonify({'entry': found, 'status': 'success'})
    except Exception:
        logger.exception('Error updating knowledge')
        return jsonify({'error': 'Failed to update knowledge'}), 500


@api_bp.delete('/knowledge/<entry_id>')
def delete_knowledge(entry_id: str):
    if not _require_admin(request):
        return jsonify({'error': 'Unauthorized'}), 401
    try:
        entries = [e for e in _ai().admin_knowledge if e.get('id') != entry_id]
        if len(entries) == len(_ai().admin_knowledge):
            return jsonify({'error': 'Entry not found'}), 404
        if not write_json_file(KNOWLEDGE_FILE, {"entries": entries}):
            return jsonify({'error': 'Failed to delete entry'}), 500
        _ai().admin_knowledge = entries
        return jsonify({'status': 'success'})
    except Exception:
        logger.exception('Error deleting knowledge')
        return jsonify({'error': 'Failed to delete knowledge'}), 500


@api_bp.post('/knowledge/pdf')
def upload_pdf_knowledge():
    if not _require_admin(request):
        return jsonify({'error': 'Unauthorized'}), 401
    try:
        ensure_data_dir()
        if 'file' not in request.files:
            return jsonify({'error': 'No file uploaded'}), 400
        file = request.files['file']
        if not file or file.filename == '':
            return jsonify({'error': 'Empty file'}), 400
        if not file.filename.lower().endswith('.pdf'):
            return jsonify({'error': 'Only PDF files are supported'}), 400

        filename = secure_filename(file.filename)
        save_path = os.path.join(UPLOAD_DIR, filename)
        file.save(save_path)

        extracted_text = ''
        try:
            from PyPDF2 import PdfReader
            with open(save_path, 'rb') as f:
                reader = PdfReader(f)
                try:
                    if getattr(reader, 'is_encrypted', False):
                        try:
                            reader.decrypt("")
                        except Exception:
                            pass
                except Exception:
                    pass
                page_texts: List[str] = []
                for page in reader.pages:
                    try:
                        text = page.extract_text() or ''
                    except Exception:
                        text = ''
                    if text:
                        page_texts.append(text)
                extracted_text = '\n\n'.join(page_texts)
        except Exception as e:
            logger.exception('PDF extraction failed')
            return jsonify({'error': f'Failed to extract PDF text: {str(e)}'}), 500

        def chunk_text(text: str, size: int = 800) -> List[str]:
            paragraphs = [p.strip() for p in re.split(r"\n\s*\n", text) if p.strip()]
            segments: List[str] = []
            for para in paragraphs:
                start = 0
                while start < len(para):
                    segment = para[start:start+size]
                    segments.append(segment)
                    start += size
            return [s for s in segments if s]

        extracted_text = re.sub(r"\u0000", "", extracted_text)
        responses = chunk_text(extracted_text, size=800)[:10]
        if not responses:
            return jsonify({'error': 'No selectable text found in PDF (likely scanned).'}), 400

        title = request.form.get('title') or os.path.splitext(filename)[0]
        raw_keywords = request.form.get('keywords') or ''
        keywords = [k.strip().lower() for k in raw_keywords.split(',') if k.strip()]

        def tokenize(text: str) -> List[str]:
            return [t for t in re.findall(r"[a-zA-Z0-9]+", text.lower()) if t]
        title_tokens = [t for t in tokenize(title) if len(t) > 2]
        base_tokens = set(keywords)
        base_tokens.update(title_tokens[:5])
        stopwords = getattr(_ai(), '_stopwords', set())
        freq: Dict[str, int] = {}
        for tok in tokenize(extracted_text):
            if len(tok) <= 2 or tok in stopwords:
                continue
            freq[tok] = freq.get(tok, 0) + 1
        for tok, _ in sorted(freq.items(), key=lambda x: x[1], reverse=True)[:10]:
            base_tokens.add(tok)
        keywords = list(base_tokens)[:25]
        if not keywords:
            return jsonify({'error': 'keywords is required (comma separated)'}), 400

        entry = {'id': str(uuid.uuid4()), 'title': str(title), 'keywords': keywords, 'responses': responses, 'created_at': datetime.now().isoformat(), 'source_pdf': filename}
        entries = _ai().admin_knowledge.copy()
        entries.append(entry)
        if not write_json_file(KNOWLEDGE_FILE, {"entries": entries}):
            return jsonify({'error': 'Failed to save entry'}), 500
        _ai().admin_knowledge = entries
        return jsonify({'entry': entry, 'status': 'success', 'extracted_preview': responses[0][:200]})
    except Exception:
        logger.exception('Error uploading PDF knowledge')
        return jsonify({'error': 'Failed to upload PDF knowledge'}), 500


@api_bp.get('/health')
def health_check():
    return jsonify({'status': 'healthy', 'timestamp': datetime.now().isoformat(), 'service': 'Cllg Chatbot API'})


@api_bp.get('/stats')
def get_stats():
    try:
        conversation_count = len(_ai().conversation_history) // 2
        last_activity = _ai().conversation_history[-1]['timestamp'] if _ai().conversation_history else None
        return jsonify({'total_conversations': conversation_count, 'last_activity': last_activity, 'status': 'success'})
    except Exception:
        logger.exception('Error getting stats')
        return jsonify({'error': 'Failed to get statistics'}), 500


@api_bp.post('/clear-history')
def clear_history():
    try:
        _ai().conversation_history.clear()
        return jsonify({'message': 'History cleared successfully', 'status': 'success'})
    except Exception:
        logger.exception('Error clearing history')
        return jsonify({'error': 'Failed to clear history'}), 500


# Locations
def _load_locations() -> List[Dict[str, Any]]:
    data = read_json_file(LOCATIONS_FILE, default={"locations": []})
    raw = data.get('locations') or []
    normalized: List[Dict[str, Any]] = []
    for loc in raw:
        normalized.append({
            'id': loc.get('id') or str(uuid.uuid4()),
            'name': str(loc.get('name') or 'Unnamed Location'),
            'category': str(loc.get('category') or 'General'),
            'description': str(loc.get('description') or ''),
            'maps_query': str(loc.get('maps_query') or ''),
            'latitude': loc.get('latitude'),
            'longitude': loc.get('longitude'),
            'created_at': loc.get('created_at') or datetime.now().isoformat()
        })
    return normalized


def _save_locations(locations: List[Dict[str, Any]]) -> bool:
    return write_json_file(LOCATIONS_FILE, {"locations": locations})


_locations_store: List[Dict[str, Any]] = _load_locations()


@api_bp.get('/locations')
def list_locations():
    try:
        return jsonify({'locations': _locations_store, 'status': 'success'})
    except Exception:
        logger.exception('Error listing locations')
        return jsonify({'error': 'Failed to list locations'}), 500


@api_bp.post('/locations')
def add_location():
    if not _require_admin(request):
        return jsonify({'error': 'Unauthorized'}), 401
    try:
        body = request.get_json() or {}
        name = str(body.get('name') or '').strip()
        if not name:
            return jsonify({'error': 'name is required'}), 400
        category = str(body.get('category') or 'General')
        description = str(body.get('description') or '')
        maps_query = str(body.get('maps_query') or '')
        def to_float_or_none(v):
            try:
                return float(v)
            except Exception:
                return None
        latitude = to_float_or_none(body.get('latitude'))
        longitude = to_float_or_none(body.get('longitude'))

        entry = {'id': str(uuid.uuid4()), 'name': name, 'category': category, 'description': description, 'maps_query': maps_query, 'latitude': latitude, 'longitude': longitude, 'created_at': datetime.now().isoformat()}
        tmp = list(_locations_store)
        tmp.append(entry)
        if not _save_locations(tmp):
            return jsonify({'error': 'Failed to save location'}), 500
        _locations_store.clear()
        _locations_store.extend(tmp)
        return jsonify({'location': entry, 'status': 'success'})
    except Exception:
        logger.exception('Error adding location')
        return jsonify({'error': 'Failed to add location'}), 500


@api_bp.put('/locations/<loc_id>')
def update_location(loc_id: str):
    if not _require_admin(request):
        return jsonify({'error': 'Unauthorized'}), 401
    try:
        body = request.get_json() or {}
        tmp = list(_locations_store)
        found = None
        for loc in tmp:
            if loc.get('id') == loc_id:
                found = loc
                break
        if not found:
            return jsonify({'error': 'Location not found'}), 404
        if 'name' in body and str(body.get('name') or '').strip():
            found['name'] = str(body['name']).strip()
        if 'category' in body and body.get('category') is not None:
            found['category'] = str(body['category'])
        if 'description' in body and body.get('description') is not None:
            found['description'] = str(body['description'])
        if 'maps_query' in body and body.get('maps_query') is not None:
            found['maps_query'] = str(body['maps_query'])
        if 'latitude' in body:
            try:
                found['latitude'] = float(body['latitude']) if body['latitude'] is not None else None
            except Exception:
                pass
        if 'longitude' in body:
            try:
                found['longitude'] = float(body['longitude']) if body['longitude'] is not None else None
            except Exception:
                pass
        if not _save_locations(tmp):
            return jsonify({'error': 'Failed to save location'}), 500
        _locations_store.clear()
        _locations_store.extend(tmp)
        return jsonify({'location': found, 'status': 'success'})
    except Exception:
        logger.exception('Error updating location')
        return jsonify({'error': 'Failed to update location'}), 500


@api_bp.delete('/locations/<loc_id>')
def delete_location(loc_id: str):
    if not _require_admin(request):
        return jsonify({'error': 'Unauthorized'}), 401
    try:
        tmp = [l for l in _locations_store if l.get('id') != loc_id]
        if len(tmp) == len(_locations_store):
            return jsonify({'error': 'Location not found'}), 404
        if not _save_locations(tmp):
            return jsonify({'error': 'Failed to delete location'}), 500
        _locations_store.clear()
        _locations_store.extend(tmp)
        return jsonify({'status': 'success'})
    except Exception:
        logger.exception('Error deleting location')
        return jsonify({'error': 'Failed to delete location'}), 500




