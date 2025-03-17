from fastapi import FastAPI
from app.routers import hello, users, posts
from app.database import Base, engine
from fastapi.middleware.cors import CORSMiddleware


app = FastAPI()

# Permite solicitudes desde todos los orígenes
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Puedes especificar dominios como ["http://example.com"]
    allow_credentials=True,
    allow_methods=["*"],  # Permite todos los métodos HTTP (GET, POST, etc.)
    allow_headers=["*"],  # Permite todas las cabeceras
)

# Incluir routers
app.include_router(hello.router)
app.include_router(users.router)
app.include_router(posts.router)

@app.get("/")
def read_root():
    return {"message": "Hello World from FastAPI"}
