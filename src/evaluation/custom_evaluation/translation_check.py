from nltk.translate.bleu_score import sentence_bleu, SmoothingFunction
from nltk.translate.meteor_score import single_meteor_score
from nltk import word_tokenize
from rouge import Rouge 


def translation_check(reference_sentence, candidate_sentence):
    # Initialize Rouge
    rouge = Rouge()

    # Tokenization for BLEU and METEOR scores
    reference = word_tokenize(reference_sentence)
    candidate = word_tokenize(candidate_sentence)
    
    # Initialize smoothing function
    smoothie = SmoothingFunction().method4
    
    # BLEU score
    bleu = sentence_bleu([reference], candidate, smoothing_function=smoothie) * 10
    
    # METEOR score
    meteor = single_meteor_score(reference, candidate) * 10
    
    # ROUGE score
    rouge_scores = rouge.get_scores(' '.join(candidate), ' '.join(reference))

    return {'bleu':bleu, 'meteor':meteor, 'rougue':rouge_scores}
