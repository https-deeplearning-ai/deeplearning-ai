# import packages
from dotenv import load_dotenv
import openai


# load environment variables from .env file
load_dotenv()

# Initialize OpenAI client
client = openai.OpenAI()

response = client.responses.create(
    model="gpt-4o",
    input=[
        {"role": "user", "content": "Explain generative AI in one sentence."}  # Prompt
    ],
    temperature=0.7,  # A bit of creativity
    max_output_tokens=100  # Limit response length
)

# print the response from OpenAI
print(response.output[0].content[0].text)
