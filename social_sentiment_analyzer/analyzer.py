# import torch
# from transformers import AutoTokenizer, AutoModelForSequenceClassification
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from typing import List, Dict
from googletrans import Translator
# from config import GEMINI_API_KEY
# import google.generativeai as genai

# Load Hugging Face model and tokenizer once
# This will download the model from the Hugging Face Hub on the first run.
# print("[INFO] Loading Hugging Face model for sentiment analysis...")
# hf_tokenizer = AutoTokenizer.from_pretrained('nlptown/bert-base-multilingual-uncased-sentiment')
# hf_model = AutoModelForSequenceClassification.from_pretrained('nlptown/bert-base-multilingual-uncased-sentiment')
# print("[INFO] Hugging Face model loaded.")


# def analyze_comments_hf(comments: List[str]) -> Dict:
#     """
#     Analyzes a list of comments for sentiment using a Hugging Face transformer model.

#     Args:
#         comments (List[str]): A list of comment strings.

#     Returns:
#         Dict: A dictionary containing sentiment counts and a list of
#               each comment with its detailed score and classification.
#     """
#     sentiment_counts = {'positive': 0, 'neutral': 0, 'negative': 0}
#     analyzed_comments = []

#     for comment in comments:
#         if not comment:
#             continue
        
#         # Tokenize the comment and get model output
#         inputs = hf_tokenizer(comment, return_tensors="pt", truncation=True, max_length=512)
#         with torch.no_grad():
#             logits = hf_model(**inputs).logits

#         # The model returns scores for 1 to 5 stars.
#         # We convert this to a classification.
#         predicted_class_id = logits.argmax().item()
        
#         # Map star ratings to sentiment
#         # 1, 2 stars -> negative
#         # 3 stars -> neutral
#         # 4, 5 stars -> positive
#         if predicted_class_id < 2: # Corresponds to 1 and 2 stars
#             sentiment_class = 'negative'
#         elif predicted_class_id == 2: # Corresponds to 3 stars
#             sentiment_class = 'neutral'
#         else: # Corresponds to 4 and 5 stars
#             sentiment_class = 'positive'

#         sentiment_counts[sentiment_class] += 1
            
#         analyzed_comments.append({
#             'original_text': comment,
#             'translated_text': None,  # No translation needed
#             'scores': {'stars': predicted_class_id + 1}, # Store star rating
#             'classification': sentiment_class
#         })

#     total_comments = len(analyzed_comments)
#     results = {
#         'sentiment_counts': sentiment_counts,
#         'sentiment_distribution': {
#             'positive': round((sentiment_counts['positive'] / total_comments) * 100, 2) if total_comments > 0 else 0,
#             'neutral': round((sentiment_counts['neutral'] / total_comments) * 100, 2) if total_comments > 0 else 0,
#             'negative': round((sentiment_counts['negative'] / total_comments) * 100, 2) if total_comments > 0 else 0,
#         },
#         'analyzed_comments': analyzed_comments
#     }
#     return results


def analyze_comments_vader(comments: List[str]) -> Dict:
    """
    Analyzes a list of comments for sentiment and categorizes them using VADER.
    Translates each comment to English before analysis.

    Args:
        comments (List[str]): A list of comment strings.

    Returns:
        Dict: A dictionary containing sentiment counts and a list of
              each comment with its detailed score and classification.
    """
    analyzer = SentimentIntensityAnalyzer()
    translator = Translator()
    sentiment_counts = {'positive': 0, 'neutral': 0, 'negative': 0}
    analyzed_comments = []

    for comment in comments:
        if not comment:
            continue
        # Translate to English
        try:
            translation = translator.translate(comment, dest='en')
            translated_text = translation.text
        except Exception as e:
            print(f"[WARNING] Translation failed for comment: {comment}\nError: {e}")
            translated_text = comment  # Fallback to original
        
        scores = analyzer.polarity_scores(translated_text)
        compound = scores['compound']

        # Classify sentiment based on the compound score
        if compound >= 0.05:
            sentiment_class = 'positive'
        elif compound <= -0.05:
            sentiment_class = 'negative'
        else:
            sentiment_class = 'neutral'
        
        sentiment_counts[sentiment_class] += 1
            
        analyzed_comments.append({
            'original_text': comment,
            'translated_text': translated_text,
            'scores': scores,
            'classification': sentiment_class
        })

    total_comments = len(analyzed_comments)
    results = {
        'sentiment_counts': sentiment_counts,
        'sentiment_distribution': {
            'positive': round((sentiment_counts['positive'] / total_comments) * 100, 2) if total_comments > 0 else 0,
            'neutral': round((sentiment_counts['neutral'] / total_comments) * 100, 2) if total_comments > 0 else 0,
            'negative': round((sentiment_counts['negative'] / total_comments) * 100, 2) if total_comments > 0 else 0,
        },
        'analyzed_comments': analyzed_comments
    }
    return results


# def analyze_comments_gemini(comments: List[str]) -> Dict:
#     """
#     Analyzes a list of comments for sentiment using Gemini API.
#     Args:
#         comments (List[str]): A list of comment strings.
#     Returns:
#         Dict: A dictionary containing sentiment counts and a list of
#               each comment with its detailed score and classification.
#     """
#     genai.configure(api_key=GEMINI_API_KEY)
#     try:
#         model = genai.GenerativeModel('models/gemini-pro')
#     except Exception as e:
#         print(f"[DEBUG] Could not initialize 'models/gemini-pro': {e}")
#         print("[DEBUG] Listing available Gemini models:")
#         for m in genai.list_models():
#             print(m.name, m.supported_generation_methods)
#         raise
#     sentiment_counts = {'positive': 0, 'neutral': 0, 'negative': 0}
#     analyzed_comments = []

#     for comment in comments:
#         if not comment:
#             continue
#         prompt = (
#             "Classify the sentiment of the following comment as strictly one of: positive, neutral, or negative. "
#             "Only return the label (positive, neutral, or negative) and nothing else.\n"
#             f"Comment: {comment}"
#         )
#         try:
#             response = model.generate_content(prompt)
#             label = response.text.strip().lower()
#             if label not in sentiment_counts:
#                 label = 'neutral'  # fallback for unexpected output
#         except Exception as e:
#             print(f"[WARNING] Gemini API failed for comment: {comment}\nError: {e}")
#             print("[DEBUG] Listing available Gemini models:")
#             for m in genai.list_models():
#                 print(m.name, m.supported_generation_methods)
#             label = 'neutral'
#         sentiment_counts[label] += 1
#         analyzed_comments.append({
#             'original_text': comment,
#             'classification': label
#         })

#     total_comments = len(analyzed_comments)
#     results = {
#         'sentiment_counts': sentiment_counts,
#         'sentiment_distribution': {
#             'positive': round((sentiment_counts['positive'] / total_comments) * 100, 2) if total_comments > 0 else 0,
#             'neutral': round((sentiment_counts['neutral'] / total_comments) * 100, 2) if total_comments > 0 else 0,
#             'negative': round((sentiment_counts['negative'] / total_comments) * 100, 2) if total_comments > 0 else 0,
#         },
#         'analyzed_comments': analyzed_comments
#     }
#     return results 
