"""
NLP Text Analysis Engine
Provides sentiment analysis, readability metrics, keyword extraction,
part-of-speech breakdown, extractive summarization, and entity extraction.
Includes graceful fallbacks so the app never crashes even if NLTK data downloads are pending.
"""

import re
import math
from collections import Counter

# Try importing NLTK and download required resources safely
NLTK_AVAILABLE = False
VADER_AVAILABLE = False
try:
    import nltk
    for pkg in ['vader_lexicon', 'punkt', 'punkt_tab', 'stopwords', 'averaged_perceptron_tagger']:
        try:
            nltk.download(pkg, quiet=True)
        except Exception:
            pass

    from nltk.sentiment.vader import SentimentIntensityAnalyzer
    from nltk.corpus import stopwords
    nltk_stopwords = set(stopwords.words('english'))
    vader_analyzer = SentimentIntensityAnalyzer()
    VADER_AVAILABLE = True
    NLTK_AVAILABLE = True
except Exception:
    nltk_stopwords = set()
    vader_analyzer = None

# Built-in lightweight fallback stopwords
FALLBACK_STOPWORDS = {
    'i', 'me', 'my', 'myself', 'we', 'our', 'ours', 'ourselves', 'you', "you're", "you've",
    "you'll", "you'd", 'your', 'yours', 'yourself', 'yourselves', 'he', 'him', 'his', 'himself',
    'she', "she's", 'her', 'hers', 'herself', 'it', "it's", 'its', 'itself', 'they', 'them',
    'their', 'theirs', 'themselves', 'what', 'which', 'who', 'whom', 'this', 'that', "that'll",
    'these', 'those', 'am', 'is', 'are', 'was', 'were', 'be', 'been', 'being', 'have', 'has',
    'had', 'having', 'do', 'does', 'did', 'doing', 'a', 'an', 'the', 'and', 'but', 'if', 'or',
    'because', 'as', 'until', 'while', 'of', 'at', 'by', 'for', 'with', 'about', 'against',
    'between', 'into', 'through', 'during', 'before', 'after', 'above', 'below', 'to', 'from',
    'up', 'down', 'in', 'out', 'on', 'off', 'over', 'under', 'again', 'further', 'then', 'once',
    'here', 'there', 'when', 'where', 'why', 'how', 'all', 'any', 'both', 'each', 'few', 'more',
    'most', 'other', 'some', 'such', 'no', 'nor', 'not', 'only', 'own', 'same', 'so', 'than',
    'too', 'very', 's', 't', 'can', 'will', 'just', 'don', "don't", 'should', "should've", 'now',
    'd', 'll', 'm', 'o', 're', 've', 'y', 'ain', 'aren', "aren't", 'couldn', "couldn't", 'didn',
    "didn't", 'doesn', "doesn't", 'hadn', "hadn't", 'hasn', "hasn't", 'haven', "haven't", 'isn',
    "isn't", 'ma', 'mightn', "mightn't", 'mustn', "mustn't", 'needn', "needn't", 'shan', "shan't",
    'shouldn', "shouldn't", 'wasn', "wasn't", 'weren', "weren't", 'won', "won't", 'wouldn', "wouldn't"
}

ALL_STOPWORDS = nltk_stopwords.union(FALLBACK_STOPWORDS)

