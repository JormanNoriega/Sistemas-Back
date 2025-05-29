# Sistema de Gestión de Cooperación y Extensión Universitaria

## Descripción General

Este proyecto es un backend desarrollado con FastAPI para gestionar diversos aspectos relacionados con la cooperación y extensión universitaria, incluyendo:

- Gestión de empresas asociadas
- Seguimiento de egresados
- Administración de convenios institucionales
- Registro de proyectos
- Gestión de eventos
- Estadísticas institucionales
- Relaciones internacionales
- Impacto social
- Salidas a prácticas

El sistema permite importar datos masivamente desde archivos CSV y provee endpoints RESTful para la gestión individual de cada tipo de entidad.

## Estructura del Proyecto

```
Sistemas Back/
├── app/                       # Directorio principal de la aplicación
│   ├── models/                # Modelos de datos para la base de datos
│   ├── routers/               # Rutas y endpoints de la API
│   ├── schemas/               # Esquemas Pydantic para validación de datos
│   ├── utils/                 # Utilidades (parseo de CSV, etc.)
│   ├── __init__.py            # Inicializador del paquete
│   ├── config.py              # Configuración de la aplicación
│   ├── database.py            # Configuración de la base de datos
│   └── main.py                # Punto de entrada de la aplicación
├── *.csv                      # Archivos CSV de ejemplo para cargas masivas
├── main.py                    # Script de inicio alternativo
└── requirements.txt           # Dependencias del proyecto
```

## Tecnologías Utilizadas

- **FastAPI**: Framework web asíncrono de alto rendimiento
- **SQLAlchemy**: ORM para interacción con la base de datos
- **Pydantic**: Validación de datos y serialización
- **Pandas**: Procesamiento de archivos CSV
- **PostgreSQL**: Base de datos relacional
- **Python-Multipart**: Manejo de formularios y archivos
- **Python-dotenv**: Gestión de variables de entorno

## Modelos de Datos

### Empresa

- empresa_id (PK)
- nombre_empresa (único)
- nit (único)
- sector
- fecha_convenio

### Egresado

- egresado_id (PK)
- nombre_completo
- año_graduacion
- empleabilidad (Enum: EMPLEADO, DESEMPLEADO, EMPRENDEDOR)
- email (único)

### Empresa Aliada

- empresa_id (PK)
- nombre_empresa (único)
- nit (único)
- sector
- fecha_convenio

### Convenio

- convenio_id (PK)
- compania_id (FK → Empresa Aliada)
- titulo_compania
- tipo_de_convenio
- descripcion
- beneficios
- fecha
- fecha_vencimiento
- estatus (Enum: ACTIVE, EXPIRED, PENDING)

### Proyectos

- proyecto_id (PK)
- titulo
- area_tematica
- fecha_inicio

### Eventos

- evento_id (PK)
- tipo
- fecha
- asistentes
- multimedia
- descripcion

### Estadísticas

- estadistica_id (PK)
- categoria
- value
- descripcion

### Publicaciones

- publicacion_id (PK)
- titulo
- autores
- area
- fecha
- enlace
- tipo

### Relación Internacional

- relacion_id (PK)
- nombre
- pais
- institucion
- tipo (Enum: MOBILITY, AGREEMENT, PROJECT, NETWORK)
- fecha_inicio
- fecha_finalizacion
- descripcion
- participantes
- resultados
- estado (Enum: ACTIVE, EXPIRED, PENDING)

### Impacto Social

- id_impacto_social (PK)
- nombre_actividad
- fecha_realizacion
- lugar
- poblacion_beneficiada
- responsable
- descripcion
- resultados

### Salida a Prácticas

- id_salida_practica (PK)
- fecha_salida
- lugar_destino
- responsable
- cantidad_estudiantes
- hora_salida
- hora_regreso
- observaciones

### Publicaciones

- publicacion_id (PK)
- titulo
- autores
- area
- fecha
- enlace
- tipo

## Características Principales

### Importación de CSV

Cada entidad dispone de un endpoint para importar datos desde archivos CSV. Las características de esta importación incluyen:

1. **Validación de columnas requeridas**: Verifica que el archivo CSV contenga todas las columnas necesarias.
2. **Detección de duplicados internos**: Identifica y filtra registros duplicados dentro del mismo CSV.
3. **Validación contra base de datos**: Evita insertar registros que ya existen en la base de datos.
4. **Informe de resultados**: Proporciona un informe detallado de los registros procesados, incluyendo:
   - Registros insertados con éxito
   - Registros duplicados en el CSV
   - Registros duplicados en la base de datos
   - Registros con errores de formato

### API REST Completa

Cada entidad dispone de endpoints para:

- Crear nuevos registros
- Listar todos los registros
- Obtener un registro por ID
- Actualizar registros existentes
- Eliminar registros

## Configuración

### Variables de Entorno

El proyecto utiliza un archivo `.env` (que debe crearse) con las siguientes variables:

```
DATABASE_URL=postgresql://usuario:contraseña@host:puerto/nombre_db
```

### Dependencias

Las dependencias del proyecto están listadas en el archivo `requirements.txt`.

## Ejecución del Proyecto

1. **Instalación de dependencias**:

   ```bash
   pip install -r requirements.txt
   ```

2. **Configuración de la base de datos**:

   - Crear una base de datos PostgreSQL
   - Configurar el archivo `.env` con la URL de conexión

