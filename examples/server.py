__dockerfile__ = """
from python:3.11-slim

RUN pip install fastapi
RUN pip install uvicorn

EXPOSE 8000

CMD ["uvicorn", "server:app", "--host", "0.0.0.0", "--port", "8000"]
"""
from fastapi import FastAPI

app = FastAPI()

value = 0

@app.get("/")
def index():
  return {"hello": "from docker!"}

@app.get("/hit")
def hit():
  global value
  value += 1
  return {"value": value}
