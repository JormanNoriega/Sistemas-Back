from pydantic import BaseModel
from typing import Optional
from datetime import date
from app.models.convenio import EstatusConvenio, TipoConvenio

# Esquema básico para información de empresa
class EmpresaInfo(BaseModel):
    empresa_id: int
    nombre_empresa: str
    sector: str

    class Config:
        from_attributes = True

# Esquema para crear un convenio
class ConvenioCreate(BaseModel):
    compania_id: int
    titulo_compania: str
    tipo_de_convenio: TipoConvenio
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
    tipo_de_convenio: Optional[TipoConvenio] = None
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
    empresa: Optional[EmpresaInfo] = None

    class Config:
        from_attributes = True