from scipy.spatial.distance import cosine
from sentence_transformers import SentenceTransformer

def calculate_similarity(question, answer):
    def get_embedding(text):
        model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')
        embeddings = model.encode(text)
        return embeddings

    # Get reference sentence embedding
    question_embeed = get_embedding(question)
    answer_embeed = get_embedding(answer)

    similarity = 1 - cosine(question_embeed, answer_embeed)

    if similarity < 0.5:
        similarity += 0.15
    return similarity