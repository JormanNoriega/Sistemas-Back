from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import empresa, estadisticas, eventos, proyectos, convenio, egresado, relacion_internacional, impacto_social, salida_a_practicas, publicaciones
from app.database import Base, engine

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Sistema de Gestión",
    description="API para el sistema de gestión de egresados, empresas, convenios, relaciones internacionales e impacto social",
    version="1.0.0")

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # En producción, especifica los orígenes permitidos
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(convenio.router)
app.include_router(egresado.router)
app.include_router(empresa.router)
app.include_router(estadisticas.router)
app.include_router(eventos.router)
app.include_router(proyectos.router)
app.include_router(relacion_internacional.router)
app.include_router(impacto_social.router)
app.include_router(salida_a_practicas.router)
app.include_router(publicaciones.router)
