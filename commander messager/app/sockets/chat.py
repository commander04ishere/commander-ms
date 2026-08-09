from flask import session

from flask_socketio import emit, join_room

from app import db, socketio

from app.models.user import User
from app.models.chat import Chat
from app.models.chat_member import ChatMember
from app.models.message import Message


def get_current_user():

    user_id = session.get("user_id")

    if not user_id:
        return None

    return db.session.get(User, user_id)


def is_chat_member(user_id, chat_id):

    return (
        ChatMember.query
        .filter_by(
            chat_id=chat_id,
            user_id=user_id
        )
        .first()
        is not None
    )


@socketio.on("join_chat")
def handle_join_chat(data):

    user = get_current_user()

    if not user:

        emit(
            "socket_error",
            {
                "message": "You are not logged in."
            }
        )

        return

    try:

        chat_id = int(data.get("chat_id"))

    except (TypeError, ValueError):

        emit(
            "socket_error",
            {
                "message": "Invalid chat."
            }
        )

        return

    chat = db.session.get(Chat, chat_id)

    if not chat:

        emit(
            "socket_error",
            {
                "message": "Chat not found."
            }
        )

        return

    if not is_chat_member(user.id, chat.id):

        emit(
            "socket_error",
            {
                "message": "You are not a member of this chat."
            }
        )

        return

    room = f"chat_{chat.id}"

    join_room(room)

    emit(
        "joined_chat",
        {
            "chat_id": chat.id
        }
    )


@socketio.on("send_message")
def handle_send_message(data):

    user = get_current_user()

    if not user:

        emit(
            "socket_error",
            {
                "message": "You are not logged in."
            }
        )

        return

    try:

        chat_id = int(data.get("chat_id"))

    except (TypeError, ValueError):

        emit(
            "socket_error",
            {
                "message": "Invalid chat."
            }
        )

        return

    content = str(
        data.get("content", "")
    ).strip()

    if not content:

        return

    if len(content) > 5000:

        emit(
            "socket_error",
            {
                "message": "Message is too long."
            }
        )

        return

    if not is_chat_member(user.id, chat_id):

        emit(
            "socket_error",
            {
                "message": "You cannot send messages here."
            }
        )

        return

    message = Message(
        chat_id=chat_id,
        sender_id=user.id,
        content=content
    )

    db.session.add(message)

    db.session.commit()

    room = f"chat_{chat_id}"

    emit(
        "new_message",
        {
            "id": message.id,
            "sender_id": user.id,
            "username": user.username,
            "display_name": user.display_name,
            "content": message.content,
            "created_at": message.created_at.strftime("%H:%M")
        },
        room=room
    )


@socketio.on("delete_messages")
def handle_delete_messages(data):

    user = get_current_user()

    if not user:

        emit(
            "socket_error",
            {
                "message": "You are not logged in."
            }
        )

        return

    try:

        chat_id = int(data.get("chat_id"))

    except (TypeError, ValueError):

        emit(
            "socket_error",
            {
                "message": "Invalid chat."
            }
        )

        return

    if not is_chat_member(user.id, chat_id):

        emit(
            "socket_error",
            {
                "message": "You are not a member of this chat."
            }
        )

        return

    message_ids = data.get("message_ids", [])

    if not isinstance(message_ids, list):

        emit(
            "socket_error",
            {
                "message": "Invalid message list."
            }
        )

        return

    if not message_ids:

        return

    if len(message_ids) > 100:

        emit(
            "socket_error",
            {
                "message": "You can delete up to 100 messages at once."
            }
        )

        return

    clean_ids = []

    for message_id in message_ids:

        try:

            clean_ids.append(
                int(message_id)
            )

        except (TypeError, ValueError):

            continue

    if not clean_ids:

        return

    messages = (
        Message.query
        .filter(
            Message.id.in_(clean_ids),
            Message.chat_id == chat_id,
            Message.sender_id == user.id
        )
        .all()
    )

    deleted_ids = [
        message.id
        for message in messages
    ]

    if not deleted_ids:

        emit(
            "socket_error",
            {
                "message": "No messages can be deleted."
            }
        )

        return

    for message in messages:

        db.session.delete(message)

    db.session.commit()

    room = f"chat_{chat_id}"

    emit(
        "messages_deleted",
        {
            "message_ids": deleted_ids
        },
        room=room
    )
