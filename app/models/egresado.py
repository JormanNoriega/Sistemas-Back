from sqlalchemy import Column, Integer, String, Date, Enum
from app.database import Base
import enum
from pydantic import BaseModel, validator
from pydantic import EmailStr
from datetime import date

class EstadoEmpleabilidad(str, enum.Enum):
    EMPLEADO = "Empleado"
    DESEMPLEADO = "Desempleado"
    EMPRENDEDOR = "Emprendedor"

class Egresado(Base):
    __tablename__ = "egresados"

    egresado_id = Column(Integer, primary_key=True, index=True)
    nombre_completo = Column(String, nullable=False)
    año_graduacion = Column(Date, nullable=False)
    empleabilidad = Column(Enum(EstadoEmpleabilidad), nullable=False)
    email = Column(String, nullable=False, unique=True)
