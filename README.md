### pydockrun - single file containerized python scripts

Inspired by PEP 723 ;)
Run your python scripts within a docker container, with the
Dockerfile defined right in your script!
Example script for a FastAPI server:
```python
# server.py: 
__dockerfile__ = """
from python:3.11-slim

RUN pip install fastapi uvicorn

EXPOSE 8000

CMD ["uvicorn", "server:app", "--host", "0.0.0.0", "--port", "8000"]
"""
from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def index():
  return {"hello": "from docker!"}
```

Then, run the container with:

```
$ pydockrun server.py
```
