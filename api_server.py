from fastapi import FastAPI, UploadFile, File, HTTPException, BackgroundTasks, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
import pandas as pd
import os
import tempfile
import uuid
from datetime import datetime
import asyncio
import json

from main import AutoAnalyst
from database_service import get_database_service, get_cache_service
from realtime_service import get_realtime_analyzer, get_metrics_collector
from email_service import EmailService
import config

app = FastAPI(
    title="AutoAnalyst API",
    description="Autonomous Data Science Consultant API",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class AnalysisRequest(BaseModel):
    dataset_name: str
    analysis_type: str = "full"
    use_autogen: bool = False
    interactive: bool = False
    email_notification: Optional[str] = None

class StreamConfig(BaseModel):
    stream_id: str
    data_source: str
    batch_size: int = 100
    thresholds: Dict[str, Dict[str, float]] = {}

class StreamData(BaseModel):
    stream_id: str
    data: List[Dict[str, Any]]

class EmailRequest(BaseModel):
    recipient_email: str
    dataset_name: str = "Analysis"

db_service = get_database_service()
cache_service = get_cache_service()
realtime_analyzer = get_realtime_analyzer()
metrics_collector = get_metrics_collector()
email_service = EmailService()

@app.on_event("startup")
async def startup_event():
    realtime_analyzer.start_service()

@app.on_event("shutdown")
async def shutdown_event():
    realtime_analyzer.stop_service()
    db_service.close()

@app.get("/")
async def root():
    return {"message": "AutoAnalyst API", "version": "1.0.0", "status": "active"}

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "services": {
            "database": "connected",
            "cache": "active",
            "realtime": "running" if realtime_analyzer.is_running else "stopped"
        }
    }

@app.post("/upload")
async def upload_dataset(file: UploadFile = File(...)):
    if not file.filename.endswith('.csv'):
        raise HTTPException(status_code=400, detail="Only CSV files are supported")
    
    try:
        contents = await file.read()
        df = pd.read_csv(pd.io.common.StringIO(contents.decode('utf-8')))
        
        file_id = str(uuid.uuid4())
        file_path = f"datasets/uploaded_{file_id}.csv"
        df.to_csv(file_path, index=False)
        
        metadata_id = db_service.save_dataset_metadata(df, file.filename)
        
        metrics_collector.record_metric("datasets_uploaded", 1)
        
        return {
            "file_id": file_id,
            "filename": file.filename,
            "file_path": file_path,
            "metadata_id": metadata_id,
            "shape": df.shape,
            "columns": list(df.columns),
            "upload_time": datetime.now().isoformat()
        }
    
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error processing file: {str(e)}")

