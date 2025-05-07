import pandas as pd
from datetime import datetime

def parse_csv(file) -> list:
    df = pd.read_csv(file, encoding="utf-8-sig")
    df.columns = df.columns.str.strip().str.lower()

    required_columns = {"nombre_empresa", "nit", "sector", "fecha_convenio"}
    if not required_columns.issubset(set(df.columns)):
        raise ValueError(f"El CSV debe contener las columnas: {required_columns}")

    empresas = []
    for _, row in df.iterrows():
        try:
            fecha = datetime.strptime(str(row["fecha_convenio"]).strip(), "%Y-%m-%d").date()
        except ValueError:
            raise ValueError(f"Fecha inválida: {row['fecha_convenio']}")

        empresas.append({
            "nombre_empresa": str(row["nombre_empresa"]).strip(),
            "nit": str(row["nit"]).strip(),
            "sector": str(row["sector"]).strip(),
            "fecha_convenio": fecha
        })

    return empresas
