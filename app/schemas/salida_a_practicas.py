# app/schemas/salida_a_practicas.py
from pydantic import BaseModel
from datetime import date, time
from typing import Optional

# Esquema para crear una salida a prácticas
class SalidaPracticaCreate(BaseModel):
    fecha_salida: date
    lugar_destino: str
    responsable: str
    cantidad_estudiantes: int
    hora_salida: time
    hora_regreso: time
    observaciones: Optional[str] = None

    class Config:
        from_attributes = True

# Esquema para actualizar una salida a prácticas
class SalidaPracticaUpdate(BaseModel):
    fecha_salida: Optional[date] = None
    lugar_destino: Optional[str] = None
    responsable: Optional[str] = None
    cantidad_estudiantes: Optional[int] = None
    hora_salida: Optional[time] = None
    hora_regreso: Optional[time] = None
    observaciones: Optional[str] = None

    class Config:
        from_attributes = True

# Esquema para la salida de datos de una salida a prácticas
class SalidaPracticaOut(SalidaPracticaCreate):
    id_salida_practica: int

    class Config:
        from_attributes = True
