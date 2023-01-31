from fastapi import HTTPException, status


class UserNotFound(HTTPException):
    def __init__(self, user_id: str) -> None:
        super().__init__(
            status.HTTP_404_NOT_FOUND,
            f"User with ID: {user_id} not found",
        )


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


class OutletWriteAccessException(HTTPException):
    def __init__(self, user_id: str, outlet_id: str) -> None:
        super().__init__(
            status.HTTP_403_FORBIDDEN,
            f"User: {user_id} doesn't have write access to outlet: {outlet_id}",
        )


class OutletReadAccessException(HTTPException):
    def __init__(self, user_id: str, outlet_id: str) -> None:
        super().__init__(
            status.HTTP_403_FORBIDDEN,
            f"User: {user_id} doesn't have read access to outlet: {outlet_id}",
        )


class DeviceExamAccessException(HTTPException):
    def __init__(self, device_id: str, worker_id: str) -> None:
        super().__init__(
            status.HTTP_403_FORBIDDEN,
            f"Worker: {worker_id} doesn't have read access to device: {device_id}",
        )