3. **Iniciar la aplicación**:

   ```bash
   python -m app.main
   ```

   o

   ```bash
   uvicorn app.main:app --reload
   ```

4. **Acceder a la documentación de la API**:
   Abrir en el navegador: `http://localhost:8000/docs`

## Ejemplos de Uso

### Cargar empresas desde CSV

```http
POST /api/empresas/upload-csv
```

Cuerpo: Formulario con archivo CSV que contenga las columnas:

- nombre_empresa
- nit
- sector
- fecha_convenio

### Cargar convenios desde CSV

```http
POST /api/convenios/upload
```

Cuerpo: Formulario con archivo CSV que contenga las columnas:

- compania_id (debe ser un ID válido de una empresa existente)
- titulo_compania
- tipo_de_convenio
- descripcion
- beneficios
- fecha (formato YYYY-MM-DD)
- fecha_vencimiento (formato YYYY-MM-DD)
- estatus (valores aceptados: active, expired, pending)

### Cargar publicaciones desde CSV

```http
POST /api/publicaciones/upload
```

Cuerpo: Formulario con archivo CSV que contenga las columnas:

- titulo
- autores (cuando hay múltiples autores, incluirlos entre comillas)
- area
- fecha (formato YYYY-MM-DD)
- enlace
- tipo

### Crear un nuevo egresado

```http
POST /api/egresados/
```

Cuerpo JSON:

```json
{
  "nombre_completo": "Juan Pérez",
  "año_graduacion": "2023-05-15",
  "empleabilidad": "Empleado",
  "email": "juan.perez@ejemplo.com"
}
```

### Crear un nuevo convenio

```http
POST /api/convenios/
```

Cuerpo JSON:

```json
{
  "compania_id": 40,
  "titulo_compania": "Convenio con Empresa Tecnológica",
  "tipo_de_convenio": "Prácticas profesionales",
  "descripcion": "Convenio para prácticas de estudiantes en áreas de desarrollo de software",
  "beneficios": "Experiencia laboral, posibilidad de contratación",
  "fecha_firma": "2025-01-01",
  "fecha_vencimiento": "2026-01-01",
  "estatus": "active"
}
```

> **Nota importante**: Al crear o actualizar convenios, asegúrate que el `compania_id` corresponda a una empresa existente en la base de datos.

### Crear una nueva publicación

```http
POST /api/publicaciones/
```

Cuerpo JSON:

```json
{
  "titulo": "Inteligencia Artificial en la Educación Superior",
  "autores": "Juan Pérez, María García",
  "area": "IA",
  "fecha": "2025-05-15",
  "enlace": "https://ejemplo.com/publicacion123",
  "tipo": "Artículo"
}
```

### Cargar publicaciones desde CSV

```http
POST /api/publicaciones/upload
```

Cuerpo: Formulario con archivo CSV que contenga las columnas:

- titulo
- autores
- area
- fecha (formato YYYY-MM-DD)
- enlace
- tipo

### Crear una nueva publicación

```http
POST /api/publicaciones/
```

Cuerpo JSON:

```json
{
  "titulo": "Análisis de Big Data en empresas",
  "autores": "Juan Pérez, Ana Ruiz",
  "area": "IA",
  "fecha": "2024-11-10",
  "enlace": "https://revista.com/p1",
  "tipo": "Artículo"
}
```

## Implementación de Seguridad

Actualmente, el proyecto permite conexiones desde cualquier origen mediante la configuración CORS. Para un entorno de producción, se recomienda:

1. Restringir los orígenes permitidos en la configuración CORS
2. Implementar autenticación (JWT, OAuth2)
3. Agregar rate limiting para prevenir abusos

## Mejoras Recientes

Se han implementado las siguientes mejoras y correcciones en el sistema:

### 1. Corrección de inconsistencias en el modelo de Convenios

- Se corrigió la inconsistencia entre el nombre de los campos en el código (`compania_id`) y en la base de datos (`compañia_id`)
- Se estandarizó el uso de `compania_id` y `titulo_compania` sin la letra "ñ" para evitar problemas de codificación
- Se cambió el campo `tipo_convenio` por `tipo_de_convenio` para mantener consistencia con el CSV

### 2. Mejoras en la validación de datos

- Validación previa a la inserción de convenios para verificar la existencia de empresas asociadas
- Manejo de errores detallado para cada tipo de problema (duplicados, empresas inexistentes, errores de formato)
- Categorización de errores para facilitar su solución

### 3. Relación entre Empresas Aliadas y Convenios

- Se actualizó la clave foránea en el modelo Convenio para que apunte a la nueva tabla `empresas_aliadas`
- Se añadió una relación bidireccional usando `relationship` para facilitar el acceso a los datos relacionados
- Se actualizó el esquema de salida de convenios para incluir información básica de la empresa relacionada

### 4. Optimización del procesamiento de CSV

- Normalización de nombres de columnas para mayor flexibilidad
- Detección más robusta de duplicados en los CSV
- Tolerancia a variaciones en los nombres de campos (CSV de egresados y relaciones internacionales)

### 4. Archivos CSV de ejemplo actualizados

- Se crearon archivos CSV de ejemplo que siguen correctamente la estructura requerida
- Ejemplos con datos de prueba válidos para cada tipo de entidad

### 5. Documentación

- Actualización del README con los cambios realizados
- Documentación de los formatos CSV requeridos
