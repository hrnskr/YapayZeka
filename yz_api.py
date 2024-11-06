!pip install groq together openai
import os
import time
from openai import OpenAI
from groq import Groq
from together import Together


# Set the API key for the OPENROUTER API
os.environ["GROQ_API_KEY"] = "gsk_ZonjYIIUHmOxbGrCOaFyWGdyb3FYLtn8SKzMuPxKh9xk6fq4uQ**"  # Replace with your actual OpenAI key
# Set the API key for the NVIDIA API
nvidia_api_key = "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**"
# Set the API key for OpenRouter API
os.environ["OPENAI_API_KEY"] = "sk-or-v1-f514471e03abae4c1eed7412a88ff0b20f375baf30dae914e9e571b8160ac9**"
#os.environ["OPENAI_API_KEY"] = "sk-or-v1-d28f31a29084d0a4a0f0dd6471ed3088cee2ec994bc9daf141fe85fff5c9e0**"  # Replace with your actual OpenAI key
os.environ["TOGETHER_API_KEY"] = "f7f1989e199852e8ad53b2798ad669b9f8ff1ad4e57f9b3162d9a8e57aab49**"



'''
GROQ API
'''
# Initialize the Groq client
groq_client = Groq(
    api_key=os.environ.get("GROQ_API_KEY"),
)

# Measure time for Groq API
start_time_groq = time.time()

# Create a chat completion for Groq
groq_completion = groq_client.chat.completions.create(
    messages=[
        {
            "role": "user",
            "content": "Write e-mail regex with python",
        }
    ],
    model="llama3-8b-8192",
)

# Print the result for Groq API
print(groq_completion.choices[0].message.content)

end_time_groq = time.time()
execution_time_groq = end_time_groq - start_time_groq


'''
NVIDIA API
'''

# Initialize the OpenAI client for NVIDIA API
nvidia_client = OpenAI(
    base_url="https://integrate.api.nvidia.com/v1",
    api_key=nvidia_api_key,
)

# Measure time for NVIDIA API
start_time_nvidia = time.time()

completion_nvidia = nvidia_client.chat.completions.create(
    model="meta/llama-3.1-70b-instruct",
    messages=[{"role": "user", "content": "Write python regex for e-mail."}],
    temperature=0.2,
    top_p=0.7,
    max_tokens=1024,
    stream=True
)

# Print NVIDIA API response
for chunk in completion_nvidia:
    if chunk.choices[0].delta.content is not None:
        print(chunk.choices[0].delta.content, end="")

end_time_nvidia = time.time()
execution_time_nvidia = end_time_nvidia - start_time_nvidia


'''
OPENROUTER API
'''

# Initialize OpenAI client for OpenRouter API
openrouter_client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=os.environ["OPENAI_API_KEY"],
)

# Measure time for OpenRouter API
start_time_openrouter = time.time()

try:
    # Create a chat completion for OpenRouter
    completion_openrouter = openrouter_client.chat.completions.create(
        extra_headers={
            "HTTP-Referer": "YOUR_SITE_URL",  # Optional
            "X-Title": "YOUR_APP_NAME",        # Optional
        },
        model="meta-llama/llama-3.1-405b-instruct:free",
        messages=[{"role": "user", "content": "Write e-mail regex with python"}]
    )
    
    # Print the result for OpenRouter API
    print(completion_openrouter.choices[0].message.content)

except Exception as e:
    print(f"An error occurred: {e}")

end_time_openrouter = time.time()
execution_time_openrouter = end_time_openrouter - start_time_openrouter



# Initialize Together client
together_client = Together(api_key=os.environ.get("TOGETHER_API_KEY"))

# Measure time for Together API
start_time_together = time.time()
try:
    together_response = together_client.chat.completions.create(
        model="meta-llama/Meta-Llama-3.1-405B-Instruct-Turbo",
        messages=[{"role": "user", "content": "write regex email python"}],
        max_tokens=None,
        temperature=0.7,
        top_p=0.7,
        top_k=50,
        repetition_penalty=1,
        stop=["<|eot_id|>", "<|eom_id|>"],
        safety_model="meta-llama/Meta-Llama-Guard-3-8B"
    )
    print("Together Response:", together_response.choices[0].message.content)

except Exception as e:
    print(f"Together Error: {e}")

end_time_together = time.time()
execution_time_together = end_time_together - start_time_together

# Print execution times
print(f"\nGROQ API Execution Time: {execution_time_groq:.2f} seconds")
print(f"\nTogether API Execution Time: {execution_time_together:.2f} seconds")
print(f"\nOpenRouter API Execution Time: {execution_time_openrouter:.2f} seconds")
print(f"\nNVIDIA API Execution Time: {execution_time_nvidia:.2f} seconds")
