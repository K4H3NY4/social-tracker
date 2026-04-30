import json
import os
import re
from collections import Counter

from dotenv import load_dotenv
from google import genai


load_dotenv()

api_key = os.environ.get("API_KEY")
client = genai.Client(api_key=api_key) if api_key else None


VIDEO_TYPES = {
    "reel", "reels", "video", "videos", "vid", "vids",
    "animation", "animations", "animated", "anim", "anims"
}


def count_facebook_content(posts: list) -> dict:
    post_count = 0
    video_count = 0

    for post in posts:
        raw_type = (post.get("post_type") or "").strip().lower()
        if raw_type in VIDEO_TYPES:
            video_count += 1
        else:
            post_count += 1

    return {
        "posts": post_count,
        "videos": video_count,
        "total": post_count + video_count
    }


def count_instagram_content_types(posts: list) -> dict:
    carousel_count = 0
    image_count = 0
    video_count = 0

    for post in posts:
        content_type = (post.get("content_type") or "").strip().lower()

        if content_type in {"carousel", "carousels", "album"}:
            carousel_count += 1
        elif content_type in {"image", "images", "photo", "photos", "picture"}:
            image_count += 1
        elif content_type in VIDEO_TYPES:
            video_count += 1
        else:
            image_count += 1

    return {
        "carousel": carousel_count,
        "image": image_count,
        "video": video_count,
        "total": carousel_count + image_count + video_count
    }


def count_tiktok_content(posts: list) -> dict:
    video_count = 0
    image_count = 0

    for post in posts:
        raw_type = (post.get("post_type") or "").strip().lower()
        if raw_type in {"image", "images", "photo", "photos", "picture"}:
            image_count += 1
        else:
            video_count += 1

    return {
        "videos": video_count,
        "images": image_count,
        "total": video_count + image_count
    }


def count_collaborative_posts(posts: list, username: str = None) -> dict:
    collaborative_count = 0
    solo_count = 0

    for post in posts:
        coauthors = post.get("coauthor_producers") or ""
        user_posted = post.get("user_posted") or ""
        is_collab = bool(coauthors.strip()) if not username else bool(coauthors and username in coauthors)

        if username and user_posted != username and coauthors and username in coauthors:
            is_collab = True

        if is_collab:
            collaborative_count += 1
        else:
            solo_count += 1

    total = collaborative_count + solo_count
    return {
        "collaborative": collaborative_count,
        "solo": solo_count,
        "total": total,
        "collaboration_rate": round((collaborative_count / total * 100), 2) if total else 0
    }


CAPTION_STOPWORDS = {
    "the", "and", "for", "you", "your", "with", "this", "that", "from", "are",
    "was", "were", "have", "has", "had", "but", "not", "our", "out", "all",
    "can", "will", "just", "now", "new", "get", "got", "its", "it", "is",
    "in", "on", "at", "to", "of", "a", "an", "be", "by", "or", "as", "we",
    "us", "they", "their", "them", "what", "when", "where", "who", "why",
    "how", "more", "up", "down", "over", "under", "into", "than", "then",
    "so", "if", "about", "here", "there", "today", "tomorrow", "yesterday",
    "make", "made", "like", "love", "use", "using", "via", "also", "still",
    "see", "let", "lets", "one", "two", "per", "amp"
}


def parse_ai_json(response_text: str) -> dict:
    response_text = response_text.strip()
    if response_text.startswith("```"):
        response_text = response_text.split("```")[1]
        if response_text.startswith("json"):
            response_text = response_text[4:]
    return json.loads(response_text.strip())


def shorten_caption(caption: str, max_length: int = 220) -> str:
    caption = re.sub(r"\s+", " ", caption or "").strip()
    if len(caption) <= max_length:
        return caption
    return caption[:max_length].rstrip() + "..."


def keyword_caption_analysis(caption_records: list) -> dict:
    all_text = " ".join(record.get("caption", "") for record in caption_records)
    hashtags = Counter(tag.lower() for tag in re.findall(r"#([A-Za-z0-9_]+)", all_text))
    mentions = Counter(mention.lower() for mention in re.findall(r"@([A-Za-z0-9_.]+)", all_text))

    cleaned_text = re.sub(r"https?://\S+", " ", all_text.lower())
    cleaned_text = re.sub(r"[@#][A-Za-z0-9_.]+", " ", cleaned_text)
    words = [
        word for word in re.findall(r"[a-zA-Z][a-zA-Z']{2,}", cleaned_text)
        if word not in CAPTION_STOPWORDS
    ]
    top_terms = Counter(words).most_common(10)

    themes = []
    for term, count in top_terms[:6]:
        samples = [
            shorten_caption(record.get("caption", ""))
            for record in caption_records
            if term in (record.get("caption") or "").lower()
        ][:3]
        themes.append({
            "theme": term.replace("_", " ").title(),
            "description": f"Frequently mentioned caption term appearing {count} times.",
            "post_count": len(samples),
            "representative_terms": [term],
            "sample_captions": samples
        })

    return {
        "summary": "Keyword analysis based on the available captions. Configure API_KEY and GEMINI_MODEL for deeper theme interpretation.",
        "themes": themes,
        "topics": [
            {
                "topic": term.replace("_", " ").title(),
                "what_was_said": f'The captions repeatedly referenced "{term}".',
                "post_count": sum(1 for record in caption_records if term in (record.get("caption") or "").lower())
            }
            for term, _count in top_terms[:8]
        ],
        "content_intents": [],
        "hashtags": [{"tag": tag, "count": count} for tag, count in hashtags.most_common(12)],
        "mentions": [{"handle": handle, "count": count} for handle, count in mentions.most_common(12)],
        "analysis_source": "fallback_keyword_analysis"
    }


