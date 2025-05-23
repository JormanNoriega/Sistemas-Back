from sqlalchemy import Column, Integer, String, Date, Time
from app.database import Base

class SalidaPractica(Base):
    __tablename__ = "salidas_practicas"

    id_salida_practica = Column(Integer, primary_key=True, index=True)
    fecha_salida = Column(Date, nullable=False)
    lugar_destino = Column(String, nullable=False)
    responsable = Column(String, nullable=False)
    cantidad_estudiantes = Column(Integer, nullable=False)
    hora_salida = Column(Time, nullable=False)
    hora_regreso = Column(Time, nullable=False)
    observaciones = Column(String, nullable=True)