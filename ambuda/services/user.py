from datetime import datetime, timedelta

from ambuda.repository import DataSession, PasswordResetToken, User, Role, SiteRole
from werkzeug.security import generate_password_hash, check_password_hash

from repository.user_role import UserRoles
from unstd.data import List, Optional

BOT_USER = "ambuda-bot"
BOT_EMAIL = "bot@ambuda.org"

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
        return self.has_any_role([role])

    def has_any_role(self, roles: list[SiteRole]) -> bool:
        with DataSession() as ds:
            xs = Role.all(ds)
            ys = UserRoles.select_by_user(ds, self.id).map(lambda x: xs.filter(lambda y: x.role_id == y.id).head().name)
            return ys.filter(lambda x: List(roles).filter(lambda y:  x == y.value).is_not_empty()).is_not_empty()

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
    def get_bot(ds: DataSession) -> Optional[AmbudaUser]:
        return UserService.get_by_name(ds, BOT_USER)

    @staticmethod
    def create_bot(ds: DataSession, password: str):
        user = UserService.get_by_name(ds, BOT_USER)
        if not user:
            UserService.create_user(ds, BOT_USER, BOT_EMAIL, password, "Bot")

    @staticmethod
    def password_is_valid(ds: DataSession, user: User, raw_password: str):
        return check_password_hash(user.password_hash, raw_password)

    @staticmethod
    def set_password(ds: DataSession, user: User, raw_password: str):
        user.password_hash = generate_password_hash(raw_password)
        User.update(ds, **user.__dict__)

    @staticmethod
    def update_password(ds: DataSession, user: User, old_raw_password: str, new_raw_password: str) -> bool:
        is_valid = check_password_hash(user.password_hash, old_raw_password)
        if not is_valid:
            return False
        UserService.set_password(ds, user, new_raw_password)
        return True

    @staticmethod
    def update_description(ds: DataSession, user: User):
        u = User.select(ds, user.id)
        if u:
            u.description = user.description = user.description
            User.update(ds, **u.__dict__)

    @staticmethod
    def create_user(ds: DataSession, username: str, email: str, raw_password: str, description: str) -> Optional[AmbudaUser]:
        user_id = User.insert(ds, username, email, generate_password_hash(raw_password), description)
        user = UserService.get(ds, user_id)
        user = UserService.__get_valid(user)

        # Allow all users to be proofreaders
        p1 = Role.all(ds).filter(lambda x: x.name == SiteRole.P1.value).head()

        UserRoles.insert(ds, user_id, p1.id)

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

        PasswordResetToken.update(ds, token.id, time)
        return True

    @staticmethod
    def roles(ds: DataSession) -> List[Role]:
        return Role.all(ds)

    @staticmethod
    def roles_by_user(ds: DataSession, user: AmbudaUser) -> List[int]:
        return UserRoles.select_by_user(ds, user.id).map(lambda x: x.role_id)

    @staticmethod
    def delete_roles_by_user(ds: DataSession, user: AmbudaUser):
        UserRoles.delete_by_user(ds, user.id)

    @staticmethod
    def add_role(ds: DataSession, user: AmbudaUser, r: Role):
        UserRoles.insert(ds, user.id, r.id)