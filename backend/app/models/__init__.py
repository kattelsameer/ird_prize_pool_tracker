"""SQLAlchemy models. Import this package to register all models on Base.metadata
(needed by Alembic autogenerate and by create_all in demo/dev bootstrapping).
"""
from app.models.base import Base  # noqa: F401
from app.models.coupon import Coupon  # noqa: F401
from app.models.network import Network  # noqa: F401
from app.models.notification import Notification  # noqa: F401
from app.models.prize_pool import PrizePoolWinner  # noqa: F401
from app.models.profile import ConsumerProfile  # noqa: F401
from app.models.settings import AppSettings  # noqa: F401
from app.models.sync_run import SyncRun  # noqa: F401

__all__ = [
    "Base",
    "Coupon",
    "Network",
    "Notification",
    "PrizePoolWinner",
    "ConsumerProfile",
    "AppSettings",
    "SyncRun",
]
