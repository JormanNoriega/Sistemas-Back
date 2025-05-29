# app/routers/empresa.py
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from fastapi.responses import JSONResponse
from typing import List

from app.database import get_db
from app.schemas.empresa import EmpresaCreate, EmpresaUpdate, EmpresaOut
from app.services.empresa_service import (
    procesar_csv_empresas,
    crear_empresa,
    obtener_empresas,
    obtener_empresa_por_id,
    eliminar_empresa,
    actualizar_empresa,
)

router = APIRouter(prefix="/api/empresas", tags=["Empresas Aliadas"])

# Subir empresas desde un archivo CSV
@router.post("/upload-csv")
async def upload_csv(file: UploadFile = File(...), db: Session = Depends(get_db)):
    if not file.filename.endswith(".csv"):
        raise HTTPException(status_code=400, detail="Solo se permiten archivos CSV")
    return await procesar_csv_empresas(file, db)

# Crear una nueva empresa
@router.post("/", response_model=EmpresaOut)
def create_empresa(empresa: EmpresaCreate, db: Session = Depends(get_db)):
    return crear_empresa(empresa, db)

# Obtener todas las empresas
@router.get("/", response_model=List[EmpresaOut])
def get_empresas(db: Session = Depends(get_db)):
    return obtener_empresas(db)

# Obtener una empresa por ID
@router.get("/{empresa_id}", response_model=EmpresaOut)
def get_empresa(empresa_id: int, db: Session = Depends(get_db)):
    return obtener_empresa_por_id(empresa_id, db)

# Eliminar una empresa
@router.delete("/{empresa_id}")
def delete_empresa(empresa_id: int, db: Session = Depends(get_db)):
    return eliminar_empresa(empresa_id, db)

# Actualizar una empresa
@router.put("/{empresa_id}", response_model=EmpresaOut)
def update_empresa(empresa_id: int, updated_data: EmpresaUpdate, db: Session = Depends(get_db)):
    return actualizar_empresa(empresa_id, updated_data, db)
