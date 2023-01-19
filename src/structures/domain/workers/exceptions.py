from fastapi import HTTPException, status


class WorkerNotFound(HTTPException):
    def __init__(self, worker_id: str) -> None:
        super().__init__(
            status.HTTP_404_NOT_FOUND,
            f"Worker with ID: {worker_id} not found",
        )


class WorkerConstraintException(HTTPException):
    def __init__(self) -> None:
        super().__init__(
            status.HTTP_422_UNPROCESSABLE_ENTITY,
            "Worker with this drivers license is already working in company",
        )
