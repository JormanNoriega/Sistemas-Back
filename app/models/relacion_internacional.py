from sqlalchemy import Column, Integer, String, Date, Enum
from app.database import Base
import enum

class TipoRelacion(str, enum.Enum):
    MOBILITY = "mobility"
    AGREEMENT = "agreement"
    PROJECT = "project"
    NETWORK = "network"

class EstadoRelacion(str, enum.Enum):
    ACTIVE = "active"
    EXPIRED = "expired"
    PENDING = "pending"

class RelacionInternacional(Base):
    __tablename__ = "relaciones_internacionales"

    relacion_id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String, nullable=False)
    pais = Column(String, nullable=False)
    institucion = Column(String, nullable=False)
    tipo = Column(Enum(TipoRelacion), nullable=False)
    fecha_inicio = Column(Date, nullable=False)
    fecha_finalizacion = Column(Date, nullable=False)
    descripcion = Column(String, nullable=False)
    participantes = Column(String, nullable=False)
    resultados = Column(String, nullable=False)
    estado = Column(Enum(EstadoRelacion), nullable=False, default=EstadoRelacion.PENDING) 