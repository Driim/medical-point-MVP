from fastapi import HTTPException, status


class DeviceNotFound(HTTPException):
    def __init__(self, device_id: str) -> None:
        super().__init__(
            status.HTTP_404_NOT_FOUND,
            f"Device with ID: {device_id} not found",
        )
