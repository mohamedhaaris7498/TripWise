import uvicorn
from app.config import settings

if __name__ == "__main__":
    print(f"Starting TripWise REST API on http://{settings.HOST}:{settings.PORT}")
    print(f"Swagger API Documentation: http://127.0.0.1:{settings.PORT}/docs")
    print(f"ReDoc Documentation: http://127.0.0.1:{settings.PORT}/redoc")
    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG
    )
