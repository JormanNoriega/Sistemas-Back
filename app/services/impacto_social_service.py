# app/services/impacto_social_service.py

from sqlalchemy.orm import Session
from app.models.Impacto_social import ImpactoSocial
from app.schemas.impacto_social import ImpactoSocialCreate, ImpactoSocialUpdate
from app.utils.csv_parser import parse_csv_impacto_social
from fastapi import HTTPException, UploadFile
from fastapi.responses import JSONResponse

def crear_impacto_social(db: Session, impacto_data: ImpactoSocialCreate):
    """Crea un nuevo registro de impacto social"""
    # Verificar si ya existe un impacto con el mismo título y ubicación
    existing_impacto = db.query(ImpactoSocial).filter(
        (ImpactoSocial.titulo == impacto_data.titulo) & 
        (ImpactoSocial.ubicacion == impacto_data.ubicacion)
    ).first()
    
    if existing_impacto:
        raise HTTPException(status_code=400, detail="Ya existe un registro con este título y ubicación")
    
    nuevo_impacto = ImpactoSocial(
        titulo=impacto_data.titulo,
        beneficiarios=impacto_data.beneficiarios,
        ubicacion=impacto_data.ubicacion,
        fecha_inicio=impacto_data.fecha_inicio,
        fecha_final=impacto_data.fecha_final,
        descripcion=impacto_data.descripcion,
        objetivos=impacto_data.objetivos,
        resultados=impacto_data.resultados,
        participantes=impacto_data.participantes,
        estado=impacto_data.estado
    )
    db.add(nuevo_impacto)
    db.commit()
    db.refresh(nuevo_impacto)
    return nuevo_impacto

def obtener_impacto_social(db: Session, impacto_id: int):
    """Obtiene un impacto social por su ID"""
    return db.query(ImpactoSocial).filter(ImpactoSocial.impacto_id == impacto_id).first()

def obtener_impactos_sociales(db: Session, skip: int = 0, limit: int = 100):
    """Obtiene todos los impactos sociales"""
    return db.query(ImpactoSocial).offset(skip).limit(limit).all()

def actualizar_impacto_social(db: Session, impacto_id: int, impacto_data: ImpactoSocialUpdate):
    """Actualiza un impacto social existente"""
    impacto = obtener_impacto_social(db, impacto_id)
    if impacto:
        for key, value in impacto_data.dict(exclude_unset=True).items():
            setattr(impacto, key, value)
        db.commit()
        db.refresh(impacto)
    return impacto

def eliminar_impacto_social(db: Session, impacto_id: int):
    """Elimina un impacto social"""
    impacto = obtener_impacto_social(db, impacto_id)
    if impacto:
        db.delete(impacto)
        db.commit()
        return True
    return False

async def procesar_csv_impacto_social(file: UploadFile, db: Session):
    """Procesa un archivo CSV de impacto social y gestiona la validación y registro en BD"""
    try:
        # Obtener impactos sociales válidos y duplicados del CSV
        impactos_validos, impactos_duplicados_csv = parse_csv_impacto_social(file.file)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

    impactos_db = []
    registros_duplicados_bd = []
    
    for impacto in impactos_validos:
        # Verificar si ya existe un impacto con el mismo título y ubicación
        existing_impacto = db.query(ImpactoSocial).filter(
            (ImpactoSocial.titulo == impacto.get('titulo')) & 
            (ImpactoSocial.ubicacion == impacto.get('ubicacion'))
        ).first()
        
        if existing_impacto:
            # El impacto ya existe en la BD
            registros_duplicados_bd.append({
                "titulo": impacto.get('titulo'),
                "ubicacion": impacto.get('ubicacion'),
                "error": f"Ya existe en la base de datos (ID: {existing_impacto.impacto_id})"
            })
        else:
            # El impacto no existe, se puede agregar
            impacto_db = ImpactoSocial(
                titulo=impacto.get('titulo'),
                beneficiarios=impacto.get('beneficiarios'),
                ubicacion=impacto.get('ubicacion'),
                fecha_inicio=impacto.get('fecha_inicio'),
                fecha_final=impacto.get('fecha_final'),
                descripcion=impacto.get('descripcion'),
                objetivos=impacto.get('objetivos'),
                resultados=impacto.get('resultados'),
                participantes=impacto.get('participantes'),
                estado=impacto.get('estado')
            )
            impactos_db.append(impacto_db)

    try:
        if impactos_db:
            db.add_all(impactos_db)
            db.commit()
            
        # Combinar todos los registros con problemas
        todos_registros_problematicos = impactos_duplicados_csv + registros_duplicados_bd
        
        return JSONResponse(content={
            "mensaje": f"{len(impactos_db)} registros de impacto social subidos correctamente",
            "total_registros": len(impactos_validos) + len(impactos_duplicados_csv),
            "registros_validos": len(impactos_db),
            "registros_duplicados_csv": len(impactos_duplicados_csv),
            "registros_duplicados_bd": len(registros_duplicados_bd),
            "total_problemas": len(todos_registros_problematicos),
            "detalle_problemas": todos_registros_problematicos
        })
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error al guardar en BD: {str(e)}")
