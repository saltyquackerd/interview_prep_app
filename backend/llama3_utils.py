# Llama 3 utilities
from huggingface_hub import InferenceClient

client = InferenceClient()

def get_llama3_question(chat_messages):
	completion = client.chat.completions.create(
		model="meta-llama/Meta-Llama-3-8B-Instruct",
		messages=chat_messages,
	)
	return completion.choices[0].message.content.strip()
