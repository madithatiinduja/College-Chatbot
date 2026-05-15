import json
import logging
import os
import random
import re
import uuid
from datetime import datetime
from typing import Any, Dict, List, Set

from .storage import (
    KNOWLEDGE_FILE,
)

logger = logging.getLogger(__name__)


class CollegeAI:
    def __init__(self, data_dir: str):
        self.data_dir = data_dir
        self.knowledge_base = self._load_knowledge_base()
        self.conversation_history: List[Dict[str, Any]] = []
        self.admin_knowledge: List[Dict[str, Any]] = self._load_admin_knowledge()
        self._stopwords: Set[str] = set([
            'the','a','an','and','or','but','if','then','else','on','in','at','for','to','from','by','with','of','is','are','was','were','be','been','it','this','that','these','those','as','about','into','over','under','after','before','between','how','what','when','where','which','who','whom','why','can','do','does','did','will','would','should','could','may','might','you','your','yours','we','our','ours','they','their','theirs','i','me','my','mine'
        ])

    def _load_knowledge_base(self) -> Dict[str, Any]:
        # Minimal default set; the full set remains as in the original app
        return {
            'admission': {
                'keywords': ['admission', 'requirements', 'apply', 'application', 'enroll', 'enrollment'],
                'responses': [
                    "Here are the general admission requirements for our college:\n\n• High school diploma or equivalent (GED)\n• Completed application form with $50 application fee\n• Official high school transcripts\n• SAT or ACT scores (recommended)\n• Personal statement or essay\n• Letters of recommendation (2 required)\n• Application deadline: March 1st for Fall semester\n\nFor specific programs, additional requirements may apply. Would you like me to provide details about a particular major or program?"
                ]
            }
        }

    def _load_admin_knowledge(self) -> List[Dict[str, Any]]:
        try:
            if not os.path.isfile(KNOWLEDGE_FILE):
                return []
            with open(KNOWLEDGE_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
            entries = data.get('entries', [])
            normalized: List[Dict[str, Any]] = []
            for entry in entries:
                responses = entry.get('responses') or []
                if not isinstance(responses, list):
                    responses = []
                normalized.append({
                    'id': entry.get('id') or str(uuid.uuid4()),
                    'title': entry.get('title') or 'Custom',
                    'keywords': [str(k).lower() for k in entry.get('keywords', []) if isinstance(k, str)],
                    'responses': [str(r) for r in responses if isinstance(r, str)],
                    'created_at': entry.get('created_at') or datetime.now().isoformat(),
                    'source_pdf': entry.get('source_pdf')
                })
            return normalized
        except Exception:
            logger.exception("Failed to load admin knowledge")
            return []

    def _tokenize(self, text: str) -> List[str]:
        tokens = re.findall(r"[a-zA-Z0-9]+", text.lower())
        return [t for t in tokens if t and t not in self._stopwords]

    def _score_entry_match(self, user_message_lower: str, user_tokens: Set[str], entry: Dict[str, Any]) -> int:
        keywords: List[str] = entry.get('keywords', []) or []
        keyword_hits = sum(1 for k in keywords if k and k in user_message_lower)
        score = keyword_hits * 3
        keyword_tokens = set()
        for k in keywords:
            keyword_tokens.update(self._tokenize(k))
        score += min(len(user_tokens & keyword_tokens), 4)
        title = entry.get('title') or ''
        title_tokens = set(self._tokenize(title))
        score += min(len(user_tokens & title_tokens), 2)
        responses: List[str] = entry.get('responses') or []
        sample = " \n ".join(responses[:2])
        resp_tokens = set(self._tokenize(sample))
        score += min(len(user_tokens & resp_tokens), 5)
        return score

    def get_response(self, user_message: str) -> str:
        user_message_lower = user_message.lower()
        user_tokens = set(self._tokenize(user_message))

        self.conversation_history.append({'user': user_message, 'timestamp': datetime.now().isoformat()})

        best_admin = None
        best_admin_score = 0
        for entry in self.admin_knowledge:
            score = self._score_entry_match(user_message_lower, user_tokens, entry)
            if score > best_admin_score:
                best_admin_score = score
                best_admin = entry
        if best_admin and best_admin_score > 0 and best_admin.get('responses'):
            response = random.choice(best_admin['responses'])
            if '?' in user_message and response and not response.strip().endswith('?'):
                response += "\n\nIs there anything else you'd like to know?"
            self.conversation_history.append({'bot': response, 'timestamp': datetime.now().isoformat()})
            return response

        best_match = None
        highest_score = 0
        for category, data in self.knowledge_base.items():
            score = sum(1 for keyword in data['keywords'] if keyword in user_message_lower)
            if score > highest_score:
                highest_score = score
                best_match = category
        if best_match and highest_score > 0:
            responses = self.knowledge_base[best_match]['responses']
            response = random.choice(responses)
            if '?' in user_message:
                response += "\n\nIs there anything else you'd like to know?"
        else:
            response = "I'm here to help with college questions. Could you rephrase or specify your topic?"

        self.conversation_history.append({'bot': response, 'timestamp': datetime.now().isoformat()})
        return response

    def get_response_with_meta(self, user_message: str) -> Dict[str, Any]:
        user_message_lower = user_message.lower()
        user_tokens = set(self._tokenize(user_message))
        best_admin = None
        best_admin_score = 0
        for entry in self.admin_knowledge:
            score = self._score_entry_match(user_message_lower, user_tokens, entry)
            if score > best_admin_score:
                best_admin_score = score
                best_admin = entry
        if best_admin and best_admin_score > 0 and best_admin.get('responses'):
            text = random.choice(best_admin['responses'])
            if '?' in user_message and text and not text.strip().endswith('?'):
                text += "\n\nIs there anything else you'd like to know?"
            self.conversation_history.append({'user': user_message, 'timestamp': datetime.now().isoformat()})
            self.conversation_history.append({'bot': text, 'timestamp': datetime.now().isoformat()})
            return {'text': text, 'source': {'type': 'admin', 'id': best_admin.get('id'), 'title': best_admin.get('title'), 'source_pdf': best_admin.get('source_pdf')}}
        text = self.get_response(user_message)
        return {'text': text, 'source': None}


def init_ai_assistant() -> CollegeAI:
    data_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir, os.pardir, 'data'))
    return CollegeAI(data_dir=data_dir)




