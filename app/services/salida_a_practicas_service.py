# app/services/salida_a_practicas_service.py

from sqlalchemy.orm import Session
from app.models.salida_a_practicas import SalidaPractica
from app.schemas.salida_a_practicas import SalidaPracticaCreate, SalidaPracticaUpdate
from app.utils.csv_parser import parse_csv_salidas_practicas
from fastapi import HTTPException, UploadFile
from fastapi.responses import JSONResponse

def crear_salida_practica(db: Session, salida_data: SalidaPracticaCreate):
    """Crea un nuevo registro de salida a prácticas"""
    # Verificar si ya existe una salida con la misma fecha, destino y hora
    existing_salida = db.query(SalidaPractica).filter(
        (SalidaPractica.fecha_salida == salida_data.fecha_salida) & 
        (SalidaPractica.lugar_destino == salida_data.lugar_destino) &
        (SalidaPractica.hora_salida == salida_data.hora_salida)
    ).first()
    
    if existing_salida:
        raise HTTPException(status_code=400, detail="Ya existe una salida a prácticas programada para la misma fecha, destino y hora")
    
    nueva_salida = SalidaPractica(
        fecha_salida=salida_data.fecha_salida,
        lugar_destino=salida_data.lugar_destino,
        responsable=salida_data.responsable,
        cantidad_estudiantes=salida_data.cantidad_estudiantes,
        hora_salida=salida_data.hora_salida,
        hora_regreso=salida_data.hora_regreso,
        observaciones=salida_data.observaciones
    )
    db.add(nueva_salida)
    db.commit()
    db.refresh(nueva_salida)
    return nueva_salida

def obtener_salida_practica(db: Session, salida_id: int):
    """Obtiene una salida a prácticas por su ID"""
    return db.query(SalidaPractica).filter(SalidaPractica.id_salida_practica == salida_id).first()

def obtener_salidas_practicas(db: Session, skip: int = 0, limit: int = 100):
    """Obtiene todas las salidas a prácticas"""
    return db.query(SalidaPractica).offset(skip).limit(limit).all()

def actualizar_salida_practica(db: Session, salida_id: int, salida_data: SalidaPracticaUpdate):
    """Actualiza una salida a prácticas existente"""
    salida = obtener_salida_practica(db, salida_id)
    if salida:
        for key, value in salida_data.dict(exclude_unset=True).items():
            setattr(salida, key, value)
        db.commit()
        db.refresh(salida)
    return salida

def eliminar_salida_practica(db: Session, salida_id: int):
    """Elimina una salida a prácticas"""
    salida = obtener_salida_practica(db, salida_id)
    if salida:
        db.delete(salida)
        db.commit()
        return True
    return False

async def procesar_csv_salidas_practicas(file: UploadFile, db: Session):
    """Procesa un archivo CSV de salidas a prácticas y gestiona la validación y registro en BD"""
    try:
        # Obtener salidas a prácticas válidas y duplicadas del CSV
        salidas_validas, salidas_duplicadas_csv = parse_csv_salidas_practicas(file.file)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

    salidas_db = []
    registros_duplicados_bd = []
    
    for salida in salidas_validas:
        # Verificar si ya existe una salida con la misma fecha, destino y hora
        existing_salida = db.query(SalidaPractica).filter(
            (SalidaPractica.fecha_salida == salida.get('fecha_salida')) & 
            (SalidaPractica.lugar_destino == salida.get('lugar_destino')) &
            (SalidaPractica.hora_salida == salida.get('hora_salida'))
        ).first()
        
        if existing_salida:
            # La salida ya existe en la BD
            registros_duplicados_bd.append({
                "fecha_salida": str(salida.get('fecha_salida')),
                "lugar_destino": salida.get('lugar_destino'),
                "hora_salida": str(salida.get('hora_salida')),
                "error": f"Ya existe en la base de datos (ID: {existing_salida.id_salida_practica})"
            })
        else:
            # La salida no existe, se puede agregar
            salida_db = SalidaPractica(
                fecha_salida=salida.get('fecha_salida'),
                lugar_destino=salida.get('lugar_destino'),
                responsable=salida.get('responsable'),
                cantidad_estudiantes=salida.get('cantidad_estudiantes'),
                hora_salida=salida.get('hora_salida'),
                hora_regreso=salida.get('hora_regreso'),
                observaciones=salida.get('observaciones')
            )
            salidas_db.append(salida_db)

    try:
        if salidas_db:
            db.add_all(salidas_db)
            db.commit()
            
        # Combinar todos los registros con problemas
        todos_registros_problematicos = salidas_duplicadas_csv + registros_duplicados_bd
        
        return JSONResponse(content={
            "mensaje": f"{len(salidas_db)} registros de salidas a prácticas subidos correctamente",
            "total_registros": len(salidas_validas) + len(salidas_duplicadas_csv),
            "registros_validos": len(salidas_db),
            "registros_duplicados_csv": len(salidas_duplicadas_csv),
            "registros_duplicados_bd": len(registros_duplicados_bd),
            "total_problemas": len(todos_registros_problematicos),
            "detalle_problemas": todos_registros_problematicos
        })
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error al guardar en BD: {str(e)}")
