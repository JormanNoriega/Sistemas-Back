from sqlalchemy import Column, Integer, String, Date, ForeignKey
from app.database import Base

class Proyectos(Base):
    __tablename__ = "proyectos"

    proyecto_id = Column(Integer, primary_key=True, index=True)
    titulo = Column(String, nullable=False)
    area_tematica = Column(String, nullable=False)
    fecha_inicio = Column(Date, nullable=False)
    
    