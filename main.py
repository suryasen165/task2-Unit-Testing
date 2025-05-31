#main.py
from fastapi import FastAPI, UploadFile, File, Query, HTTPException, Path
from contextlib import asynccontextmanager
from database import initialize_db, insert_csv_data, fetch_records, update_record, delete_record, get_record_by_id
from utils import process_csv
from typing import Dict, Any
import uvicorn
from database import engine

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    initialize_db()
    yield
    # Shutdown (if needed)

app = FastAPI(
    title="CSV Upload API with PostgreSQL", 
    version="2.0.0",
    lifespan=lifespan
)

@app.post("/upload/", summary="Upload CSV file")
async def upload_csv(file: UploadFile = File(...)):
    """Upload and store CSV data in PostgreSQL"""
    try:
        content = await file.read()
        df = process_csv(content)
        insert_csv_data(df)
        return {"message": f"CSV uploaded successfully. {len(df)} records stored."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/records/", summary="Get all records")
async def get_records(column: str = Query(None), value: str = Query(None)):
    """Fetch records with optional filtering"""
    try:
        records = fetch_records(column, value)
        return {"records": records, "count": len(records)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/records/{record_id}", summary="Get record by ID")
async def get_record(record_id: int = Path(..., description="Record ID")):
    """Get a specific record by ID"""
    try:
        record = get_record_by_id(record_id)
        if not record:
            raise HTTPException(status_code=404, detail="Record not found")
        return {"record": record}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.put("/records/{record_id}", summary="Update record")
async def update_record_endpoint(
    record_id: int = Path(..., description="Record ID"),
    updates: Dict[str, Any] = None
):
    """Update a specific record"""
    try:
        if not updates:
            raise HTTPException(status_code=400, detail="No updates provided")
        
        # Check if record exists
        existing_record = get_record_by_id(record_id)
        if not existing_record:
            raise HTTPException(status_code=404, detail="Record not found")
        
        success = update_record(record_id, updates)
        if success:
            return {"message": "Record updated successfully"}
        else:
            raise HTTPException(status_code=500, detail="Failed to update record")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/records/{record_id}", summary="Delete record")
async def delete_record_endpoint(record_id: int = Path(..., description="Record ID")):  
    """Delete a specific record"""
    try:
        # Check if record exists
        existing_record = get_record_by_id(record_id)
        if not existing_record:
            raise HTTPException(status_code=404, detail="Record not found")
        
        success = delete_record(record_id)
        if success:
            return {"message": "Record deleted successfully"}
        else:
            raise HTTPException(status_code=500, detail="Failed to delete record")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health", summary="Health check")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "database": "postgresql"}

@app.get("/debug/columns")
async def get_columns():
    from sqlalchemy import inspect
    inspector = inspect(engine)
    columns = inspector.get_columns("uploaded_data")
    return [{"name": col["name"], "type": str(col["type"])} for col in columns]

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)