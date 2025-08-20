import spacy
import re
from typing import List, Dict, Tuple, Optional
from transformers import pipeline, AutoTokenizer, AutoModelForSeq2SeqLM
import nltk
from textblob import TextBlob
from loguru import logger
import asyncio
from dataclasses import dataclass
import json

@dataclass
class RefinementResult:
    original_text: str
    refined_text: str
    changes_made: List[Dict]
    confidence_score: float
    processing_time: float

class TranslationRefiner:
    """Advanced NLP processor for refining machine-translated novel text"""
    
    def __init__(self):
        self.nlp = None
        self.grammar_checker = None
        self.paraphrasing_model = None
        self.tokenizer = None
        self.loaded = False
        
        # Common translation issues patterns
        self.awkward_patterns = [
            (r'\b(?:he|she|it)\s+(?:he|she|it)\b', 'pronoun_repetition'),
            (r'\b(?:the|a|an)\s+(?:the|a|an)\b', 'article_repetition'),
            (r'\bvery\s+very\b', 'adverb_repetition'),
            (r'\band\s+and\b', 'conjunction_repetition'),
            (r'\b(?:that|which)\s+(?:that|which)\b', 'relative_pronoun_repetition'),
        ]
        
        # Character name patterns (common in machine translations)
        self.name_inconsistency_patterns = [
            r'(?:Xiao|Little|Young)\s+\w+',  # Chinese naming patterns
            r'\w+(?:\s+)?(?:er|Young Master|Senior|Junior)',
            r'(?:Elder|Sect Leader|Master)\s+\w+',
        ]
        
        # Common machine translation artifacts
        self.mt_artifacts = [
            (r'\bthis\s+(?:king|emperor|lord|young\s+master)\b', 'referring_pattern'),
            (r'\b(?:en|um|ah|oh)\s*[.!?]\s*', 'hesitation_artifacts'),
            (r'\b(?:cough|cough\s+cough)\b', 'sound_effects'),
            (r'\[.*?\]', 'bracket_notes'),
            (r'\(.*?\)', 'parenthetical_notes'),
        ]
    
    async def initialize(self):
        """Initialize NLP models and resources"""
        try:
            logger.info("Initializing NLP models...")
            
            # Load spaCy model
            try:
                self.nlp = spacy.load("en_core_web_sm")
            except OSError:
                logger.warning("en_core_web_sm not found, downloading...")
                spacy.cli.download("en_core_web_sm")
                self.nlp = spacy.load("en_core_web_sm")
            
            # Download NLTK data
            try:
                nltk.data.find('tokenizers/punkt')
            except LookupError:
                nltk.download('punkt')
            
            # Initialize grammar checking pipeline
            self.grammar_checker = pipeline(
                "text2text-generation",
                model="vennify/t5-base-grammar-correction",
                max_length=512
            )
            
            # Initialize paraphrasing model for style improvement
            model_name = "tuner007/pegasus_paraphrase"
            self.tokenizer = AutoTokenizer.from_pretrained(model_name)
            self.paraphrasing_model = AutoModelForSeq2SeqLM.from_pretrained(model_name)
            
            self.loaded = True
            logger.info("NLP models initialized successfully")
            
        except Exception as e:
            logger.error(f"Error initializing NLP models: {e}")
            raise
    
    async def refine_text(self, text: str, glossary_terms: List[Dict] = None) -> RefinementResult:
        """Main method to refine machine-translated text"""
        import time
        start_time = time.time()
        
        if not self.loaded:
            await self.initialize()
        
        original_text = text
        changes_made = []
        
        try:
            # Step 1: Clean up basic formatting and artifacts
            text, formatting_changes = self._clean_formatting(text)
            changes_made.extend(formatting_changes)
            
            # Step 2: Fix obvious machine translation artifacts
            text, artifact_changes = self._fix_mt_artifacts(text)
            changes_made.extend(artifact_changes)
            
            # Step 3: Apply glossary consistency
            if glossary_terms:
                text, glossary_changes = self._apply_glossary_consistency(text, glossary_terms)
                changes_made.extend(glossary_changes)
            
            # Step 4: Fix pronoun and reference issues
            text, pronoun_changes = self._fix_pronoun_issues(text)
            changes_made.extend(pronoun_changes)
            
            # Step 5: Improve sentence structure
            text, structure_changes = await self._improve_sentence_structure(text)
            changes_made.extend(structure_changes)
            
            # Step 6: Grammar correction
            text, grammar_changes = await self._correct_grammar(text)
            changes_made.extend(grammar_changes)
            
            # Step 7: Style refinement
            text, style_changes = await self._refine_style(text)
            changes_made.extend(style_changes)
            
            # Calculate confidence score
            confidence = self._calculate_confidence_score(original_text, text, changes_made)
            
            processing_time = time.time() - start_time
            
            return RefinementResult(
                original_text=original_text,
                refined_text=text,
                changes_made=changes_made,
                confidence_score=confidence,
                processing_time=processing_time
            )
            
        except Exception as e:
            logger.error(f"Error refining text: {e}")
            return RefinementResult(
                original_text=original_text,
                refined_text=original_text,
                changes_made=[{"type": "error", "description": str(e)}],
                confidence_score=0.0,
                processing_time=time.time() - start_time
            )
    
    def _clean_formatting(self, text: str) -> Tuple[str, List[Dict]]:
        """Clean up basic formatting issues"""
        changes = []
        original_text = text
        
        # Fix spacing issues
        text = re.sub(r'\s+', ' ', text)  # Multiple spaces to single space
        text = re.sub(r'\n\s*\n\s*\n+', '\n\n', text)  # Multiple newlines to double
        text = re.sub(r'([.!?])\s*\n\s*([A-Z])', r'\1\n\n\2', text)  # Proper paragraph breaks
        
        # Fix punctuation spacing
        text = re.sub(r'\s+([,.!?;:])', r'\1', text)  # Remove space before punctuation
        text = re.sub(r'([.!?])\s*([A-Z])', r'\1 \2', text)  # Space after sentence end
        
        if text != original_text:
            changes.append({
                "type": "formatting",
                "description": "Fixed spacing and punctuation formatting"
            })
        
        return text.strip(), changes
    
    def _fix_mt_artifacts(self, text: str) -> Tuple[str, List[Dict]]:
        """Fix common machine translation artifacts"""
        changes = []
        
        for pattern, artifact_type in self.mt_artifacts:
            original_text = text
            
            if artifact_type == "referring_pattern":
                # Fix "this king/emperor" patterns
                text = re.sub(r'\bthis\s+(king|emperor|lord)\b', r'I', text, flags=re.IGNORECASE)
                text = re.sub(r'\bthis\s+young\s+master\b', r'I', text, flags=re.IGNORECASE)
            
            elif artifact_type == "hesitation_artifacts":
                # Remove hesitation sounds
                text = re.sub(pattern, '', text, flags=re.IGNORECASE)
            
            elif artifact_type == "sound_effects":
                # Remove or replace sound effects
                text = re.sub(r'\bcough\s*cough\b', '', text, flags=re.IGNORECASE)
                text = re.sub(r'\bcough\b', '', text, flags=re.IGNORECASE)
            
            elif artifact_type in ["bracket_notes", "parenthetical_notes"]:
                # Remove translator notes in brackets/parentheses
                if re.search(r'(?:TL|TN|Note|Author)', text, re.IGNORECASE):
                    text = re.sub(pattern, '', text)
            
            if text != original_text:
                changes.append({
                    "type": "mt_artifact",
                    "description": f"Fixed {artifact_type} artifacts"
                })
        
        return text, changes
    
    def _apply_glossary_consistency(self, text: str, glossary_terms: List[Dict]) -> Tuple[str, List[Dict]]:
        """Apply glossary terms for consistent naming"""
        changes = []
        
        for term in glossary_terms:
            original_term = term.get('original_term', '')
            preferred_term = term.get('preferred_term', '')
            term_type = term.get('term_type', 'general')
            
            if original_term and preferred_term and original_term != preferred_term:
                # Use word boundaries for character names and proper nouns
                if term_type in ['character', 'place', 'organization']:
                    pattern = r'\b' + re.escape(original_term) + r'\b'
                    if re.search(pattern, text, re.IGNORECASE):
                        text = re.sub(pattern, preferred_term, text, flags=re.IGNORECASE)
                        changes.append({
                            "type": "glossary",
                            "description": f"Replaced '{original_term}' with '{preferred_term}'"
                        })
        
        return text, changes
    
    def _fix_pronoun_issues(self, text: str) -> Tuple[str, List[Dict]]:
        """Fix pronoun and reference consistency issues"""
        changes = []
        doc = self.nlp(text)
        
        # Track entities and their pronouns
        entity_pronouns = {}
        
        for ent in doc.ents:
            if ent.label_ == "PERSON":
                # Determine likely gender based on context (simplified)
                entity_pronouns[ent.text] = self._infer_gender_pronoun(ent.text, text)
        
        # Fix obvious pronoun repetitions
        original_text = text
        for pattern, issue_type in self.awkward_patterns:
            text = re.sub(pattern, lambda m: self._fix_repetition(m.group()), text, flags=re.IGNORECASE)
        
        if text != original_text:
            changes.append({
                "type": "pronoun",
                "description": "Fixed pronoun repetition and consistency issues"
            })
        
        return text, changes
    
    def _infer_gender_pronoun(self, name: str, context: str) -> str:
        """Infer appropriate pronoun for a character name"""
        # Simple gender inference (could be improved with more sophisticated methods)
        male_indicators = ['master', 'king', 'emperor', 'lord', 'sir', 'he', 'his', 'him']
        female_indicators = ['lady', 'queen', 'empress', 'she', 'her', 'hers']
        
        context_lower = context.lower()
        
        # Count gender indicators near the name
        male_count = sum(1 for indicator in male_indicators if indicator in context_lower)
        female_count = sum(1 for indicator in female_indicators if indicator in context_lower)
        
        if male_count > female_count:
            return 'he'
        elif female_count > male_count:
            return 'she'
        else:
            return 'they'  # Default to neutral
    
    def _fix_repetition(self, repetition: str) -> str:
        """Fix repetitive phrases"""
        words = repetition.split()
        if len(words) >= 2 and words[0].lower() == words[1].lower():
            return words[0]
        return repetition
    
    async def _improve_sentence_structure(self, text: str) -> Tuple[str, List[Dict]]:
        """Improve sentence structure and flow"""
        changes = []
        
        # Split into sentences
        sentences = nltk.sent_tokenize(text)
        improved_sentences = []
        
        for sentence in sentences:
            # Fix run-on sentences
            if len(sentence.split()) > 40:  # Very long sentence
                # Try to split at logical points
                improved_sentence = self._split_long_sentence(sentence)
                if improved_sentence != sentence:
                    changes.append({
                        "type": "sentence_structure",
                        "description": "Split overly long sentence"
                    })
                improved_sentences.append(improved_sentence)
            else:
                improved_sentences.append(sentence)
        
        return ' '.join(improved_sentences), changes
    
    def _split_long_sentence(self, sentence: str) -> str:
        """Attempt to split long sentences at logical points"""
        # Look for coordinating conjunctions where we can split
        split_points = [', and ', ', but ', ', or ', ', so ', ', yet ']
        
        for split_point in split_points:
            if split_point in sentence:
                parts = sentence.split(split_point, 1)
                if len(parts) == 2 and len(parts[0].split()) > 15:
                    # Create two sentences
                    first_part = parts[0].strip()
                    second_part = parts[1].strip()
                    
                    # Ensure proper capitalization
                    if second_part and not second_part[0].isupper():
                        second_part = second_part[0].upper() + second_part[1:]
                    
                    return f"{first_part}. {second_part}"
        
        return sentence
    
    async def _correct_grammar(self, text: str) -> Tuple[str, List[Dict]]:
        """Apply grammar correction using transformer model"""
        changes = []
        
        try:
            # Process in chunks to avoid token limits
            sentences = nltk.sent_tokenize(text)
            corrected_sentences = []
            
            for sentence in sentences:
                if len(sentence.split()) > 3:  # Only process substantial sentences
                    # Use grammar correction model
                    corrected = self.grammar_checker(f"grammar: {sentence}", max_length=len(sentence) + 50)
                    corrected_text = corrected[0]['generated_text']
                    
                    # Only use if significantly different and improved
                    if self._is_improvement(sentence, corrected_text):
                        corrected_sentences.append(corrected_text)
                        changes.append({
                            "type": "grammar",
                            "description": f"Corrected grammar in sentence"
                        })
                    else:
                        corrected_sentences.append(sentence)
                else:
                    corrected_sentences.append(sentence)
            
            return ' '.join(corrected_sentences), changes
            
        except Exception as e:
            logger.warning(f"Grammar correction failed: {e}")
            return text, changes
    
    async def _refine_style(self, text: str) -> Tuple[str, List[Dict]]:
        """Refine writing style and make it more natural"""
        changes = []
        
        # Replace overly literal translations with more natural expressions
        style_replacements = [
            (r'\bvery\s+much\s+like\b', 'similar to'),
            (r'\bat\s+this\s+time\b', 'now'),
            (r'\bin\s+this\s+moment\b', 'at this moment'),
            (r'\bmore\s+and\s+more\b', 'increasingly'),
            (r'\bwhat\s+kind\s+of\b', 'what'),
            (r'\bthis\s+kind\s+of\b', 'this type of'),
        ]
        
        original_text = text
        for pattern, replacement in style_replacements:
            text = re.sub(pattern, replacement, text, flags=re.IGNORECASE)
        
        if text != original_text:
            changes.append({
                "type": "style",
                "description": "Improved naturalness and style"
            })
        
        return text, changes
    
    def _is_improvement(self, original: str, corrected: str) -> bool:
        """Determine if corrected text is an improvement"""
        # Simple heuristics to check if correction is beneficial
        if len(corrected) > len(original) * 1.5:  # Too much change
            return False
        
        if corrected.lower() == original.lower():  # No meaningful change
            return False
        
        # Check if basic grammar improved
        original_blob = TextBlob(original)
        corrected_blob = TextBlob(corrected)
        
        # Very basic check: corrected version should have better structure
        return len(corrected_blob.words) >= len(original_blob.words) * 0.8
    
    def _calculate_confidence_score(self, original: str, refined: str, changes: List[Dict]) -> float:
        """Calculate confidence score for the refinement"""
        if not changes:
            return 1.0  # No changes needed
        
        # Base score
        score = 0.7
        
        # Adjust based on types of changes
        change_types = [change.get('type', '') for change in changes]
        
        # More points for structural improvements
        if 'grammar' in change_types:
            score += 0.1
        if 'sentence_structure' in change_types:
            score += 0.1
        if 'style' in change_types:
            score += 0.05
        
        # Slight deduction for too many changes (might indicate poor original quality)
        if len(changes) > 10:
            score -= 0.1
        
        return max(0.0, min(1.0, score))

