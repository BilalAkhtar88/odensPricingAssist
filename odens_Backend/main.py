from fastapi import FastAPI
from routes import health, auth, user, predict

app = FastAPI(title="Odens Pricing Backend")

@app.get("/", summary="Welcome Message!")
def welcome():
    return {"status": "ok", "message": "Welcome to Odens Pricing Assistant"}


# Register routers
app.include_router(health.router, prefix="/health", tags=["Health"])
app.include_router(auth.router, prefix="/auth", tags=["Authentication"])
app.include_router(user.router, prefix="/user", tags=["User"])
app.include_router(predict.router, prefix="/predict", tags=["Prediction"]) 
