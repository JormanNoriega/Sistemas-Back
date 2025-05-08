from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from app.database import Base

class Eventos(Base):
    __tablename__ = "eventos"

    evento_id = Column(Integer, primary_key=True, index=True)
    tipo = Column(String, nullable=False)
    fecha = Column(DateTime, nullable=False)
    asistentes = Column(Integer, nullable=False)
    multimedia = Column(String, nullable=False)    
    descripcion = Column(String, nullable=False)
    