"""SatLink API (FastAPI)
Provides simple REST endpoints and WebSocket for live data.
"""

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import JSONResponse
import json
from typing import List, Dict
import asyncio
from datetime import datetime

app = FastAPI(title="SatLink API")
from fastapi.middleware.cors import CORSMiddleware
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])


# Mock in-memory data (replace with real DB connection)
terminals_data = {}
ws_connections: List[WebSocket] = []

@app.get("/health")
def health():
    return {"status": "ok", "timestamp": datetime.utcnow().isoformat()}

@app.get("/terminals")
def list_terminals():
    return {"terminals": list(terminals_data.keys())}

@app.get("/terminals/{terminal_id}/state")
def get_state(terminal_id: int):
    state = terminals_data.get(terminal_id)
    if state:
        return JSONResponse(state)
    return JSONResponse({"error": "Terminal not found"}, status=404)

@app.websocket("/ws/live")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    ws_connections.append(websocket)
    try:
        while True:
            # Simulate sending state updates (in real app, use Redis pub/sub)
            await websocket.send_json({
                "type": "state_update",
                "timestamp": datetime.utcnow().isoformat(),
                "message": "Mock live update"
            })
            await asyncio.sleep(1)
    except WebSocketDisconnect:
        ws_connections.remove(websocket)

# Helper to broadcast updates (in real app, use Redis pub/sub)
async def broadcast_state_update(data: Dict):
    for ws in ws_connections:
        try:
            await ws.send_json(data)
        except:
            pass

# Startup event placeholder
@app.on_event("startup")
async def startup_event():
    # Initialize with sample terminal data
    for tid in [42, 101, 202]:
        terminals_data[tid] = {
            "id": tid,
            "name": f"Terminal-{tid}",
            "type": "sensor",
            "latitude": 37.7749,
            "longitude": -122.4194,
            "status": "active",
            "last_seen": datetime.utcnow().isoformat()
        }
    print("[API] SatLink API initialized with sample terminals")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=3000)


