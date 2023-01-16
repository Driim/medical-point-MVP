from fastapi import HTTPException, status


class OutletNotFound(HTTPException):
    def __init__(self, outlet_id: str) -> None:
        super().__init__(
            status.HTTP_404_NOT_FOUND,
            f"Outlet with ID: {outlet_id} not found",
        )
