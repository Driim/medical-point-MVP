from fastapi import HTTPException, status


class NotImplementedException(HTTPException):
    def __init__(self) -> None:
        super().__init__(status.HTTP_418_IM_A_TEAPOT, "Operation not implemented")
