from .clarity_check import clarity_check
from .code_generation_check import code_generation_check
from .grammer_check import compute_grammar_scores
from .similarity_check import calculate_similarity
from .toxicity_check import get_toxicity_scores
from .translation_check import translation_check
import json

def custom_eval(models, sentences, ref_sentence, prompt, type, groq_api_key = ''):
    results = {}
    if type == "General_Knowledge":
        for model, sentence in zip(models, sentences):
            # Calculate similarity score
            similarity_score = calculate_similarity(prompt, sentence)
            
            # Calculate grammar score
            grammar_score = compute_grammar_scores(sentence)

            toxicity_scores_dict = get_toxicity_scores(sentence)
            
            # Calculate clarity score
            clarity_score = clarity_check(sentence)
            
            # Store the results in a dictionary
            results[model] = {
                "similarity_score": similarity_score,
                "grammar_score": grammar_score,
                "toxicity_scores": toxicity_scores_dict,
                "clarity_score": clarity_score
            }
    elif type == "Code_Generation":
        if groq_api_key != '':
            code_gen_check_result = code_generation_check(models, sentences, prompt, groq_api_key)
            return code_gen_check_result
        else:
            return json.dumps({'code_generation':0})
    elif type == 'Translation':
        for model, sentence in zip(models, sentences):
            # Calculate similarity score
            similarity_score = calculate_similarity(ref_sentence, sentence)
            
            # Calculate grammar score
            grammar_score = compute_grammar_scores(sentence)
            
            # Calculate clarity score
            clarity_score = clarity_check(sentence)
            
            # Calculate translation scores
            translation_scores = translation_check(ref_sentence, sentence)
            
            # Store the results in a dictionary
            results[model] = {
                "similarity_score": similarity_score,
                "grammar_score": grammar_score,
                "clarity_score": clarity_score,
                "translation_scores": translation_scores
            }
    elif type == 'Text_Generation':
        for model_name, sentence in zip(models, sentences):
            # Calculate similarity score
            similarity_score = calculate_similarity(prompt, sentence)
            
            # Calculate grammar score
            grammar_score = compute_grammar_scores(sentence)
            
            # Calculate toxicity scores
            toxicity_scores_dict = get_toxicity_scores(sentence)
            
            # Calculate clarity score
            clarity_score = clarity_check(sentence)
            
            # Store the results in a dictionary
            results[model_name] = {
                "similarity_score": similarity_score,
                "grammar_score": grammar_score,
                "toxicity_scores": toxicity_scores_dict,
                "clarity_score": clarity_score
            }

    return json.dumps(results)