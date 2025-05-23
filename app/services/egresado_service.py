from app.models.egresado import Egresado, EstadoEmpleabilidad
from app.schemas.egresado import EgresadoCreate, EgresadoUpdate
from app.utils.csv_parser import parse_csv_egresados
from fastapi import HTTPException, UploadFile
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from datetime import datetime
from typing import List

async def procesar_csv_egresados(file: UploadFile, db: Session):
    try:
        egresados_validos, egresados_duplicados_csv = parse_csv_egresados(file.file)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

    egresados_db = []
    registros_con_error = []
    registros_duplicados_bd = []

    for egresado in egresados_validos:
        try:
            # Ya no necesitamos convertir la fecha porque parse_csv_egresados ya lo hace
            fecha_graduacion = datetime.strptime(egresado.get('año_graduacion'), '%Y-%m-%d').date()
            
            existing = db.query(Egresado).filter(
                (Egresado.nombre_completo == egresado.get('nombre')) &
                (Egresado.email == egresado.get('email'))
            ).first()
            
            if existing:
                registros_duplicados_bd.append({
                    "nombre": egresado.get('nombre'),
                    "email": egresado.get('email'),
                    "error": f"Ya existe en la base de datos (ID: {existing.egresado_id})"
                })
            else:
                # Convertir estado_empleabilidad a enum si es necesario
                empleabilidad = egresado.get('estado_empleabilidad')
                if empleabilidad not in [item.value for item in EstadoEmpleabilidad]:
                    empleabilidad = EstadoEmpleabilidad.DESEMPLEADO
                
                egresado_db = Egresado(
                    nombre_completo=egresado.get('nombre'),
                    año_graduacion=fecha_graduacion,
                    empleabilidad=empleabilidad,
                    email=egresado.get('email')
                )
                egresados_db.append(egresado_db)
        except Exception as e:
            registros_con_error.append({
                "nombre": egresado.get('nombre', 'Desconocido'),
                "email": egresado.get('email', 'Desconocido'),
                "error": f"Error al procesar: {str(e)}"
            })

    try:
        if egresados_db:
            db.add_all(egresados_db)
            db.commit()
        todos_registros_problematicos = egresados_duplicados_csv + registros_duplicados_bd + registros_con_error
        return JSONResponse(content={
            "mensaje": f"{len(egresados_db)} egresados subidos correctamente",
            "total_registros": len(egresados_validos) + len(egresados_duplicados_csv),
            "registros_validos": len(egresados_db),
            "registros_duplicados_csv": len(egresados_duplicados_csv),
            "registros_duplicados_bd": len(registros_duplicados_bd),
            "registros_con_error": len(registros_con_error),
            "total_problemas": len(todos_registros_problematicos),
            "detalle_problemas": todos_registros_problematicos
        })
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error al procesar el archivo CSV: {str(e)}")

def crear_egresado(egresado: EgresadoCreate, db: Session) -> Egresado:
    new_egresado = Egresado(**egresado.dict())
    try:
        db.add(new_egresado)
        db.commit()
        db.refresh(new_egresado)
        return new_egresado
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error al guardar en BD: {str(e)}")

def obtener_egresados(db: Session) -> List[Egresado]:
    return db.query(Egresado).all()

def obtener_egresado_por_id(egresado_id: int, db: Session) -> Egresado:
    egresado = db.query(Egresado).filter(Egresado.egresado_id == egresado_id).first()
    if not egresado:
        raise HTTPException(status_code=404, detail="Egresado no encontrado")
    return egresado

def actualizar_egresado(egresado_id: int, updated_data: EgresadoUpdate, db: Session) -> Egresado:
    egresado = obtener_egresado_por_id(egresado_id, db)
    for key, value in updated_data.dict(exclude_unset=True).items():
        setattr(egresado, key, value)
    db.commit()
    db.refresh(egresado)
    return egresado

def eliminar_egresado(egresado_id: int, db: Session):
    egresado = obtener_egresado_por_id(egresado_id, db)
    db.delete(egresado)
    db.commit()
    return {"detail": "Egresado eliminado"}