def analyze_caption_themes(caption_records: list, platform: str, username: str, date_range: dict) -> dict:
    if not caption_records:
        return {
            "summary": "No captions were available to analyze.",
            "themes": [],
            "topics": [],
            "content_intents": [],
            "hashtags": [],
            "mentions": [],
            "analysis_source": "none"
        }

    if not client:
        return keyword_caption_analysis(caption_records)

    caption_lines = []
    for index, record in enumerate(caption_records[:80], start=1):
        caption = shorten_caption(record.get("caption", ""), max_length=500)
        caption_lines.append(
            f"{index}. date={record.get('date')}; type={record.get('type')}; caption={caption}"
        )

    prompt = f"""
    You are a social media content strategist.
    Analyze the captions for {platform.upper()} account "{username}".
    Date range: {date_range.get('start') or 'not specified'} to {date_range.get('end') or 'not specified'}.

    CAPTIONS:
    {chr(10).join(caption_lines)}

    Identify the main themes and explain what the captions were talking about.
    Infer only from the caption text. Do not invent products, campaigns, or events that are not present.

    Return ONLY valid JSON with this exact shape:
    {{
        "summary": "2-4 sentence plain-English summary of what they talked about",
        "themes": [
            {{
                "theme": "theme name",
                "description": "what this theme means in the captions",
                "post_count": 0,
                "representative_terms": ["term 1", "term 2"],
                "sample_captions": ["short caption excerpt 1", "short caption excerpt 2"]
            }}
        ],
        "topics": [
            {{
                "topic": "specific topic",
                "what_was_said": "what the posts said about this topic",
                "post_count": 0
            }}
        ],
        "content_intents": ["promotion", "education", "engagement", "announcement"],
        "hashtags": [
            {{"tag": "example", "count": 0}}
        ],
        "mentions": [
            {{"handle": "example", "count": 0}}
        ]
    }}
    """

    try:
        response = client.models.generate_content(
            model=os.environ.get("GEMINI_MODEL"),
            contents=prompt
        )
        analysis = parse_ai_json(response.text)
        analysis["analysis_source"] = "gemini"
        return analysis
    except Exception as exc:
        fallback = keyword_caption_analysis(caption_records)
        fallback["ai_error"] = str(exc)
        return fallback


def analyze_contract_compliance(
    contract: str,
    posts: list,
    username: str,
    date_range: dict,
    platform: str,
    content_stats: dict,
    collaboration_stats: dict = None
) -> dict:
    start_date = date_range.get("start", "N/A")
    end_date = date_range.get("end", "N/A")

    if not client or not contract:
        return {
            "compliance_status": "unknown",
            "compliance_score": 0,
            "analysis": "AI not configured or no contract found",
            "deliverables_met": [],
            "deliverables_missing": [],
            "recommendations": []
        }

    collaboration_stats = collaboration_stats or {}
    posts_summary = [
        f"Platform: {platform.upper()}",
        f"Client: {username}",
        f"Date Range: {start_date} to {end_date}",
        f"Total Posts: {len(posts)}",
        f"Content Stats: {json.dumps(content_stats)}",
        f"Collaboration Stats: {json.dumps(collaboration_stats)}",
        "",
        "Sample Content:"
    ]

    for index, post in enumerate(posts[:3], start=1):
        content = post.get("description") or post.get("content") or ""
        content_type = post.get("content_type") or post.get("post_type") or "Unknown"
        posts_summary.append(f"{index}. [{content_type}] {shorten_caption(content, 180)}")

    prompt = f"""
    You are a contract compliance analyst. Focus ONLY on {platform.upper()}.

    CONTRACT REQUIREMENTS:
    {contract}

    DELIVERED CONTENT:
    {chr(10).join(posts_summary)}

    Note: Video includes Reels, Videos, and Animations where applicable.

    Return ONLY valid JSON:
    {{
        "compliance_status": "fully_compliant" or "partially_compliant" or "non_compliant",
        "compliance_score": 0 to 100,
        "analysis": "detailed analysis referencing date range {start_date} to {end_date}",
        "deliverables_met": ["deliverable 1", "deliverable 2"],
        "deliverables_missing": ["missing 1", "missing 2"],
        "post_frequency": {{
            "required": "contract requirement",
            "delivered": "{len(posts)} posts from {start_date} to {end_date}",
            "status": "met" or "not_met"
        }},
        "content_quality": {{
            "assessment": "assessment",
            "score": 0 to 100
        }},
        "content_breakdown": {{
            "stats": {json.dumps(content_stats)},
            "status": "complete" or "incomplete"
        }},
        "collaborations": {{
            "stats": {json.dumps(collaboration_stats)},
            "status": "strong" or "moderate" or "weak"
        }},
        "recommendations": ["recommendation 1", "recommendation 2"]
    }}
    """

    try:
        response = client.models.generate_content(
            model=os.environ.get("GEMINI_MODEL"),
            contents=prompt
        )
        return parse_ai_json(response.text)
    except Exception as exc:
        return {
            "compliance_status": "error",
            "compliance_score": 0,
            "analysis": f"Error: {str(exc)}",
            "deliverables_met": [],
            "deliverables_missing": [],
            "recommendations": []
        }
