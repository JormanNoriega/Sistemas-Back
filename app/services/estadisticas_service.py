from app.models.estadisticas import Estadisticas
from app.schemas.estadisticas import EstadisticaCreate, EstadisticaUpdate
from app.utils.csv_parser import parse_csv_estadisticas
from fastapi import HTTPException, UploadFile
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from typing import List

async def procesar_csv_estadisticas(file: UploadFile, db: Session):
    try:
        estadisticas_validas, estadisticas_duplicadas_csv = parse_csv_estadisticas(file.file)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

    estadisticas_db = []
    registros_duplicados_bd = []

    for estadistica in estadisticas_validas:
        existing = db.query(Estadisticas).filter(
            (Estadisticas.categoria == estadistica.get('categoria')) &
            (Estadisticas.descripcion == estadistica.get('descripcion'))
        ).first()
        if existing:
            registros_duplicados_bd.append({
                "categoria": estadistica.get('categoria'),
                "descripcion": estadistica.get('descripcion'),
                "error": f"Ya existe en la base de datos (ID: {existing.estadistica_id})"
            })
        else:
            estadistica_db = Estadisticas(
                categoria=estadistica.get("categoria"),
                value=estadistica.get("value"),
                descripcion=estadistica.get("descripcion"),
            )
            estadisticas_db.append(estadistica_db)

    try:
        if estadisticas_db:
            db.add_all(estadisticas_db)
            db.commit()
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

def crear_estadistica(estadistica: EstadisticaCreate, db: Session) -> Estadisticas:
    new_estadistica = Estadisticas(**estadistica.dict())
    try:
        db.add(new_estadistica)
        db.commit()
        db.refresh(new_estadistica)
        return new_estadistica
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error al guardar en BD: {str(e)}")

def obtener_estadisticas(db: Session) -> List[Estadisticas]:
    return db.query(Estadisticas).all()

def obtener_estadistica_por_id(estadistica_id: int, db: Session) -> Estadisticas:
    estadistica = db.query(Estadisticas).filter(Estadisticas.estadistica_id == estadistica_id).first()
    if not estadistica:
        raise HTTPException(status_code=404, detail="Estadística no encontrada")
    return estadistica

def actualizar_estadistica(estadistica_id: int, updated_data: EstadisticaUpdate, db: Session) -> Estadisticas:
    estadistica = obtener_estadistica_por_id(estadistica_id, db)
    for key, value in updated_data.dict(exclude_unset=True).items():
        setattr(estadistica, key, value)
    db.commit()
    db.refresh(estadistica)
    return estadistica

def eliminar_estadistica(estadistica_id: int, db: Session):
    estadistica = obtener_estadistica_por_id(estadistica_id, db)
    db.delete(estadistica)
    db.commit()
    return {"detail": "Estadística eliminada"}