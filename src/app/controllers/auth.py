from functools import wraps
from flask import session, redirect

def login_required(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        if "usuario_logado" not in session:
            return redirect("/")
        return func(*args, **kwargs)
    return wrapper
