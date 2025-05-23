from sqlalchemy import Column, Integer, String, Date, ForeignKey, Enum
from app.database import Base
import enum

class EstatusConvenio(str, enum.Enum):
    ACTIVE = "active"
    EXPIRED = "expired"
    PENDING = "pending"

class Convenio(Base):
    __tablename__ = "convenios"

    convenio_id = Column(Integer, primary_key=True, index=True)
    compania_id = Column(Integer, ForeignKey("empresas.empresa_id"), nullable=False)
    titulo_compania = Column(String, nullable=False)
    tipo_de_convenio = Column(String, nullable=False)
    descripcion = Column(String, nullable=False)
    beneficios = Column(String, nullable=False)
    fecha = Column(Date, nullable=False)
    fecha_vencimiento = Column(Date, nullable=False)
    estatus = Column(Enum(EstatusConvenio), nullable=False, default=EstatusConvenio.PENDING)