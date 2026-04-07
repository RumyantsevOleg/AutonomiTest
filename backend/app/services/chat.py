import openai

from app.config import settings
from app.models import Article, ChatMessage

client = openai.OpenAI(api_key=settings.OPENAI_API_KEY)


def chat_about_article(
    article: Article, history: list[ChatMessage], user_message: str
) -> str:
    messages = [
        {
            "role": "system",
            "content": (
                "You are a helpful assistant discussing a news article. "
                "Answer questions based on both the original and satirical versions.\n\n"
                f"Original title: {article.original_title}\n"
                f"Original description: {article.original_description}\n"
                f"Satirical title: {article.fake_title}\n"
                f"Satirical description: {article.fake_description}\n"
                f"Source: {article.source.name}\n"
                f"Published: {article.published_at}"
            ),
        },
    ]

    for msg in history:
        messages.append({"role": msg.role, "content": msg.content})

    messages.append({"role": "user", "content": user_message})

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=messages,
        timeout=30,
    )
    return response.choices[0].message.content
