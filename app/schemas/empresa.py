from pydantic import BaseModel
from datetime import date

class EmpresaBase(BaseModel):
    nombre_empresa: str
    nit: str
    sector: str
    fecha_convenio: date

class EmpresaCreate(EmpresaBase):
    pass

class EmpresaOut(EmpresaBase):
    empresa_id: int

    class Config:
        orm_mode = True
