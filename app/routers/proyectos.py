from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from fastapi.responses import JSONResponse
from typing import List

from app.database import get_db
from app.models.proyectos import Proyectos
from app.schemas.proyectos import ProyectoCreate, ProyectoUpdate, ProyectoOut
from app.utils.csv_parser import parse_csv_proyectos  

router = APIRouter(prefix="/api/proyectos", tags=["Proyectos"])

# Subir proyectos desde un archivo CSV
@router.post("/upload_csv")
async def upload_csv(file: UploadFile = File(...), db: Session = Depends(get_db)):
    """
    Subir proyectos desde un archivo CSV.
    """
    if not file.filename.endswith(".csv"):
        raise HTTPException(status_code=400, detail="Solo se permiten archivos CSV")

    try:
        # Obtener proyectos válidos y duplicados del CSV
        proyectos_validos, proyectos_duplicados_csv = parse_csv_proyectos(file.file)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

    proyectos_db = []
    registros_duplicados_bd = []
    
    for proyecto in proyectos_validos:
        # Verificar si ya existe un proyecto con el mismo título y área temática
        existing_proyecto = db.query(Proyectos).filter(
            (Proyectos.titulo == proyecto.get('titulo')) & 
            (Proyectos.area_tematica == proyecto.get('area_tematica'))
        ).first()
        
        if existing_proyecto:
            # El proyecto ya existe en la BD
            registros_duplicados_bd.append({
                "titulo": proyecto.get('titulo'),
                "area_tematica": proyecto.get('area_tematica'),
                "error": f"Ya existe en la base de datos (ID: {existing_proyecto.proyecto_id})"
            })
        else:
            # El proyecto no existe, se puede agregar
            proyecto_db = Proyectos(
                titulo=proyecto.get('titulo'),
                area_tematica=proyecto.get('area_tematica'),
                fecha_inicio=proyecto.get('fecha_inicio'),
            )
            proyectos_db.append(proyecto_db)

    try:
        if proyectos_db:
            db.add_all(proyectos_db)
            db.commit()
            
        # Combinar todos los registros con problemas
        todos_registros_problematicos = proyectos_duplicados_csv + registros_duplicados_bd
        
        return JSONResponse(content={
            "mensaje": f"{len(proyectos_db)} proyectos subidos correctamente",
            "total_registros": len(proyectos_validos) + len(proyectos_duplicados_csv),
            "registros_validos": len(proyectos_db),
            "registros_duplicados_csv": len(proyectos_duplicados_csv),
            "registros_duplicados_bd": len(registros_duplicados_bd),
            "total_problemas": len(todos_registros_problematicos),
            "detalle_problemas": todos_registros_problematicos
        })
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error al guardar en BD: {str(e)}")

# Crear un nuevo proyecto
@router.post("/", response_model=ProyectoOut)
def create_proyecto(proyecto: ProyectoCreate, db: Session = Depends(get_db)):
    # Verificar si ya existe un proyecto con el mismo título
    existing_proyecto = db.query(Proyectos).filter(Proyectos.titulo == proyecto.titulo).first()
    if existing_proyecto:
        raise HTTPException(status_code=400, detail="Ya existe un proyecto con este título")

    # Crear el objeto Proyectos con los datos recibidos
    new_proyecto = Proyectos(
        titulo=proyecto.titulo,
        area_tematica=proyecto.area_tematica,
        fecha_inicio=proyecto.fecha_inicio
    )

    try:
        # Agregar a la base de datos
        db.add(new_proyecto)
        db.commit()
        db.refresh(new_proyecto)  # Refrescar el objeto para obtener el ID generado
        return new_proyecto  # Retornar el nuevo proyecto creado
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error al guardar en BD: {str(e)}")
    
# Obtener todos los proyectos
@router.get("/", response_model=List[ProyectoOut])
def get_proyectos(db: Session = Depends(get_db)):
    proyectos = db.query(Proyectos).all()
    return proyectos

# Obtener un proyecto por ID
@router.get("/{proyecto_id}", response_model=ProyectoOut)
def get_proyecto(proyecto_id: int, db: Session = Depends(get_db)):
    proyecto = db.query(Proyectos).filter(Proyectos.id == proyecto_id).first()
    if not proyecto:
        raise HTTPException(status_code=404, detail="Proyecto no encontrado")
    return proyecto

# Eliminar un proyecto
@router.delete("/{proyecto_id}")
def delete_proyecto(proyecto_id: int, db: Session = Depends(get_db)):
    proyecto = db.query(Proyectos).filter(Proyectos.id == proyecto_id).first()
    if not proyecto:
        raise HTTPException(status_code=404, detail="Proyecto no encontrado")
    
    try:
        db.delete(proyecto)
        db.commit()
        return JSONResponse(content={"mensaje": "Proyecto eliminado correctamente"})
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error al eliminar el proyecto: {str(e)}")
    
# Actualizar un proyecto
@router.put("/{proyecto_id}", response_model=ProyectoOut)
def update_proyecto(proyecto_id: int, proyecto: ProyectoUpdate, db: Session = Depends(get_db)):
    existing_proyecto = db.query(Proyectos).filter(Proyectos.id == proyecto_id).first()
    if not existing_proyecto:
        raise HTTPException(status_code=404, detail="Proyecto no encontrado")
    
    # Actualizar los campos del proyecto
    for key, value in proyecto.dict(exclude_unset=True).items():
        setattr(existing_proyecto, key, value)

    try:
        db.commit()
        db.refresh(existing_proyecto)  # Refrescar el objeto para obtener los datos actualizados
        return existing_proyecto  # Retornar el proyecto actualizado
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error al actualizar el proyecto: {str(e)}")   
        