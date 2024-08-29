from transformers import AutoTokenizer, GemmaTokenizerFast

class MISTRAL_EVAL:
    def __init__(self) -> None:
        self.tokenizer = AutoTokenizer.from_pretrained("mistralai/Mistral-7B-v0.1")
        pass

    def mistral_token_count(self, messages):
        """Return the number of tokens used by a list of messages."""
        if messages == []:
            return 0
        # Load the tokenizer for the specific LLaMA model
        # Define your sentence
        inputs = self.tokenizer(messages, return_tensors="pt")

        # Get the token count
        token_count = len(inputs['input_ids'][0])
        return token_count