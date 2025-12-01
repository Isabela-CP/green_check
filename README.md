# Green Check 

## Estrutura do Projeto

```
green_check_python/
├── server.py                 # Arquivo principal para iniciar o servidor
├── requirements.txt          # Dependências Python
├── Dockerfile                # Configuração da imagem Docker
├── docker-compose.yml        # Configuração dos serviços (DB + Web)
├── Makefile                  # Comandos simplificados para desenvolvimento
├── src/
│   ├── config/
│   │   ├── app.py           # Configuração do Flask
│   │   └── database.py      # Configuração do banco de dados
│   └── app/
│       ├── BD/
│       │   ├── clientes_dao.py    # DAO para árvores
│       │   └── usuarios_dao.py    # DAO para usuários
│       ├── controllers/
│       │   ├── clientes_controllers.py
│       │   └── usuarios_controllers.py
│       ├── rotas/
│       │   └── rotas.py
│       └── views/
│           ├── templates/   # Templates Jinja2
│           └── css/         # Arquivos CSS
└── db/
    └── init/
        └── 01_schema.sql    # Schema do banco de dados
```

## Instalação

### Requisitos

Antes de iniciar, certifique-se de ter as seguintes versões instaladas:

- **Docker**: versão 20.10 ou superior
- **Docker Compose**: versão 2.0 ou superior (ou Docker Compose Plugin v2)
- **Make**: versão 4.0 ou superior (geralmente já incluído em sistemas Linux/macOS)

Para verificar as versões instaladas:
```bash
docker --version
docker compose version
make --version
```

### Opção 1: Usando Make (Recomendado)

O projeto inclui um `Makefile` com comandos simplificados:

1. Iniciar a aplicação em modo desenvolvimento:
```bash
make dev
```

2. Acesse a aplicação em `http://localhost:3000`

3. Faça login usando uma das credenciais abaixo:

**Credenciais de Acesso:**

| Email | Senha | Papel |
|-------|-------|-------|
| `admin@sistema.com` | `123456789` | Munícipe |
| `maria.silva@email.com` | `senha12345` | Munícipe |
| `joao.oliveira@email.com` | `senha98765` | Munícipe |
| `carlos.lima@crea.com` | `senha11111` | Responsável Técnico |
| `fernanda.rodrigues@crea.com` | `senha22222` | Responsável Técnico |

**Comandos disponíveis:**
- `make dev` - Inicia os containers em modo desenvolvimento (com logs visíveis)
- `make down` - Para os containers
- `make soft-clean` - Remove dados do banco e para containers (útil após alterar schema)
- `make clean` - Limpa tudo: dados, volumes, imagens e containers

### Opção 2: Usando Docker Compose diretamente

1. Construa e inicie todos os serviços (banco de dados + aplicação web):
```bash
docker compose up -d --build
```

2. Verifique os logs:
```bash
docker compose logs -f web
```

3. Acesse a aplicação em `http://localhost:3000`

4. Faça login usando uma das credenciais da seção "Credenciais de Acesso" acima.

**Comandos úteis:**
- Parar os serviços: `docker compose down`
- Ver logs: `docker compose logs -f`
- Reconstruir: `docker compose up -d --build`

### Opção 3: Instalação Local

1. Instale as dependências:
```bash
pip install -r requirements.txt
```

2. Inicie o banco de dados PostgreSQL:
```bash
docker compose up -d db
```

3. Execute o servidor:
```bash
python server.py
```

O servidor estará disponível em `http://localhost:3000`

**Credenciais de Acesso:**
- Email: `admin@sistema.com` | Senha: `123456789`
- Email: `carlos.lima@crea.com` | Senha: `senha11111`
- Ver seção completa de credenciais acima.

## Testar Consultas SQL

O projeto inclui consultas SQL complexas em `db/scripts/consultas.sql` que podem ser testadas diretamente no banco de dados.

### Usando psql (linha de comando)

Para testar as consultas usando o `psql`, execute:

```bash
psql -h localhost -p 5555 -U arvore_user -d arvore_urbana
```

Quando solicitado, digite a senha: `arvore_pass`

Dentro do `psql`, você pode:

1. **Executar uma consulta específica:**
   ```sql
   -- Copie e cole a consulta desejada do arquivo db/scripts/consultas.sql
   ```

2. **Executar todas as consultas de um arquivo:**
   ```sql
   \i db/scripts/consultas.sql
   ```

3. **Executar uma consulta diretamente do arquivo (sem entrar no psql):**
   ```bash
   psql -h localhost -p 5555 -U arvore_user -d arvore_urbana -f db/scripts/consultas.sql
   ```

### Usando Cliente Gráfico PostgreSQL

Você também pode usar qualquer cliente gráfico PostgreSQL de sua preferência, como:
- **pgAdmin**
- **DBeaver**
- **DataGrip**
- **TablePlus**
- **Postico** (macOS)
- **pgAdmin Web** (via Docker)

**Configurações de conexão:**
- **Host:** `localhost`
- **Porta:** `5555`
- **Usuário:** `arvore_user`
- **Senha:** `arvore_pass`
- **Banco de dados:** `arvore_urbana`

Após conectar, você pode abrir e executar as consultas do arquivo `db/scripts/consultas.sql`.

## Reiniciar o Banco de Dados (Alterações no Schema)

Quando o schema do banco de dados (`db/init/01_schema.sql`) for alterado, é necessário reiniciar o banco de dados para que as mudanças sejam aplicadas. **ATENÇÃO:** Isso irá apagar todos os dados existentes no banco.

### Usando Make (Recomendado)

```bash
# Remove dados do banco e reinicia os containers
make soft-clean
make dev
```

### Usando Docker Compose diretamente

```bash
# 1. Parar os containers
docker compose down

# 2. Remover o diretório de dados (com sudo se necessário)
sudo rm -rf ./db/data

# 3. Reiniciar os containers
docker compose up -d --build
```

## Tecnologias Utilizadas

- **Flask**: Framework web Python
- **Jinja2**: Engine de templates (integrado ao Flask)
- **psycopg2**: Driver PostgreSQL para Python
- **PostgreSQL**: Banco de dados
- **Bootstrap**: Framework CSS (via CDN)
- **Docker**: Containerização da aplicação
- **Docker Compose**: Orquestração de serviços


## Rotas Disponíveis

- `GET /` - Página de login
- `GET /clientes` - Listagem de árvores
- `GET /inclusaoClientes` - Formulário de inclusão
- `POST /validaBDUsuarios` - Validação de login
- `POST /insertBDClientes` - Inserção de nova árvore
- `GET /listaDadosClientes/<id>` - Edição de árvore
- `POST /updateBDCliente` - Atualização de árvore
- `GET /removeCliente/<id>` - Remoção de árvore

