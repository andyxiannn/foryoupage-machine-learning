from fastapi.responses import JSONResponse

class NotFoundError(Exception):
    def __init__(self, message: str):
        self.message = message
class SendRequestError(Exception):
    def __init__(self, message: str):
        self.message = message
class InvalidInputError(Exception):
    def __init__(self, message: str):
        self.message = message
class IncorrectCredentialsError(Exception):
    def __init__(self, message: str):
        self.message = message
class JwtError(Exception):
    def __init__(self, message: str):
        self.message = message
class ExistedError(Exception):
    def __init__(self, message: str):
        self.message = message
class VSYSError(Exception):
    def __init__(self, message: str):
        self.message = message
