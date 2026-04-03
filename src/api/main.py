from fastapi import FastAPI, status
from src.api.routes import health

app = FastAPI()

app.include_router(health.router)

@app.get("/", status_code=status.HTTP_200_OK)
def root():
    return {"message": "Wellcome to the API!"}
