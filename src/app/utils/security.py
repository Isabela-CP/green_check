"""
Módulo de segurança para autenticação
- Hash de senhas usando bcrypt
- Geração e validação de tokens seguros
"""
import bcrypt
import secrets
import hashlib
from datetime import datetime, timedelta
from itsdangerous import URLSafeTimedSerializer, BadSignature, SignatureExpired


class SecurityManager:
    """Gerenciador de segurança para autenticação"""
    
    def __init__(self, secret_key):
        """
        Inicializa o gerenciador de segurança
        
        Args:
            secret_key: Chave secreta para assinatura de tokens
        """
        self.secret_key = secret_key
        self.serializer = URLSafeTimedSerializer(secret_key)
        self.token_expiration_hours = 24  # Tokens expiram em 24 horas
    
    def hash_password(self, password: str) -> str:
        """
        Gera hash bcrypt da senha
        
        Args:
            password: Senha em texto plano
            
        Returns:
            String com o hash da senha
        """
        # Gera salt e hash
        salt = bcrypt.gensalt(rounds=12)
        hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
        return hashed.decode('utf-8')
    
    def verify_password(self, password: str, hashed_password: str) -> bool:
        """
        Verifica se a senha corresponde ao hash
        
        Args:
            password: Senha em texto plano
            hashed_password: Hash armazenado no banco
            
        Returns:
            True se a senha corresponde, False caso contrário
        """
        try:
            return bcrypt.checkpw(
                password.encode('utf-8'),
                hashed_password.encode('utf-8')
            )
        except Exception as e:
            print(f"Erro ao verificar senha: {e}")
            return False
    
    def generate_token(self, user_email: str) -> str:
        """
        Gera token seguro para o usuário
        
        Args:
            user_email: Email do usuário
            
        Returns:
            Token seguro assinado
        """
        # Cria payload com email e timestamp
        payload = {
            'email': user_email,
            'timestamp': datetime.utcnow().isoformat()
        }
        
        # Gera token assinado com expiração
        token = self.serializer.dumps(
            payload,
            salt='auth-token'
        )
        return token
    
    def verify_token(self, token: str) -> dict:
        """
        Verifica e decodifica token
        
        Args:
            token: Token a ser verificado
            
        Returns:
            Dicionário com dados do token se válido, None se inválido
        """
        try:
            # Tenta decodificar o token (com expiração)
            payload = self.serializer.loads(
                token,
                salt='auth-token',
                max_age=self.token_expiration_hours * 3600  # Converter horas para segundos
            )
            return payload
        except SignatureExpired:
            print("Token expirado")
            return None
        except BadSignature:
            print("Token inválido")
            return None
        except Exception as e:
            print(f"Erro ao verificar token: {e}")
            return None
    
    def generate_csrf_token(self) -> str:
        """
        Gera token CSRF para proteção contra ataques
        
        Returns:
            Token CSRF
        """
        return secrets.token_urlsafe(32)