# Built-in Sentiment Lexicon (for fast zero-dependency fallback)
LEXICON_FALLBACK = {
    'excellent': 0.8, 'amazing': 0.8, 'fantastic': 0.8, 'superb': 0.8, 'outstanding': 0.8,
    'wonderful': 0.75, 'great': 0.7, 'good': 0.5, 'love': 0.65, 'loved': 0.65, 'lovely': 0.6,
    'best': 0.7, 'better': 0.4, 'awesome': 0.75, 'happy': 0.6, 'delighted': 0.7, 'perfect': 0.8,
    'beautiful': 0.6, 'brilliant': 0.7, 'positive': 0.5, 'recommend': 0.5, 'impressive': 0.6,
    'efficient': 0.5, 'clean': 0.4, 'easy': 0.4, 'fast': 0.4, 'smooth': 0.4, 'terrific': 0.7,
    'bad': -0.5, 'terrible': -0.8, 'horrible': -0.8, 'awful': -0.8, 'poor': -0.5, 'worse': -0.6,
    'worst': -0.8, 'hate': -0.7, 'hated': -0.7, 'disappointed': -0.6, 'disappointing': -0.6,
    'slow': -0.4, 'broken': -0.6, 'ugly': -0.5, 'annoying': -0.5, 'boring': -0.4, 'failed': -0.6,
    'failure': -0.6, 'useless': -0.7, 'waste': -0.6, 'pain': -0.5, 'problem': -0.4, 'issues': -0.3,
    'flaw': -0.5, 'defective': -0.6, 'crash': -0.5, 'crashes': -0.5, 'expensive': -0.3,
    'difficult': -0.4, 'confusing': -0.4, 'negative': -0.5, 'mess': -0.5
}


def count_syllables(word: str) -> int:
    """Estimates the number of syllables in an English word."""
    word = word.lower().strip()
    if not word:
        return 0
    if len(word) <= 3:
        return 1
    # Remove non-alpha
    word = re.sub(r'[^a-z]', '', word)
    if not word:
        return 1
    # Count vowel groups
    word = re.sub(r'(?:[^laeiouy]|ed|es|e)$', '', word)
    word = re.sub(r'^y', '', word)
    syllables = len(re.findall(r'[aeiouy]{1,2}', word))
    return max(1, syllables)


def split_sentences(text: str) -> list[str]:
    """Splits text into sentences cleanly."""
    if not text.strip():
        return []
    sentences = re.split(r'(?<=[.!?])\s+', text.strip())
    return [s.strip() for s in sentences if s.strip()]


def tokenize_words(text: str) -> list[str]:
    """Extracts alphanumeric words from text."""
    return re.findall(r"\b[A-Za-z0-9]+(?:'[A-Za-z0-9]+)?\b", text)


def get_sentiment(text: str) -> dict:
    """
    Computes sentiment scores:
    Returns polarity (-1.0 to 1.0), subjectivity (0.0 to 1.0),
    label (Positive, Negative, Neutral), confidence, and mood.
    """
    if not text.strip():
        return {
            'polarity': 0.0,
            'subjectivity': 0.0,
            'compound': 0.0,
            'pos': 0.0,
            'neu': 1.0,
            'neg': 0.0,
            'label': 'Neutral',
            'mood': 'Neutral 😐',
            'color': '#64748b'
        }

    # Use VADER if available
    if VADER_AVAILABLE and vader_analyzer is not None:
        scores = vader_analyzer.polarity_scores(text)
        compound = scores['compound']
        pos = scores['pos']
        neg = scores['neg']
        neu = scores['neu']
    else:
        # Fallback lexicon calculation
        words = tokenize_words(text.lower())
        pos_score = 0.0
        neg_score = 0.0
        match_count = 0
        for w in words:
            if w in LEXICON_FALLBACK:
                val = LEXICON_FALLBACK[w]
                if val > 0:
                    pos_score += val
                else:
                    neg_score += abs(val)
                match_count += 1
        
        total = max(1, match_count)
        compound = (pos_score - neg_score) / (total + 1.0)
        compound = max(-1.0, min(1.0, compound * 2.0))
        pos = round(pos_score / (total + 1.0), 3)
        neg = round(neg_score / (total + 1.0), 3)
        neu = max(0.0, round(1.0 - (pos + neg), 3))
        scores = {'compound': compound, 'pos': pos, 'neu': neu, 'neg': neg}

    # Subjectivity estimation
    words = tokenize_words(text.lower())
    subjective_hits = sum(1 for w in words if w in LEXICON_FALLBACK or w in ['feel', 'think', 'believe', 'opinion', 'seems', 'probably', 'maybe', 'personally'])
    subjectivity = round(min(1.0, (subjective_hits * 2.5) / max(10, len(words))), 2)

    compound = scores['compound']
    if compound >= 0.05:
        if compound >= 0.5:
            label = 'Very Positive'
            mood = 'Joyful / Enthusiastic 🎉'
            color = '#10b981'
        else:
            label = 'Positive'
            mood = 'Optimistic / Satisfied 😊'
            color = '#34d399'
    elif compound <= -0.05:
        if compound <= -0.5:
            label = 'Very Negative'
            mood = 'Critical / Frustrated 😠'
            color = '#ef4444'
        else:
            label = 'Negative'
            mood = 'Concerned / Displeased 🙁'
            color = '#f87171'
    else:
        label = 'Neutral'
        mood = 'Objective / Informative 😐'
        color = '#94a3b8'

    return {
        'polarity': round(compound, 2),
        'subjectivity': subjectivity,
        'compound': round(compound, 3),
        'pos': round(scores['pos'], 3),
        'neu': round(scores['neu'], 3),
        'neg': round(scores['neg'], 3),
        'label': label,
        'mood': mood,
        'color': color
    }


