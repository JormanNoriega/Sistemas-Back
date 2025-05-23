# app/schemas/impacto_social.py
from pydantic import BaseModel
from datetime import date
from typing import Optional
from app.models.Impacto_social import EstadoImpacto

# Esquema para crear un impacto social
class ImpactoSocialCreate(BaseModel):
    titulo: str
    beneficiarios: str
    ubicacion: str
    fecha_inicio: date
    fecha_final: date
    descripcion: str
    objetivos: str
    resultados: str
    participantes: str
    estado: EstadoImpacto = EstadoImpacto.PENDING

    class Config:
        orm_mode = True

# Esquema para actualizar un impacto social
class ImpactoSocialUpdate(BaseModel):
    titulo: Optional[str] = None
    beneficiarios: Optional[str] = None
    ubicacion: Optional[str] = None
    fecha_inicio: Optional[date] = None
    fecha_final: Optional[date] = None
    descripcion: Optional[str] = None
    objetivos: Optional[str] = None
    resultados: Optional[str] = None
    participantes: Optional[str] = None
    estado: Optional[EstadoImpacto] = None

    class Config:
        orm_mode = True

# Esquema para la salida de datos de un impacto social
class ImpactoSocialOut(ImpactoSocialCreate):
    impacto_id: int

    class Config:
        orm_mode = True
