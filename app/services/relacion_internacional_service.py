from app.models.relacion_internacional import RelacionInternacional, TipoRelacion, EstadoRelacion
from app.schemas.relacion_internacional import RelacionInternacionalCreate, RelacionInternacionalUpdate
from app.utils.csv_parser import parse_csv_relaciones_internacionales
from fastapi import HTTPException, UploadFile
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from datetime import datetime
from typing import List

async def procesar_csv_relaciones(file: UploadFile, db: Session):
    try:
        relaciones_validas, relaciones_duplicadas_csv = parse_csv_relaciones_internacionales(file.file)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

    relaciones_db = []
    registros_con_error = []
    registros_duplicados_bd = []

    for relacion in relaciones_validas:
        try:
            # Ya no necesitamos convertir las fechas porque parse_csv_relaciones_internacionales ya lo hace
            existing_relacion = db.query(RelacionInternacional).filter(
                (RelacionInternacional.nombre == relacion.get('nombre')) &
                (RelacionInternacional.institucion == relacion.get('institucion'))
            ).first()
            
            if existing_relacion:
                registros_duplicados_bd.append({
                    "nombre": relacion.get('nombre'),
                    "institucion": relacion.get('institucion'),
                    "error": f"Ya existe en la base de datos (ID: {existing_relacion.relacion_id})"
                })
            else:
                # Validar el tipo de relación
                tipo_relacion = relacion.get('tipo')
                if tipo_relacion not in [item.value for item in TipoRelacion]:
                    tipo_relacion = TipoRelacion.PROJECT
                
                # Validar el estado de la relación
                estado_relacion = relacion.get('estado')
                if estado_relacion not in [item.value for item in EstadoRelacion]:
                    estado_relacion = EstadoRelacion.PENDING
                    
                relacion_db = RelacionInternacional(
                    nombre=relacion.get('nombre'),
                    pais=relacion.get('pais'),
                    institucion=relacion.get('institucion'),
                    tipo=tipo_relacion,
                    fecha_inicio=relacion.get('fecha_inicio'),
                    fecha_finalizacion=relacion.get('fecha_finalizacion'),
                    descripcion=relacion.get('descripcion'),
                    participantes=relacion.get('participantes'),
                    resultados=relacion.get('resultados'),
                    estado=estado_relacion
                )
                relaciones_db.append(relacion_db)
        except Exception as e:
            registros_con_error.append({
                "nombre": relacion.get('nombre'),
                "institucion": relacion.get('institucion'),
                "error": f"Error al procesar: {str(e)}"
            })

    try:
        if relaciones_db:
            db.add_all(relaciones_db)
            db.commit()
        todos_registros_problematicos = relaciones_duplicadas_csv + registros_duplicados_bd + registros_con_error
        return JSONResponse(content={
            "mensaje": f"{len(relaciones_db)} relaciones internacionales subidas correctamente",
            "total_registros": len(relaciones_validas) + len(relaciones_duplicadas_csv),
            "registros_validos": len(relaciones_db),
            "registros_duplicados_csv": len(relaciones_duplicadas_csv),
            "registros_duplicados_bd": len(registros_duplicados_bd),
            "registros_con_errores_formato": len(registros_con_error),
            "total_problemas": len(todos_registros_problematicos),
            "detalle_problemas": todos_registros_problematicos
        })
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error al guardar en BD: {str(e)}")

def crear_relacion(relacion: RelacionInternacionalCreate, db: Session) -> RelacionInternacional:
    new_relacion = RelacionInternacional(**relacion.dict())
    try:
        db.add(new_relacion)
        db.commit()
        db.refresh(new_relacion)
        return new_relacion
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error al guardar en BD: {str(e)}")

def obtener_relaciones(db: Session) -> List[RelacionInternacional]:
    return db.query(RelacionInternacional).all()

def obtener_relacion_por_id(relacion_id: int, db: Session) -> RelacionInternacional:
    relacion = db.query(RelacionInternacional).filter(RelacionInternacional.relacion_id == relacion_id).first()
    if not relacion:
        raise HTTPException(status_code=404, detail="Relación internacional no encontrada")
    return relacion

def eliminar_relacion(relacion_id: int, db: Session):
    relacion = obtener_relacion_por_id(relacion_id, db)
    db.delete(relacion)
    db.commit()
    return {"detail": "Relación internacional eliminada"}

def actualizar_relacion(relacion_id: int, updated_data: RelacionInternacionalUpdate, db: Session) -> RelacionInternacional:
    relacion = obtener_relacion_por_id(relacion_id, db)
    for key, value in updated_data.dict(exclude_unset=True).items():
        setattr(relacion, key, value)
    db.commit()
    db.refresh(relacion)
    return relacion

def obtener_relaciones_por_tipo(tipo: TipoRelacion, db: Session) -> List[RelacionInternacional]:
    return db.query(RelacionInternacional).filter(RelacionInternacional.tipo == tipo).all()

def obtener_relaciones_por_estado(estado: EstadoRelacion, db: Session) -> List[RelacionInternacional]:
    return db.query(RelacionInternacional).filter(RelacionInternacional.estado == estado).all()

def obtener_relaciones_por_pais(pais: str, db: Session) -> List[RelacionInternacional]:
    return db.query(RelacionInternacional).filter(RelacionInternacional.pais == pais).all()