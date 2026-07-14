# Re-export all models so Alembic can discover them when Base.metadata is inspected
from app.models.hcp import HCP
from app.models.interaction import Interaction
from app.models.product import Product
from app.models.follow_up import FollowUp

__all__ = ["HCP", "Interaction", "Product", "FollowUp"]
