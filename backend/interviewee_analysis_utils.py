# Interviewee analysis utilities
from transformers import pipeline
import re

# Load sentiment analysis pipeline (can be replaced with a more professional model)
sentiment_analyzer = pipeline('sentiment-analysis')

FILLER_WORDS = [
    'um', 'uh', 'like', 'you know', 'so', 'actually', 'basically', 'literally', 'well', 'hmm', 'er', 'ah', 'okay', 'right', 'I mean'
]

def analyze_sentiment(text):
    result = sentiment_analyzer(text[:512])[0]  # Truncate for model input
    return {'label': result['label'], 'score': float(result['score'])}

def count_filler_words(text):
    text_lower = text.lower()
    counts = {}
    total = 0
    for word in FILLER_WORDS:
        # Use word boundaries for single words, substring for phrases
        if ' ' in word:
            count = text_lower.count(word)
        else:
            count = len(re.findall(r'\\b' + re.escape(word) + r'\\b', text_lower))
        counts[word] = count
        total += count
    return {'total_fillers': total, 'details': counts}

def analyze_professionalism(text):
    # Simple heuristic: more fillers, negative sentiment, short answers = less professional
    sentiment = analyze_sentiment(text)
    fillers = count_filler_words(text)
    length = len(text.split())
    professionalism_score = max(0, 1.0 - 0.2*fillers['total_fillers'] - (0.2 if sentiment['label'] == 'NEGATIVE' else 0) + 0.1*(length > 20))
    return {
        'sentiment': sentiment,
        'filler_words': fillers,
        'word_count': length,
        'professionalism_score': round(professionalism_score, 2)
    }
