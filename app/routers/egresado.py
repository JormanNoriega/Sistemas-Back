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
        # Obtener egresados válidos y duplicados del CSV
        egresados_validos, egresados_duplicados_csv = parse_csv_egresados(file.file)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

    egresados_db = []
    registros_con_error = []
    registros_duplicados_bd = []
    
    for egresado in egresados_validos:
        try:
            # Convertir la fecha de string a objeto date
            fecha_graduacion = datetime.strptime(egresado.get('año_graduacion'), '%Y-%m-%d').date()
            
            # Verificar si ya existe un egresado con el mismo email o nombre
            existing_egresado = db.query(Egresado).filter(
                (Egresado.email == egresado.get('email')) | 
                (Egresado.nombre_completo == egresado.get('nombre_completo'))
            ).first()
            
            if existing_egresado:
                # El egresado ya existe en la BD
                registros_duplicados_bd.append({
                    "nombre_completo": egresado.get('nombre_completo'),
                    "email": egresado.get('email'),
                    "error": f"Ya existe en la base de datos (ID: {existing_egresado.egresado_id})"
                })
            else:
                # El egresado no existe, se puede agregar
                egresado_db = Egresado(
                    nombre_completo=egresado.get('nombre_completo'),
                    año_graduacion=fecha_graduacion,
                    empleabilidad=egresado.get('empleabilidad'),
                    email=egresado.get('email')
                )
                egresados_db.append(egresado_db)
                
        except Exception as e:
            # Si hay error en el procesamiento de algún egresado, lo agregamos al informe
            registros_con_error.append({
                "nombre_completo": egresado.get('nombre_completo'),
                "email": egresado.get('email'),
                "error": f"Error de formato: {str(e)}"
            })

    try:
        if egresados_db:
            db.add_all(egresados_db)
            db.commit()
        
        # Combinar todos los registros con problemas
        todos_registros_problematicos = egresados_duplicados_csv + registros_duplicados_bd + registros_con_error
        
        return JSONResponse(content={
            "mensaje": f"{len(egresados_db)} egresados subidos correctamente",
            "total_registros": len(egresados_validos) + len(egresados_duplicados_csv),
            "registros_validos": len(egresados_db),
            "registros_duplicados_csv": len(egresados_duplicados_csv),
            "registros_duplicados_bd": len(registros_duplicados_bd),
            "registros_con_errores_formato": len(registros_con_error),
            "total_problemas": len(todos_registros_problematicos),
            "detalle_problemas": todos_registros_problematicos
        })
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