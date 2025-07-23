"""
Intelligent Question Router using Gemini AI
Brain Team Enhancement

This module uses Gemini AI to intelligently route questions and frame answers
from the campus database, providing much better accuracy than keyword matching.
"""

import json
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from .mvp_gemini_handler import GeminiHandler

@dataclass
class RoutingResult:
    """Result from intelligent routing"""
    is_campus_question: bool
    categories: List[str]
    key_entities: List[str]
    confidence: float
    reasoning: str

class IntelligentRouter:
    """
    Uses Gemini AI to intelligently route questions and extract relevant information
    """
    
    def __init__(self):
        self.gemini = GeminiHandler()
        
        # Load campus database for context
        self.campus_info = self._load_campus_context()
    
    def _load_campus_context(self) -> Dict:
        """Load campus database structure for AI context"""
        try:
            with open('data/campus_qa/expanded_database.json', 'r') as f:
                db = json.load(f)
                
            # Extract key information for AI context
            categories = db.get('campus_database', {}).get('categories', {})
            context = {
                'available_categories': list(categories.keys()),
                'sample_questions': {}
            }
            
            # Get sample questions from each category
            for cat_name, cat_data in categories.items():
                questions = cat_data.get('questions', [])
                if questions:
                    context['sample_questions'][cat_name] = [
                        q['question'] for q in questions[:3]  # First 3 questions as examples
                    ]
            
            return context
        except Exception as e:
            print(f"Warning: Could not load campus context: {e}")
            return {}
    
    def analyze_question(self, user_question: str) -> RoutingResult:
        """
        Use Gemini AI to analyze if question is campus-related and extract routing info
        """
        if not self.gemini.is_available():
            # Fallback to simple keyword detection
            return self._fallback_analysis(user_question)
        
        prompt = self._create_analysis_prompt(user_question)
        
        try:
            response = self.gemini.generate_response(prompt, "analysis")
            if response:
                return self._parse_analysis_response(response.text, user_question)
        except Exception as e:
            print(f"Gemini analysis error: {e}")
        
        # Fallback if AI analysis fails
        return self._fallback_analysis(user_question)
    
    def _create_analysis_prompt(self, user_question: str) -> str:
        """Create prompt for Gemini to analyze the question"""
        categories_info = ""
        if self.campus_info.get('available_categories'):
            categories_info = f"Available campus categories: {', '.join(self.campus_info['available_categories'])}"
        
        prompt = f"""You are an expert at analyzing student questions for a campus AI assistant. 

Analyze this student question: "{user_question}"

Campus context:
{categories_info}

Please determine:
1. Is this a campus-related question? (YES/NO)
2. If YES, which categories are most relevant? (pick 1-3 from the available categories)
3. What are the key entities/keywords to search for?
4. Confidence level (0.0-1.0)

Respond in this exact format:
CAMPUS_QUESTION: YES/NO
CATEGORIES: category1, category2, category3
ENTITIES: entity1, entity2, entity3
CONFIDENCE: 0.X
REASONING: Brief explanation

Campus questions include: locations, hours, contacts, procedures, events, dining, academic services, etc.
Non-campus questions include: general knowledge, weather, math, personal advice, etc."""

        return prompt
    
    def _parse_analysis_response(self, response_text: str, original_question: str) -> RoutingResult:
        """Parse Gemini's analysis response"""
        try:
            lines = response_text.strip().split('\n')
            
            is_campus = False
            categories = []
            entities = []
            confidence = 0.5
            reasoning = "AI analysis"
            
            for line in lines:
                line = line.strip()
                if line.startswith('CAMPUS_QUESTION:'):
                    is_campus = 'YES' in line.upper()
                elif line.startswith('CATEGORIES:'):
                    cats = line.split(':', 1)[1].strip()
                    categories = [c.strip().lower() for c in cats.split(',') if c.strip()]
                elif line.startswith('ENTITIES:'):
                    ents = line.split(':', 1)[1].strip()
                    entities = [e.strip().lower() for e in ents.split(',') if e.strip()]
                elif line.startswith('CONFIDENCE:'):
                    conf_str = line.split(':', 1)[1].strip()
                    try:
                        confidence = float(conf_str)
                    except:
                        confidence = 0.7
                elif line.startswith('REASONING:'):
                    reasoning = line.split(':', 1)[1].strip()
            
            return RoutingResult(
                is_campus_question=is_campus,
                categories=categories,
                key_entities=entities,
                confidence=confidence,
                reasoning=reasoning
            )
            
        except Exception as e:
            print(f"Error parsing analysis response: {e}")
            return self._fallback_analysis(original_question)
    
    def _fallback_analysis(self, user_question: str) -> RoutingResult:
        """Fallback analysis when Gemini is not available"""
        user_lower = user_question.lower()
        
        # Campus keywords
        campus_keywords = [
            'library', 'gym', 'cafeteria', 'dining', 'hall', 'building', 'room', 'parking',
            'campus', 'student', 'class', 'course', 'professor', 'wifi', 'registration',
            'contact', 'hours', 'open', 'close', 'schedule', 'event', 'club', 'sport',
            'department', 'office', 'staff', 'faculty', 'id', 'card', 'portal', 'email',
            'mess', 'canteen', 'food', 'it', 'support', 'tech', 'computer', 'help',
            'desk', 'service', 'services', 'facility', 'facilities', 'location',
            'where', 'find', 'chancellor', 'vice', 'admin', 'administration'
        ]
        
        is_campus = any(keyword in user_lower for keyword in campus_keywords)
        
        # Simple category detection
        categories = []
        if any(word in user_lower for word in ['contact', 'support', 'help', 'phone', 'email', 'it']):
            categories.append("contact")
        if any(word in user_lower for word in ['hours', 'time', 'open', 'close', 'schedule']):
            categories.append("hours")
        if any(word in user_lower for word in ['eat', 'food', 'dining', 'mess', 'cafeteria']):
            categories.append("dining")
        if any(word in user_lower for word in ['where', 'location', 'find']):
            categories.append("navigation")
        
        if not categories and is_campus:
            categories = ["navigation"]  # Default for campus questions
        
        # Extract key entities
        entities = [word for word in user_lower.split() if word in campus_keywords]
        
        return RoutingResult(
            is_campus_question=is_campus,
            categories=categories,
            key_entities=entities,
            confidence=0.6 if is_campus else 0.3,
            reasoning="Keyword-based fallback analysis"
        )
    
    def find_best_answer(self, user_question: str, routing_result: RoutingResult, 
                        campus_database: Dict) -> Optional[str]:
        """
        Use Gemini AI to find and frame the best answer from campus database
        """
        if not routing_result.is_campus_question:
            return None
        
        # Get relevant database entries
        relevant_entries = self._get_relevant_entries(routing_result, campus_database)
        
        if not relevant_entries:
            return None
        
        if not self.gemini.is_available():
            # Fallback to simple matching
            return self._simple_answer_matching(user_question, relevant_entries)
        
        # Use Gemini to find and frame the best answer
        return self._ai_answer_selection(user_question, relevant_entries)
    
    def _get_relevant_entries(self, routing_result: RoutingResult, 
                            campus_database: Dict) -> List[Dict]:
        """Extract relevant database entries based on routing result"""
        entries = []
        
        categories = campus_database.get('campus_database', {}).get('categories', {})
        
        for category_name in routing_result.categories:
            if category_name in categories:
                questions = categories[category_name].get('questions', [])
                entries.extend(questions)
        
        return entries
    
    def _ai_answer_selection(self, user_question: str, entries: List[Dict]) -> Optional[str]:
        """Use Gemini AI to select and frame the best answer"""
        if not entries:
            return None
        
        # Create context with available answers
        context = "Available campus information:\n"
        for i, entry in enumerate(entries):
            context += f"{i+1}. Q: {entry.get('question', '')}\n"
            context += f"   A: {entry.get('answer', '')}\n\n"
        
        prompt = f"""You are NEXi, a helpful campus AI assistant. A student asked: "{user_question}"

{context}

Please:
1. Find the most relevant answer from the campus information above
2. If found, provide that exact answer (don't modify the content)
3. If no perfect match, provide a helpful response directing them to relevant services
4. Keep the response concise and friendly

Response:"""
        
        try:
            response = self.gemini.generate_response(prompt, "answer_selection")
            if response:
                return response.text
        except Exception as e:
            print(f"AI answer selection error: {e}")
        
        # Fallback to simple matching
        return self._simple_answer_matching(user_question, entries)
    
    def _simple_answer_matching(self, user_question: str, entries: List[Dict]) -> Optional[str]:
        """Simple fallback answer matching"""
        user_lower = user_question.lower()
        
        # Remove common words for better matching
        stop_words = {'where', 'is', 'the', 'a', 'an', 'how', 'do', 'i', 'can', 'what', 'when'}
        user_words = [word.strip('?,!.') for word in user_lower.split() 
                     if word.strip('?,!.') not in stop_words and len(word) > 2]
        
        best_score = 0
        best_answer = None
        
        for entry in entries:
            question = entry.get('question', '').lower()
            answer = entry.get('answer', '')
            
            # Score based on word overlap
            question_words = [word.strip('?,!.') for word in question.split() 
                            if word.strip('?,!.') not in stop_words and len(word) > 2]
            
            common_words = set(user_words) & set(question_words)
            score = len(common_words)
            
            if score > best_score and score > 0:
                best_score = score
                best_answer = answer
        
        return best_answer

# Test function
def test_intelligent_router():
    """Test the intelligent router"""
    router = IntelligentRouter()
    
    test_questions = [
        "Where is the library?",
        "Where is mess?",
        "Where can I find IT support?", 
        "What time does the dining hall close?",
        "Can I meet the Vice Chancellor?",
        "What's the weather like?",
        "What's 2 + 2?"
    ]
    
    print("🧠 Testing Intelligent Router")
    print("=" * 50)
    
    for question in test_questions:
        result = router.analyze_question(question)
        print(f"\nQ: {question}")
        print(f"Campus Question: {result.is_campus_question}")
        print(f"Categories: {result.categories}")
        print(f"Entities: {result.key_entities}")
        print(f"Confidence: {result.confidence:.2f}")
        print(f"Reasoning: {result.reasoning}")

if __name__ == "__main__":
    test_intelligent_router()
