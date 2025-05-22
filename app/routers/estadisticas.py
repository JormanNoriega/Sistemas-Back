from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from fastapi.responses import JSONResponse
from typing import List

from app.database import get_db
from app.models.estadisticas import Estadisticas
from app.schemas.estadisticas import EstadisticaCreate, EstadisticaUpdate, EstadisticaOut
from app.utils.csv_parser import parse_csv_estadisticas

router = APIRouter(prefix="/api/estadisticas", tags=["Estadísticas"])

# Subir estadísticas desde un archivo CSV
@router.post("/upload_csv")
async def upload_csv(file: UploadFile = File(...), db: Session = Depends(get_db)):
    """
    Subir estadísticas desde un archivo CSV.
    """
    if not file.filename.endswith(".csv"):
        raise HTTPException(status_code=400, detail="Solo se permiten archivos CSV")

    try:
        # Obtener estadísticas válidas y duplicadas del CSV
        estadisticas_validas, estadisticas_duplicadas_csv = parse_csv_estadisticas(file.file)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

    estadisticas_db = []
    registros_duplicados_bd = []
    
    for estadistica in estadisticas_validas:
        # Verificar si ya existe una estadística con la misma categoría y descripción
        existing_estadistica = db.query(Estadisticas).filter(
            (Estadisticas.categoria == estadistica.get('categoria')) & 
            (Estadisticas.descripcion == estadistica.get('descripcion'))
        ).first()
        
        if existing_estadistica:
            # La estadística ya existe en la BD
            registros_duplicados_bd.append({
                "categoria": estadistica.get('categoria'),
                "descripcion": estadistica.get('descripcion'),
                "error": f"Ya existe en la base de datos (ID: {existing_estadistica.estadistica_id})"
            })
        else:
            # La estadística no existe, se puede agregar
            estadistica_db = Estadisticas(
                categoria=estadistica.get("categoria"),
                value=estadistica.get("value"),
                descripcion=estadistica.get("descripcion"),
            )
            estadisticas_db.append(estadistica_db)

    try:
        if estadisticas_db:
            # Guardar las estadísticas en la base de datos
            db.add_all(estadisticas_db)
            db.commit()
        
        # Combinar todos los registros con problemas
        todos_registros_problematicos = estadisticas_duplicadas_csv + registros_duplicados_bd
        
        return JSONResponse(content={
            "mensaje": f"{len(estadisticas_db)} estadísticas subidas correctamente",
            "total_registros": len(estadisticas_validas) + len(estadisticas_duplicadas_csv),
            "registros_validos": len(estadisticas_db),
            "registros_duplicados_csv": len(estadisticas_duplicadas_csv),
            "registros_duplicados_bd": len(registros_duplicados_bd),
            "total_problemas": len(todos_registros_problematicos),
            "detalle_problemas": todos_registros_problematicos
        })
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