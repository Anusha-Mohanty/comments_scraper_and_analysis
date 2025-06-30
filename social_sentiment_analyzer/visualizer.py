import matplotlib.pyplot as plt
from wordcloud import WordCloud, STOPWORDS
from typing import List, Dict
import os

def create_sentiment_bar_chart(sentiment_counts: Dict, output_path: str):
    """
    Creates and saves a bar chart of sentiment distribution.

    Args:
        sentiment_counts (Dict): A dictionary with keys 'positive', 'neutral', 'negative' and their counts.
        output_path (str): The path to save the bar chart image.
    """
    labels = list(sentiment_counts.keys())
    values = list(sentiment_counts.values())
    
    colors = ['#45BD62', '#BCC0C4', '#F3425F'] # Green, Gray, Red
    
    fig, ax = plt.subplots(figsize=(8, 6))
    bars = ax.bar(labels, values, color=colors)
    
    ax.set_title('Sentiment Analysis Results', fontsize=16, weight='bold')
    ax.set_ylabel('Number of Comments', fontsize=12)
    ax.set_ylim(0, max(values) * 1.15 if values else 10) # Dynamic y-axis
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.tick_params(axis='x', which='both', bottom=False)
    
    # Add counts on top of bars
    for bar in bars:
        yval = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2.0, yval + (max(values) * 0.02), int(yval), ha='center', va='bottom', fontsize=11)

    plt.tight_layout()
    plt.savefig(output_path, dpi=300)
    plt.close()
    print(f"[INFO] Sentiment bar chart saved to {output_path}")

def create_word_cloud(comments: List[str], output_path: str):
    """
    Creates and saves a word cloud from a list of comments.

    Args:
        comments (List[str]): A list of comment strings.
        output_path (str): The path to save the word cloud image.
    """
    if not comments:
        print("[WARNING] No comments provided for word cloud generation.")
        return

    text = " ".join(comment for comment in comments)
    
    # Customize stopwords if needed
    stopwords = set(STOPWORDS)
    # stopwords.update(["and", "the", "is", "a", "to", "of"])
    
    wordcloud = WordCloud(
        width=800, 
        height=400, 
        background_color='white',
        stopwords=stopwords,
        min_font_size=10,
        colormap='viridis' # A visually appealing color map
    ).generate(text)
    
    plt.figure(figsize=(10, 5), facecolor=None)
    plt.imshow(wordcloud)
    plt.axis("off")
    plt.tight_layout(pad=0)
    
    plt.savefig(output_path, dpi=300)
    plt.close()
    print(f"[INFO] Word cloud saved to {output_path}") 