import requests
import json

def check_grammar(text):
    url = "https://languagetool.org/api/v2/check"
    data = {'text': text, 'language':'en-US'}
    response = requests.post(url, data=data)
    js = json.loads(response.text)
    return len(js['matches'])

def compute_grammar_scores(sentence, max_errors=10):
    score = 0
    num_errors = check_grammar(sentence)
    # If number of errors exceed the cap, assign the minimum score.
    if num_errors >= max_errors:
        return 1
    else:
        # Decrease the score linearly with the number of mistakes
        score = 10 - ((num_errors / max_errors) * 9)
    return round(score, 2)