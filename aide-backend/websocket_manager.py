"""
WebSocket Manager

Manages WebSocket connections for real-time experiment updates.
"""

import json
import asyncio
from typing import Dict, List, Any
from fastapi import WebSocket, WebSocketDisconnect
import logging

logger = logging.getLogger(__name__)

class WebSocketManager:
    """Manages WebSocket connections for real-time updates."""
    
    def __init__(self):
        # Dictionary mapping experiment_id to list of WebSocket connections
        self.active_connections: Dict[str, List[WebSocket]] = {}
        self.connection_info: Dict[WebSocket, Dict[str, Any]] = {}

    async def connect(self, websocket: WebSocket, experiment_id: str):
        """Accept a new WebSocket connection for an experiment."""
        await websocket.accept()
        
        # Add to active connections
        if experiment_id not in self.active_connections:
            self.active_connections[experiment_id] = []
        
        self.active_connections[experiment_id].append(websocket)
        self.connection_info[websocket] = {
            "experiment_id": experiment_id,
            "connected_at": asyncio.get_event_loop().time()
        }
        
        logger.info(f"WebSocket connected for experiment {experiment_id}")
        
        try:
            # Send initial connection confirmation
            await self.send_to_connection(websocket, {
                "type": "connection_established",
                "data": {
                    "experimentId": experiment_id,
                    "message": "Connected to experiment updates"
                }
            })
            
            # Keep connection alive and handle incoming messages
            while True:
                try:
                    # Wait for messages from client (heartbeat, etc.)
                    message = await asyncio.wait_for(
                        websocket.receive_text(), 
                        timeout=30.0  # 30 second timeout
                    )
                    
                    # Handle client messages if needed
                    await self._handle_client_message(websocket, experiment_id, message)
                    
                except asyncio.TimeoutError:
                    # Send heartbeat to keep connection alive
                    await self.send_to_connection(websocket, {
                        "type": "heartbeat",
                        "data": {"timestamp": asyncio.get_event_loop().time()}
                    })
                    
        except WebSocketDisconnect:
            logger.info(f"WebSocket disconnected for experiment {experiment_id}")
        except Exception as e:
            logger.error(f"WebSocket error for experiment {experiment_id}: {str(e)}")
        finally:
            await self.disconnect(websocket, experiment_id)

    async def disconnect(self, websocket: WebSocket, experiment_id: str):
        """Remove a WebSocket connection."""
        # Remove from active connections
        if experiment_id in self.active_connections:
            if websocket in self.active_connections[experiment_id]:
                self.active_connections[experiment_id].remove(websocket)
            
            # Clean up empty experiment connection lists
            if not self.active_connections[experiment_id]:
                del self.active_connections[experiment_id]
        
        # Remove connection info
        if websocket in self.connection_info:
            del self.connection_info[websocket]
        
        logger.info(f"WebSocket disconnected and cleaned up for experiment {experiment_id}")

    async def send_to_experiment(self, experiment_id: str, message: Dict[str, Any]):
        """Send a message to all connections for a specific experiment."""
        if experiment_id not in self.active_connections:
            logger.warning(f"No active connections for experiment {experiment_id}")
            return
        
        # Get list of connections (copy to avoid modification during iteration)
        connections = self.active_connections[experiment_id].copy()
        
        # Send to all connections
        disconnected_connections = []
        for connection in connections:
            try:
                await self.send_to_connection(connection, message)
            except Exception as e:
                logger.error(f"Failed to send message to connection: {str(e)}")
                disconnected_connections.append(connection)
        
        # Clean up disconnected connections
        for connection in disconnected_connections:
            await self.disconnect(connection, experiment_id)

    async def send_to_connection(self, websocket: WebSocket, message: Dict[str, Any]):
        """Send a message to a specific WebSocket connection."""
        try:
            await websocket.send_text(json.dumps(message))
        except Exception as e:
            logger.error(f"Failed to send WebSocket message: {str(e)}")
            raise

    async def broadcast_to_all(self, message: Dict[str, Any]):
        """Broadcast a message to all active connections."""
        for experiment_id in list(self.active_connections.keys()):
            await self.send_to_experiment(experiment_id, message)

    async def _handle_client_message(self, websocket: WebSocket, experiment_id: str, message: str):
        """Handle incoming messages from clients."""
        try:
            data = json.loads(message)
            message_type = data.get("type")
            
            if message_type == "ping":
                # Respond to ping with pong
                await self.send_to_connection(websocket, {
                    "type": "pong",
                    "data": {"timestamp": asyncio.get_event_loop().time()}
                })
            elif message_type == "subscribe":
                # Handle subscription requests (if needed)
                logger.info(f"Client subscribed to updates for experiment {experiment_id}")
            else:
                logger.warning(f"Unknown message type from client: {message_type}")
                
        except json.JSONDecodeError:
            logger.error(f"Invalid JSON message from client: {message}")
        except Exception as e:
            logger.error(f"Error handling client message: {str(e)}")

    def get_connection_count(self, experiment_id: str = None) -> int:
        """Get the number of active connections."""
        if experiment_id:
            return len(self.active_connections.get(experiment_id, []))
        else:
            return sum(len(connections) for connections in self.active_connections.values())

    def get_active_experiments(self) -> List[str]:
        """Get list of experiment IDs with active connections."""
        return list(self.active_connections.keys())

    def get_connection_stats(self) -> Dict[str, Any]:
        """Get WebSocket connection statistics."""
        total_connections = self.get_connection_count()
        active_experiments = len(self.active_connections)
        
        experiment_stats = {}
        for exp_id, connections in self.active_connections.items():
            experiment_stats[exp_id] = len(connections)
        
        return {
            "totalConnections": total_connections,
            "activeExperiments": active_experiments,
            "experimentStats": experiment_stats,
            "connectionDetails": [
                {
                    "experimentId": info["experiment_id"],
                    "connectedAt": info["connected_at"]
                }
                for info in self.connection_info.values()
            ]
        }
