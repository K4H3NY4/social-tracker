from google import genai
import os
from dotenv import load_dotenv
from google.genai import types

# Load .env file
load_dotenv()

# Get the API key from environment variables
api_key = os.environ.get("API_KEY")  # Make sure your .env has: API_KEY=your_key_here

# Initialize the GenAI client
client = genai.Client(api_key=api_key)


""""# 
# Generate content
response = client.models.generate_content(
    model="gemini-3-flash-preview",
    contents="Explain how AI works in a few words"
)


"""
grounding_tool = types.Tool(
    google_search=types.GoogleSearch()
)

config = types.GenerateContentConfig(
    tools=[grounding_tool]
)

response = client.models.generate_content(
    model="gemini-3-flash-preview",
    contents="What is brookside's kenya sentiment on social media, and what are the top 3 posts driving that sentiment, share the links and the dates of those posts",
    config=config,
)



print(response.text) 