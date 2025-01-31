"""FastAPI server for receiving and storing metrics"""
from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from typing import Dict, Any, List, Optional
import uvicorn
from datetime import datetime
import json
import os
from src.utils.timer import Timer

app = FastAPI(title="Metrics Server")

# Store metrics in memory
metrics_store = []
METRICS_DIR = os.path.join(os.path.dirname(__file__), "data")
METRICS_FILE = os.path.join(METRICS_DIR, "received_metrics.json")

# Ensure the data directory exists
os.makedirs(METRICS_DIR, exist_ok=True)

class MetricsData(BaseModel):
    metadata: Dict[str, Any]
    data: Dict[str, Any]
    status: Dict[str, Any]

class MetricsResponse(BaseModel):
    status: str
    timestamp: str
    message: str

@app.get("/", response_class=HTMLResponse)
async def root():
    """Root endpoint with links"""
    return """
    <html>
        <head>
            <title>Metrics Server</title>
            <script>
                async function clearMetrics() {
                    if (confirm('Are you sure you want to clear all metrics?')) {
                        const response = await fetch('/metrics/clear', { method: 'DELETE' });
                        const result = await response.json();
                        alert(result.message);
                        location.reload();
                    }
                }
            </script>
        </head>
        <body>
            <h1>Metrics Server</h1>
            <ul>
                <li><a href="/docs">API Documentation</a></li>
                <li><a href="/metrics/Metrics Monitor">View Latest Metrics</a></li>
                <li><a href="#" onclick="clearMetrics()">Delete All Metrics</a></li>
            </ul>
        </body>
    </html>
    """

@app.delete("/metrics/clear")
async def clear_metrics():
    """Clear all stored metrics"""
    try:
        with Timer("DELETE /metrics/clear"):
            # Clear memory store
            metrics_store.clear()
            
            # Clear file
            if os.path.exists(METRICS_FILE):
                os.remove(METRICS_FILE)
                
            return {
                "status": "success",
                "timestamp": datetime.now().isoformat(),
                "message": "All metrics cleared successfully"
            }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/metrics", response_model=MetricsResponse)
async def receive_metrics(metrics: MetricsData):
    try:
        with Timer("POST /metrics"):
            # Store metrics with timestamp
            metric_entry = {
                'timestamp': datetime.now().isoformat(),
                'metrics': metrics.model_dump()
            }
            metrics_store.append(metric_entry)
            
            # Keep only last 1000 metrics
            if len(metrics_store) > 1000:
                metrics_store.pop(0)
                
            # Save to file
            with open(METRICS_FILE, 'a') as f:
                f.write(json.dumps(metric_entry) + '\n')
            
            return MetricsResponse(
                status="success",
                timestamp=datetime.now().isoformat(),
                message="Metrics received successfully"
            )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/metrics/{device_id}", response_model=List[Dict[str, Any]])
async def get_metrics(device_id: str, limit: int = 100):
    """Get metrics for a specific device"""
    try:
        with Timer(f"GET /metrics/{device_id}"):
            # Filter metrics by device_id and return most recent
            device_metrics = [
                m for m in metrics_store 
                if m['metrics']['metadata']['source'] == device_id
            ]
            return device_metrics[-limit:]
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

def run_server():
    """Run the metrics server"""
    uvicorn.run(app, host="127.0.0.1", port=8000)

if __name__ == "__main__":
    run_server() 