from pydantic import BaseModel
from typing import Optional
from datetime import date
from app.models.relacion_internacional import TipoRelacion, EstadoRelacion

# Esquema para crear una relación internacional
class RelacionInternacionalCreate(BaseModel):
    nombre: str
    pais: str
    institucion: str
    tipo: TipoRelacion
    fecha_inicio: date
    fecha_finalizacion: date
    descripcion: str
    participantes: str
    resultados: str
    estado: EstadoRelacion = EstadoRelacion.PENDING

    class Config:
        from_attributes = True

# Esquema para actualizar una relación internacional
class RelacionInternacionalUpdate(BaseModel):
    nombre: Optional[str] = None
    pais: Optional[str] = None
    institucion: Optional[str] = None
    tipo: Optional[TipoRelacion] = None
    fecha_inicio: Optional[date] = None
    fecha_finalizacion: Optional[date] = None
    descripcion: Optional[str] = None
    participantes: Optional[str] = None
    resultados: Optional[str] = None
    estado: Optional[EstadoRelacion] = None

    class Config:
        from_attributes = True

# Esquema para la salida de datos de una relación internacional
class RelacionInternacionalOut(RelacionInternacionalCreate):
    relacion_id: int

    class Config:
        from_attributes = True 