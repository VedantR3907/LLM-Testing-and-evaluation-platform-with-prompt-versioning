class GOOGLE_EVAL:
    def __init__(self) -> None:
        pass

    def gemini_token_count(self,model, messages):
        """Return the number of tokens used by a list of messages."""
        if messages == []:
            return 0
        tokens = model.count_tokens(messages)
        return tokens.total_tokens
        
    
    def cal_pricing_token(self, model_name, prompt_token, response_token):
        return 0