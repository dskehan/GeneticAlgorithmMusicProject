"""
WebSocket Manager

Manages WebSocket connections for real-time evolution updates.
"""

import json
from typing import Dict, List, Any
from fastapi import WebSocket
import asyncio


class WebSocketManager:
    """Manages WebSocket connections for real-time updates."""
    
    def __init__(self):
        # job_id -> list of websockets
        self.connections: Dict[str, List[WebSocket]] = {}
    
    async def connect(self, job_id: str, websocket: WebSocket):
        """Connect a WebSocket to a specific job."""
        if job_id not in self.connections:
            self.connections[job_id] = []
        
        self.connections[job_id].append(websocket)
        print(f"📡 WebSocket connected to job {job_id}")
    
    async def disconnect(self, job_id: str, websocket: WebSocket):
        """Disconnect a WebSocket from a job."""
        if job_id in self.connections:
            try:
                self.connections[job_id].remove(websocket)
                print(f"📡 WebSocket disconnected from job {job_id}")
                
                # Clean up empty job connections
                if not self.connections[job_id]:
                    del self.connections[job_id]
            except ValueError:
                pass  # WebSocket not in list
    
    async def broadcast_to_job(self, job_id: str, data: Dict[str, Any]):
        """Broadcast data to all WebSockets connected to a specific job."""
        if job_id not in self.connections:
            return
        
        # Create message
        message = json.dumps({
            "type": "evolution_update",
            "job_id": job_id,
            "data": data
        })
        
        # Send to all connected clients for this job
        disconnected = []
        for websocket in self.connections[job_id]:
            try:
                await websocket.send_text(message)
            except Exception as e:
                print(f"❌ Error sending to WebSocket: {e}")
                disconnected.append(websocket)
        
        # Remove disconnected WebSockets
        for websocket in disconnected:
            await self.disconnect(job_id, websocket)
    
    async def broadcast_to_all(self, data: Dict[str, Any]):
        """Broadcast data to all connected WebSockets."""
        message = json.dumps({
            "type": "global_update",
            "data": data
        })
        
        all_websockets = []
        for job_connections in self.connections.values():
            all_websockets.extend(job_connections)
        
        disconnected = []
        for websocket in all_websockets:
            try:
                await websocket.send_text(message)
            except Exception as e:
                print(f"❌ Error broadcasting to WebSocket: {e}")
                disconnected.append(websocket)
        
        # Clean up disconnected WebSockets
        for websocket in disconnected:
            for job_id, job_connections in self.connections.items():
                if websocket in job_connections:
                    await self.disconnect(job_id, websocket)
                    break
    
    async def send_to_job(self, job_id: str, message_type: str, data: Dict[str, Any]):
        """Send a specific message type to all clients of a job."""
        message = json.dumps({
            "type": message_type,
            "job_id": job_id,
            "data": data
        })
        
        if job_id in self.connections:
            disconnected = []
            for websocket in self.connections[job_id]:
                try:
                    await websocket.send_text(message)
                except Exception as e:
                    print(f"❌ Error sending {message_type} to WebSocket: {e}")
                    disconnected.append(websocket)
            
            # Remove disconnected WebSockets
            for websocket in disconnected:
                await self.disconnect(job_id, websocket)
    
    def get_connection_count(self, job_id: str = None) -> int:
        """Get the number of active connections."""
        if job_id:
            return len(self.connections.get(job_id, []))
        else:
            return sum(len(connections) for connections in self.connections.values())
    
    def get_active_jobs(self) -> List[str]:
        """Get list of jobs with active WebSocket connections."""
        return list(self.connections.keys())
    
    async def cleanup(self):
        """Clean up all connections."""
        for job_id in list(self.connections.keys()):
            for websocket in self.connections[job_id][:]:  # Copy list to avoid modification during iteration
                try:
                    await websocket.close()
                except:
                    pass
                await self.disconnect(job_id, websocket)
        
        self.connections.clear()
        print("🧹 WebSocket manager cleaned up")