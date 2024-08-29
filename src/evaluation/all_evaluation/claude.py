class CLAUDE_EVAL:
    def __init__(self) -> None:
        pass

    def cal_pricing_token(self, model_name, prompt_token, response_token):
        # Pricing per million tokens for each model in USD
        pricing_info = {
            'claude-3-haiku': {'input': 0.25, 'output': 1.25},
            'claude-3-sonnet': {'input': 3, 'output': 15},
            'claude-3-opus': {'input': 15, 'output': 75},
        }

        # Calculate the cost based on tokens and pricing information
        if model_name in pricing_info:
            input_cost = prompt_token / 1e6 * pricing_info[model_name]['input']
            output_cost = response_token / 1e6 * pricing_info[model_name]['output']
            total_cost = input_cost + output_cost

            return round(total_cost, 6)
        else:
            return "Model name not recognized."