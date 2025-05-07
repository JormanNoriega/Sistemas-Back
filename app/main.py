from fastapi import FastAPI
from app.api import empresa
from app.database import Base, engine

# Crear tablas si no existen
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Empresa API")

app.include_router(empresa.router, prefix="/api")
from fastapi import FastAPI
from app.api import empresa
from app.database import Base, engine

# Crear tablas si no existen
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Empresa API")

app.include_router(empresa.router, prefix="/api")
