from fastapi import FastAPI, Response, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
import uuid
import json
import time

class ConnectionManager:
    def __init__(self):
        self.active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def send_personal_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            await connection.send_text(message)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

indexes_cache = {}
checkboxes = [{
    'uuid': str(uuid.uuid4()),
    'isChecked': False,
} for _ in range(100)]

for index, checkbox in enumerate(checkboxes):
    indexes_cache[checkbox['uuid']] = index

@app.get('/api/v1/')
def root():
    return {
        'version': '1.0.0'
    }

@app.get('/api/v1/checkboxes')
def get_checkboxes():
    return checkboxes

@app.patch('/api/v1/checkboxes/{uuid}')
def update_checkbox(uuid: uuid.UUID, isChecked: bool):
    index = indexes_cache.get(uuid)
    if index is not None:
        checkboxes[index]['isChecked'] = isChecked
        return checkboxes[index]
    return Response(status_code=404)

manager = ConnectionManager()

@app.websocket("/api/v1/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    await websocket.send_json({
        'action': 'update_checkboxes',
        'data': checkboxes
    })
    last_sync = time.time()
    try:
        while True:
            # if last_sync was more than 30 seconds ago, send all checkboxes
            if time.time() - last_sync > 30:
                await websocket.send_json({
                    'action': 'update_checkboxes',
                    'data': checkboxes
                })
                last_sync = time.time()
                
            data = await websocket.receive_json()
            action = data.get('action')
            if action == 'update_checkbox':
                # Update checkbox
                # data = { action: 'update_checkbox', data: { uuid: '...', isChecked: true } }
                uuid = data.get('data', {}).get('uuid')
                isChecked = bool(data.get('data', {}).get('isChecked'))
                index = indexes_cache.get(uuid)
                if index is not None:
                    checkboxes[index]['isChecked'] = isChecked
                    await manager.broadcast(json.dumps({
                        'action': 'update_checkbox',
                        'data': checkboxes[index]
                    }))
                else:
                    await websocket.send_json({
                        'error': 'Checkbox not found'
                    })
                
            else:
                await websocket.send_json({
                    'error': 'Invalid action'
                })
    except WebSocketDisconnect:
        manager.disconnect(websocket)

if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app)
