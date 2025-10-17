from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import quiz, dashboard

app = FastAPI(
    title="Colmeia API",
    description="API para o Quiz de Análise de Crédito da Colmeia",
    version="1.0.0",
)
origins = ['*']
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(quiz.router, prefix="/api/quiz", tags=["Quiz"])
app.include_router(dashboard.router, prefix="/api", tags=["Dashboard & History"])

@app.get("/", tags=["Root"])
async def read_root():
    return {"message": "Welcome to the Colmeia API!"}

