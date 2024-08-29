from transformers import AutoModelForSequenceClassification, AutoTokenizer

def load_model(model_name):
    model = AutoModelForSequenceClassification.from_pretrained(model_name)
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    return model, tokenizer

def get_toxicity_scores(sentence):
    model_name, tokenizer = load_model("unitary/toxic-bert")
    inputs = tokenizer.encode_plus(sentence, return_tensors='pt', max_length=512)
    outputs = model_name(**inputs)
    scores = outputs[0].softmax(1).detach().numpy()[0]
    labels = ['toxic', 'obscene', 'insult']
    scores_dict = {label: float(score) for label, score in zip(labels, scores)}
    return scores_dict