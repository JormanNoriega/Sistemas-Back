from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from fastapi.responses import JSONResponse
from typing import List

from app.database import get_db
from app.models.eventos import Eventos
from app.schemas.eventos import EventoCreate, EventoUpdate, EventoOut
from app.utils.csv_parser import parse_csv_eventos

router = APIRouter(prefix="/api/eventos", tags=["Eventos"])

# Subir eventos desde un archivo CSV
@router.post("/upload_csv")
async def upload_csv(file: UploadFile = File(...), db: Session = Depends(get_db)):
    if not file.filename.endswith(".csv"):
        raise HTTPException(status_code=400, detail="Solo se permiten archivos CSV")

    try:
        # Obtener eventos válidos y duplicados del CSV
        eventos_validos, eventos_duplicados_csv = parse_csv_eventos(file.file)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

    eventos_db = []
    registros_duplicados_bd = []
    
    for evento in eventos_validos:
        # Verificar si ya existe un evento con el mismo tipo, fecha y descripción
        existing_evento = db.query(Eventos).filter(
            (Eventos.tipo == evento.get('tipo')) & 
            (Eventos.fecha == evento.get('fecha')) & 
            (Eventos.descripcion == evento.get('descripcion'))
        ).first()
        
        if existing_evento:
            # El evento ya existe en la BD
            registros_duplicados_bd.append({
                "tipo": evento.get('tipo'),
                "fecha": str(evento.get('fecha')),
                "descripcion": evento.get('descripcion'),
                "error": f"Ya existe en la base de datos (ID: {existing_evento.evento_id})"
            })
        else:
            # El evento no existe, se puede agregar
            evento_db = Eventos(
                tipo=evento.get('tipo'),
                fecha=evento.get('fecha'),
                asistentes=evento.get('asistentes'),
                multimedia=evento.get('multimedia'),
                descripcion=evento.get('descripcion'),
            )
            eventos_db.append(evento_db)

    try:
        if eventos_db:
            db.add_all(eventos_db)
            db.commit()
        
        # Combinar todos los registros con problemas
        todos_registros_problematicos = eventos_duplicados_csv + registros_duplicados_bd
        
        return JSONResponse(content={
            "mensaje": f"{len(eventos_db)} eventos subidos correctamente",
            "total_registros": len(eventos_validos) + len(eventos_duplicados_csv),
            "registros_validos": len(eventos_db),
            "registros_duplicados_csv": len(eventos_duplicados_csv),
            "registros_duplicados_bd": len(registros_duplicados_bd),
            "total_problemas": len(todos_registros_problematicos),
            "detalle_problemas": todos_registros_problematicos
        })
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error al guardar en BD: {str(e)}")

# Crear un nuevo evento
@router.post("/", response_model=EventoOut)
def create_evento(evento: EventoCreate, db: Session = Depends(get_db)):
    # Crear el objeto Eventos con los datos recibidos
    new_evento = Eventos(
        tipo=evento.tipo,
        fecha=evento.fecha,
        asistentes=evento.asistentes,
        multimedia=evento.multimedia,
        descripcion=evento.descripcion
    )

    try:
        # Agregar a la base de datos
        db.add(new_evento)
        db.commit()
        db.refresh(new_evento)  # Refrescar el objeto para obtener el ID generado
        return new_evento  # Retornar el nuevo evento creado
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error al guardar en BD: {str(e)}")

# Obtener todos los eventos
@router.get("/", response_model=List[EventoOut])
def get_eventos(db: Session = Depends(get_db)):
    eventos = db.query(Eventos).all()
    return eventos

# Obtener un evento por ID
@router.get("/{evento_id}", response_model=EventoOut)
def get_evento(evento_id: int, db: Session = Depends(get_db)):
    evento = db.query(Eventos).filter(Eventos.evento_id == evento_id).first()
    if not evento:
        raise HTTPException(status_code=404, detail="Evento no encontrado")
    return evento

# Eliminar un evento
@router.delete("/{evento_id}")
def delete_evento(evento_id: int, db: Session = Depends(get_db)):
    evento = db.query(Eventos).filter(Eventos.evento_id == evento_id).first()
    if not evento:
        raise HTTPException(status_code=404, detail="Evento no encontrado")
    
    try:
        db.delete(evento)
        db.commit()
        return JSONResponse(content={"mensaje": "Evento eliminado correctamente"})
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error al eliminar el evento: {str(e)}")

# Actualizar un evento
@router.put("/{evento_id}", response_model=EventoOut)
def update_evento(evento_id: int, evento: EventoUpdate, db: Session = Depends(get_db)):
    existing_evento = db.query(Eventos).filter(Eventos.evento_id == evento_id).first()
    if not existing_evento:
        raise HTTPException(status_code=404, detail="Evento no encontrado")
    
    # Actualizar los campos del evento
    for key, value in evento.dict(exclude_unset=True).items():
        setattr(existing_evento, key, value)

    try:
        db.commit()
        db.refresh(existing_evento)  # Refrescar el objeto para obtener los datos actualizados
        return existing_evento  # Retornar el evento actualizado
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error al actualizar el evento: {str(e)}")