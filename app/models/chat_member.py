from datetime import datetime, timezone

from app import db


class ChatMember(db.Model):
    __tablename__ = "chat_members"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    chat_id = db.Column(
        db.Integer,
        db.ForeignKey("chats.id"),
        nullable=False
    )

    user_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id"),
        nullable=False
    )

    joined_at = db.Column(
        db.DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )

    chat = db.relationship(
        "Chat",
        back_populates="members"
    )

    user = db.relationship(
        "User",
        back_populates="chat_memberships"
    )

    __table_args__ = (
        db.UniqueConstraint(
            "chat_id",
            "user_id",
            name="unique_chat_member"
        ),
    )

    def __repr__(self):
        return f"<ChatMember chat={self.chat_id} user={self.user_id}>"
