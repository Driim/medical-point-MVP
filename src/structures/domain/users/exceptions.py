from fastapi import HTTPException, status


class UserNotFound(HTTPException):
    def __init__(self, user_id: str) -> None:
        super().__init__(
            status.HTTP_404_NOT_FOUND,
            f"User with ID: {user_id} not found",
        )
