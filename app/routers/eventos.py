from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from fastapi.responses import JSONResponse
from typing import List

from app.database import get_db
from app.schemas.eventos import EventoCreate, EventoUpdate, EventoOut
from app.services.eventos_service import (
    procesar_csv_eventos,
    crear_evento,
    obtener_eventos,
    obtener_evento_por_id,
    actualizar_evento,
    eliminar_evento,
)

router = APIRouter(prefix="/api/eventos", tags=["Eventos"])

# Subir eventos desde un archivo CSV
@router.post("/upload_csv")
async def upload_csv(file: UploadFile = File(...), db: Session = Depends(get_db)):
    if not file.filename.endswith(".csv"):
        raise HTTPException(status_code=400, detail="Solo se permiten archivos CSV")
    return await procesar_csv_eventos(file, db)

# Crear un nuevo evento
@router.post("/", response_model=EventoOut)
def create_evento(evento: EventoCreate, db: Session = Depends(get_db)):
    return crear_evento(evento, db)

# Obtener todos los eventos
@router.get("/", response_model=List[EventoOut])
def get_eventos(db: Session = Depends(get_db)):
    return obtener_eventos(db)

# Obtener un evento por ID
@router.get("/{evento_id}", response_model=EventoOut)
def get_evento(evento_id: int, db: Session = Depends(get_db)):
    return obtener_evento_por_id(evento_id, db)

# Actualizar un evento
@router.put("/{evento_id}", response_model=EventoOut)
def update_evento(evento_id: int, updated_data: EventoUpdate, db: Session = Depends(get_db)):
    return actualizar_evento(evento_id, updated_data, db)

# Eliminar un evento
@router.delete("/{evento_id}")
def delete_evento(evento_id: int, db: Session = Depends(get_db)):
    return eliminar_evento(evento_id, db)