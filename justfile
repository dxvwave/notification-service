export PYTHONPATH := "src"

run:
    uvicorn src.main:app --host 0.0.0.0 --port 8002 --reload

db-migrate:
    alembic upgrade head

db-revision name:
    alembic revision --autogenerate -m "{{name}}"
