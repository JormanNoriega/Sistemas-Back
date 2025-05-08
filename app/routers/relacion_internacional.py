from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from fastapi.responses import JSONResponse
from typing import List
from datetime import datetime

from app.database import get_db
from app.models.relacion_internacional import RelacionInternacional, TipoRelacion, EstadoRelacion
from app.schemas.relacion_internacional import RelacionInternacionalCreate, RelacionInternacionalUpdate, RelacionInternacionalOut
from app.utils.csv_parser import parse_csv_relaciones_internacionales

router = APIRouter(prefix="/api/relaciones-internacionales", tags=["Relaciones Internacionales"])

# Subir relaciones internacionales desde un archivo CSV
@router.post("/upload")
async def upload_csv(file: UploadFile = File(...), db: Session = Depends(get_db)):
    if not file.filename.endswith(".csv"):
        raise HTTPException(status_code=400, detail="Solo se permiten archivos CSV")

    try:
        relaciones_data = parse_csv_relaciones_internacionales(file.file)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

    relaciones_db = []
    for relacion in relaciones_data:
        fecha_inicio = datetime.strptime(relacion.get('fecha_inicio'), '%Y-%m-%d').date()
        fecha_finalizacion = datetime.strptime(relacion.get('fecha_finalizacion'), '%Y-%m-%d').date()
        relacion_db = RelacionInternacional(
            nombre=relacion.get('nombre'),
            pais=relacion.get('pais'),
            institucion=relacion.get('institucion'),
            tipo=relacion.get('tipo'),
            fecha_inicio=fecha_inicio,
            fecha_finalizacion=fecha_finalizacion,
            descripcion=relacion.get('descripcion'),
            participantes=relacion.get('participantes'),
            resultados=relacion.get('resultados'),
            estado=relacion.get('estado', EstadoRelacion.PENDING)
        )
        relaciones_db.append(relacion_db)

    try:
        db.add_all(relaciones_db)
        db.commit()
        return JSONResponse(content={"mensaje": f"{len(relaciones_db)} relaciones internacionales subidas correctamente"})
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error al guardar en BD: {str(e)}")

# Crear una nueva relación internacional
@router.post("/", response_model=RelacionInternacionalOut)
def create_relacion(relacion: RelacionInternacionalCreate, db: Session = Depends(get_db)):
    new_relacion = RelacionInternacional(
        nombre=relacion.nombre,
        pais=relacion.pais,
        institucion=relacion.institucion,
        tipo=relacion.tipo,
        fecha_inicio=relacion.fecha_inicio,
        fecha_finalizacion=relacion.fecha_finalizacion,
        descripcion=relacion.descripcion,
        participantes=relacion.participantes,
        resultados=relacion.resultados,
        estado=relacion.estado
    )

    try:
        db.add(new_relacion)
        db.commit()
        db.refresh(new_relacion)
        return new_relacion
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error al guardar en BD: {str(e)}")

# Obtener todas las relaciones internacionales
@router.get("/", response_model=List[RelacionInternacionalOut])
def get_relaciones(db: Session = Depends(get_db)):
    return db.query(RelacionInternacional).all()

# Obtener una relación internacional por ID
@router.get("/{relacion_id}", response_model=RelacionInternacionalOut)
def get_relacion(relacion_id: int, db: Session = Depends(get_db)):
    relacion = db.query(RelacionInternacional).filter(RelacionInternacional.relacion_id == relacion_id).first()
    if not relacion:
        raise HTTPException(status_code=404, detail="Relación internacional no encontrada")
    return relacion

# Eliminar una relación internacional
@router.delete("/{relacion_id}")
def delete_relacion(relacion_id: int, db: Session = Depends(get_db)):
    relacion = db.query(RelacionInternacional).filter(RelacionInternacional.relacion_id == relacion_id).first()
    if not relacion:
        raise HTTPException(status_code=404, detail="Relación internacional no encontrada")
    db.delete(relacion)
    db.commit()
    return {"detail": "Relación internacional eliminada"}

# Actualizar una relación internacional
@router.put("/{relacion_id}", response_model=RelacionInternacionalOut)
def update_relacion(relacion_id: int, updated_data: RelacionInternacionalUpdate, db: Session = Depends(get_db)):
    relacion = db.query(RelacionInternacional).filter(RelacionInternacional.relacion_id == relacion_id).first()
    if not relacion:
        raise HTTPException(status_code=404, detail="Relación internacional no encontrada")

    for key, value in updated_data.dict(exclude_unset=True).items():
        setattr(relacion, key, value)

    db.commit()
    db.refresh(relacion)
    return relacion

# Obtener relaciones por tipo
@router.get("/tipo/{tipo}", response_model=List[RelacionInternacionalOut])
def get_relaciones_by_type(tipo: TipoRelacion, db: Session = Depends(get_db)):
    return db.query(RelacionInternacional).filter(RelacionInternacional.tipo == tipo).all()

# Obtener relaciones por estado
@router.get("/estado/{estado}", response_model=List[RelacionInternacionalOut])
def get_relaciones_by_status(estado: EstadoRelacion, db: Session = Depends(get_db)):
    return db.query(RelacionInternacional).filter(RelacionInternacional.estado == estado).all()

# Obtener relaciones por país
@router.get("/pais/{pais}", response_model=List[RelacionInternacionalOut])
def get_relaciones_by_country(pais: str, db: Session = Depends(get_db)):
    return db.query(RelacionInternacional).filter(RelacionInternacional.pais == pais).all() 