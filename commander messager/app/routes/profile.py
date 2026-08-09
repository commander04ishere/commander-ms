import os
import re

from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    url_for,
    session,
    flash,
    current_app,
)
from werkzeug.utils import secure_filename

from app import db
from app.models.user import User


profile_bp = Blueprint(
    "profile",
    __name__,
    url_prefix="/profile"
)


ALLOWED_EXTENSIONS = {
    "png",
    "jpg",
    "jpeg",
    "webp"
}


def get_current_user():
    user_id = session.get("user_id")

    if not user_id:
        return None

    return User.query.get(user_id)


def allowed_file(filename):
    if "." not in filename:
        return False

    extension = filename.rsplit(".", 1)[1].lower()

    return extension in ALLOWED_EXTENSIONS


# ==========================================
# MY PROFILE
# ==========================================

@profile_bp.get("/")
def my_profile():

    user = get_current_user()

    if not user:
        return redirect(url_for("auth.login"))

    return render_template(
        "profile.html",
        user=user,
        is_own_profile=True
    )


# ==========================================
# OTHER USER PROFILE
# ==========================================

@profile_bp.get("/<int:user_id>")
def user_profile(user_id):

    user = get_current_user()

    if not user:
        return redirect(url_for("auth.login"))

    profile_user = User.query.get_or_404(user_id)

    is_own_profile = (
        profile_user.id == user.id
    )

    return render_template(
        "profile.html",
        user=user,
        profile_user=profile_user,
        is_own_profile=is_own_profile
    )


# ==========================================
# EDIT PROFILE
# ==========================================

@profile_bp.route("/edit", methods=["GET", "POST"])
def edit_profile():

    user = get_current_user()

    if not user:
        return redirect(url_for("auth.login"))

    if request.method == "POST":

        display_name = request.form.get(
            "display_name",
            ""
        ).strip()

        username = request.form.get(
            "username",
            ""
        ).strip().lower()

        bio = request.form.get(
            "bio",
            ""
        ).strip()

        # ----------------------------------
        # DISPLAY NAME
        # ----------------------------------

        if not display_name:

            flash(
                "Display name cannot be empty.",
                "error"
            )

            return redirect(
                url_for("profile.edit_profile")
            )

        if len(display_name) > 50:

            flash(
                "Display name is too long.",
                "error"
            )

            return redirect(
                url_for("profile.edit_profile")
            )

        # ----------------------------------
        # USERNAME
        # ----------------------------------

        if not username:

            flash(
                "Username cannot be empty.",
                "error"
            )

            return redirect(
                url_for("profile.edit_profile")
            )

        if len(username) < 3:

            flash(
                "Username must be at least 3 characters.",
                "error"
            )

            return redirect(
                url_for("profile.edit_profile")
            )

        if len(username) > 32:

            flash(
                "Username is too long.",
                "error"
            )

            return redirect(
                url_for("profile.edit_profile")
            )

        if not re.fullmatch(
            r"[a-z0-9_.]+",
            username
        ):

            flash(
                "Username can only contain letters, numbers, dots and underscores.",
                "error"
            )

            return redirect(
                url_for("profile.edit_profile")
            )

        # ----------------------------------
        # CHECK USERNAME
        # ----------------------------------

        existing_user = User.query.filter(
            User.username.ilike(username)
        ).first()

        if (
            existing_user
            and existing_user.id != user.id
        ):

            flash(
                "This username is already taken.",
                "error"
            )

            return redirect(
                url_for("profile.edit_profile")
            )

        # ----------------------------------
        # BIO
        # ----------------------------------

        if len(bio) > 160:

            flash(
                "Bio must be 160 characters or less.",
                "error"
            )

            return redirect(
                url_for("profile.edit_profile")
            )

        # ----------------------------------
        # UPDATE TEXT
        # ----------------------------------

        user.display_name = display_name
        user.username = username
        user.bio = bio

        # ----------------------------------
        # AVATAR
        # ----------------------------------

        avatar = request.files.get("avatar")

        if avatar and avatar.filename:

            if not allowed_file(
                avatar.filename
            ):

                flash(
                    "Invalid image format.",
                    "error"
                )

                return redirect(
                    url_for("profile.edit_profile")
                )

            filename = secure_filename(
                avatar.filename
            )

            extension = filename.rsplit(
                ".",
                1
            )[1].lower()

            filename = (
                f"user_{user.id}.{extension}"
            )

            upload_folder = os.path.join(
                current_app.static_folder,
                "uploads",
                "avatars"
            )

            os.makedirs(
                upload_folder,
                exist_ok=True
            )

            # Remove old avatar files
            for old_extension in ALLOWED_EXTENSIONS:

                old_file = os.path.join(
                    upload_folder,
                    f"user_{user.id}.{old_extension}"
                )

                if os.path.exists(old_file):

                    try:
                        os.remove(old_file)

                    except OSError:
                        pass

            avatar.save(
                os.path.join(
                    upload_folder,
                    filename
                )
            )

            user.avatar = (
                f"uploads/avatars/{filename}"
            )

        db.session.commit()

        flash(
            "Profile updated successfully.",
            "success"
        )

        return redirect(
            url_for(
                "profile.my_profile"
            )
        )

    return render_template(
        "edit_profile.html",
        user=user
    )