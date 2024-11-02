
class UserAgentInvalidException(Exception):
    def __init__(self, message="User agent inválido"):
        self.message = message
        super().__init__(self.message)

class TokenGenerationException(Exception):
    def __init__(self, message="Hubo un problema al generar el token"):
        self.message = message
        super().__init__(self.message)
