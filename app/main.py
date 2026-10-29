import logging
from datetime import datetime

from fastapi import FastAPI, Query
from fastapi.responses import JSONResponse
from sqlalchemy.exc import SQLAlchemyError

from app import models  # Регистрируем модели перед созданием таблиц.
from app.database import Base, SessionLocal, engine
from app.models import MountainPass
from app.repository import PassRepository
from app.schemas import PassSubmission

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="API перевалов ФСТР")


@app.on_event("startup")
def create_tables() -> None:
    try:
        Base.metadata.create_all(bind=engine)
    except SQLAlchemyError:
        logger.exception("Не удалось подключиться к базе данных при запуске")


def serialize_pass(mountain_pass: MountainPass) -> dict:
    user = mountain_pass.user
    coordinates = mountain_pass.coordinates
    level = mountain_pass.level

    return {
        "id": mountain_pass.id,
        "beauty_title": mountain_pass.beauty_title,
        "title": mountain_pass.title,
        "other_titles": mountain_pass.other_titles,
        "connect": mountain_pass.connect,
        "add_time": mountain_pass.add_time,
        "date_added": (
            mountain_pass.date_added.isoformat()
            if isinstance(mountain_pass.date_added, datetime)
            else mountain_pass.date_added
        ),
        "status": mountain_pass.status,
        "user": {
            "email": user.email,
            "fam": user.fam,
            "name": user.name,
            "otc": user.otc,
            "phone": user.phone,
        },
        "coords": (
            {
                "latitude": coordinates.latitude,
                "longitude": coordinates.longitude,
                "height": coordinates.height,
            }
            if coordinates is not None
            else None
        ),
        "level": (
            {
                "winter": level.winter,
                "summer": level.summer,
                "autumn": level.autumn,
                "spring": level.spring,
            }
            if level is not None
            else None
        ),
        "images": [
            {"data": image.data, "title": image.title}
            for image in mountain_pass.images
        ],
    }


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
        logger.exception("Не удалось сохранить данные о перевале")
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


@app.get("/submitData/{pass_id}")
def get_pass(pass_id: int) -> JSONResponse:
    session = SessionLocal()
    try:
        mountain_pass = PassRepository(session).get_pass_by_id(pass_id)
        if mountain_pass is None:
            return JSONResponse(
                status_code=404,
                content={"message": "Перевал с таким id не найден"},
            )
        return JSONResponse(status_code=200, content=serialize_pass(mountain_pass))
    except SQLAlchemyError:
        logger.exception("Не удалось получить данные о перевале")
        return JSONResponse(
            status_code=500,
            content={"message": "Не удалось получить данные из базы данных"},
        )
    finally:
        session.close()


@app.patch("/submitData/{pass_id}")
def edit_pass(pass_id: int, submission: PassSubmission) -> JSONResponse:
    missing_fields = submission.missing_required_fields()
    if missing_fields:
        return JSONResponse(
            status_code=400,
            content={
                "state": 0,
                "message": "Не заполнены обязательные поля: " + ", ".join(missing_fields),
            },
        )

    session = SessionLocal()
    try:
        updated, message = PassRepository(session).update_pass(pass_id, submission)
        if not updated:
            return JSONResponse(
                status_code=400,
                content={"state": 0, "message": message},
            )
        return JSONResponse(
            status_code=200,
            content={"state": 1, "message": message},
        )
    except SQLAlchemyError:
        session.rollback()
        logger.exception("Не удалось обновить данные о перевале")
        return JSONResponse(
            status_code=500,
            content={"state": 0, "message": "Не удалось обновить данные в базе данных"},
        )
    finally:
        session.close()


@app.get("/submitData")
def get_passes_by_user(user__email: str = Query(..., min_length=1)) -> JSONResponse:
    session = SessionLocal()
    try:
        passes = PassRepository(session).get_passes_by_email(user__email)
        return JSONResponse(
            status_code=200,
            content=[serialize_pass(mountain_pass) for mountain_pass in passes],
        )
    except SQLAlchemyError:
        logger.exception("Не удалось получить перевалы пользователя")
        return JSONResponse(
            status_code=500,
            content={"message": "Не удалось получить данные из базы данных"},
        )
    finally:
        session.close()
