from transformers import AutoTokenizer, GemmaTokenizerFast

class GEMMA_EVAL:
    def __init__(self) -> None:
        self.tokenizer = GemmaTokenizerFast.from_pretrained("hf-internal-testing/dummy-gemma")
        pass

    def gemma_token_count(self, messages):
        """Return the number of tokens used by a list of messages."""
        if messages == []:
            return 0
        # Load the tokenizer for the specific LLaMA model
        # Define your sentence
        inputs = self.tokenizer.encode(messages)

        # Get the token count
        token_count = len(inputs)
        return token_count