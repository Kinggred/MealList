from fastapi.exceptions import HTTPException
from fastapi import status


class NotFoundException(HTTPException):
    def __init__(self, message: str = None):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND, detail="Requested resource not found"
        )


class DatabaseException(HTTPException):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Bad request",
        )


class BadRequestException(HTTPException):
    def __init__(self):
        super().__init__(status_code=status.HTTP_400_BAD_REQUEST, detail="Bad request")


class UnauthorizedException(HTTPException):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
        )


class ForbiddenException(HTTPException):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Tried updating resource without access",
        )
