# app/routers/salida_a_practicas.py
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.schemas.salida_a_practicas import SalidaPracticaCreate, SalidaPracticaUpdate, SalidaPracticaOut
from app.services.salida_a_practicas_service import (
    obtener_salida_practica,
    obtener_salidas_practicas,
    crear_salida_practica,
    actualizar_salida_practica,
    eliminar_salida_practica,
    procesar_csv_salidas_practicas
)

router = APIRouter(prefix="/api/salidas-practicas", tags=["Salidas a Prácticas"])

# Subir salidas a prácticas desde un archivo CSV
@router.post("/upload_csv")
async def upload_csv(file: UploadFile = File(...), db: Session = Depends(get_db)):
    """
    Subir registros de salidas a prácticas desde un archivo CSV.
    """
    if not file.filename.endswith(".csv"):
        raise HTTPException(status_code=400, detail="Solo se permiten archivos CSV")
    
    return await procesar_csv_salidas_practicas(file, db)

# Crear una nueva salida a prácticas
@router.post("/", response_model=SalidaPracticaOut)
def create_salida_practica(salida: SalidaPracticaCreate, db: Session = Depends(get_db)):
    return crear_salida_practica(db, salida)

# Obtener todas las salidas a prácticas
@router.get("/", response_model=List[SalidaPracticaOut])
def get_salidas_practicas(db: Session = Depends(get_db)):
    return obtener_salidas_practicas(db)

# Obtener una salida a prácticas por ID
@router.get("/{salida_id}", response_model=SalidaPracticaOut)
def get_salida_practica(salida_id: int, db: Session = Depends(get_db)):
    salida = obtener_salida_practica(db, salida_id)
    if not salida:
        raise HTTPException(status_code=404, detail="Registro de salida a prácticas no encontrado")
    return salida

# Eliminar una salida a prácticas
@router.delete("/{salida_id}")
def delete_salida_practica(salida_id: int, db: Session = Depends(get_db)):
    result = eliminar_salida_practica(db, salida_id)
    if not result:
        raise HTTPException(status_code=404, detail="Registro de salida a prácticas no encontrado")
    return {"mensaje": "Registro de salida a prácticas eliminado correctamente"}

# Actualizar una salida a prácticas
@router.put("/{salida_id}", response_model=SalidaPracticaOut)
def update_salida_practica(salida_id: int, salida_data: SalidaPracticaUpdate, db: Session = Depends(get_db)):
    updated_salida = actualizar_salida_practica(db, salida_id, salida_data)
    if not updated_salida:
        raise HTTPException(status_code=404, detail="Registro de salida a prácticas no encontrado")
    return updated_salida