class ContextTracker:
    """Track context and maintain consistency across chapters"""
    
    def __init__(self):
        self.character_names = {}
        self.place_names = {}
        self.term_frequency = {}
        self.chapter_context = []
    
    def update_context(self, text: str, chapter_number: int):
        """Update context information from new chapter"""
        doc = spacy.load("en_core_web_sm")(text)
        
        # Extract and track entities
        for ent in doc.ents:
            if ent.label_ == "PERSON":
                self._track_entity(ent.text, self.character_names)
            elif ent.label_ in ["GPE", "LOC"]:  # Geographic/Location entities
                self._track_entity(ent.text, self.place_names)
        
        # Track term frequency
        words = [token.text.lower() for token in doc if token.is_alpha]
        for word in words:
            self.term_frequency[word] = self.term_frequency.get(word, 0) + 1
        
        self.chapter_context.append({
            'chapter': chapter_number,
            'entities': [ent.text for ent in doc.ents],
            'word_count': len(words)
        })
    
    def _track_entity(self, entity: str, entity_dict: Dict):
        """Track entity frequency and variations"""
        entity_lower = entity.lower()
        if entity_lower not in entity_dict:
            entity_dict[entity_lower] = {
                'canonical_form': entity,
                'variations': [entity],
                'frequency': 1
            }
        else:
            entity_dict[entity_lower]['frequency'] += 1
            if entity not in entity_dict[entity_lower]['variations']:
                entity_dict[entity_lower]['variations'].append(entity)
    
    def get_consistency_suggestions(self) -> List[Dict]:
        """Get suggestions for maintaining consistency"""
        suggestions = []
        
        # Suggest canonical forms for character names
        for name_key, name_data in self.character_names.items():
            if len(name_data['variations']) > 1:
                suggestions.append({
                    'type': 'character_name',
                    'original_variations': name_data['variations'],
                    'suggested_canonical': name_data['canonical_form'],
                    'frequency': name_data['frequency']
                })
        
        return suggestions 