def get_sentence_sentiments(text: str) -> list[dict]:
    """Analyzes sentiment for each sentence individually."""
    sentences = split_sentences(text)
    results = []
    for s in sentences[:25]:  # limit to top 25 for quick rendering
        sent_metrics = get_sentiment(s)
        results.append({
            'text': s,
            'label': sent_metrics['label'],
            'polarity': sent_metrics['polarity'],
            'color': sent_metrics['color']
        })
    return results


def get_readability(text: str) -> dict:
    """
    Computes readability scores:
    - Flesch Reading Ease
    - Flesch-Kincaid Grade Level
    - Coleman-Liau Index
    - Automated Readability Index (ARI)
    - Reading time (wpm = 200) & Speaking time (wpm = 130)
    """
    sentences = split_sentences(text)
    words = tokenize_words(text)
    total_words = len(words)
    total_sentences = max(1, len(sentences))
    total_characters = sum(len(w) for w in words)
    total_syllables = sum(count_syllables(w) for w in words)

    if total_words == 0:
        return {
            'flesch_reading_ease': 100.0,
            'reading_ease_level': 'Very Easy',
            'flesch_kincaid_grade': 0.0,
            'grade_level': 'Pre-school',
            'coleman_liau': 0.0,
            'ari': 0.0,
            'reading_time_min': 0,
            'speaking_time_min': 0,
            'avg_sentence_len': 0,
            'avg_syllables_per_word': 0
        }

    # Flesch Reading Ease
    # 206.835 - 1.015 * (total words / total sentences) - 84.6 * (total syllables / total words)
    fre = 206.835 - 1.015 * (total_words / total_sentences) - 84.6 * (total_syllables / total_words)
    fre = round(max(0.0, min(100.0, fre)), 1)

    if fre >= 90:
        reading_ease_level = 'Very Easy (5th grade)'
    elif fre >= 80:
        reading_ease_level = 'Easy (6th grade)'
    elif fre >= 70:
        reading_ease_level = 'Fairly Easy (7th grade)'
    elif fre >= 60:
        reading_ease_level = 'Standard (8th-9th grade)'
    elif fre >= 50:
        reading_ease_level = 'Fairly Difficult (10th-12th grade)'
    elif fre >= 30:
        reading_ease_level = 'Difficult (College level)'
    else:
        reading_ease_level = 'Very Confusing (College Graduate)'

    # Flesch-Kincaid Grade Level
    # 0.39 * (total words / total sentences) + 11.8 * (total syllables / total words) - 15.59
    fk_grade = 0.39 * (total_words / total_sentences) + 11.8 * (total_syllables / total_words) - 15.59
    fk_grade = round(max(0.0, fk_grade), 1)

    # Coleman-Liau Index
    # 0.0588 * L - 0.296 * S - 15.8
    # L = avg number of letters per 100 words, S = avg number of sentences per 100 words
    l_val = (total_characters / total_words) * 100
    s_val = (total_sentences / total_words) * 100
    cli = 0.0588 * l_val - 0.296 * s_val - 15.8
    cli = round(max(0.0, cli), 1)

    # Automated Readability Index (ARI)
    # 4.71 * (characters / words) + 0.5 * (words / sentences) - 21.43
    ari = 4.71 * (total_characters / total_words) + 0.5 * (total_words / total_sentences) - 21.43
    ari = round(max(0.0, ari), 1)

    # Reading & speaking time in seconds/minutes
    reading_seconds = math.ceil((total_words / 200) * 60)
    speaking_seconds = math.ceil((total_words / 130) * 60)

    return {
        'flesch_reading_ease': fre,
        'reading_ease_level': reading_ease_level,
        'flesch_kincaid_grade': fk_grade,
        'coleman_liau': cli,
        'ari': ari,
        'reading_time_sec': reading_seconds,
        'speaking_time_sec': speaking_seconds,
        'reading_time_text': f"{math.ceil(reading_seconds/60)} min" if reading_seconds >= 60 else f"{reading_seconds} sec",
        'speaking_time_text': f"{math.ceil(speaking_seconds/60)} min" if speaking_seconds >= 60 else f"{speaking_seconds} sec",
        'avg_sentence_len': round(total_words / total_sentences, 1),
        'avg_syllables_per_word': round(total_syllables / total_words, 2)
    }


