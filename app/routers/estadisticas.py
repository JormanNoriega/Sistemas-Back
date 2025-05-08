from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from fastapi.responses import JSONResponse
from typing import List

from app.database import get_db
from app.models.estadisticas import Estadisticas
from app.schemas.estadisticas import EstadisticaCreate, EstadisticaUpdate, EstadisticaOut

router = APIRouter(prefix="/api/estadisticas", tags=["Estadísticas"])

# Subir estadísticas desde un archivo CSV (opcional, si se necesita)
@router.post("/upload_csv")
async def upload_csv(file: UploadFile = File(...), db: Session = Depends(get_db)):
    """
    Subir estadísticas desde un archivo CSV.
    """
    if not file.filename.endswith(".csv"):
        raise HTTPException(status_code=400, detail="Solo se permiten archivos CSV")

    try:
        # Leer el contenido del archivo CSV
        import csv
        content = file.file.read().decode("utf-8").splitlines()
        reader = csv.DictReader(content)

        estadisticas_db = []
        for row in reader:
            estadistica_db = Estadisticas(
                categoria=row.get("categoria"),
                value=row.get("value"),
                descripcion=row.get("descripcion"),
            )
            estadisticas_db.append(estadistica_db)

        # Guardar las estadísticas en la base de datos
        db.add_all(estadisticas_db)
        db.commit()
        return JSONResponse(content={"mensaje": f"{len(estadisticas_db)} estadísticas subidas correctamente"})
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error al procesar el archivo CSV: {str(e)}")

# Crear una nueva estadística
@router.post("/", response_model=EstadisticaOut)
def create_estadistica(estadistica: EstadisticaCreate, db: Session = Depends(get_db)):
    new_estadistica = Estadisticas(
        categoria=estadistica.categoria,
        value=estadistica.value,
        descripcion=estadistica.descripcion
    )

    try:
        db.add(new_estadistica)
        db.commit()
        db.refresh(new_estadistica)  # Refrescar el objeto para obtener el ID generado
        return new_estadistica
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error al guardar en BD: {str(e)}")

# Obtener todas las estadísticas
@router.get("/", response_model=List[EstadisticaOut])
def get_estadisticas(db: Session = Depends(get_db)):
    estadisticas = db.query(Estadisticas).all()
    return estadisticas

# Obtener una estadística por ID
@router.get("/{estadistica_id}", response_model=EstadisticaOut)
def get_estadistica(estadistica_id: int, db: Session = Depends(get_db)):
    estadistica = db.query(Estadisticas).filter(Estadisticas.estadistica_id == estadistica_id).first()
    if not estadistica:
        raise HTTPException(status_code=404, detail="Estadística no encontrada")
    return estadistica

# Actualizar una estadística
@router.put("/{estadistica_id}", response_model=EstadisticaOut)
def update_estadistica(estadistica_id: int, estadistica: EstadisticaUpdate, db: Session = Depends(get_db)):
    existing_estadistica = db.query(Estadisticas).filter(Estadisticas.estadistica_id == estadistica_id).first()
    if not existing_estadistica:
        raise HTTPException(status_code=404, detail="Estadística no encontrada")

    # Actualizar los campos de la estadística
    for key, value in estadistica.dict(exclude_unset=True).items():
        setattr(existing_estadistica, key, value)

    try:
        db.commit()
        db.refresh(existing_estadistica)  # Refrescar el objeto para obtener los datos actualizados
        return existing_estadistica
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error al actualizar la estadística: {str(e)}")

# Eliminar una estadística
@router.delete("/{estadistica_id}")
def delete_estadistica(estadistica_id: int, db: Session = Depends(get_db)):
    estadistica = db.query(Estadisticas).filter(Estadisticas.estadistica_id == estadistica_id).first()
    if not estadistica:
        raise HTTPException(status_code=404, detail="Estadística no encontrada")

    try:
        db.delete(estadistica)
        db.commit()
        return JSONResponse(content={"mensaje": "Estadística eliminada correctamente"})
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error al eliminar la estadística: {str(e)}")