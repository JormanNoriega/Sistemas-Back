# filepath: c:\Users\jorma\Desktop\Sistemas Back\app\models\publicaciones.py
from sqlalchemy import Column, Integer, String, Date
from app.database import Base

class Publicacion(Base):
    __tablename__ = "publicaciones"

    publicacion_id = Column(Integer, primary_key=True, index=True)
    titulo = Column(String, nullable=False)
    autores = Column(String, nullable=False)
    area = Column(String, nullable=False)
    fecha = Column(Date, nullable=False)
    enlace = Column(String, nullable=False)
    tipo = Column(String, nullable=False)