# Ambiente de Monitoria Online - Backend

Preview: https://amo-mvp.herokuapp.com/ | API Schema: https://amo-mvp.herokuapp.com/api/schema/openapi/
## Como executar
### Dependências
As dependências do projeto são gerenciadas utilizando o [Poetry](https://python-poetry.org). Arquivos requirements.txt e requirements-dev.txt são gerados automaticamente para maior compatibilidade.
#### Via Poetry
```bash
# Instala o projeto e dependências para execução e desenvolvimento
$ poetry install
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
