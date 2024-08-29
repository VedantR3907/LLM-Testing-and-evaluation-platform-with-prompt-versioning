import requests
import os
from datetime import datetime, timezone
from dotenv import load_dotenv

load_dotenv()

def query_huggingface_api(sent1, sent2):
    """Query Hugging Face API to get text similarity score."""
    API_URL = "https://api-inference.huggingface.co/models/sentence-transformers/all-MiniLM-L6-v2"
    headers = {"Authorization": f"Bearer {os.environ.get('HUGGINGFACE_API_KEY')}"}
    payload = {
        "inputs": {
            "source_sentence": sent1,
            "sentences": [sent2]
        }
    }
    response = requests.post(API_URL, headers=headers, json=payload)
    return response.json()[-1]  # Adjust based on the actual response structure

def determine_version_increment(last_updated, similarity_score, similarity_threshold_high=0.8, similarity_threshold_low=0.7, days_threshold=3):
    """Determines the version increment based on the conditions specified."""

    current_time = datetime.now(timezone.utc)
    days_elapsed = (current_time - last_updated).days
    major_vote = 0
    minor_vote = 0

    # Voting based on similarity score
    if similarity_score < similarity_threshold_low:
        major_vote += 1
    elif similarity_score < similarity_threshold_high:
        minor_vote += 1
    
    # Voting based on time elapsed
    if days_elapsed > days_threshold:
        major_vote += 1
    else:
        minor_vote += 1

    # Final decision based on votes
    if major_vote > 0:
        return "+1"
    elif minor_vote > 1:
        return "+.1"

    return "+.1"  # Default minor update


