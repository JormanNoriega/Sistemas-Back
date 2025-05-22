from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.schemas.estadisticas import EstadisticaCreate, EstadisticaUpdate, EstadisticaOut
from app.services.estadisticas_service import (
    procesar_csv_estadisticas,
    crear_estadistica,
    obtener_estadisticas,
    obtener_estadistica_por_id,
    actualizar_estadistica,
    eliminar_estadistica,
)

router = APIRouter(prefix="/api/estadisticas", tags=["Estadísticas"])

@router.post("/upload_csv")
async def upload_csv(file: UploadFile = File(...), db: Session = Depends(get_db)):
    """
    Subir estadísticas desde un archivo CSV.
    """
    if not file.filename.endswith(".csv"):
        raise HTTPException(status_code=400, detail="Solo se permiten archivos CSV")
    return await procesar_csv_estadisticas(file, db)

# Crear una nueva estadística
@router.post("/", response_model=EstadisticaOut)
def create_estadistica(estadistica: EstadisticaCreate, db: Session = Depends(get_db)):
    return crear_estadistica(estadistica, db)

# Obtener todas las estadísticas
@router.get("/", response_model=List[EstadisticaOut])
def get_estadisticas(db: Session = Depends(get_db)):
    return obtener_estadisticas(db)

# Obtener una estadística por ID
@router.get("/{estadistica_id}", response_model=EstadisticaOut)
def get_estadistica(estadistica_id: int, db: Session = Depends(get_db)):
    return obtener_estadistica_por_id(estadistica_id, db)

# Actualizar una estadística
@router.put("/{estadistica_id}", response_model=EstadisticaOut)
def update_estadistica(estadistica_id: int, updated_data: EstadisticaUpdate, db: Session = Depends(get_db)):
    return actualizar_estadistica(estadistica_id, updated_data, db)

# Eliminar una estadística
@router.delete("/{estadistica_id}")
def delete_estadistica(estadistica_id: int, db: Session = Depends(get_db)):
    return eliminar_estadistica(estadistica_id, db)