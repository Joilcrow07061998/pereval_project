from typing import Any

from pydantic import BaseModel, ConfigDict


class UserData(BaseModel):
    model_config = ConfigDict(extra="ignore")

    email: str | None = None
    fam: str | None = None
    name: str | None = None
    otc: str | None = None
    phone: str | None = None


class CoordinatesData(BaseModel):
    model_config = ConfigDict(extra="ignore")

    latitude: float | None = None
    longitude: float | None = None
    height: int | None = None


class LevelData(BaseModel):
    model_config = ConfigDict(extra="ignore")

    winter: str | None = None
    summer: str | None = None
    autumn: str | None = None
    spring: str | None = None


class ImageData(BaseModel):
    model_config = ConfigDict(extra="ignore")

    data: str | None = None
    title: str | None = None


class PassSubmission(BaseModel):
    model_config = ConfigDict(extra="ignore")

    beauty_title: str | None = None
    title: str | None = None
    other_titles: str | None = None
    connect: str | None = None
    add_time: str | None = None
    user: UserData | None = None
    coords: CoordinatesData | None = None
    level: LevelData | None = None
    images: list[ImageData] | None = None

    def missing_required_fields(self) -> list[str]:
        missing = []
        for field in ("title", "add_time", "user", "coords", "level"):
            if getattr(self, field) is None:
                missing.append(field)

        if self.user is not None:
            for field in ("email", "fam", "name", "phone"):
                if not getattr(self.user, field):
                    missing.append(f"user.{field}")

        if self.coords is not None:
            for field in ("latitude", "longitude", "height"):
                if getattr(self.coords, field) is None:
                    missing.append(f"coords.{field}")

        return missing


class SubmissionResult(BaseModel):
    status: int
    message: str | None = None
    id: int | None = None
