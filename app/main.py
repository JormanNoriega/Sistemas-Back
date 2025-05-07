from fastapi import FastAPI
from app.routers import empresa
from app.database import Base, engine

Base.metadata.create_all(bind=engine)

app = FastAPI(title="API de Empresas")

app.include_router(empresa.router)
