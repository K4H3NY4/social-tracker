from google import genai
from google.genai import types
import os
from dotenv import load_dotenv
from datetime import datetime

# Load environment variables
load_dotenv()

# Get API key
api_key = os.environ.get("API_KEY")
if not api_key:
    raise ValueError("❌ API_KEY not found. Ensure your .env file contains: API_KEY=your_key_here")

# Initialize client
client = genai.Client(api_key=api_key)

# Configure grounding with Google Search (This enables real-time data lookup)
grounding_tool = types.Tool(google_search=types.GoogleSearch())
config = types.GenerateContentConfig(
    tools=[grounding_tool],
    temperature=0.2,  # Low temperature for factual accuracy
)

# Define the analysis prompt with strict "Search First" instructions
prompt = """
TASK: Conduct a real-time social media sentiment analysis for "Brookside Dairy Ltd Kenya".

⚠️ CRITICAL INSTRUCTIONS:
1. USE GOOGLE SEARCH FIRST: You must search for recent news, public tweets, and discussions about Brookside Kenya from the last 90 days.
2. NO HALLUCINATIONS: If you cannot find specific engagement numbers (likes/shares) or direct URLs via search, explicitly write "Not publicly indexed" instead of inventing numbers.
3. VERIFIABLE DATA: Only report posts that are publicly accessible via search results.

🔹 DELIVERABLES (Fill this with real data found via search):

1. SENTIMENT OVERVIEW
   - Overall sentiment split (estimate based on search results): % Positive | % Neutral | % Negative
   - Total mention volume (approximate based on search results)
   - Top 3 themes driving sentiment (e.g., product quality, pricing, CSR)

2. TOP 3 POSTS DRIVING SENTIMENT (Must be real, searchable posts)
   For each post:
   - Platform + direct URL (must be clickable)
   - Publication date (UTC+3)
   - Engagement metrics (Only if visible in search snippet, otherwise state "Not publicly indexed")
   - Sentiment classification + 1-sentence rationale
   - Short excerpt of post content

3. HIGH-LEVEL SUMMARY
   - 3–5 bullet insights backed by found data
   - 3 sample posts (positive, neutral, negative)
   - One strategic takeaway for marketing teams

🔹 CONSTRAINTS:
   - Focus on Kenya-centric conversations.
   - Prioritize posts with high visibility.
   - Cite sources with timestamps.
   - Max 1 page, scannable format with bold headers.

🔹 OUTPUT FORMAT:
   - Professional, agency-ready report.
   - Kenya-focused context.
"""

# Generate content with grounding
try:
    print("🔍 Searching for real-time data... (This may take 10-20 seconds)")
    response = client.models.generate_content(
        model="gemini-3-flash-preview",  # Stable model with grounding support
        contents=prompt,
        config=config,
    )
    
    # Generate timestamp for filename
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"brookside_report_{timestamp}.md"

    print("\n" + "=" * 80)
    print("📊 BROOKSIDE KENYA SENTIMENT ANALYSIS REPORT (GENERATED)")
    print("=" * 80)
    print(response.text)
    print("=" * 80)
    
    # Save to file
    with open(filename, "w", encoding="utf-8") as f:
        f.write(response.text)
    
    print(f"\n✅ Report saved to '{filename}'")

except Exception as e:
    print(f"❌ Error generating content: {str(e)}")
    # Print specific error details for debugging
    import traceback
    traceback.print_exc()