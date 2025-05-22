from pydantic import BaseModel
from datetime import date
from typing import Optional

# Esquema para crear un evento
class EventoCreate(BaseModel):
    tipo: str
    fecha: date
    asistentes: int
    multimedia: str
    descripcion: str    
    
    class Config:
        from_attributes = True  # Habilita la conversión de objetos ORM a diccionarios

# Esquema para actualizar un evento
class EventoUpdate(BaseModel):
    tipo: Optional[str] = None
    fecha: Optional[date] = None
    asistentes: Optional[int] = None
    multimedia: Optional[str] = None
    descripcion: Optional[str] = None

    class Config:
        from_attributes = True  # Habilita la conversión de objetos ORM a diccionarios        

# Esquema para la salida de datos de un evento
class EventoOut(EventoCreate):
    evento_id: int

    class Config:
        from_attributes = True  # Habilita la conversión de objetos ORM a diccionarios        