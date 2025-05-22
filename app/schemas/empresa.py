# app/schemas/empresa.py
from pydantic import BaseModel
from datetime import date
from typing import Optional

# Esquema para crear una empresa
class EmpresaCreate(BaseModel):
    nombre_empresa: str
    nit: str
    sector: str
    fecha_convenio: date

    class Config:
        from_attributes = True  # Habilita la conversión de objetos ORM a diccionarios

# Esquema para actualizar una empresa
class EmpresaUpdate(BaseModel):
    nombre_empresa: Optional[str] = None
    nit: Optional[str] = None
    sector: Optional[str] = None
    fecha_convenio: Optional[date] = None

    class Config:
        from_attributes = True  # Habilita la conversión de objetos ORM a diccionarios

# Esquema para la salida de datos de una empresa
class EmpresaOut(EmpresaCreate):
    empresa_id: int

    class Config:
        from_attributes = True  # Habilita la conversión de objetos ORM a diccionarios
