from fastapi import HTTPException, status


class WorkerNotFound(HTTPException):
    def __init__(self, worker_id: str) -> None:
        super().__init__(
            status.HTTP_404_NOT_FOUND,
            f"Worker with ID: {worker_id} not found",
        )
