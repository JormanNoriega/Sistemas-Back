from sqlalchemy import Column, Integer, String, Date
from sqlalchemy.orm import relationship
from app.database import Base

class Empresa(Base):
    __tablename__ = "empresas_aliadas"

    empresa_id = Column(Integer, primary_key=True, index=True)
    nombre_empresa = Column(String, nullable=False)
    nit = Column(String, nullable=False, unique=True)
    sector = Column(String, nullable=False)
    fecha_convenio = Column(Date, nullable=False)
