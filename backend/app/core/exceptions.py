"""
core/exceptions.py — Project-level custom exception classes.

These are domain exceptions that services raise; routers or exception
handlers catch them and translate them into HTTP responses.
"""


class HCPNotFoundError(Exception):
    """Raised when an HCP cannot be found in the database."""
    def __init__(self, identifier: str | int = ""):
        self.identifier = identifier
        super().__init__(f"HCP not found: {identifier}")


class DuplicateEmailError(Exception):
    """Raised when a registration attempt uses an already-registered email."""
    def __init__(self, email: str = ""):
        self.email = email
        super().__init__(f"An account with email '{email}' already exists")


class InteractionNotFoundError(Exception):
    """Raised when an interaction record cannot be found."""
    def __init__(self, interaction_id: int = 0):
        self.interaction_id = interaction_id
        super().__init__(f"Interaction not found: {interaction_id}")


class FollowUpNotFoundError(Exception):
    """Raised when a follow-up record cannot be found."""
    def __init__(self, follow_up_id: int = 0):
        self.follow_up_id = follow_up_id
        super().__init__(f"Follow-up not found: {follow_up_id}")


class InvalidCredentialsError(Exception):
    """Raised when login credentials are invalid."""


class AccountInactiveError(Exception):
    """Raised when a user account is deactivated."""


class InvalidOTPError(Exception):
    """Raised when an OTP is invalid, expired, or already used."""
