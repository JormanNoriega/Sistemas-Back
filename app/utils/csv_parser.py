import pandas as pd
from datetime import datetime
import unicodedata

def parse_csv(file) -> list:
    df = pd.read_csv(file, encoding="utf-8-sig")
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

def match_column(posibles, columnas):
    for posible in posibles:
        for col in columnas:
            col_norm = unicodedata.normalize('NFKD', col).encode('ascii', 'ignore').decode('utf-8').lower().replace(' ', '').replace('_', '')
            posible_norm = unicodedata.normalize('NFKD', posible).encode('ascii', 'ignore').decode('utf-8').lower().replace(' ', '').replace('_', '')
            if col_norm == posible_norm:
                return col
    return None

def parse_csv_egresados(file):
    df = pd.read_csv(file, encoding="utf-8-sig")
    print("Columnas recibidas:", df.columns)
    columnas = list(df.columns)
    # Definir las variantes aceptadas para cada campo
    campos = {
        'nombre_completo': ['nombre_completo', 'nombre completo', 'nombre'],
        'año_graduacion': ['año_graduacion', 'ano_graduacion', 'año de graduacion', 'ano de graduacion', 'año', 'ano'],
        'empleabilidad': ['empleabilidad', 'empleo', 'estado_empleo'],
        'email': ['email', 'correo', 'correo_electronico', 'e-mail', 'Email']
    }
    mapeo = {}
    for clave, variantes in campos.items():
        col = match_column(variantes, columnas)
        if not col:
            raise Exception(f"Falta la columna para '{clave}'. Encabezados recibidos: {columnas}")
        mapeo[clave] = col

    # Procesar los datos con los nombres internos correctos
    registros = []
    for _, row in df.iterrows():
        registro = {
            'nombre_completo': str(row[mapeo['nombre_completo']]).strip(),
            'año_graduacion': str(row[mapeo['año_graduacion']]).strip(),
            'empleabilidad': str(row[mapeo['empleabilidad']]).strip(),
            'email': str(row[mapeo['email']]).strip()
        }
        registros.append(registro)
    return registros

def parse_csv_convenios(file):
    df = pd.read_csv(file)
    required_columns = {'compania_id', 'titulo_compania', 'tipo_de_convenio', 'descripcion', 'beneficios', 'fecha_firma', 'fecha_vencimiento', 'estatus'}
    if not required_columns.issubset(set(df.columns)):
        raise Exception(f"El CSV debe contener las columnas: {required_columns}")
    return df.to_dict(orient='records')

def parse_csv_relaciones_internacionales(file):
    df = pd.read_csv(file)
    required_columns = {'nombre', 'pais', 'institucion', 'tipo', 'fecha_inicio', 'fecha_finalizacion', 'descripcion', 'participantes', 'resultados', 'estado'}
    if not required_columns.issubset(set(df.columns)):
        raise Exception(f"El CSV debe contener las columnas: {required_columns}")
    return df.to_dict(orient='records')
