from fastapi import HTTPException, status

class AppException(HTTPException):
    def __init__(self, message: str, status_code: int = status.HTTP_400_BAD_REQUEST):
        super().__init__(status_code=status_code, detail=message)


class FileProcessingError(AppException):
    def __init__(self, message="Error processing uploaded file"):
        super().__init__(message, status.HTTP_422_UNPROCESSABLE_ENTITY)


class TextExtractionError(AppException):
    def __init__(self, message="Failed to extract text from resume"):
        super().__init__(message, status.HTTP_422_UNPROCESSABLE_ENTITY)


class ScoringError(AppException):
    def __init__(self, message="Error computing resume score"):
        super().__init__(message, status.HTTP_500_INTERNAL_SERVER_ERROR)