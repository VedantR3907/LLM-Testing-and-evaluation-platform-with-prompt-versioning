from groq import Groq
from dotenv import load_dotenv

load_dotenv()

def code_generation_check(models, responses, prompt, api_key):
    client = Groq(
    api_key=api_key,
)

    chat_completion = client.chat.completions.create(
        messages=[
            {
                "role": "system",
                                "content": '''You are tasked with evaluating code responses to a user's prompt. The responses are generated by two models named model_1_name and model_2_name. Please rate each response on a scale of 1-10 based on the following criteria:

                1. Correctness: Does the generated code perform the intended function without errors?
                2. Logical: Does the code follow logical programming principles?
                3. Relevance: Is the code relevant to the task of calculating a factorial?
                4. Functionality: Does the code perform the desired function correctly?
                5. Efficiency: Is the code optimized for performance?
                6. Readability: Is the code easy to read and understand?

                If no code is present in the response, all points should be returned as zero points.

                Your response should be a JSON object similar to the following example:

                {\"model_1_name\": {\"Correctness\": 7, \"Logical\": 8, \"Relevance\": 9, \"Functionality\": 10, \"Efficiency\": 6, \"Readability\": 8}, \"model_2_name\": {\"Correctness\": 7, \"Logical\": 8, \"Relevance\": 9, \"Functionality\": 10, \"Efficiency\": 6, \"Readability\": 8}}

                Please note that your response should only contain the JSON object and no additional explanation. Also, if the code responses include explanations along with the code, do not deduct points for this.''',
            },
            {
                "role": "user",
                "content": create_user_prompt(models, responses, prompt),
            }
        ],
        model="llama3-70b-8192",
    )
    return chat_completion.choices[0].message.content

def create_user_prompt(models, responses, prompt):
    return '\n'.join([f"{model}: {response}" for model, response in zip(models, responses)])