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
        # Obtener convenios válidos y duplicados del CSV
        convenios_validos, convenios_duplicados_csv = parse_csv_convenios(file.file)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

    convenios_db = []
    registros_con_error = []
    registros_duplicados_bd = []
    
    for convenio in convenios_validos:
        try:
            # Convertir fechas
            fecha_firma = datetime.strptime(convenio.get('fecha_firma'), '%Y-%m-%d').date()
            fecha_vencimiento = datetime.strptime(convenio.get('fecha_vencimiento'), '%Y-%m-%d').date()
            
            # Verificar si ya existe un convenio con la misma compañía y título
            existing_convenio = db.query(Convenio).filter(
                (Convenio.compañia_id == convenio.get('compania_id')) & 
                (Convenio.titulo_compañia == convenio.get('titulo_compania'))
            ).first()
            
            if existing_convenio:
                # El convenio ya existe en la BD
                registros_duplicados_bd.append({
                    "compania_id": convenio.get('compania_id'),
                    "titulo_compania": convenio.get('titulo_compania'),
                    "error": f"Ya existe en la base de datos (ID: {existing_convenio.convenio_id})"
                })
            else:
                # El convenio no existe, se puede agregar
                # Nota: Usando los nombres de columna correctos según el modelo
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
            # Si hay error en el procesamiento de algún convenio, lo agregamos al informe
            registros_con_error.append({
                "compania_id": convenio.get('compania_id'),
                "titulo_compania": convenio.get('titulo_compania'),
                "error": f"Error de formato: {str(e)}"
            })

    try:
        if convenios_db:
            db.add_all(convenios_db)
            db.commit()
        
        # Combinar todos los registros con problemas
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