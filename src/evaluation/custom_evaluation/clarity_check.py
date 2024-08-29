from textstat import flesch_reading_ease

def clarity_check(sentence):
    fre = flesch_reading_ease(sentence)
    scaled_fre = max(1, min(10, fre / 10))
    return scaled_fre