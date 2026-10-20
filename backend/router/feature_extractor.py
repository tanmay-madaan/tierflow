import re

class FeatureExtractor:
    def extract(self, query: str) -> dict:
        query_lower = query.lower()
        
        # Text statistics
        query_length = len(query)
        words = query.split()
        word_count = len(words)
        sentence_count = max(1, len(re.split(r'[.!?]+', query)) - 1)
        
        # Keyword features
        math_keywords = ['calculate', 'equation', 'integral', 'derivative', 'sum', 'probability', 'matrix', 'vector', 'algebra', 'theorem', 'proof', 'mathematical']
        has_math_keywords = sum(1 for kw in math_keywords if kw in query_lower)
        
        code_keywords = ['code', 'function', 'algorithm', 'implement', 'debug', 'error', 'class', 'api', 'database', 'sql', 'python', 'javascript', 'optimize', 'refactor', 'compile']
        has_code_keywords = sum(1 for kw in code_keywords if kw in query_lower)
        
        reasoning_keywords = ['explain', 'analyze', 'compare', 'evaluate', 'design', 'why', 'how', 'implications', 'trade-off', 'pros and cons', 'argue', 'justify', 'critique']
        has_reasoning_keywords = sum(1 for kw in reasoning_keywords if kw in query_lower)
        
        # Question type
        q_types = ['what', 'who', 'when', 'where', 'why', 'how', 'define', 'list', 'design']
        question_type = 'other'
        for qt in q_types:
            if query_lower.startswith(qt) or f" {qt} " in query_lower:
                question_type = qt
                break
                
        # Constraints
        constraint_indicators = ['must', 'should', 'need', 'require', 'ensure', 'constraint', 'condition', 'at least', 'at most', 'maximum', 'minimum']
        num_constraints = sum(1 for kw in constraint_indicators if kw in query_lower)
        
        # Multi-step
        multi_step_indicators = ['step by step', 'first', 'then', 'and also', 'additionally', 'furthermore', 'multiple', 'pipeline', 'workflow', 'sequence']
        has_multi_step = sum(1 for kw in multi_step_indicators if kw in query_lower)
        
        # Estimated complexity heuristic
        complexity_score = word_count * 0.1 + has_math_keywords * 2 + has_code_keywords * 2 + has_reasoning_keywords * 2 + num_constraints * 1.5 + has_multi_step * 2
        
        if complexity_score < 3:
            estimated_complexity = 'LOW'
        elif complexity_score < 8:
            estimated_complexity = 'MODERATE'
        else:
            estimated_complexity = 'HIGH'
            
        return {
            'query_length': query_length,
            'word_count': word_count,
            'sentence_count': sentence_count,
            'has_math_keywords': has_math_keywords,
            'has_code_keywords': has_code_keywords,
            'has_reasoning_keywords': has_reasoning_keywords,
            'question_type': question_type,
            'num_constraints': num_constraints,
            'has_multi_step': has_multi_step,
            'estimated_complexity': estimated_complexity
        }
