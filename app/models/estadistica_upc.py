from sqlalchemy import Column, Integer, String, Date, ForeignKey
from app.database import Base

class Estadisticas(Base):
    __tablename__ = "estadistica_upc"
    
    estadistica_id = Column(Integer, primary_key=True, index=True)
    categoria = Column(String, nullable=False)
    value = Column(String, nullable=False)
    descripcion = Column(String, nullable=False)
    