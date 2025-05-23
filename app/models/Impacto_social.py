from sqlalchemy import Column, Integer, String, Date, Enum
from app.database import Base
import enum

class EstadoImpacto(str, enum.Enum):
    ACTIVE = "activo"
    FINISHED = "finalizado"
    PENDING = "pendiente"

class ImpactoSocial(Base):
    __tablename__ = "impacto_social"

    impacto_id = Column(Integer, primary_key=True, index=True)
    titulo = Column(String, nullable=False)
    beneficiarios = Column(String, nullable=False)
    ubicacion = Column(String, nullable=False)
    fecha_inicio = Column(Date, nullable=False)
    fecha_final = Column(Date, nullable=False)
    descripcion = Column(String, nullable=False)
    objetivos = Column(String, nullable=False)
    resultados = Column(String, nullable=False)
    participantes = Column(String, nullable=False)
    estado = Column(Enum(EstadoImpacto), nullable=False, default=EstadoImpacto.PENDING)