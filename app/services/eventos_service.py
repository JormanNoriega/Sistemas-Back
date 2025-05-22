from app.models.eventos import Eventos
from app.schemas.eventos import EventoCreate, EventoUpdate
from app.utils.csv_parser import parse_csv_eventos
from fastapi import HTTPException, UploadFile
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from typing import List

async def procesar_csv_eventos(file: UploadFile, db: Session):
    try:
        eventos_validos, eventos_duplicados_csv = parse_csv_eventos(file.file)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

    eventos_db = []
    registros_duplicados_bd = []

    for evento in eventos_validos:
        existing_evento = db.query(Eventos).filter(
            (Eventos.tipo == evento.get('tipo')) &
            (Eventos.fecha == evento.get('fecha')) &
            (Eventos.descripcion == evento.get('descripcion'))
        ).first()
        if existing_evento:
            registros_duplicados_bd.append({
                "tipo": evento.get('tipo'),
                "fecha": str(evento.get('fecha')),
                "descripcion": evento.get('descripcion'),
                "error": f"Ya existe en la base de datos (ID: {existing_evento.evento_id})"
            })
        else:
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

def crear_evento(evento: EventoCreate, db: Session) -> Eventos:
    new_evento = Eventos(**evento.dict())
    try:
        db.add(new_evento)
        db.commit()
        db.refresh(new_evento)
        return new_evento
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error al guardar en BD: {str(e)}")

def obtener_eventos(db: Session) -> List[Eventos]:
    return db.query(Eventos).all()

def obtener_evento_por_id(evento_id: int, db: Session) -> Eventos:
    evento = db.query(Eventos).filter(Eventos.evento_id == evento_id).first()
    if not evento:
        raise HTTPException(status_code=404, detail="Evento no encontrado")
    return evento

def actualizar_evento(evento_id: int, updated_data: EventoUpdate, db: Session) -> Eventos:
    evento = obtener_evento_por_id(evento_id, db)
    for key, value in updated_data.dict(exclude_unset=True).items():
        setattr(evento, key, value)
    db.commit()
    db.refresh(evento)
    return evento

def eliminar_evento(evento_id: int, db: Session):
    evento = obtener_evento_por_id(evento_id, db)
    db.delete(evento)
    db.commit()
    return {"mensaje": "Evento eliminado correctamente"}