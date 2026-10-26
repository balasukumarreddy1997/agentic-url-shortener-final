<<<<<<< HEAD
import logging
=======
>>>>>>> origin/main
import secrets
import string
from datetime import UTC, datetime

<<<<<<< HEAD
from app.store import DuplicateCode, SQLiteStore

ALPHABET = string.ascii_letters + string.digits
logger = logging.getLogger(__name__)
MAX_GENERATION_ATTEMPTS = 5


class CodeConflict(Exception):
    """The requested custom code is already taken."""


class CodeSpaceExhausted(Exception):
    """A unique random code could not be allocated within the attempt budget."""
=======
from app.store import SQLiteStore

ALPHABET = string.ascii_letters + string.digits
>>>>>>> origin/main


def utc_now() -> str:
    return datetime.now(UTC).isoformat()


class URLService:
    def __init__(self, store: SQLiteStore):
        self.store = store

    def _new_code(self, length: int = 7) -> str:
        return "".join(secrets.choice(ALPHABET) for _ in range(length))

    def shorten(self, original_url: str, custom_code: str | None = None):
<<<<<<< HEAD
        # The database primary key is the source of truth for uniqueness. Checking first and
        # inserting second is a race between concurrent requests, so we insert and handle the
        # constraint violation instead.
        created_at = utc_now()
        if custom_code:
            try:
                self.store.insert_url(custom_code, original_url, created_at)
            except DuplicateCode as exc:
                raise CodeConflict("Custom code already exists") from exc
            code = custom_code
        else:
            for _ in range(MAX_GENERATION_ATTEMPTS):
                code = self._new_code()
                try:
                    self.store.insert_url(code, original_url, created_at)
                    break
                except DuplicateCode:
                    continue
            else:
                raise CodeSpaceExhausted("Could not allocate a unique short code")
=======
        created_at = utc_now()
        if custom_code:
            if self.store.get_url(custom_code):
                raise ValueError("Custom code already exists")
            code = custom_code
        else:
            code = self._new_code()
            # Collision handling is bounded rather than an unbounded retry loop.
            for _ in range(5):
                if not self.store.get_url(code):
                    break
                code = self._new_code()
            else:
                raise RuntimeError("Could not allocate a unique short code")
        self.store.insert_url(code, original_url, created_at)
>>>>>>> origin/main
        return {"code": code, "original_url": original_url, "created_at": created_at}

    def resolve(self, code: str, user_agent: str | None = None, referrer: str | None = None):
        record = self.store.get_url(code)
        if not record:
            raise KeyError(code)
<<<<<<< HEAD
        # The redirect is the product; the click count is bookkeeping. If analytics cannot be
        # written (e.g. the database is locked), still redirect and accept an undercount
        # rather than failing the user's navigation.
        try:
            self.store.record_click(code, utc_now(), user_agent, referrer)
        except Exception:
            logger.warning("click_record_failed", extra={"code": code}, exc_info=True)
=======
        self.store.record_click(code, utc_now(), user_agent, referrer)
>>>>>>> origin/main
        return record["original_url"]

    def analytics(self, code: str):
        record = self.store.get_url(code)
        if not record:
            raise KeyError(code)
        return {
            "code": record["code"],
            "original_url": record["original_url"],
            "clicks": record["clicks"],
            "created_at": record["created_at"],
            "last_clicked_at": record["last_clicked_at"],
        }
