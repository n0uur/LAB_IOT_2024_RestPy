from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get('/api/hello')
def hello_world():
    return {
        'message': 'Hello World'
    }

if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app)
