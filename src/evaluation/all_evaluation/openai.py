import tiktoken

class OPENAI_EVAL:
    def __init__(self) -> None:
        pass

    def openai_token_count(self,model, messages):
        """Return the number of tokens used by a list of messages."""
        try:
            encoding = tiktoken.encoding_for_model(model)
        except KeyError:
            print("Warning: model not found. Using cl100k_base encoding.")
            encoding = tiktoken.get_encoding("cl100k_base")
        if type(messages) == list:
            if model in {
                "gpt-3.5-turbo-0613",
                "gpt-3.5-turbo-16k-0613",
                "gpt-4-0314",
                "gpt-4-32k-0314",
                "gpt-4-0613",
                "gpt-4-32k-0613",
                }:
                tokens_per_message = 3
                tokens_per_name = 1
            elif model == "gpt-3.5-turbo-0301":
                tokens_per_message = 4  # every message follows <|start|>{role/name}\n{content}<|end|>\n
                tokens_per_name = -1  # if there's a name, the role is omitted
            elif "gpt-3.5-turbo" in model:
                print("Warning: gpt-3.5-turbo may update over time. Returning num tokens assuming gpt-3.5-turbo-0613.")
                return self.openai_token_count(model="gpt-3.5-turbo-0613", messages=messages)
            elif "gpt-4" in model:
                print("Warning: gpt-4 may update over time. Returning num tokens assuming gpt-4-0613.")
                return self.openai_token_count(model="gpt-4-0613", messages=messages)
            else:
                raise NotImplementedError(
                    f"""num_tokens_from_messages() is not implemented for model {model}. See https://github.com/openai/openai-python/blob/main/chatml.md for information on how messages are converted to tokens."""
                )
            num_tokens = 0
            for message in messages:
                num_tokens += tokens_per_message
                for key, value in message.items():
                    num_tokens += len(encoding.encode(value))
                    if key == "name":
                        num_tokens += tokens_per_name
            num_tokens += 3  # every reply is primed with <|start|>assistant<|message|>
            return num_tokens
        else:
            return len(encoding.encode(messages))
    
    def cal_pricing_token(self, model_name, prompt_token, response_token):
    # Pricing per 1000 tokens for each model in USD
        pricing_info = {
            'gpt-4': {'input': 0.03, 'output': 0.06},
            'gpt-4-turbo-2024-04-09': {'input':0.01, 'output':0.03},
            'gpt-4-turbo': {'input':0.01, 'output':0.03},
            'gpt-4-32k': {'input': 0.06, 'output': 0.12},
            'gpt-3.5-turbo': {'input': 0.0030, 'output': 0.0060},
            'gpt-4-0125-preview': {'input': 0.0100, 'output': 0.0300},
            'gpt-4-1106-preview': {'input': 0.0100, 'output': 0.0300},
            'gpt-4-vision-preview': {'input': 0.0100, 'output': 0.0300},
            'gpt-3.5-turbo-1106': {'input': 0.0010, 'output': 0.0020},
            'gpt-3.5-turbo-0613': {'input': 0.0015, 'output': 0.0020},
            'gpt-3.5-turbo-16k-0613': {'input': 0.0030, 'output': 0.0040},
            'gpt-3.5-turbo-0301': {'input': 0.0015, 'output': 0.0020},
            'gpt-3.5-turbo-0125': {'input': 0.0005, 'output': 0.0015},
            'gpt-3.5-turbo-instruct': {'input': 0.0015, 'output': 0.0020}
        }

        # Calculate the cost based on tokens and pricing information
        if model_name in pricing_info:
            input_cost = prompt_token / 1000 * pricing_info[model_name]['input']
            output_cost = response_token / 1000 * pricing_info[model_name]['output']
            total_cost = input_cost + output_cost

            return round(total_cost, 6)
        else:
            return "Model name not recognized."