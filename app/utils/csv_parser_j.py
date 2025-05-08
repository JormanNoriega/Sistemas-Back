import pandas as pd
from datetime import datetime

def parse_csv_proyectos(file) -> list :
    df = pd.read_csv(file, encoding="utf-8-sig")
    df.columns = df.columns.str.strip().str.lower()

    required_columns = {"titulo", "area_tematica", "fecha_inicio"}
    if not required_columns.issubset(set(df.columns)):
        raise ValueError(f"El CSV debe contener las columnas: {required_columns}")

    proyectos = []
    for _, row in df.iterrows():
        try:
            fecha = datetime.strptime(str(row["fecha_inicio"]).strip(), "%Y-%m-%d").date()
        except ValueError:
            raise ValueError(f"Fecha inválida: {row['fecha_inicio']}")

        proyectos.append({
            "titulo": str(row["titulo"]).strip(),
            "area_tematica": str(row["area_tematica"]).strip(),
            "fecha_inicio": fecha
        })
        
    return proyectos

def parse_csv_eventos(file) -> list:
    df = pd.read_csv(file, encoding="utf-8-sig")
    df.columns = df.columns.str.strip().str.lower()

    required_columns = {"tipo", "fecha", "asistentes", "multimedia", "descripcion"}
    if not required_columns.issubset(set(df.columns)):
        raise ValueError(f"El CSV debe contener las columnas: {required_columns}")

    eventos = []
    for _, row in df.iterrows():
        try:
            fecha = datetime.strptime(str(row["fecha"]).strip(), "%Y-%m-%d").date()
            asistentes = int(row["asistentes"])            
        except ValueError:
            raise ValueError(f"Fecha inválida: {row['fecha']}")
        except TypeError:
            raise ValueError(f"El número de asistentes debe ser un entero: {row['asistentes']}")
        
        eventos.append({
            "tipo": str(row["tipo"]).strip(),
            "fecha": fecha,
            "asistentes": asistentes,
            "multimedia": str(row["multimedia"]).strip(),
            "descripcion": str(row["descripcion"]).strip()
        }) 
        
    return eventos


def parse_csv_estadisticas (file) -> list:
    df = pd.read_csv(file, encoding="utf-8-sig")
    df.columns = df.columns.str.strip().str.lower()

    required_columns = {"categoria", "value", "descripcion"}
    if not required_columns.issubset(set(df.columns)):
        raise ValueError(f"El CSV debe contener las columnas: {required_columns}")

    estadisticas = []
    for _, row in df.iterrows():
        
        estadisticas.append({
            "categoria": str(row["categoria"]).strip(),
            "value": str(row["value"]).strip(),
            "descripcion": str(row["descripcion"]).strip(),
        }) 
        
    return estadisticas