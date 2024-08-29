from transformers import AutoTokenizer, GemmaTokenizerFast

class LLAMA_EVAL:
    def __init__(self) -> None:
        self.tokenizer = AutoTokenizer.from_pretrained("meta-llama/Llama-2-7b-hf")
        pass

    def llama_token_count(self, messages):
        """Return the number of tokens used by a list of messages."""
        if messages == []:
            return 0
        # Load the tokenizer for the specific LLaMA model
        # Define your sentence
        inputs = self.tokenizer(messages, return_tensors="pt")

        # Get the token count
        token_count = len(inputs['input_ids'][0])
        return token_count