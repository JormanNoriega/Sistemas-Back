from pydantic import BaseModel
from typing import Optional
from datetime import date
from app.models.convenio import EstatusConvenio

# Esquema para crear un convenio
class ConvenioCreate(BaseModel):
    compania_id: int
    titulo_compania: str
    tipo_de_convenio: str
    descripcion: str
    beneficios: str
    fecha: date
    fecha_vencimiento: date
    estatus: EstatusConvenio = EstatusConvenio.PENDING

    class Config:
        from_attributes = True

# Esquema para actualizar un convenio
class ConvenioUpdate(BaseModel):
    compania_id: Optional[int] = None
    titulo_compania: Optional[str] = None
    tipo_de_convenio: Optional[str] = None
    descripcion: Optional[str] = None
    beneficios: Optional[str] = None
    fecha: Optional[date] = None
    fecha_vencimiento: Optional[date] = None
    estatus: Optional[EstatusConvenio] = None

    class Config:
        from_attributes = True

# Esquema para la salida de datos de un convenio
class ConvenioOut(ConvenioCreate):
    convenio_id: int

    class Config:
        from_attributes = True 