# app/routers/empresa.py
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from fastapi.responses import JSONResponse
from typing import List

from app.database import get_db
from app.models.empresa import Empresa
from app.schemas.empresa import EmpresaCreate, EmpresaUpdate, EmpresaOut
from app.utils.csv_parser import parse_csv  # Suponiendo que tienes un parser CSV en utils

router = APIRouter(prefix="/api/empresas", tags=["Empresas"])

# Subir empresas desde un archivo CSV
@router.post("/")
async def upload_csv(file: UploadFile = File(...), db: Session = Depends(get_db)):
    if not file.filename.endswith(".csv"):
        raise HTTPException(status_code=400, detail="Solo se permiten archivos CSV")

    try:
        empresas_data = parse_csv(file.file)  # Se supone que parse_csv devuelve una lista de diccionarios
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

    empresas_db = []
    for empresa in empresas_data:
        empresa_db = Empresa(
            nombre_empresa=empresa.get('nombre_empresa'),
            nit=empresa.get('nit'),
            sector=empresa.get('sector'),
            fecha_convenio=empresa.get('fecha_convenio'),
        )
        empresas_db.append(empresa_db)

    try:
        db.add_all(empresas_db)
        db.commit()
        return JSONResponse(content={"mensaje": f"{len(empresas_db)} empresas subidas correctamente"})
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error al guardar en BD: {str(e)}")

# Crear una nueva empresa
@router.post("/", response_model=EmpresaOut)
def create_empresa(empresa: EmpresaCreate, db: Session = Depends(get_db)):
    # Verificar si ya existe una empresa con el mismo NIT
    existing_empresa = db.query(Empresa).filter(Empresa.nit == empresa.nit).first()
    if existing_empresa:
        raise HTTPException(status_code=400, detail="Ya existe una empresa con este NIT")

    # Crear el objeto Empresa con los datos recibidos
    new_empresa = Empresa(
        nombre_empresa=empresa.nombre_empresa,
        nit=empresa.nit,
        sector=empresa.sector,
        fecha_convenio=empresa.fecha_convenio
    )

    try:
        # Agregar a la base de datos
        db.add(new_empresa)
        db.commit()
        db.refresh(new_empresa)  # Obtener los datos más recientes de la empresa creada
        return new_empresa
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error al guardar en BD: {str(e)}")

# Obtener todas las empresas
@router.get("/", response_model=List[EmpresaOut])
def get_empresas(db: Session = Depends(get_db)):
    return db.query(Empresa).all()

# Obtener una empresa por ID
@router.get("/{empresa_id}", response_model=EmpresaOut)
def get_empresa(empresa_id: int, db: Session = Depends(get_db)):
    empresa = db.query(Empresa).filter(Empresa.empresa_id == empresa_id).first()
    if not empresa:
        raise HTTPException(status_code=404, detail="Empresa no encontrada")
    return empresa

# Eliminar una empresa
@router.delete("/{empresa_id}")
def delete_empresa(empresa_id: int, db: Session = Depends(get_db)):
    empresa = db.query(Empresa).filter(Empresa.empresa_id == empresa_id).first()
    if not empresa:
        raise HTTPException(status_code=404, detail="Empresa no encontrada")
    db.delete(empresa)
    db.commit()
    return {"detail": "Empresa eliminada"}

# Actualizar una empresa
@router.put("/{empresa_id}", response_model=EmpresaOut)
def update_empresa(empresa_id: int, updated_data: EmpresaUpdate, db: Session = Depends(get_db)):
    empresa = db.query(Empresa).filter(Empresa.empresa_id == empresa_id).first()
    if not empresa:
        raise HTTPException(status_code=404, detail="Empresa no encontrada")

    for key, value in updated_data.dict(exclude_unset=True).items():
        setattr(empresa, key, value)

    db.commit()
    db.refresh(empresa)
    return empresa
# app/routers/empresa.py
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from fastapi.responses import JSONResponse
from typing import List

from app.database import get_db
from app.models.empresa import Empresa
from app.schemas.empresa import EmpresaCreate, EmpresaUpdate, EmpresaOut
from app.utils.csv_parser import parse_csv  # Suponiendo que tienes un parser CSV en utils

router = APIRouter(prefix="/api/empresas", tags=["Empresas"])

# Subir empresas desde un archivo CSV
@router.post("/")
async def upload_csv(file: UploadFile = File(...), db: Session = Depends(get_db)):
    if not file.filename.endswith(".csv"):
        raise HTTPException(status_code=400, detail="Solo se permiten archivos CSV")

    try:
        empresas_data = parse_csv(file.file)  # Se supone que parse_csv devuelve una lista de diccionarios
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

    empresas_db = []
    for empresa in empresas_data:
        empresa_db = Empresa(
            nombre_empresa=empresa.get('nombre_empresa'),
            nit=empresa.get('nit'),
            sector=empresa.get('sector'),
            fecha_convenio=empresa.get('fecha_convenio'),
        )
        empresas_db.append(empresa_db)

    try:
        db.add_all(empresas_db)
        db.commit()
        return JSONResponse(content={"mensaje": f"{len(empresas_db)} empresas subidas correctamente"})
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error al guardar en BD: {str(e)}")

# Crear una nueva empresa
@router.post("/", response_model=EmpresaOut)
def create_empresa(empresa: EmpresaCreate, db: Session = Depends(get_db)):
    # Verificar si ya existe una empresa con el mismo NIT
    existing_empresa = db.query(Empresa).filter(Empresa.nit == empresa.nit).first()
    if existing_empresa:
        raise HTTPException(status_code=400, detail="Ya existe una empresa con este NIT")

    # Crear el objeto Empresa con los datos recibidos
    new_empresa = Empresa(
        nombre_empresa=empresa.nombre_empresa,
        nit=empresa.nit,
        sector=empresa.sector,
        fecha_convenio=empresa.fecha_convenio
    )

    try:
        # Agregar a la base de datos
        db.add(new_empresa)
        db.commit()
        db.refresh(new_empresa)  # Obtener los datos más recientes de la empresa creada
        return new_empresa
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error al guardar en BD: {str(e)}")