def get_keywords(text: str, top_n: int = 10) -> list[dict]:
    """Finds most frequent meaningful words, excluding stopwords."""
    words = tokenize_words(text.lower())
    filtered = [w for w in words if len(w) > 2 and w not in ALL_STOPWORDS and not w.isdigit()]
    if not filtered:
        return []
    total = len(filtered)
    counts = Counter(filtered).most_common(top_n)
    return [
        {
            'word': word,
            'count': count,
            'percentage': round((count / total) * 100, 1)
        }
        for word, count in counts
    ]


def get_pos_distribution(text: str) -> dict:
    """
    Computes Part-of-Speech breakdown (Nouns, Verbs, Adjectives, Adverbs, Others).
    Uses NLTK pos_tag if available, otherwise heuristic suffix tagging.
    """
    words = tokenize_words(text)
    if not words:
        return {'Nouns': 0, 'Verbs': 0, 'Adjectives': 0, 'Adverbs': 0, 'Other': 0}

    pos_counts = {'Nouns': 0, 'Verbs': 0, 'Adjectives': 0, 'Adverbs': 0, 'Other': 0}

    if NLTK_AVAILABLE:
        try:
            tagged = nltk.pos_tag(words)
            for _, tag in tagged:
                if tag.startswith('NN'):
                    pos_counts['Nouns'] += 1
                elif tag.startswith('VB'):
                    pos_counts['Verbs'] += 1
                elif tag.startswith('JJ'):
                    pos_counts['Adjectives'] += 1
                elif tag.startswith('RB'):
                    pos_counts['Adverbs'] += 1
                else:
                    pos_counts['Other'] += 1
            return pos_counts
        except Exception:
            pass

    # Heuristic fallback
    for w in words:
        lw = w.lower()
        if lw.endswith(('tion', 'ment', 'ness', 'ity', 'er', 'or', 'ship', 'ism')):
            pos_counts['Nouns'] += 1
        elif lw.endswith(('ing', 'ed', 'ize', 'ate', 'ify')):
            pos_counts['Verbs'] += 1
        elif lw.endswith(('able', 'ible', 'al', 'ful', 'ic', 'ive', 'less', 'ous')):
            pos_counts['Adjectives'] += 1
        elif lw.endswith('ly'):
            pos_counts['Adverbs'] += 1
        else:
            if len(w) > 3 and w[0].isupper():
                pos_counts['Nouns'] += 1
            else:
                pos_counts['Other'] += 1

    return pos_counts


