from pydantic import BaseModel
from typing import Optional

# Esquema para crear una estadística
class EstadisticaCreate(BaseModel):
    categoria: str
    value: str
    descripcion: str

    class Config:
        orm_mode = True  # Habilita la conversión de objetos ORM a diccionarios
        
# Esquema para actualizar una estadística
class EstadisticaUpdate(BaseModel):
    categoria: Optional[str] = None
    value: Optional[str] = None
    descripcion: Optional[str] = None

    class Config:
        orm_mode = True  # Habilita la conversión de objetos ORM a diccionarios
        
# Esquema para la salida de datos de una estadística
class EstadisticaOut(EstadisticaCreate):
    estadistica_id: int

    class Config:
        orm_mode = True  # Habilita la conversión de objetos ORM a diccionarios