# Obtener todas las empresas
@router.get("/", response_model=List[EmpresaOut])
def get_empresas(db: Session = Depends(get_db)):
    return db.query(Empresa).all()

# Obtener una empresa por ID
@router.get("/{empresa_id}", response_model=EmpresaOut)
def get_empresa(empresa_id: int, db: Session = Depends(get_db)):
    empresa = db.query(Empresa).filter(Empresa.empresa_id == empresa_id).first()
    if not empresa:
        raise HTTPException(status_code=404, detail="Empresa no encontrada")
    return empresa

# Eliminar una empresa
@router.delete("/{empresa_id}")
def delete_empresa(empresa_id: int, db: Session = Depends(get_db)):
    empresa = db.query(Empresa).filter(Empresa.empresa_id == empresa_id).first()
    if not empresa:
        raise HTTPException(status_code=404, detail="Empresa no encontrada")
    db.delete(empresa)
    db.commit()
    return {"detail": "Empresa eliminada"}

# Actualizar una empresa
@router.put("/{empresa_id}", response_model=EmpresaOut)
def update_empresa(empresa_id: int, updated_data: EmpresaUpdate, db: Session = Depends(get_db)):
    empresa = db.query(Empresa).filter(Empresa.empresa_id == empresa_id).first()
    if not empresa:
        raise HTTPException(status_code=404, detail="Empresa no encontrada")

    for key, value in updated_data.dict(exclude_unset=True).items():
        setattr(empresa, key, value)

    db.commit()
    db.refresh(empresa)
    return empresa
# app/routers/empresa.py
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from fastapi.responses import JSONResponse
from typing import List

from app.database import get_db
from app.models.empresa import Empresa
from app.schemas.empresa import EmpresaCreate, EmpresaUpdate, EmpresaOut
from app.utils.csv_parser import parse_csv  # Suponiendo que tienes un parser CSV en utils

router = APIRouter(prefix="/api/empresas", tags=["Empresas"])

# Subir empresas desde un archivo CSV
@router.post("/")
async def upload_csv(file: UploadFile = File(...), db: Session = Depends(get_db)):
    if not file.filename.endswith(".csv"):
        raise HTTPException(status_code=400, detail="Solo se permiten archivos CSV")

    try:
        empresas_data = parse_csv(file.file)  # Se supone que parse_csv devuelve una lista de diccionarios
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

    empresas_db = []
    for empresa in empresas_data:
        empresa_db = Empresa(
            nombre_empresa=empresa.get('nombre_empresa'),
            nit=empresa.get('nit'),
            sector=empresa.get('sector'),
            fecha_convenio=empresa.get('fecha_convenio'),
        )
        empresas_db.append(empresa_db)

    try:
        db.add_all(empresas_db)
        db.commit()
        return JSONResponse(content={"mensaje": f"{len(empresas_db)} empresas subidas correctamente"})
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error al guardar en BD: {str(e)}")

# Crear una nueva empresa
@router.post("/", response_model=EmpresaOut)
def create_empresa(empresa: EmpresaCreate, db: Session = Depends(get_db)):
    # Verificar si ya existe una empresa con el mismo NIT
    existing_empresa = db.query(Empresa).filter(Empresa.nit == empresa.nit).first()
    if existing_empresa:
        raise HTTPException(status_code=400, detail="Ya existe una empresa con este NIT")

    # Crear el objeto Empresa con los datos recibidos
    new_empresa = Empresa(
        nombre_empresa=empresa.nombre_empresa,
        nit=empresa.nit,
        sector=empresa.sector,
        fecha_convenio=empresa.fecha_convenio
    )

    try:
        # Agregar a la base de datos
        db.add(new_empresa)
        db.commit()
        db.refresh(new_empresa)  # Obtener los datos más recientes de la empresa creada
        return new_empresa
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error al guardar en BD: {str(e)}")

# Obtener todas las empresas
@router.get("/", response_model=List[EmpresaOut])
def get_empresas(db: Session = Depends(get_db)):
    return db.query(Empresa).all()

# Obtener una empresa por ID
@router.get("/{empresa_id}", response_model=EmpresaOut)
def get_empresa(empresa_id: int, db: Session = Depends(get_db)):
    empresa = db.query(Empresa).filter(Empresa.empresa_id == empresa_id).first()
    if not empresa:
        raise HTTPException(status_code=404, detail="Empresa no encontrada")
    return empresa

# Eliminar una empresa
@router.delete("/{empresa_id}")
def delete_empresa(empresa_id: int, db: Session = Depends(get_db)):
    empresa = db.query(Empresa).filter(Empresa.empresa_id == empresa_id).first()
    if not empresa:
        raise HTTPException(status_code=404, detail="Empresa no encontrada")
    db.delete(empresa)
    db.commit()
    return {"detail": "Empresa eliminada"}

# Actualizar una empresa
@router.put("/{empresa_id}", response_model=EmpresaOut)
def update_empresa(empresa_id: int, updated_data: EmpresaUpdate, db: Session = Depends(get_db)):
    empresa = db.query(Empresa).filter(Empresa.empresa_id == empresa_id).first()
    if not empresa:
        raise HTTPException(status_code=404, detail="Empresa no encontrada")

    for key, value in updated_data.dict(exclude_unset=True).items():
        setattr(empresa, key, value)

    db.commit()
    db.refresh(empresa)
    return empresa
