from datetime import datetime, timezone

from app import db


class Message(db.Model):
    __tablename__ = "messages"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    chat_id = db.Column(
        db.Integer,
        db.ForeignKey("chats.id"),
        nullable=False,
        index=True
    )

    sender_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id"),
        nullable=False,
        index=True
    )

    content = db.Column(
        db.Text,
        nullable=False
    )

    created_at = db.Column(
        db.DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
        index=True
    )

    edited_at = db.Column(
        db.DateTime(timezone=True),
        nullable=True
    )

    is_deleted = db.Column(
        db.Boolean,
        default=False,
        nullable=False
    )

    chat = db.relationship(
        "Chat",
        back_populates="messages"
    )

    sender = db.relationship(
        "User",
        back_populates="messages"
    )

    def __repr__(self):
        return f"<Message {self.id}>"
