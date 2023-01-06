from fastapi import HTTPException, status


class WriteAccessException(HTTPException):
    def __init__(self, user_id: str, organization_id: str) -> None:
        super().__init__(
            status.HTTP_403_FORBIDDEN,
            f"User: {user_id} doesn't have write access to {organization_id}",
        )


class ReadAccessException(HTTPException):
    def __init__(self, user_id: str, organization_id: str) -> None:
        super().__init__(
            status.HTTP_403_FORBIDDEN,
            f"User: {user_id} doesn't have read access to {organization_id}",
        )


class OrganizationUnitNotFound(HTTPException):
    def __init__(self, organization_id: str) -> None:
        super().__init__(
            status.HTTP_404_NOT_FOUND,
            f"Organization with ID: {organization_id} not found",
        )
