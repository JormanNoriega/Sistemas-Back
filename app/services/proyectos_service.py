from app.models.proyectos import Proyectos
from app.schemas.proyectos import ProyectoCreate, ProyectoUpdate
from app.utils.csv_parser import parse_csv_proyectos
from fastapi import HTTPException, UploadFile
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from typing import List

async def procesar_csv_proyectos(file: UploadFile, db: Session):
    try:
        proyectos_validos, proyectos_duplicados_csv = parse_csv_proyectos(file.file)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

    proyectos_db = []
    registros_duplicados_bd = []

    for proyecto in proyectos_validos:
        existing_proyecto = db.query(Proyectos).filter(
            (Proyectos.titulo == proyecto.get('titulo')) &
            (Proyectos.area_tematica == proyecto.get('area_tematica'))
        ).first()
        if existing_proyecto:
            registros_duplicados_bd.append({
                "titulo": proyecto.get('titulo'),
                "area_tematica": proyecto.get('area_tematica'),
                "error": f"Ya existe en la base de datos (ID: {existing_proyecto.proyecto_id})"
            })
        else:
            proyecto_db = Proyectos(
                titulo=proyecto.get('titulo'),
                area_tematica=proyecto.get('area_tematica'),
                fecha_inicio=proyecto.get('fecha_inicio'),
            )
            proyectos_db.append(proyecto_db)

    try:
        if proyectos_db:
            db.add_all(proyectos_db)
            db.commit()
        todos_registros_problematicos = proyectos_duplicados_csv + registros_duplicados_bd
        return JSONResponse(content={
            "mensaje": f"{len(proyectos_db)} proyectos subidos correctamente",
            "total_registros": len(proyectos_validos) + len(proyectos_duplicados_csv),
            "registros_validos": len(proyectos_db),
            "registros_duplicados_csv": len(proyectos_duplicados_csv),
            "registros_duplicados_bd": len(registros_duplicados_bd),
            "total_problemas": len(todos_registros_problematicos),
            "detalle_problemas": todos_registros_problematicos
        })
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error al guardar en BD: {str(e)}")

def crear_proyecto(proyecto: ProyectoCreate, db: Session) -> Proyectos:
    existing_proyecto = db.query(Proyectos).filter(Proyectos.titulo == proyecto.titulo).first()
    if existing_proyecto:
        raise HTTPException(status_code=400, detail="Ya existe un proyecto con este título")
    new_proyecto = Proyectos(**proyecto.dict())
    try:
        db.add(new_proyecto)
        db.commit()
        db.refresh(new_proyecto)
        return new_proyecto
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error al guardar en BD: {str(e)}")

def obtener_proyectos(db: Session) -> List[Proyectos]:
    return db.query(Proyectos).all()

def obtener_proyecto_por_id(proyecto_id: int, db: Session) -> Proyectos:
    proyecto = db.query(Proyectos).filter(Proyectos.proyecto_id == proyecto_id).first()
    if not proyecto:
        raise HTTPException(status_code=404, detail="Proyecto no encontrado")
    return proyecto

def eliminar_proyecto(proyecto_id: int, db: Session):
    proyecto = obtener_proyecto_por_id(proyecto_id, db)
    db.delete(proyecto)
    db.commit()
    return {"mensaje": "Proyecto eliminado correctamente"}

def actualizar_proyecto(proyecto_id: int, updated_data: ProyectoUpdate, db: Session) -> Proyectos:
    proyecto = obtener_proyecto_por_id(proyecto_id, db)
    for key, value in updated_data.dict(exclude_unset=True).items():
        setattr(proyecto, key, value)
    db.commit()
    db.refresh(proyecto)
    return proyecto