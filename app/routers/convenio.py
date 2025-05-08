from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from fastapi.responses import JSONResponse
from typing import List
from datetime import datetime

from app.database import get_db
from app.models.convenio import Convenio, EstatusConvenio
from app.schemas.convenio import ConvenioCreate, ConvenioUpdate, ConvenioOut
from app.utils.csv_parser import parse_csv_convenios

router = APIRouter(prefix="/api/convenios", tags=["Convenios"])

# Subir convenios desde un archivo CSV
@router.post("/upload")
async def upload_csv(file: UploadFile = File(...), db: Session = Depends(get_db)):
    if not file.filename.endswith(".csv"):
        raise HTTPException(status_code=400, detail="Solo se permiten archivos CSV")

    try:
        convenios_data = parse_csv_convenios(file.file)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

    convenios_db = []
    for convenio in convenios_data:
        # Convertir fechas
        fecha_firma = datetime.strptime(convenio.get('fecha_firma'), '%Y-%m-%d').date()
        fecha_vencimiento = datetime.strptime(convenio.get('fecha_vencimiento'), '%Y-%m-%d').date()
        convenio_db = Convenio(
            compania_id=convenio.get('compania_id'),
            titulo_compania=convenio.get('titulo_compania'),
            tipo_de_convenio=convenio.get('tipo_de_convenio'),
            descripcion=convenio.get('descripcion'),
            beneficios=convenio.get('beneficios'),
            fecha_firma=fecha_firma,
            fecha_vencimiento=fecha_vencimiento,
            estatus=convenio.get('estatus', EstatusConvenio.PENDING)
        )
        convenios_db.append(convenio_db)

    try:
        db.add_all(convenios_db)
        db.commit()
        return JSONResponse(content={"mensaje": f"{len(convenios_db)} convenios subidos correctamente"})
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error al guardar en BD: {str(e)}")

# Crear un nuevo convenio
@router.post("/", response_model=ConvenioOut)
def create_convenio(convenio: ConvenioCreate, db: Session = Depends(get_db)):
    new_convenio = Convenio(
        compania_id=convenio.compania_id,
        titulo_compania=convenio.titulo_compania,
        tipo_de_convenio=convenio.tipo_de_convenio,
        descripcion=convenio.descripcion,
        beneficios=convenio.beneficios,
        fecha_firma=convenio.fecha_firma,
        fecha_vencimiento=convenio.fecha_vencimiento,
        estatus=convenio.estatus
    )

    try:
        db.add(new_convenio)
        db.commit()
        db.refresh(new_convenio)
        return new_convenio
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error al guardar en BD: {str(e)}")

# Obtener todos los convenios
@router.get("/", response_model=List[ConvenioOut])
def get_convenios(db: Session = Depends(get_db)):
    return db.query(Convenio).all()

# Obtener un convenio por ID
@router.get("/{convenio_id}", response_model=ConvenioOut)
def get_convenio(convenio_id: int, db: Session = Depends(get_db)):
    convenio = db.query(Convenio).filter(Convenio.convenio_id == convenio_id).first()
    if not convenio:
        raise HTTPException(status_code=404, detail="Convenio no encontrado")
    return convenio

# Eliminar un convenio
@router.delete("/{convenio_id}")
def delete_convenio(convenio_id: int, db: Session = Depends(get_db)):
    convenio = db.query(Convenio).filter(Convenio.convenio_id == convenio_id).first()
    if not convenio:
        raise HTTPException(status_code=404, detail="Convenio no encontrado")
    db.delete(convenio)
    db.commit()
    return {"detail": "Convenio eliminado"}

# Actualizar un convenio
@router.put("/{convenio_id}", response_model=ConvenioOut)
def update_convenio(convenio_id: int, updated_data: ConvenioUpdate, db: Session = Depends(get_db)):
    convenio = db.query(Convenio).filter(Convenio.convenio_id == convenio_id).first()
    if not convenio:
        raise HTTPException(status_code=404, detail="Convenio no encontrado")

    for key, value in updated_data.dict(exclude_unset=True).items():
        setattr(convenio, key, value)

    db.commit()
    db.refresh(convenio)
    return convenio

# Obtener convenios por estatus
@router.get("/estatus/{estatus}", response_model=List[ConvenioOut])
def get_convenios_by_status(estatus: EstatusConvenio, db: Session = Depends(get_db)):
    return db.query(Convenio).filter(Convenio.estatus == estatus).all()

# Obtener convenios por compañía
@router.get("/compania/{compania_id}", response_model=List[ConvenioOut])
def get_convenios_by_company(compania_id: int, db: Session = Depends(get_db)):
    return db.query(Convenio).filter(Convenio.compania_id == compania_id).all() 