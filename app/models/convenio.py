from sqlalchemy import Column, Integer, String, Date, ForeignKey, Enum
from sqlalchemy.orm import relationship
from app.database import Base
import enum
from app.models.empresas_aliadas import Empresa

class EstatusConvenio(str, enum.Enum):
    ACTIVE = "active"
    EXPIRED = "expired"
    PENDING = "pending"

class TipoConvenio(str, enum.Enum):
    ACADEMIC = "academic"
    GOVERNMENT = "government"
    NETWORKING = "networking"
    RESEARCH = "research"
    INTERNATIONAL = "international"

class Convenio(Base):
    __tablename__ = "convenios"

    convenio_id = Column(Integer, primary_key=True, index=True)
    compania_id = Column(Integer, ForeignKey("empresas_aliadas.empresa_id"), nullable=False)
    titulo_compania = Column(String, nullable=False)
    tipo_de_convenio = Column(Enum(TipoConvenio), nullable=False)
    descripcion = Column(String, nullable=False)
    beneficios = Column(String, nullable=False)
    fecha = Column(Date, nullable=False)
    fecha_vencimiento = Column(Date, nullable=False)
    estatus = Column(Enum(EstatusConvenio), nullable=False, default=EstatusConvenio.PENDING)
    
    # Relación con la empresa
    empresa = relationship(Empresa, back_populates="convenios")