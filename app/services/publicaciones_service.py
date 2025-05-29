from app.schemas.publicaciones import PublicacionCreate, PublicacionUpdate
from app.models.publicaciones import Publicacion
from app.utils.csv_parser import parse_csv_publicaciones
from fastapi import HTTPException, UploadFile
from fastapi.responses import JSONResponse
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from typing import List

async def procesar_csv_publicaciones(file: UploadFile, db: Session):
    try:
        publicaciones_validas, publicaciones_duplicadas_csv = parse_csv_publicaciones(file.file)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

    publicaciones_db = []
    registros_con_error = []
    registros_duplicados_bd = []

    for publicacion in publicaciones_validas:
        try:
            existing_publicacion = db.query(Publicacion).filter(
                (Publicacion.titulo == publicacion.get('titulo')) &
                (Publicacion.autores == publicacion.get('autores'))
            ).first()

            if existing_publicacion:
                registros_duplicados_bd.append({
                    "titulo": publicacion.get('titulo'),
                    "autores": publicacion.get('autores'),
                    "error": f"Ya existe en la base de datos (ID: {existing_publicacion.publicacion_id})"
                })
            else:
                publicacion_db = Publicacion(
                    titulo=publicacion.get('titulo'),
                    autores=publicacion.get('autores'),
                    area=publicacion.get('area'),
                    fecha=publicacion.get('fecha'),
                    enlace=publicacion.get('enlace'),
                    tipo=publicacion.get('tipo')
                )
                publicaciones_db.append(publicacion_db)

        except Exception as e:
            registros_con_error.append({
                "titulo": publicacion.get('titulo'),
                "autores": publicacion.get('autores'),
                "error": f"Error de formato: {str(e)}"
            })

    try:
        if publicaciones_db:
            db.add_all(publicaciones_db)
            db.commit()

        todos_registros_problematicos = publicaciones_duplicadas_csv + registros_duplicados_bd + registros_con_error

        return JSONResponse(content={
            "mensaje": f"{len(publicaciones_db)} publicaciones subidas correctamente",
            "total_registros": len(publicaciones_validas) + len(publicaciones_duplicadas_csv),
            "registros_validos": len(publicaciones_db),
            "registros_duplicados_csv": len(publicaciones_duplicadas_csv),
            "registros_duplicados_bd": len(registros_duplicados_bd),
            "registros_con_errores_formato": len(registros_con_error),
            "total_problemas": len(todos_registros_problematicos),
            "detalle_problemas": todos_registros_problematicos
        })

    except IntegrityError as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error al guardar en BD: {str(e)}")

def crear_publicacion(publicacion: PublicacionCreate, db: Session) -> Publicacion:
    new_publicacion = Publicacion(**publicacion.dict())

    try:
        db.add(new_publicacion)
        db.commit()
        db.refresh(new_publicacion)
        return new_publicacion
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error al guardar en BD: {str(e)}")

def obtener_publicaciones(db: Session) -> List[Publicacion]:
    return db.query(Publicacion).all()

def obtener_publicacion_por_id(publicacion_id: int, db: Session) -> Publicacion:
    publicacion = db.query(Publicacion).filter(Publicacion.publicacion_id == publicacion_id).first()
    if not publicacion:
        raise HTTPException(status_code=404, detail="Publicación no encontrada")
    return publicacion

def eliminar_publicacion(publicacion_id: int, db: Session):
    publicacion = obtener_publicacion_por_id(publicacion_id, db)
    db.delete(publicacion)
    db.commit()
    return {"detail": "Publicación eliminada"}

def actualizar_publicacion(publicacion_id: int, updated_data: PublicacionUpdate, db: Session) -> Publicacion:
    publicacion = obtener_publicacion_por_id(publicacion_id, db)
    for key, value in updated_data.dict(exclude_unset=True).items():
        setattr(publicacion, key, value)

    db.commit()
    db.refresh(publicacion)
    return publicacion

def obtener_publicaciones_por_area(area: str, db: Session) -> List[Publicacion]:
    return db.query(Publicacion).filter(Publicacion.area == area).all()

def obtener_publicaciones_por_tipo(tipo: str, db: Session) -> List[Publicacion]:
    return db.query(Publicacion).filter(Publicacion.tipo == tipo).all()
