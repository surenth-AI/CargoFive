import os
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")
print("Retrieved API Key:", api_key[:10] + "..." if api_key else "None")

genai.configure(api_key=api_key)

models = [
    "gemini-1.5-flash",
    "gemini-2.5-flash",
    "gemini-2.5-flash-lite"
]

for model_name in models:
    print(f"\n--- Testing Model: {model_name} ---")
    try:
        model = genai.GenerativeModel(model_name)
        response = model.generate_content("Hello! What is your name?")
        print("Success! Response:")
        print(response.text)
    except Exception as e:
        print("Failed with error:", e)
