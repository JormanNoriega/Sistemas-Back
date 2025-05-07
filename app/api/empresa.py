from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.schemas.empresa import EmpresaOut
from app.crud.empresa import create_empresa
from app.services.csv_service import parse_csv

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/empresas/upload", response_model=list[EmpresaOut])
async def upload_csv(file: UploadFile = File(...), db: Session = Depends(get_db)):
    if not file.filename.endswith(".csv"):
        raise HTTPException(status_code=400, detail="El archivo debe ser un CSV")

    try:
        data = parse_csv(file.file)
        results = []
        for item in data:
            empresa = create_empresa(db, item)
            results.append(empresa)
        return results
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
