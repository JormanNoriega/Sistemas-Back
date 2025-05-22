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

### Convenio

- convenio_id (PK)
- compañia_id (FK → Empresa)
- titulo_compañia
- tipo_convenio
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

## Implementación de Seguridad

Actualmente, el proyecto permite conexiones desde cualquier origen mediante la configuración CORS. Para un entorno de producción, se recomienda:

1. Restringir los orígenes permitidos en la configuración CORS
2. Implementar autenticación (JWT, OAuth2)
3. Agregar rate limiting para prevenir abusos

## Mantenimiento y Desarrollo Futuro

Para la extensión del sistema, se recomienda:

1. Agregar tests automatizados
2. Implementar un sistema de logging más robusto
3. Agregar un sistema de respaldo de datos
4. Desarrollar un panel de administración
5. Implementar un sistema de notificaciones
