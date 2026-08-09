from datetime import datetime, timezone

from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    url_for,
    flash,
    session
)

from app import db

from app.models.user import User
from app.models.chat import Chat
from app.models.chat_member import ChatMember
from app.models.message import Message


messenger_bp = Blueprint(
    "messenger",
    __name__,
    url_prefix="/messenger"
)


def get_current_user():
    user_id = session.get("user_id")

    if not user_id:
        return None

    return db.session.get(User, user_id)


@messenger_bp.route("/")
def dashboard():

    user = get_current_user()

    if not user:
        return redirect(
            url_for("auth.login")
        )

    memberships = (
        ChatMember.query
        .filter_by(user_id=user.id)
        .all()
    )

    chats = [
        membership.chat
        for membership in memberships
    ]

    return render_template(
        "messenger/dashboard.html",
        user=user,
        chats=chats
    )


@messenger_bp.route("/search")
def search():

    user = get_current_user()

    if not user:
        return redirect(
            url_for("auth.login")
        )

    query = request.args.get(
        "q",
        ""
    ).strip()

    users = []

    if query:

        users = (
            User.query
            .filter(
                User.id != user.id,
                User.username.ilike(
                    f"%{query}%"
                )
            )
            .limit(20)
            .all()
        )

    return render_template(
        "messenger/search.html",
        user=user,
        users=users,
        query=query
    )


@messenger_bp.route(
    "/chat/start/<int:user_id>",
    methods=["POST"]
)
def start_chat(user_id):

    current_user = get_current_user()

    if not current_user:
        return redirect(
            url_for("auth.login")
        )

    if current_user.id == user_id:

        flash(
            "You cannot start a chat with yourself."
        )

        return redirect(
            url_for("messenger.dashboard")
        )

    other_user = db.session.get(
        User,
        user_id
    )

    if not other_user:

        flash("User not found.")

        return redirect(
            url_for("messenger.dashboard")
        )

    memberships = (
        ChatMember.query
        .filter_by(
            user_id=current_user.id
        )
        .all()
    )

    # Check whether a private chat
    # between these two users already exists.
    for membership in memberships:

        chat = membership.chat

        if chat.chat_type != "private":
            continue

        member_ids = {
            member.user_id
            for member in chat.members
        }

        if member_ids == {
            current_user.id,
            other_user.id
        }:

            return redirect(
                url_for(
                    "messenger.chat",
                    chat_id=chat.id
                )
            )

    # Create new chat
    chat = Chat(
        chat_type="private"
    )

    db.session.add(chat)

    db.session.flush()

    db.session.add(
        ChatMember(
            chat_id=chat.id,
            user_id=current_user.id
        )
    )

    db.session.add(
        ChatMember(
            chat_id=chat.id,
            user_id=other_user.id
        )
    )

    db.session.commit()

    return redirect(
        url_for(
            "messenger.chat",
            chat_id=chat.id
        )
    )


@messenger_bp.route(
    "/chat/<int:chat_id>",
    methods=["GET", "POST"]
)
def chat(chat_id):

    user = get_current_user()

    if not user:
        return redirect(
            url_for("auth.login")
        )

    chat = db.session.get(
        Chat,
        chat_id
    )

    if not chat:

        flash("Chat not found.")

        return redirect(
            url_for("messenger.dashboard")
        )

    # Security check:
    # The current user MUST be a member.
    membership = (
        ChatMember.query
        .filter_by(
            chat_id=chat.id,
            user_id=user.id
        )
        .first()
    )

    if not membership:

        flash(
            "You don't have access to this chat."
        )

        return redirect(
            url_for("messenger.dashboard")
        )

    # Send message
    if request.method == "POST":

        content = request.form.get(
            "content",
            ""
        ).strip()

        if not content:

            flash(
                "Message cannot be empty."
            )

            return redirect(
                url_for(
                    "messenger.chat",
                    chat_id=chat.id
                )
            )

        # Prevent extremely large messages.
        if len(content) > 5000:

            flash(
                "Message is too long."
            )

            return redirect(
                url_for(
                    "messenger.chat",
                    chat_id=chat.id
                )
            )

        message = Message(
            chat_id=chat.id,
            sender_id=user.id,
            content=content,
            created_at=datetime.now(
                timezone.utc
            )
        )

        db.session.add(message)

        # Update user's last seen time.
        user.last_seen = datetime.now(
            timezone.utc
        )

        db.session.commit()

        return redirect(
            url_for(
                "messenger.chat",
                chat_id=chat.id
            )
        )

    # Load messages
    messages = (
        Message.query
        .filter_by(chat_id=chat.id)
        .order_by(Message.created_at.asc())
        .all()
    )

    other_member = next(
        (
            member
            for member in chat.members
            if member.user_id != user.id
        ),
        None
    )

    other_user = (
        other_member.user
        if other_member
        else None
    )

    return render_template(
        "messenger/chat.html",
        user=user,
        chat=chat,
        other_user=other_user,
        messages=messages
    )
