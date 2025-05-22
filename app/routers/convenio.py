from app.schemas.convenio import ConvenioCreate, ConvenioUpdate, ConvenioOut
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from app.models.convenio import EstatusConvenio
from sqlalchemy.orm import Session
from app.database import get_db
from typing import List
from app.services.convenio_service import (
    procesar_csv_convenios,
    crear_convenio,
    obtener_convenios,
    obtener_convenio_por_id,
    eliminar_convenio,
    actualizar_convenio,
    obtener_convenios_por_estatus,
    obtener_convenios_por_compania,
)

router = APIRouter(prefix="/api/convenios", tags=["Convenios"])

@router.post("/upload")
async def upload_csv(file: UploadFile = File(...), db: Session = Depends(get_db)):
    if not file.filename.endswith(".csv"):
        raise HTTPException(status_code=400, detail="Solo se permiten archivos CSV")
    return await procesar_csv_convenios(file, db)

@router.post("/", response_model=ConvenioOut)
def create_convenio(convenio: ConvenioCreate, db: Session = Depends(get_db)):
    return crear_convenio(convenio, db)

@router.get("/", response_model=List[ConvenioOut])
def get_convenios(db: Session = Depends(get_db)):
    return obtener_convenios(db)

@router.get("/{convenio_id}", response_model=ConvenioOut)
def get_convenio(convenio_id: int, db: Session = Depends(get_db)):
    return obtener_convenio_por_id(convenio_id, db)

@router.delete("/{convenio_id}")
def delete_convenio(convenio_id: int, db: Session = Depends(get_db)):
    return eliminar_convenio(convenio_id, db)

@router.put("/{convenio_id}", response_model=ConvenioOut)
def update_convenio(convenio_id: int, updated_data: ConvenioUpdate, db: Session = Depends(get_db)):
    return actualizar_convenio(convenio_id, updated_data, db)

@router.get("/estatus/{estatus}", response_model=List[ConvenioOut])
def get_convenios_by_status(estatus: EstatusConvenio, db: Session = Depends(get_db)):
    return obtener_convenios_por_estatus(estatus, db)

@router.get("/compania/{compania_id}", response_model=List[ConvenioOut])
def get_convenios_by_company(compania_id: int, db: Session = Depends(get_db)):
    return obtener_convenios_por_compania(compania_id, db)
