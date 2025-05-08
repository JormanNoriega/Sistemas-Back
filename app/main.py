from fastapi import FastAPI
from app.routers import empresa, estadisticas, eventos, proyectos
from app.database import Base, engine

Base.metadata.create_all(bind=engine)

app = FastAPI(title="API de Empresas")

app.include_router(empresa.router)



app.include_router(estadisticas.router)
app.include_router(eventos.router)
app.include_router(proyectos.router)
