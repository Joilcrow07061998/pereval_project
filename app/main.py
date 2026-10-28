from fastapi import FastAPI
from fastapi.responses import JSONResponse
from sqlalchemy.exc import SQLAlchemyError

from app.database import Base, SessionLocal, engine
from app import models
from app.repository import PassRepository
from app.schemas import PassSubmission

app = FastAPI(title="API перевалов ФСТР")


@app.on_event("startup")
def create_tables() -> None:
    Base.metadata.create_all(bind=engine)


@app.get("/")
def home() -> dict[str, str]:
    return {"message": "API для отправки данных о горных перевалах ФСТР"}


@app.post("/submitData")
def submit_data(submission: PassSubmission) -> JSONResponse:
    missing_fields = submission.missing_required_fields()
    if missing_fields:
        return JSONResponse(
            status_code=400,
            content={
                "status": 400,
                "message": "Не заполнены обязательные поля: " + ", ".join(missing_fields),
                "id": None,
            },
        )

    session = SessionLocal()
    try:
        pass_id = PassRepository(session).add_pass(submission)
        return JSONResponse(
            status_code=200,
            content={"status": 200, "message": None, "id": pass_id},
        )
    except SQLAlchemyError:
        session.rollback()
        return JSONResponse(
            status_code=500,
            content={
                "status": 500,
                "message": "Не удалось сохранить данные в базе данных",
                "id": None,
            },
        )
    finally:
        session.close()
