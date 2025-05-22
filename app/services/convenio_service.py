# convenios/service.py
from app.schemas.convenio import ConvenioCreate, ConvenioUpdate
from app.models.convenio import Convenio, EstatusConvenio
from app.utils.csv_parser import parse_csv_convenios
from fastapi import HTTPException, UploadFile
from fastapi.responses import JSONResponse
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from datetime import datetime
from typing import List
import psycopg2

async def procesar_csv_convenios(file : UploadFile, db : Session):
    try:
        convenios_validos, convenios_duplicados_csv = parse_csv_convenios(file.file)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

    convenios_db = []
    registros_con_error = []
    registros_duplicados_bd = []

    for convenio in convenios_validos:
        try:
            fecha_firma = datetime.strptime(convenio.get('fecha_firma'), '%Y-%m-%d').date()
            fecha_vencimiento = datetime.strptime(convenio.get('fecha_vencimiento'), '%Y-%m-%d').date()

            existing_convenio = db.query(Convenio).filter(
                (Convenio.compañia_id == convenio.get('compania_id')) &
                (Convenio.titulo_compañia == convenio.get('titulo_compania'))
            ).first()

            if existing_convenio:
                registros_duplicados_bd.append({
                    "compania_id": convenio.get('compania_id'),
                    "titulo_compania": convenio.get('titulo_compania'),
                    "error": f"Ya existe en la base de datos (ID: {existing_convenio.convenio_id})"
                })
            else:
                convenio_db = Convenio(
                    compañia_id=convenio.get('compania_id'),
                    titulo_compañia=convenio.get('titulo_compania'),
                    tipo_convenio=convenio.get('tipo_de_convenio'),
                    descripcion=convenio.get('descripcion'),
                    beneficios=convenio.get('beneficios'),
                    fecha=fecha_firma,
                    fecha_vencimiento=fecha_vencimiento,
                    estatus=convenio.get('estatus', EstatusConvenio.PENDING)
                )
                convenios_db.append(convenio_db)

        except Exception as e:
            registros_con_error.append({
                "compania_id": convenio.get('compania_id'),
                "titulo_compania": convenio.get('titulo_compania'),
                "error": f"Error de formato: {str(e)}"
            })

    try:
        if convenios_db:
            db.add_all(convenios_db)
            db.commit()

        todos_registros_problematicos = convenios_duplicados_csv + registros_duplicados_bd + registros_con_error

        return JSONResponse(content={
            "mensaje": f"{len(convenios_db)} convenios subidos correctamente",
            "total_registros": len(convenios_validos) + len(convenios_duplicados_csv),
            "registros_validos": len(convenios_db),
            "registros_duplicados_csv": len(convenios_duplicados_csv),
            "registros_duplicados_bd": len(registros_duplicados_bd),
            "registros_con_errores_formato": len(registros_con_error),
            "total_problemas": len(todos_registros_problematicos),
            "detalle_problemas": todos_registros_problematicos
        })

    except IntegrityError as e:
        db.rollback()
        if isinstance(e.orig, psycopg2.errors.ForeignKeyViolation):
            raise HTTPException(
                status_code=400,
                detail="Error: La compañía asociada al convenio no existe en la base de datos."
            )
        raise HTTPException(status_code=500, detail=f"Error al guardar en BD: {str(e)}")

def crear_convenio(convenio: ConvenioCreate, db: Session) -> Convenio:
    new_convenio = Convenio(**convenio.dict())

    try:
        db.add(new_convenio)
        db.commit()
        db.refresh(new_convenio)
        return new_convenio
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error al guardar en BD: {str(e)}")

def obtener_convenios(db: Session) -> List[Convenio]:
    return db.query(Convenio).all()

def obtener_convenio_por_id(convenio_id: int, db: Session) -> Convenio:
    convenio = db.query(Convenio).filter(Convenio.convenio_id == convenio_id).first()
    if not convenio:
        raise HTTPException(status_code=404, detail="Convenio no encontrado")
    return convenio

def eliminar_convenio(convenio_id: int, db: Session):
    convenio = obtener_convenio_por_id(convenio_id, db)
    db.delete(convenio)
    db.commit()
    return {"detail": "Convenio eliminado"}

def actualizar_convenio(convenio_id: int, updated_data: ConvenioUpdate, db: Session) -> Convenio:
    convenio = obtener_convenio_por_id(convenio_id, db)
    for key, value in updated_data.dict(exclude_unset=True).items():
        setattr(convenio, key, value)

    db.commit()
    db.refresh(convenio)
    return convenio

def obtener_convenios_por_estatus(estatus: EstatusConvenio, db: Session) -> List[Convenio]:
    return db.query(Convenio).filter(Convenio.estatus == estatus).all()

def obtener_convenios_por_compania(compania_id: int, db: Session) -> List[Convenio]:
    return db.query(Convenio).filter(Convenio.compania_id == compania_id).all()