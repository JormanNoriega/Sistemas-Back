import pandas as pd
from datetime import datetime
import unicodedata

def parse_csv_empresas(file) -> tuple:
    df = pd.read_csv(file, encoding="utf-8-sig")
    required_columns = {"nombre_empresa", "nit", "sector", "fecha_convenio"}
    if not required_columns.issubset(set(df.columns)):
        raise ValueError(f"El CSV debe contener las columnas: {required_columns}")

    # Encontrar duplicados por 'nombre_empresa' y 'nit'
    duplicates = df.duplicated(subset=["nombre_empresa", "nit"], keep='first')
    duplicados_df = df[duplicates].copy()
    
    # Quedarnos solo con registros únicos
    df_unicos = df.drop_duplicates(subset=["nombre_empresa", "nit"], keep='first')
    
    empresas = []
    registros_con_error = []
    
    # Procesar los registros únicos
    for _, row in df_unicos.iterrows():
        try:
            fecha = datetime.strptime(str(row["fecha_convenio"]).strip(), "%Y-%m-%d").date()
            empresas.append({
                "nombre_empresa": str(row["nombre_empresa"]).strip(),
                "nit": str(row["nit"]).strip(),
                "sector": str(row["sector"]).strip(),
                "fecha_convenio": fecha
            })
        except ValueError:
            registros_con_error.append({
                "nombre_empresa": str(row["nombre_empresa"]).strip(),
                "nit": str(row["nit"]).strip(),
                "error": f"Fecha inválida: {row['fecha_convenio']}"
            })
    
    # Agregar duplicados al informe de errores
    for _, row in duplicados_df.iterrows():
        registros_con_error.append({
            "nombre_empresa": str(row["nombre_empresa"]).strip(),
            "nit": str(row["nit"]).strip(),
            "error": "Registro duplicado"
        })
    
    return empresas, registros_con_error

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
        
    # Identificar duplicados por 'nombre_completo' y 'email'
    duplicates = df.duplicated(subset=[mapeo['nombre_completo'], mapeo['email']], keep='first')
    duplicados_df = df[duplicates].copy()
    
    # Quedarnos solo con registros únicos
    df_unicos = df.drop_duplicates(subset=[mapeo['nombre_completo'], mapeo['email']], keep='first')
    
    # Procesar los datos con los nombres internos correctos
    registros = []
    registros_duplicados = []
    
    for _, row in df_unicos.iterrows():
        registro = {
            'nombre_completo': str(row[mapeo['nombre_completo']]).strip(),
            'año_graduacion': str(row[mapeo['año_graduacion']]).strip(),
            'empleabilidad': str(row[mapeo['empleabilidad']]).strip(),
            'email': str(row[mapeo['email']]).strip()
        }
        registros.append(registro)
    
    # Procesar los duplicados para el informe
    for _, row in duplicados_df.iterrows():
        registro_duplicado = {
            'nombre_completo': str(row[mapeo['nombre_completo']]).strip(),
            'email': str(row[mapeo['email']]).strip(),
            'error': "Registro duplicado"
        }
        registros_duplicados.append(registro_duplicado)
    
    return registros, registros_duplicados

def parse_csv_convenios(file):
    df = pd.read_csv(file)
    required_columns = {'compania_id', 'titulo_compania', 'tipo_de_convenio', 'descripcion', 'beneficios', 'fecha_firma', 'fecha_vencimiento', 'estatus'}
    if not required_columns.issubset(set(df.columns)):
        raise Exception(f"El CSV debe contener las columnas: {required_columns}")
    
    # Identificar duplicados por 'compania_id' y 'titulo_compania'
    duplicates = df.duplicated(subset=['compania_id', 'titulo_compania'], keep='first')
    duplicados_df = df[duplicates].copy()
    
    # Quedarnos solo con registros únicos
    df_unicos = df.drop_duplicates(subset=['compania_id', 'titulo_compania'], keep='first')
    
    # Convertir registros únicos a diccionarios
    registros_validos = df_unicos.to_dict(orient='records')
    
    # Crear informe de duplicados
    registros_duplicados = []
    for _, row in duplicados_df.iterrows():
        registro_duplicado = {
            'compania_id': row['compania_id'],
            'titulo_compania': row['titulo_compania'],
            'error': "Registro duplicado"
        }
        registros_duplicados.append(registro_duplicado)
    
    return registros_validos, registros_duplicados

def parse_csv_relaciones_internacionales(file):
    df = pd.read_csv(file)
    required_columns = {'nombre', 'pais', 'institucion', 'tipo', 'fecha_inicio', 'fecha_finalizacion', 'descripcion', 'participantes', 'resultados', 'estado'}
    if not required_columns.issubset(set(df.columns)):
        raise Exception(f"El CSV debe contener las columnas: {required_columns}")
    
    # Identificar duplicados por 'nombre' e 'institucion'
    duplicates = df.duplicated(subset=['nombre', 'institucion'], keep='first')
    duplicados_df = df[duplicates].copy()
    
    # Quedarnos solo con registros únicos
    df_unicos = df.drop_duplicates(subset=['nombre', 'institucion'], keep='first')
    
    # Convertir registros únicos a diccionarios
    registros_validos = df_unicos.to_dict(orient='records')
    
    # Crear informe de duplicados
    registros_duplicados = []
    for _, row in duplicados_df.iterrows():
        registro_duplicado = {
            'nombre': row['nombre'],
            'institucion': row['institucion'],
            'error': "Registro duplicado"
        }
        registros_duplicados.append(registro_duplicado)
    
    return registros_validos, registros_duplicados

