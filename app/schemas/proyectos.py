from pydantic import BaseModel
from datetime import date
from typing import Optional

# Esquema para crear un proyecto
class ProyectoCreate(BaseModel):
    titulo: str
    area_tematica: str
    fecha_inicio: date
    
    class Config:
        from_attributes = True  # Habilita la conversión de objetos ORM a diccionarios
        
# Esquema para actualizar un proyecto
class ProyectoUpdate(BaseModel):
    titulo: Optional[str] = None
    area_tematica: Optional[str] = None
    fecha_inicio: Optional[date] = None

    class Config:
        from_attributes = True  # Habilita la conversión de objetos ORM a diccionarios

# Esquema para la salida de datos de un proyecto       
class ProyectoOut(ProyectoCreate):
    proyecto_id: int

    class Config:
        from_attributes = True  # Habilita la conversión de objetos ORM a diccionarios        