def extract_entities(text: str) -> dict:
    """Extracts URLs, emails, phone numbers, hashtags, mentions, and capitalized proper nouns."""
    urls = re.findall(r'https?://[^\s<>"]+|www\.[^\s<>"]+', text)
    emails = re.findall(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', text)
    phones = re.findall(r'(?:\+\d{1,3}[- ]?)?\(?\d{3}\)?[-. ]?\d{3}[-. ]?\d{4}', text)
    hashtags = re.findall(r'#\w+', text)
    mentions = re.findall(r'@\w+', text)

    # Extract capitalized multi-word or single named entities (excluding start of sentence)
    sentences = split_sentences(text)
    entities = set()
    for s in sentences:
        words = s.split()
        if len(words) > 1:
            for w in words[1:]:
                clean = re.sub(r'[^\w]', '', w)
                if clean and clean[0].isupper() and clean.lower() not in ALL_STOPWORDS and len(clean) > 2:
                    entities.add(clean)

    return {
        'urls': list(set(urls))[:8],
        'emails': list(set(emails))[:8],
        'phone_numbers': list(set(phones))[:8],
        'hashtags': list(set(hashtags))[:8],
        'mentions': list(set(mentions))[:8],
        'named_entities': list(entities)[:12]
    }


def generate_summary(text: str, max_sentences: int = 3) -> str:
    """Generates an extractive text summary based on word-frequency sentence scoring."""
    sentences = split_sentences(text)
    if len(sentences) <= max_sentences:
        return text.strip()

    words = tokenize_words(text.lower())
    filtered_words = [w for w in words if w not in ALL_STOPWORDS and len(w) > 2]
    if not filtered_words:
        return " ".join(sentences[:max_sentences])

    word_frequencies = Counter(filtered_words)
    max_freq = max(word_frequencies.values())
    for w in word_frequencies:
        word_frequencies[w] = word_frequencies[w] / max_freq

    sentence_scores = {}
    for i, s in enumerate(sentences):
        score = 0
        s_words = tokenize_words(s.lower())
        if not s_words:
            continue
        for sw in s_words:
            if sw in word_frequencies:
                score += word_frequencies[sw]
        # Normalize by length to prevent favoring overly long sentences
        sentence_scores[i] = score / (len(s_words) ** 0.5)

    # Pick top N sentences maintaining original narrative order
    ranked_indices = sorted(sentence_scores, key=sentence_scores.get, reverse=True)[:max_sentences]
    ordered_indices = sorted(ranked_indices)
    return " ".join(sentences[i] for i in ordered_indices)


def analyze_text(text: str) -> dict:
    """Runs the complete NLP analysis pipeline on input text."""
    clean_text = text.strip()
    words = tokenize_words(clean_text)
    characters_with_spaces = len(clean_text)
    characters_without_spaces = len(re.sub(r'\s+', '', clean_text))
    sentences = split_sentences(clean_text)
    paragraphs = [p for p in clean_text.split('\n') if p.strip()]

    # Collect all analyses
    stats = {
        'word_count': len(words),
        'char_count': characters_with_spaces,
        'char_no_spaces': characters_without_spaces,
        'sentence_count': len(sentences),
        'paragraph_count': len(paragraphs)
    }

    sentiment = get_sentiment(clean_text)
    sentence_sentiments = get_sentence_sentiments(clean_text)
    readability = get_readability(clean_text)
    keywords = get_keywords(clean_text, top_n=10)
    pos_distribution = get_pos_distribution(clean_text)
    entities = extract_entities(clean_text)
    summary = generate_summary(clean_text, max_sentences=3)

    return {
        'stats': stats,
        'sentiment': sentiment,
        'sentence_sentiments': sentence_sentiments,
        'readability': readability,
        'keywords': keywords,
        'pos': pos_distribution,
        'entities': entities,
        'summary': summary
    }
