# app/routers/impacto_social.py
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.models.Impacto_social import ImpactoSocial
from app.schemas.impacto_social import ImpactoSocialCreate, ImpactoSocialUpdate, ImpactoSocialOut
from app.services.impacto_social_service import (
    obtener_impacto_social,
    obtener_impactos_sociales,
    crear_impacto_social,
    actualizar_impacto_social,
    eliminar_impacto_social,
    procesar_csv_impacto_social
)

router = APIRouter(prefix="/api/impacto-social", tags=["Impacto Social"])

# Subir impactos sociales desde un archivo CSV
@router.post("/upload_csv")
async def upload_csv(file: UploadFile = File(...), db: Session = Depends(get_db)):
    """
    Subir registros de impacto social desde un archivo CSV.
    """
    if not file.filename.endswith(".csv"):
        raise HTTPException(status_code=400, detail="Solo se permiten archivos CSV")
    
    return await procesar_csv_impacto_social(file, db)

# Crear un nuevo impacto social
@router.post("/", response_model=ImpactoSocialOut)
def create_impacto(impacto: ImpactoSocialCreate, db: Session = Depends(get_db)):
    return crear_impacto_social(db, impacto)

# Obtener todos los impactos sociales
@router.get("/", response_model=List[ImpactoSocialOut])
def get_impactos(db: Session = Depends(get_db)):
    return obtener_impactos_sociales(db)

# Obtener un impacto social por ID
@router.get("/{impacto_id}", response_model=ImpactoSocialOut)
def get_impacto(impacto_id: int, db: Session = Depends(get_db)):
    impacto = obtener_impacto_social(db, impacto_id)
    if not impacto:
        raise HTTPException(status_code=404, detail="Registro de impacto social no encontrado")
    return impacto

# Eliminar un impacto social
@router.delete("/{impacto_id}")
def delete_impacto(impacto_id: int, db: Session = Depends(get_db)):
    result = eliminar_impacto_social(db, impacto_id)
    if not result:
        raise HTTPException(status_code=404, detail="Registro de impacto social no encontrado")
    return {"mensaje": "Registro de impacto social eliminado correctamente"}

# Actualizar un impacto social
@router.put("/{impacto_id}", response_model=ImpactoSocialOut)
def update_impacto(impacto_id: int, impacto_data: ImpactoSocialUpdate, db: Session = Depends(get_db)):
    updated_impacto = actualizar_impacto_social(db, impacto_id, impacto_data)
    if not updated_impacto:
        raise HTTPException(status_code=404, detail="Registro de impacto social no encontrado")
    return updated_impacto
