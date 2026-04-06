from fastapi import FastAPI, status
from src.api.routes import health
from src.api.routes import ask
from src.api.routes import metadata
app = FastAPI()

app.include_router(health.router)
app.include_router(ask.router)
app.include_router(metadata.router)

@app.get("/", status_code=status.HTTP_200_OK)
def root():
    return {"message": "Wellcome to the API!"}
