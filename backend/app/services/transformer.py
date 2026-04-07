import json

import openai

from app.config import settings

client = openai.OpenAI(api_key=settings.OPENAI_API_KEY)


def transform_article_content(
    title: str, description: str, source_name: str
) -> dict:
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        response_format={"type": "json_object"},
        messages=[
            {
                "role": "system",
                "content": (
                    "You are a satirical news writer. Transform real news headlines "
                    "and descriptions into humorous, absurd versions. Keep them "
                    'recognizable but funny. Respond with JSON: {"title": "...", '
                    '"description": "..."}'
                ),
            },
            {
                "role": "user",
                "content": (
                    f"Transform this {source_name} article:\n"
                    f"Title: {title}\n"
                    f"Description: {description}"
                ),
            },
        ],
        timeout=30,
    )
    return json.loads(response.choices[0].message.content)
