class TokenManager():
    def __init__(self):
        self.tokens = []
        self.iter = 0
        
    def verifyToken(self, token) -> str:
        self.iter+=1
        return f"player{self.iter}"
    
tokenManager = TokenManager()