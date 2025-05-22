from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from fastapi.responses import JSONResponse
from typing import List

from app.database import get_db
from app.schemas.proyectos import ProyectoCreate, ProyectoUpdate, ProyectoOut
from app.services.proyectos_service import (
    procesar_csv_proyectos,
    crear_proyecto,
    obtener_proyectos,
    obtener_proyecto_por_id,
    eliminar_proyecto,
    actualizar_proyecto,
)

router = APIRouter(prefix="/api/proyectos", tags=["Proyectos"])

# Subir proyectos desde un archivo CSV
@router.post("/upload_csv")
async def upload_csv(file: UploadFile = File(...), db: Session = Depends(get_db)):
    """
    Subir proyectos desde un archivo CSV.
    """
    if not file.filename.endswith(".csv"):
        raise HTTPException(status_code=400, detail="Solo se permiten archivos CSV")

    return await procesar_csv_proyectos(file, db)

# Crear un nuevo proyecto
@router.post("/", response_model=ProyectoOut)
def create_proyecto(proyecto: ProyectoCreate, db: Session = Depends(get_db)):
    return crear_proyecto(proyecto, db)

# Obtener todos los proyectos
@router.get("/", response_model=List[ProyectoOut])
def get_proyectos(db: Session = Depends(get_db)):
    return obtener_proyectos(db)

# Obtener un proyecto por ID
@router.get("/{proyecto_id}", response_model=ProyectoOut)
def get_proyecto(proyecto_id: int, db: Session = Depends(get_db)):
    return obtener_proyecto_por_id(proyecto_id, db)

# Eliminar un proyecto
@router.delete("/{proyecto_id}")
def delete_proyecto(proyecto_id: int, db: Session = Depends(get_db)):
    return eliminar_proyecto(proyecto_id, db)

# Actualizar un proyecto
@router.put("/{proyecto_id}", response_model=ProyectoOut)
def update_proyecto(proyecto_id: int, updated_data: ProyectoUpdate, db: Session = Depends(get_db)):
    return actualizar_proyecto(proyecto_id, updated_data, db)
