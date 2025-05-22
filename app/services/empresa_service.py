from app.models.empresa import Empresa
from app.schemas.empresa import EmpresaCreate, EmpresaUpdate
from app.utils.csv_parser import parse_csv_empresas
from fastapi import HTTPException, UploadFile
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from typing import List

async def procesar_csv_empresas(file: UploadFile, db: Session):
    try:
        empresas_validas, empresas_duplicadas_csv = parse_csv_empresas(file.file)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

    empresas_db = []
    empresas_duplicadas_bd = []

    for empresa in empresas_validas:
        existing_empresa = db.query(Empresa).filter(
            (Empresa.nit == empresa.get('nit')) | 
            (Empresa.nombre_empresa == empresa.get('nombre_empresa'))
        ).first()
        if existing_empresa:
            empresas_duplicadas_bd.append({
                "nombre_empresa": empresa.get('nombre_empresa'),
                "nit": empresa.get('nit'),
                "error": f"Ya existe en la base de datos (ID: {existing_empresa.empresa_id})"
            })
        else:
            empresa_db = Empresa(
                nombre_empresa=empresa.get('nombre_empresa'),
                nit=empresa.get('nit'),
                sector=empresa.get('sector'),
                fecha_convenio=empresa.get('fecha_convenio'),
            )
            empresas_db.append(empresa_db)

    try:
        if empresas_db:
            db.add_all(empresas_db)
            db.commit()
        todos_duplicados = empresas_duplicadas_csv + empresas_duplicadas_bd
        return JSONResponse(content={
            "mensaje": f"{len(empresas_db)} empresas subidas correctamente",
            "total_registros": len(empresas_validas) + len(empresas_duplicadas_csv),
            "registros_validos": len(empresas_db),
            "registros_duplicados_csv": len(empresas_duplicadas_csv),
            "registros_duplicados_bd": len(empresas_duplicadas_bd),
            "total_duplicados": len(todos_duplicados),
            "detalle_duplicados": todos_duplicados
        })
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error al guardar en BD: {str(e)}")

def crear_empresa(empresa: EmpresaCreate, db: Session) -> Empresa:
    existing_empresa = db.query(Empresa).filter(Empresa.nit == empresa.nit).first()
    if existing_empresa:
        raise HTTPException(status_code=400, detail="Ya existe una empresa con este NIT")
    new_empresa = Empresa(**empresa.dict())
    try:
        db.add(new_empresa)
        db.commit()
        db.refresh(new_empresa)
        return new_empresa
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error al guardar en BD: {str(e)}")

def obtener_empresas(db: Session) -> List[Empresa]:
    return db.query(Empresa).all()

def obtener_empresa_por_id(empresa_id: int, db: Session) -> Empresa:
    empresa = db.query(Empresa).filter(Empresa.empresa_id == empresa_id).first()
    if not empresa:
        raise HTTPException(status_code=404, detail="Empresa no encontrada")
    return empresa

def eliminar_empresa(empresa_id: int, db: Session):
    empresa = obtener_empresa_por_id(empresa_id, db)
    db.delete(empresa)
    db.commit()
    return {"detail": "Empresa eliminada"}

def actualizar_empresa(empresa_id: int, updated_data: EmpresaUpdate, db: Session) -> Empresa:
    empresa = obtener_empresa_por_id(empresa_id, db)
    for key, value in updated_data.dict(exclude_unset=True).items():
        setattr(empresa, key, value)
    db.commit()
    db.refresh(empresa)
    return empresa