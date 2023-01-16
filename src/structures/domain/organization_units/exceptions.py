from fastapi import HTTPException, status


class OrganizationUnitNotFound(HTTPException):
    def __init__(self, organization_id: str) -> None:
        super().__init__(
            status.HTTP_404_NOT_FOUND,
            f"Organization with ID: {organization_id} not found",
        )
