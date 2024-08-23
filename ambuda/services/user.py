from datetime import datetime, timedelta

from ambuda.repository import DataSession, PasswordResetToken, User
from werkzeug.security import generate_password_hash, check_password_hash
from unstd.data import List, Optional

from ambuda.enums import SiteRole

class AmbudaAnonymousUser:
    """
    An anonymous user with limited permissions.
    """

    def has_role(self, _role: SiteRole):
        return False

    @property
    def is_p1(self) -> bool:
        return False

    @property
    def is_p2(self) -> bool:
        return False

    @property
    def is_proofreader(self) -> bool:
        return False

    @property
    def is_moderator(self) -> bool:
        return False

    @property
    def is_admin(self) -> bool:
        return False

    @property
    def is_ok(self) -> bool:
        return True

    @property
    def is_active(self) -> bool:
        return False

    @property
    def is_authenticated(self):
        return False

    def is_anonymous(self) -> bool:
        return True

    def get_id(self):
        raise NotImplementedError()

class AmbudaUser(User):
    def __init__(self, user: User):
        super().__init__(**user.__dict__)

    def has_role(self, role: SiteRole) -> bool:
        return role.value in {r.name for r in self.roles}

    def has_any_role(self, roles: list[SiteRole]) -> bool:
        user_roles = {r.name for r in self.roles}
        return any(r.value in user_roles for r in roles)

    @property
    def is_p1(self) -> bool:
        return self.has_role(SiteRole.P1)

    @property
    def is_p2(self) -> bool:
        return self.has_role(SiteRole.P2)

    @property
    def is_proofreader(self) -> bool:
        return self.has_any_role([SiteRole.P1, SiteRole.P2])

    @property
    def is_moderator(self) -> bool:
        return self.has_any_role([SiteRole.MODERATOR, SiteRole.ADMIN])

    @property
    def is_admin(self) -> bool:
        return self.has_role(SiteRole.ADMIN)

    @property
    def is_ok(self) -> bool:
        return not (self.is_deleted or self.is_banned)

    @property
    def is_active(self) -> bool:
        return self.is_ok and self.is_verified

    @property
    def is_authenticated(self):
        return self.is_active

    def is_anonymous(self) -> bool:
        return False

    def get_id(self):
        return str(self.id)

class UserService:
    @staticmethod
    def __get_valid(user: Optional[AmbudaUser]) -> Optional[AmbudaUser]:
        return user if user and not user.is_banned and not user.is_deleted else None

    @staticmethod
    def get(ds: DataSession, user_id: int, validate = True) -> Optional[AmbudaUser]:
        user = User.select(ds, user_id)
        user = user if user is None else AmbudaUser(user)
        return UserService.__get_valid(user) if validate else user

    @staticmethod
    def get_by_name(ds: DataSession, user_name: str, validate = True) -> Optional[AmbudaUser]:
        user = User.select_by_name(ds, user_name)
        user = user if user is None else AmbudaUser(user)
        return UserService.__get_valid(user) if validate else user

    @staticmethod
    def get_by_email(ds: DataSession, email: str, validate = True) -> Optional[AmbudaUser]:
        user = User.select_by_email(ds, email)
        user = user if user is None else AmbudaUser(user)
        return UserService.__get_valid(user) if validate else user

    @staticmethod
    def password_is_valid(ds: DataSession, user: User, raw_password: str):
        return check_password_hash(user.password_hash, raw_password)

    @staticmethod
    def set_password(ds: DataSession, user: User, raw_password: str):
        user.password_hash = generate_password_hash(raw_password)
        User.update(ds, user)

    @staticmethod
    def update_password(ds: DataSession, user: User, old_raw_password: str, new_raw_password: str) -> bool:
        is_valid = check_password_hash(user.password_hash, old_raw_password)
        if not is_valid:
            return False
        UserService.set_password(ds, user, new_raw_password)
        return True

    @staticmethod
    def create_user(ds: DataSession, username: str, email: str, raw_password: str, description: str) -> User:
        User.insert(ds, username, email, generate_password_hash(raw_password), description)


        # Allow all users to be proofreaders
        proofreader_role = (
            session.query(db.Role).filter_by(name=db.SiteRole.P1.value).first()
        )
        user_role = db.UserRoles(user_id=user.id, role_id=proofreader_role.id)
        session.add(user_role)

        return user

    #
    # def set_is_deleted(self, is_deleted: bool):
    #     """Update is_deleted."""
    #     self.is_deleted = is_deleted
    #
    # def set_is_banned(self, is_banned: bool):
    #     """Update is_banned."""
    #     self.is_banned = is_banned
    #
    # def set_is_verified(self, is_verified: bool):
    #     """Update is_verified."""
    #     self.is_verified = is_verified

    # @staticmethod
    # def exists(ds: DataSession, name: str, email: str) -> bool:
    #     return ds.exec("SELECT 1 FROM users WHERE username = ? OR email = ?", (name, email)).is_not_empty()
    #
    #
    #
    # @staticmethod
    # def add_user(ds: DataSession, name: str, password: str, email: str) -> None:
    #     if UserService.exists(ds, name, email):
    #         raise ValueError(f"User with name '{name}' or email '{email}' already exists")
    #
    #     hash = generate_password_hash(password)
    #     with DataSession() as ds:
    #         ds.exec(
    #             "INSERT INTO users (username, email, password_hash, is_verified, is_deleted, is_banned, created_at, description) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
    #             (name, email, hash, False, False, False, datetime.now(), "")
    #             )
    #
    # # role
    # def get_role(user_name: str) -> Optional[int]:
    #     with DataSession() as ds:
    #         return ds.exec("SELECT id FROM roles WHERE name = ?", (user_name,)).map(lambda xs: xs[0]).optional_head()
    #
    # def add_role(user_name: str, user_role: str) -> None:
    #     user_id = user.get(user_name)
    #     if not user_id:
    #         raise ValueError(f"User '{user_name}' does not exist")
    #
    #     role_id = get(user_role)
    #     if not role_id:
    #         raise ValueError(f"Role '{user_role}' does not exist")
    #
    #     with DataSession() as ds:
    #         ds.exec("INSERT INTO user_roles (user_id, role_id) VALUES (?, ?)", (user_id, role_id))
    #
    # # ambuda.queries
    # def user(username: str) -> db.User | None:
    #     session = get_session()
    #     return (
    #         session.query(db.User)
    #         .filter_by(username=username, is_deleted=False, is_banned=False)
    #         .first()
    #     )
    #

    #

    # ------------------------------------
    #
    @staticmethod
    def create_reset_token(ds: DataSession, user_id: int) -> str:
        import secrets
        raw_token = secrets.token_urlsafe()
        PasswordResetToken.insert(ds, user_id, raw_token)
        return raw_token


    @staticmethod
    def validate_reset_token(ds: DataSession, user_id: int, raw_token: str):
        time = datetime.utcnow()
        # token lifetime
        MAX_TOKEN_LIFESPAN_IN_HOURS = 24
        token = PasswordResetToken.select(ds, user_id)

        # No token for user
        if not token:
            return False

        # Deactivated
        if not token.is_active:
            return False

        # Token too old
        max_age = timedelta(hours=MAX_TOKEN_LIFESPAN_IN_HOURS)
        if token.created_at + max_age <= time:
            return False

        # Token mismatch
        if not check_password_hash(token.token_hash, raw_token):
            return False

        token.is_active = False
        token.used_at = time
        PasswordResetToken.update(ds, token)
        return True
