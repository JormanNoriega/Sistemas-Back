from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from fastapi.responses import JSONResponse
from typing import List
from datetime import datetime

from app.database import get_db
from app.models.egresado import Egresado, EstadoEmpleabilidad
from app.schemas.egresado import EgresadoCreate, EgresadoUpdate, EgresadoOut
from app.utils.csv_parser import parse_csv_egresados

router = APIRouter(prefix="/api/egresados", tags=["Egresados"])

# Subir egresados desde un archivo CSV
@router.post("/upload")
async def upload_csv(file: UploadFile = File(...), db: Session = Depends(get_db)):
    if not file.filename.endswith(".csv"):
        raise HTTPException(status_code=400, detail="Solo se permiten archivos CSV")

    try:
        egresados_data = parse_csv_egresados(file.file)
        # print(egresados_data[0].keys())
        # print(df.columns)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

    egresados_db = []
    for egresado in egresados_data:
        # Convertir la fecha de string a objeto date
        fecha_graduacion = datetime.strptime(egresado.get('año_graduacion'), '%Y-%m-%d').date()
        
        egresado_db = Egresado(
            nombre_completo=egresado.get('nombre_completo'),
            año_graduacion=fecha_graduacion,
            empleabilidad=egresado.get('empleabilidad'),
            email=egresado.get('email')
        )
        egresados_db.append(egresado_db)

    try:
        db.add_all(egresados_db)
        db.commit()
        return JSONResponse(content={"mensaje": f"{len(egresados_db)} egresados subidos correctamente"})
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error al guardar en BD: {str(e)}")

# Crear un nuevo egresado
@router.post("/", response_model=EgresadoOut)
def create_egresado(egresado: EgresadoCreate, db: Session = Depends(get_db)):
    # Verificar si ya existe un egresado con el mismo email
    existing_egresado = db.query(Egresado).filter(Egresado.email == egresado.email).first()
    if existing_egresado:
        raise HTTPException(status_code=400, detail="Ya existe un egresado con este email")

    new_egresado = Egresado(
        nombre_completo=egresado.nombre_completo,
        año_graduacion=egresado.año_graduacion,
        empleabilidad=egresado.empleabilidad,
        email=egresado.email
    )

    try:
        db.add(new_egresado)
        db.commit()
        db.refresh(new_egresado)
        return new_egresado
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error al guardar en BD: {str(e)}")

# Obtener todos los egresados
@router.get("/", response_model=List[EgresadoOut])
def get_egresados(db: Session = Depends(get_db)):
    return db.query(Egresado).all()

# Obtener un egresado por ID
@router.get("/{egresado_id}", response_model=EgresadoOut)
def get_egresado(egresado_id: int, db: Session = Depends(get_db)):
    egresado = db.query(Egresado).filter(Egresado.egresado_id == egresado_id).first()
    if not egresado:
        raise HTTPException(status_code=404, detail="Egresado no encontrado")
    return egresado

# Eliminar un egresado
@router.delete("/{egresado_id}")
def delete_egresado(egresado_id: int, db: Session = Depends(get_db)):
    egresado = db.query(Egresado).filter(Egresado.egresado_id == egresado_id).first()
    if not egresado:
        raise HTTPException(status_code=404, detail="Egresado no encontrado")
    db.delete(egresado)
    db.commit()
    return {"detail": "Egresado eliminado"}

# Actualizar un egresado
@router.put("/{egresado_id}", response_model=EgresadoOut)
def update_egresado(egresado_id: int, updated_data: EgresadoUpdate, db: Session = Depends(get_db)):
    egresado = db.query(Egresado).filter(Egresado.egresado_id == egresado_id).first()
    if not egresado:
        raise HTTPException(status_code=404, detail="Egresado no encontrado")

    for key, value in updated_data.dict(exclude_unset=True).items():
        setattr(egresado, key, value)

    db.commit()
    db.refresh(egresado)
    return egresado

# Obtener egresados por estado de empleabilidad
@router.get("/empleabilidad/{estado}", response_model=List[EgresadoOut])
def get_egresados_by_employment(estado: EstadoEmpleabilidad, db: Session = Depends(get_db)):
    return db.query(Egresado).filter(Egresado.empleabilidad == estado).all() 