@app.post("/analyze")
async def analyze_dataset(
    request: AnalysisRequest,
    background_tasks: BackgroundTasks
):
    try:
        file_path = f"datasets/uploaded_{request.dataset_name}.csv"
        
        if not os.path.exists(file_path):
            raise HTTPException(status_code=404, detail="Dataset not found")
        
        session_id = db_service.save_analysis_session(
            request.dataset_name,
            request.analysis_type,
            file_path,
            request.email_notification
        )
        
        background_tasks.add_task(
            run_analysis_background,
            session_id,
            file_path,
            request
        )
        
        return {
            "session_id": session_id,
            "status": "started",
            "message": "Analysis started in background",
            "timestamp": datetime.now().isoformat()
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error starting analysis: {str(e)}")

async def run_analysis_background(session_id: int, file_path: str, request: AnalysisRequest):
    try:
        analyst = AutoAnalyst()
        
        if request.use_autogen:
            from autogen_integration import enhance_autoanalyst_with_autogen
            analyst = enhance_autoanalyst_with_autogen(analyst)
        
        result = analyst.analyze_dataset(
            file_path,
            use_autogen=request.use_autogen,
            interactive=request.interactive
        )
        
        results_summary = {
            "status": "completed",
            "insights": getattr(result, 'insights', []),
            "recommendations": getattr(result, 'recommendations', []),
            "completion_time": datetime.now().isoformat()
        }
        
        db_service.update_analysis_session(session_id, "completed", results_summary)
        
        if request.email_notification:
            email_service.send_analysis_report(
                request.email_notification,
                "reports/",
                request.dataset_name
            )
        
        metrics_collector.record_metric("analyses_completed", 1)
        
    except Exception as e:
        db_service.update_analysis_session(session_id, "failed", {"error": str(e)})

@app.get("/analysis/{session_id}")
async def get_analysis_status(session_id: int):
    sessions = db_service.get_analysis_history(limit=1000)
    session_data = next((s for s in sessions if s['id'] == session_id), None)
    
    if not session_data:
        raise HTTPException(status_code=404, detail="Session not found")
    
    return session_data

@app.get("/analysis/history")
async def get_analysis_history(limit: int = 50):
    return db_service.get_analysis_history(limit)

@app.get("/datasets/stats")
async def get_dataset_stats():
    return db_service.get_dataset_stats()

@app.post("/realtime/stream")
async def create_realtime_stream(config: StreamConfig):
    stream_id = realtime_analyzer.add_data_stream(
        config.stream_id,
        config.data_source,
        {
            'batch_size': config.batch_size,
            'thresholds': config.thresholds
        }
    )
    
    return {
        "stream_id": stream_id,
        "status": "created",
        "timestamp": datetime.now().isoformat()
    }

@app.post("/realtime/data")
async def add_stream_data(data: StreamData):
    success = realtime_analyzer.update_stream_data(data.stream_id, data.data)
    
    if not success:
        raise HTTPException(status_code=404, detail="Stream not found")
    
    return {
        "status": "data_added",
        "stream_id": data.stream_id,
        "records_added": len(data.data),
        "timestamp": datetime.now().isoformat()
    }

@app.get("/realtime/streams")
async def get_active_streams():
    return realtime_analyzer.get_active_streams()

@app.get("/realtime/analysis/{stream_id}")
async def get_realtime_analysis(stream_id: str):
    analysis = realtime_analyzer.get_latest_analysis(stream_id)
    
    if not analysis:
        raise HTTPException(status_code=404, detail="No analysis found for stream")
    
    return analysis

@app.get("/realtime/history/{stream_id}")
async def get_stream_history(stream_id: str, limit: int = 50):
    return realtime_analyzer.get_analysis_history(stream_id, limit)

@app.delete("/realtime/stream/{stream_id}")
async def delete_stream(stream_id: str):
    success = realtime_analyzer.remove_stream(stream_id)
    
    if success:
        return {"status": "deleted", "stream_id": stream_id}
    else:
        raise HTTPException(status_code=404, detail="Stream not found")

@app.post("/email/send-report")
async def send_email_report(request: EmailRequest):
    try:
        success, message = email_service.send_analysis_report(
            request.recipient_email,
            "reports/",
            request.dataset_name
        )
        
        if success:
            return {"status": "sent", "message": message}
        else:
            raise HTTPException(status_code=500, detail=message)
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error sending email: {str(e)}")

@app.get("/reports/download/{filename}")
async def download_report(filename: str):
    file_path = f"reports/{filename}"
    
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="Report not found")
    
    return FileResponse(
        file_path,
        media_type='application/pdf',
        filename=filename
    )

@app.get("/visualizations/{filename}")
async def get_visualization(filename: str):
    file_path = f"visuals/{filename}"
    
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="Visualization not found")
    
    return FileResponse(file_path)

@app.get("/metrics")
async def get_system_metrics():
    return {
        "metrics": metrics_collector.get_all_metrics(),
        "system_stats": db_service.get_dataset_stats(),
        "active_streams": len(realtime_analyzer.get_active_streams()),
        "timestamp": datetime.now().isoformat()
    }

@app.get("/datasets/list")
async def list_datasets():
    stored_datasets = db_service.list_stored_datasets()
    
    uploaded_files = []
    if os.path.exists("datasets"):
        uploaded_files = [f for f in os.listdir("datasets") if f.endswith('.csv')]
    
    return {
        "stored_datasets": stored_datasets,
        "uploaded_files": uploaded_files,
        "total_count": len(stored_datasets) + len(uploaded_files)
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app,
        host=getattr(config, 'API_HOST', '0.0.0.0'),
        port=getattr(config, 'API_PORT', 8000),
        reload=True
    )