def parse_csv_proyectos(file) -> tuple:
    df = pd.read_csv(file, encoding="utf-8-sig")
    df.columns = df.columns.str.strip().str.lower()

    required_columns = {"titulo", "area_tematica", "fecha_inicio"}
    if not required_columns.issubset(set(df.columns)):
        raise ValueError(f"El CSV debe contener las columnas: {required_columns}")
    
    # Identificar duplicados por 'titulo' y 'area_tematica'
    duplicates = df.duplicated(subset=["titulo", "area_tematica"], keep='first')
    duplicados_df = df[duplicates].copy()
    
    # Quedarnos solo con registros únicos
    df_unicos = df.drop_duplicates(subset=["titulo", "area_tematica"], keep='first')
    
    proyectos = []
    registros_con_error = []
    
    # Procesar los registros únicos
    for _, row in df_unicos.iterrows():
        try:
            fecha = datetime.strptime(str(row["fecha_inicio"]).strip(), "%Y-%m-%d").date()
            proyectos.append({
                "titulo": str(row["titulo"]).strip(),
                "area_tematica": str(row["area_tematica"]).strip(),
                "fecha_inicio": fecha
            })
        except ValueError:
            registros_con_error.append({
                "titulo": str(row["titulo"]).strip(),
                "area_tematica": str(row["area_tematica"]).strip(),
                "error": f"Fecha inválida: {row['fecha_inicio']}"
            })
    
    # Agregar duplicados al informe de errores
    for _, row in duplicados_df.iterrows():
        registros_con_error.append({
            "titulo": str(row["titulo"]).strip(),
            "area_tematica": str(row["area_tematica"]).strip(),
            "error": "Registro duplicado"
        })
    
    return proyectos, registros_con_error

def parse_csv_eventos(file) -> tuple:
    df = pd.read_csv(file, encoding="utf-8-sig")
    df.columns = df.columns.str.strip().str.lower()

    required_columns = {"tipo", "fecha", "asistentes", "multimedia", "descripcion"}
    if not required_columns.issubset(set(df.columns)):
        raise ValueError(f"El CSV debe contener las columnas: {required_columns}")

    # Identificar duplicados por 'tipo', 'fecha' y 'descripcion'
    duplicates = df.duplicated(subset=["tipo", "fecha", "descripcion"], keep='first')
    duplicados_df = df[duplicates].copy()
    
    # Quedarnos solo con registros únicos
    df_unicos = df.drop_duplicates(subset=["tipo", "fecha", "descripcion"], keep='first')
    
    eventos = []
    registros_con_error = []
    
    # Procesar los registros únicos
    for _, row in df_unicos.iterrows():
        try:
            fecha = datetime.strptime(str(row["fecha"]).strip(), "%Y-%m-%d").date()
            asistentes = int(row["asistentes"])            
            
            eventos.append({
                "tipo": str(row["tipo"]).strip(),
                "fecha": fecha,
                "asistentes": asistentes,
                "multimedia": str(row["multimedia"]).strip(),
                "descripcion": str(row["descripcion"]).strip()
            })
        except ValueError:
            registros_con_error.append({
                "tipo": str(row["tipo"]).strip(),
                "fecha": str(row["fecha"]).strip(),
                "error": "Fecha inválida o número de asistentes no es un entero"
            })
    
    # Agregar duplicados al informe de errores
    for _, row in duplicados_df.iterrows():
        registros_con_error.append({
            "tipo": str(row["tipo"]).strip(),
            "fecha": str(row["fecha"]).strip(),
            "descripcion": str(row["descripcion"]).strip(),
            "error": "Registro duplicado"
        })
    
    return eventos, registros_con_error

def parse_csv_estadisticas(file) -> tuple:
    df = pd.read_csv(file, encoding="utf-8-sig")
    df.columns = df.columns.str.strip().str.lower()

    required_columns = {"categoria", "value", "descripcion"}
    if not required_columns.issubset(set(df.columns)):
        raise ValueError(f"El CSV debe contener las columnas: {required_columns}")
    
    # Identificar duplicados por 'categoria' y 'descripcion'
    duplicates = df.duplicated(subset=["categoria", "descripcion"], keep='first')
    duplicados_df = df[duplicates].copy()
    
    # Quedarnos solo con registros únicos
    df_unicos = df.drop_duplicates(subset=["categoria", "descripcion"], keep='first')
    
    estadisticas = []
    registros_duplicados = []
    
    # Procesar los registros únicos
    for _, row in df_unicos.iterrows():
        estadisticas.append({
            "categoria": str(row["categoria"]).strip(),
            "value": str(row["value"]).strip(),
            "descripcion": str(row["descripcion"]).strip()
        })
    
    # Agregar duplicados al informe
    for _, row in duplicados_df.iterrows():
        registros_duplicados.append({
            "categoria": str(row["categoria"]).strip(),
            "descripcion": str(row["descripcion"]).strip(),
            "error": "Registro duplicado"
        })
    
    return estadisticas, registros_duplicados
