import re
from typing import Dict, List, Tuple
import spacy
from sklearn.feature_extraction.text import TfidfVectorizer
import numpy as np

class EmergencyClassifier:
    def __init__(self):
        """Initialize the emergency classifier"""
        self.emergency_keywords = {
            'medical': {
                'keywords': ['heart attack', 'stroke', 'bleeding', 'unconscious', 'chest pain', 
                           'difficulty breathing', 'overdose', 'seizure', 'allergic reaction',
                           'broken bone', 'severe pain', 'can\'t breathe', 'passed out'],
                'urgency_base': 8
            },
            'fire': {
                'keywords': ['fire', 'smoke', 'burning', 'flames', 'explosion', 'gas leak',
                           'building on fire', 'house fire', 'wildfire', 'smoke alarm'],
                'urgency_base': 9
            },
            'crime': {
                'keywords': ['robbery', 'theft', 'assault', 'shooting', 'stabbing', 'kidnapping',
                           'break in', 'domestic violence', 'rape', 'murder', 'gun', 'weapon'],
                'urgency_base': 8
            },
            'accident': {
                'keywords': ['car accident', 'crash', 'collision', 'hit and run', 'motorcycle accident',
                           'truck accident', 'vehicle accident', 'traffic accident', 'wreck'],
                'urgency_base': 7
            },
            'natural_disaster': {
                'keywords': ['earthquake', 'flood', 'tornado', 'hurricane', 'landslide',
                           'tsunami', 'avalanche', 'storm', 'lightning strike'],
                'urgency_base': 9
            },
            'general': {
                'keywords': ['help', 'emergency', 'urgent', 'danger', 'trapped', 'stuck',
                           'lost', 'missing person', 'animal attack'],
                'urgency_base': 6
            }
        }
        
        self.location_keywords = [
            'near', 'at', 'by', 'on', 'street', 'road', 'avenue', 'boulevard',
            'building', 'mall', 'store', 'hospital', 'school', 'park', 'bridge'
        ]
        
        # Try to load spaCy model, fallback to basic processing if not available
        try:
            self.nlp = spacy.load("en_core_web_sm")
        except OSError:
            self.nlp = None
            print("Warning: spaCy model not found. Using basic text processing.")
    
    def classify_emergency(self, transcript: str) -> Dict:
        """Classify emergency type and urgency from transcript"""
        transcript_lower = transcript.lower()
        
        # Find matching emergency types
        matches = {}
        for emergency_type, data in self.emergency_keywords.items():
            score = 0
            matched_keywords = []
            
            for keyword in data['keywords']:
                if keyword in transcript_lower:
                    score += 1
                    matched_keywords.append(keyword)
            
            if score > 0:
                matches[emergency_type] = {
                    'score': score,
                    'keywords': matched_keywords,
                    'urgency_base': data['urgency_base']
                }
        
        # Determine primary emergency type
        if matches:
            primary_type = max(matches.keys(), key=lambda x: matches[x]['score'])
            urgency = self._calculate_urgency(transcript_lower, matches[primary_type])
            keywords = matches[primary_type]['keywords']
        else:
            primary_type = 'unknown'
            urgency = 5  # Medium urgency for unknown emergencies
            keywords = []
        
        # Extract potential location
        location_info = self._extract_location(transcript)
        
        return {
            'type': primary_type,
            'urgency': urgency,
            'keywords': keywords,
            'location_mentioned': location_info,
            'confidence': min(len(keywords) * 0.2 + 0.3, 1.0)
        }
    
    def _calculate_urgency(self, transcript: str, match_data: Dict) -> int:
        """Calculate urgency level (1-10)"""
        base_urgency = match_data['urgency_base']
        
        # Urgency modifiers
        urgency_modifiers = {
            'very': 1, 'extremely': 2, 'really': 1, 'badly': 1,
            'critical': 2, 'severe': 2, 'serious': 1, 'major': 1,
            'immediately': 2, 'now': 1, 'quickly': 1, 'fast': 1,
            'dying': 3, 'dead': 3, 'fatal': 3, 'life threatening': 3
        }
        
        modifier_bonus = 0
        for modifier, bonus in urgency_modifiers.items():
            if modifier in transcript:
                modifier_bonus += bonus
        
        # Cap urgency at 10
        final_urgency = min(base_urgency + modifier_bonus, 10)
        return max(final_urgency, 1)  # Minimum urgency of 1
    
    def _extract_location(self, transcript: str) -> str:
        """Extract potential location information from transcript"""
        if self.nlp:
            doc = self.nlp(transcript)
            locations = [ent.text for ent in doc.ents if ent.label_ in ['GPE', 'LOC', 'FAC']]
            if locations:
                return ', '.join(locations)
        
        # Fallback: simple pattern matching
        location_patterns = [
            r'(?:near|at|by|on)\s+([A-Za-z\s]+(?:street|road|avenue|blvd|boulevard|st|rd|ave))',
            r'(?:near|at|by)\s+([A-Za-z\s]+(?:mall|store|building|hospital|school|park))',
            r'(\d+\s+[A-Za-z\s]+(?:street|road|avenue|blvd|boulevard))'
        ]
        
        for pattern in location_patterns:
            match = re.search(pattern, transcript, re.IGNORECASE)
            if match:
                return match.group(1).strip()
        
        return "Location not specified"