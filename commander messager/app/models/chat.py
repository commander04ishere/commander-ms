from datetime import datetime, timezone

from app import db


class Chat(db.Model):
    __tablename__ = "chats"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    chat_type = db.Column(
        db.String(20),
        nullable=False,
        default="private"
    )

    title = db.Column(
        db.String(100),
        nullable=True
    )

    created_at = db.Column(
        db.DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )

    members = db.relationship(
        "ChatMember",
        back_populates="chat",
        cascade="all, delete-orphan"
    )

    messages = db.relationship(
        "Message",
        back_populates="chat",
        cascade="all, delete-orphan",
        order_by="Message.created_at"
    )

    def __repr__(self):
        return f"<Chat {self.id}>"
