import uvicorn
from app import app
from app.database import engine, Base

# Create all tables
Base.metadata.create_all(bind=engine)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)

