from datetime import datetime, timezone

from app import db

from werkzeug.security import (
    generate_password_hash,
    check_password_hash
)


class User(db.Model):
    __tablename__ = "users"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    username = db.Column(
        db.String(32),
        unique=True,
        nullable=False,
        index=True
    )

    password_hash = db.Column(
        db.String(255),
        nullable=False
    )

    phone_number = db.Column(
        db.String(20),
        unique=True,
        nullable=False,
        index=True
    )

    display_name = db.Column(
        db.String(50),
        nullable=False
    )

    avatar = db.Column(
        db.String(255),
        nullable=True
    )

    bio = db.Column(
        db.String(160),
        nullable=True
    )

    created_at = db.Column(
        db.DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )

    last_seen = db.Column(
        db.DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )

    is_banned = db.Column(
        db.Boolean,
        default=False,
        nullable=False
    )

    is_verified = db.Column(
    db.Boolean,
    default=False,
    nullable=False
    )

    chat_memberships = db.relationship(
        "ChatMember",
        back_populates="user",
        cascade="all, delete-orphan"
    )

    messages = db.relationship(
        "Message",
        back_populates="sender"
    )

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(
            self.password_hash,
            password
        )

    def __repr__(self):
        return f"<User {self.username}>"
