from pydantic import BaseModel, EmailStr, validator
from typing import Optional
from datetime import date
from app.models.egresado import EstadoEmpleabilidad

# Esquema para crear un egresado
class EgresadoCreate(BaseModel):
    nombre_completo: str
    año_graduacion: date
    empleabilidad: str
    email: EmailStr

    @validator('empleabilidad')
    def normaliza_empleabilidad(cls, v):
        v = v.strip().capitalize()
        if v not in ["Empleado", "Desempleado", "Emprendedor"]:
            raise ValueError("Input should be 'Empleado', 'Desempleado' or 'Emprendedor'")
        return v

    class Config:
        from_attributes = True

# Esquema para actualizar un egresado
class EgresadoUpdate(BaseModel):
    nombre_completo: Optional[str] = None
    año_graduacion: Optional[date] = None
    empleabilidad: Optional[str] = None
    email: Optional[EmailStr] = None

    @validator('empleabilidad')
    def normaliza_empleabilidad(cls, v):
        if v is None:
            return v
        v = v.strip().capitalize()
        if v not in ["Empleado", "Desempleado", "Emprendedor"]:
            raise ValueError("Input should be 'Empleado', 'Desempleado' or 'Emprendedor'")
        return v

    class Config:
        from_attributes = True

# Esquema para la salida de datos de un egresado
class EgresadoOut(BaseModel):
    egresado_id: int
    nombre_completo: str
    año_graduacion: date
    empleabilidad: str
    email: EmailStr

    class Config:
        from_attributes = True 