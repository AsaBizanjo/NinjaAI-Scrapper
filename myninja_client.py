import openai


client = openai.OpenAI(
    base_url="http://localhost:5000/v1",
    api_key="dummy-key"  
)


stream = client.chat.completions.create(
    model="myninja-ai",  
    messages=[
        {"role": "user", "content": "Tell me a joke about programming"}
    ],
    stream=True
)


full_response = ""
for chunk in stream:
    if chunk.choices[0].delta.content is not None:
        content = chunk.choices[0].delta.content
        full_response += content
        print(content, end="", flush=True)  
