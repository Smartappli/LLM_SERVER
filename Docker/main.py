from openai import OpenAI
import json

with open('Docker/cuda/config-cuda.json', 'r') as file:
    config = json.load(file)

client = OpenAI(base_url="http://localhost:8008/v1", api_key="")
for model_config in config['models']:
    print(model_config['model_alias'])
    response = client.chat.completions.create(
        model=model_config['model_alias'],
        messages=[
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": "Who are the American presidents?"},
                ],
            }
        ],
    )
    print(response)
