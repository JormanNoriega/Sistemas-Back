from app.schemas.publicaciones import PublicacionCreate, PublicacionUpdate, PublicacionOut
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from app.database import get_db
from typing import List
from app.services.publicaciones_service import (
    procesar_csv_publicaciones,
    crear_publicacion,
    obtener_publicaciones,
    obtener_publicacion_por_id,
    eliminar_publicacion,
    actualizar_publicacion,
    obtener_publicaciones_por_area,
    obtener_publicaciones_por_tipo,
)

router = APIRouter(prefix="/api/publicaciones", tags=["Publicaciones"])

@router.post("/upload")
async def upload_csv(file: UploadFile = File(...), db: Session = Depends(get_db)):
    if not file.filename.endswith(".csv"):
        raise HTTPException(status_code=400, detail="Solo se permiten archivos CSV")
    return await procesar_csv_publicaciones(file, db)

@router.post("/", response_model=PublicacionOut)
def create_publicacion(publicacion: PublicacionCreate, db: Session = Depends(get_db)):
    return crear_publicacion(publicacion, db)

@router.get("/", response_model=List[PublicacionOut])
def get_publicaciones(db: Session = Depends(get_db)):
    return obtener_publicaciones(db)

@router.get("/{publicacion_id}", response_model=PublicacionOut)
def get_publicacion(publicacion_id: int, db: Session = Depends(get_db)):
    return obtener_publicacion_por_id(publicacion_id, db)

@router.delete("/{publicacion_id}")
def delete_publicacion(publicacion_id: int, db: Session = Depends(get_db)):
    return eliminar_publicacion(publicacion_id, db)

@router.put("/{publicacion_id}", response_model=PublicacionOut)
def update_publicacion(publicacion_id: int, updated_data: PublicacionUpdate, db: Session = Depends(get_db)):
    return actualizar_publicacion(publicacion_id, updated_data, db)

@router.get("/area/{area}", response_model=List[PublicacionOut])
def get_publicaciones_by_area(area: str, db: Session = Depends(get_db)):
    return obtener_publicaciones_por_area(area, db)

@router.get("/tipo/{tipo}", response_model=List[PublicacionOut])
def get_publicaciones_by_tipo(tipo: str, db: Session = Depends(get_db)):
    return obtener_publicaciones_por_tipo(tipo, db)
