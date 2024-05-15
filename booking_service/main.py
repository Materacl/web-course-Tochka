from fastapi import FastAPI, HTTPException, Depends, Request
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from routes import router
from database import SessionLocal, engine, Base
from fastapi.security import OAuth2PasswordBearer
from typing import Annotated

Base.metadata.create_all(bind=engine)
app = FastAPI()
app.include_router(router)
app.mount("/static", StaticFiles(directory="static"), name="static")

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=8000)
