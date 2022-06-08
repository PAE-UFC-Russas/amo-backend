# Ambiente de Monitoria Online - Backend

## Como executar
### Dependências
As dependências do projeto são gerenciadas utilizando o [Poetry](https://python-poetry.org). Arquivos requirements.txt e requirements-dev.txt são gerados automaticamente para maior compatibilidade.
#### Via Poetry
```bash
# Instala o projeto e dependências para execução
$ poetry install --no-dev

# Instala o projeto e dependências para execução e desenvolvimento
$ poetry install
```
#### Via pip
```bash
# Instala dependências para execução
$ pip install -r requirements.txt
 
# Instala dependências para desenvolvimento
$ pip install -r requirements-dev.txt
```

### Execução
```bash
# Executa as migrações no banco de dados
$ python manage.py migrate

# Executa o servidor
$ python manage.py runserver
```

## Documentação
Com a aplicação em execução é possível acessar a especificação gerada pelo drf-spectacular (OpenAPI) em: http://localhost:8000/api/schema/openapi
