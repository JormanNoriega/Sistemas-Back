""" from fastapi import FastAPI, UploadFile, File, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from app.routers import egresado, empresa, convenio, relacion_internacional
from app.database import engine, Base, get_db
import logging
import tempfile
import os

# Crear las tablas en la base de datos
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Sistema de Gestión",
    description="API para el sistema de gestión de egresados, empresas, convenios y relaciones internacionales",
    version="1.0.0"
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # En producción, especifica los orígenes permitidos
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Incluir los routers
app.include_router(egresado.router)
app.include_router(empresa.router)
app.include_router(convenio.router)
app.include_router(relacion_internacional.router)

@app.get("/")
def read_root():
    return {"mensaje": "Bienvenido a la API del Sistema de Gestión"}

# Configuración de logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

@app.post("/upload-egresados/", status_code=status.HTTP_201_CREATED)
async def upload_egresados_csv(
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    logger.debug(f"Recibido archivo: {file.filename}")

    if not file.filename.endswith('.csv'):
        logger.error("Archivo no es CSV")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Solo se permiten archivos CSV"
        )
    temp_file = tempfile.NamedTemporaryFile(delete=False)
    try:
        contents = await file.read()
        temp_file.write(contents)
        temp_file.close()
        try:
            registros = parse_csv_egresados(temp_file.name)
            logger.debug(f"Registros parseados: {len(registros)}")
            logger.debug(f"Primer registro: {registros[0] if registros else None}")
        except Exception as e:
            logger.error(f"Error al parsear: {str(e)}", exc_info=True)
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Error al procesar el CSV: {str(e)}"
            )
        created_count = 0
        failed_count = 0
        errors = []
        for registro in registros:
            try:
                egresado_data = EgresadoCreate(
                    nombre_completo=registro['nombre_completo'],
                    año_graduacion=registro['año_graduacion'],
                    empleabilidad=registro['empleabilidad'],
                    email=registro['email']
                )
                create_egresado(db=db, egresado=egresado_data)
                created_count += 1
            except Exception as e:
                failed_count += 1
                logger.error(f"Error en fila {created_count + failed_count}: {str(e)}", exc_info=True)
                errors.append(f"Error en fila {created_count + failed_count}: {str(e)}")
        return {
            "success": True,
            "message": f"Se procesaron {created_count + failed_count} registros: {created_count} insertados, {failed_count} fallidos",
            "errors": errors if failed_count > 0 else []
        }
    finally:
        if os.path.exists(temp_file.name):
            os.unlink(temp_file.name)  """