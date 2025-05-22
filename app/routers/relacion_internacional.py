from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from fastapi.responses import JSONResponse
from typing import List

from app.database import get_db
from app.models.relacion_internacional import TipoRelacion, EstadoRelacion
from app.schemas.relacion_internacional import RelacionInternacionalCreate, RelacionInternacionalUpdate, RelacionInternacionalOut
from app.services.relacion_internacional_service import (
    procesar_csv_relaciones,
    crear_relacion,
    obtener_relaciones,
    obtener_relacion_por_id,
    eliminar_relacion,
    actualizar_relacion,
    obtener_relaciones_por_tipo,
    obtener_relaciones_por_estado,
    obtener_relaciones_por_pais,
)

router = APIRouter(prefix="/api/relaciones-internacionales", tags=["Relaciones Internacionales"])

# Subir relaciones internacionales desde un archivo CSV
@router.post("/upload")
async def upload_csv(file: UploadFile = File(...), db: Session = Depends(get_db)):
    if not file.filename.endswith(".csv"):
        raise HTTPException(status_code=400, detail="Solo se permiten archivos CSV")
    return await procesar_csv_relaciones(file, db)

# Crear una nueva relación internacional
@router.post("/", response_model=RelacionInternacionalOut)
def create_relacion(relacion: RelacionInternacionalCreate, db: Session = Depends(get_db)):
    return crear_relacion(relacion, db)

# Obtener todas las relaciones internacionales
@router.get("/", response_model=List[RelacionInternacionalOut])
def get_relaciones(db: Session = Depends(get_db)):
    return obtener_relaciones(db)

# Obtener una relación internacional por ID
@router.get("/{relacion_id}", response_model=RelacionInternacionalOut)
def get_relacion(relacion_id: int, db: Session = Depends(get_db)):
    return obtener_relacion_por_id(relacion_id, db)

# Eliminar una relación internacional
@router.delete("/{relacion_id}")
def delete_relacion(relacion_id: int, db: Session = Depends(get_db)):
    return eliminar_relacion(relacion_id, db)

# Actualizar una relación internacional
@router.put("/{relacion_id}", response_model=RelacionInternacionalOut)
def update_relacion(relacion_id: int, updated_data: RelacionInternacionalUpdate, db: Session = Depends(get_db)):
    return actualizar_relacion(relacion_id, updated_data, db)

# Obtener relaciones por tipo
@router.get("/tipo/{tipo}", response_model=List[RelacionInternacionalOut])
def get_relaciones_by_type(tipo: TipoRelacion, db: Session = Depends(get_db)):
    return obtener_relaciones_por_tipo(tipo, db)

# Obtener relaciones por estado
@router.get("/estado/{estado}", response_model=List[RelacionInternacionalOut])
def get_relaciones_by_status(estado: EstadoRelacion, db: Session = Depends(get_db)):
    return obtener_relaciones_por_estado(estado, db)

# Obtener relaciones por país
@router.get("/pais/{pais}", response_model=List[RelacionInternacionalOut])
def get_relaciones_by_country(pais: str, db: Session = Depends(get_db)):
    return obtener_relaciones_por_pais(pais, db)