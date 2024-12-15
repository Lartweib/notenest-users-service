
class UserAgentInvalidException(Exception):
    def __init__(self, message="User agent inválido"):
        self.message = message
        super().__init__(self.message)

class TokenGenerationException(Exception):
    def __init__(self, message="Hubo un problema al generar el token"):
        self.message = message
        super().__init__(self.message)

class RefreshTokenDataInvalidException(Exception):
    def __init__(self, message="Datos inválidos en el token"):
        self.message = message
        super().__init__(self.message)

class RefreshTokenExpiredException(Exception):
    def __init__(self, message="El refresh token ha expirado"):
        self.message = message
        super().__init__(self.message)
