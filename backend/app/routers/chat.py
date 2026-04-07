from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import selectinload
from sqlmodel import Session, col, select

from app.database import get_session
from app.models import Article, ChatMessage
from app.schemas import ChatMessageRead, ChatRequest, ChatResponse
from app.services.chat import chat_about_article

router = APIRouter(prefix="/api", tags=["chat"])


@router.get("/articles/{article_id}/chat", response_model=list[ChatMessageRead])
def get_chat_history(article_id: int, session: Session = Depends(get_session)):
    messages = session.exec(
        select(ChatMessage)
        .where(ChatMessage.article_id == article_id)
        .order_by(col(ChatMessage.created_at).asc())
    ).all()
    return messages


@router.post("/articles/{article_id}/chat", response_model=ChatResponse)
def send_chat_message(
    article_id: int,
    body: ChatRequest,
    session: Session = Depends(get_session),
):
    article = session.exec(
        select(Article)
        .options(selectinload(Article.source))
        .where(Article.id == article_id)
    ).first()
    if not article:
        raise HTTPException(status_code=404, detail="Article not found")

    # Get history
    history = session.exec(
        select(ChatMessage)
        .where(ChatMessage.article_id == article_id)
        .order_by(col(ChatMessage.created_at).asc())
    ).all()

    # Save user message
    user_msg = ChatMessage(
        article_id=article_id, role="user", content=body.message
    )
    session.add(user_msg)
    session.commit()

    # Get LLM response
    assistant_content = chat_about_article(article, list(history), body.message)

    # Save assistant message
    assistant_msg = ChatMessage(
        article_id=article_id, role="assistant", content=assistant_content
    )
    session.add(assistant_msg)
    session.commit()

    return ChatResponse(role="assistant", content=assistant_content)
