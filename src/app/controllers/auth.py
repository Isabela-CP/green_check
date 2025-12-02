from functools import wraps
from flask import session, redirect, request
from src.app.utils.security import SecurityManager
from src.config.app import aplicacao

# Instância global do gerenciador de segurança
security = SecurityManager(aplicacao.config['SECRET_KEY'])

def login_required(func):
    """
    Decorator para proteger rotas que requerem autenticação
    Valida tanto a sessão quanto o token no cookie
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        # Verifica se há usuário na sessão
        if "usuario_logado" not in session:
            return redirect("/")
        
        # Verifica token no cookie
        token = request.cookies.get('auth_token')
        if not token:
            # Token não encontrado, limpa sessão e redireciona
            session.clear()
            return redirect("/")
        
        # Valida o token
        token_data = security.verify_token(token)
        if not token_data:
            # Token inválido ou expirado, limpa sessão e redireciona
            session.clear()
            return redirect("/")
        
        # Verifica se o email do token corresponde ao da sessão
        if token_data.get('email') != session.get("usuario_logado"):
            # Token não corresponde à sessão, possível ataque
            session.clear()
            return redirect("/")
        
        # Tudo válido, permite acesso
        return func(*args, **kwargs)
    return wrapper
