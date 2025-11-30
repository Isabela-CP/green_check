# chamando a classe UsuariosDAO
from src.app.BD.usuarios_dao import Usuarios_dao
from src.config.database import connection_pool
from flask import redirect, request, session


class UsuariosControllers:
    def valida_acesso_usuario(self):
        def view():
            usuario_dao = Usuarios_dao(connection_pool)
            try:
                dados = usuario_dao.select_na_tabela_usuarios(
                    request.form.get("login"), request.form.get("senha")
                )

                if dados > 0:
                    print("USUÁRIO EXISTE!! Está VALIDADO!!")

                    session["usuario_logado"] = request.form.get("login")

                    return redirect("/clientes")

            except Exception as erro:
                print("USUÁRIO NÃO EXISTE NO BD!!")
                return redirect("/")

        return view
