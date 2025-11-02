import os
import pandas as pd
from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from fastapi.responses import JSONResponse, FileResponse
from sqlmodel import Session, select
from app.db import get_session
from app.models import Upload, DataRecord

print("✅ Upload route loaded successfully from:", __file__)

router = APIRouter(prefix="/upload", tags=["File Upload"])

# Directory to store uploaded files
UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

# ---------------- Upload File ----------------
@router.post("/")
async def upload_file(file: UploadFile = File(...), session: Session = Depends(get_session)):
    allowed_types = [
        "text/csv",
        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    ]

    if file.content_type not in allowed_types:
        raise HTTPException(status_code=400, detail="Only CSV or Excel files are allowed")

    # Save file to disk
    file_path = os.path.join(UPLOAD_DIR, file.filename)
    with open(file_path, "wb") as buffer:
        buffer.write(await file.read())

    # Read file using pandas
    try:
        if file.filename.endswith(".csv"):
            df = pd.read_csv(file_path)
        else:
            df = pd.read_excel(file_path)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error reading file: {e}")

    # Basic Data Cleaning
    df = df.dropna(how="all")  # remove completely empty rows
    df.columns = [col.strip().replace(" ", "_").lower() for col in df.columns]

    # Save upload info
    upload_entry = Upload(filename=file.filename, user_id=1)  # temporary user_id
    session.add(upload_entry)
    session.commit()
    session.refresh(upload_entry)

    # Save data rows to DataRecord table
    records = []
    for _, row in df.iterrows():
        record = DataRecord(upload_id=upload_entry.id, data=row.to_dict())
        records.append(record)

    session.add_all(records)
    session.commit()

    return JSONResponse(content={
        "message": f"File '{file.filename}' uploaded and processed successfully!",
        "total_records": len(df),
        "upload_id": upload_entry.id,
        "file_path": file_path
    })


# ---------------- List All Uploads ----------------
@router.get("/list")
def list_uploads(session: Session = Depends(get_session)):
    uploads = session.exec(select(Upload)).all()
    result = []

    for upload in uploads:
        file_path = os.path.join(UPLOAD_DIR, upload.filename)
        if os.path.exists(file_path):
            size_kb = os.path.getsize(file_path) / 1024
            download_url = f"/upload/download/{upload.filename}"
            result.append({
                "id": upload.id,
                "filename": upload.filename,
                "uploaded_at": upload.uploaded_at,
                "size_kb": round(size_kb, 2),
                "download_url": download_url
            })

    return JSONResponse(content=result)


# ---------------- Download File ----------------
@router.get("/download/{filename}")
def download_file(filename: str):
    file_path = os.path.join(UPLOAD_DIR, filename)
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File not found")
    return FileResponse(path=file_path, filename=filename, media_type='application/octet-stream')
