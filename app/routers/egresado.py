from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.schemas.egresado import EgresadoCreate, EgresadoUpdate, EgresadoOut
from app.services.egresado_service import (
    procesar_csv_egresados,
    crear_egresado,
    obtener_egresados,
    obtener_egresado_por_id,
    actualizar_egresado,
    eliminar_egresado,
)

router = APIRouter(prefix="/api/egresados", tags=["Egresados"])

# Subir egresados desde un archivo CSV
@router.post("/upload")
async def upload_csv(file: UploadFile = File(...), db: Session = Depends(get_db)):
    if not file.filename.endswith(".csv"):
        raise HTTPException(status_code=400, detail="Solo se permiten archivos CSV")
    return await procesar_csv_egresados(file, db)

# Crear un nuevo egresado
@router.post("/", response_model=EgresadoOut)
def create_egresado(egresado: EgresadoCreate, db: Session = Depends(get_db)):
    return crear_egresado(egresado, db)

# Obtener todos los egresados
@router.get("/", response_model=List[EgresadoOut])
def get_egresados(db: Session = Depends(get_db)):
    return obtener_egresados(db)

# Obtener un egresado por ID
@router.get("/{egresado_id}", response_model=EgresadoOut)
def get_egresado(egresado_id: int, db: Session = Depends(get_db)):
    return obtener_egresado_por_id(egresado_id, db)

# Actualizar un egresado
@router.put("/{egresado_id}", response_model=EgresadoOut)
def update_egresado(egresado_id: int, updated_data: EgresadoUpdate, db: Session = Depends(get_db)):
    return actualizar_egresado(egresado_id, updated_data, db)

# Eliminar un egresado
@router.delete("/{egresado_id}")
def delete_egresado(egresado_id: int, db: Session = Depends(get_db)):
    return eliminar_egresado(egresado_id, db)