## cada um deve criar sua propria branch, para não dar conflitos
## depois só fazer o merge

## 1 passo --> criar uma venv - python -m venv .venv 
## 2 passo --> ativar a venv (ambiente virtual para guardar as libs do python) - source .venv/bin/activate (linux)
## 3 passo --> instalar as libs da aplicação - pip install -r requirements.txt 

## criar um arquivo .env, nesse arquivo deve conter os dados do banco de dados de vcs, na seguinte estrutura: 

DB_HOST = localhost
DB_USER = user_database
DB_PASSWORD = user_pass
DB_NAME = dbname
