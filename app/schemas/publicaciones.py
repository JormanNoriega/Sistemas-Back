from pydantic import BaseModel
from typing import Optional
from datetime import date

# Esquema para crear una publicación
class PublicacionCreate(BaseModel):
    titulo: str
    autores: str
    area: str
    fecha: date
    enlace: str
    tipo: str

    class Config:
        from_attributes = True

# Esquema para actualizar una publicación
class PublicacionUpdate(BaseModel):
    titulo: Optional[str] = None
    autores: Optional[str] = None
    area: Optional[str] = None
    fecha: Optional[date] = None
    enlace: Optional[str] = None
    tipo: Optional[str] = None

    class Config:
        from_attributes = True

# Esquema para la salida de datos de una publicación
class PublicacionOut(PublicacionCreate):
    publicacion_id: int

    class Config:
        from_attributes = True
