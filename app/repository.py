from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.models import Coordinates, MountainPass, PassImage, PassLevel, User
from app.schemas import PassSubmission


class PassRepository:
    def __init__(self, session: Session):
        self.session = session

    def add_pass(self, submission: PassSubmission) -> int:
        user_data = submission.user
        coordinates_data = submission.coords
        level_data = submission.level

        user = self.session.scalar(
            select(User).where(User.email == user_data.email)
        )
        if user is None:
            user = User(
                email=user_data.email,
                fam=user_data.fam,
                name=user_data.name,
                otc=user_data.otc,
                phone=user_data.phone,
            )
            self.session.add(user)
            self.session.flush()
        else:
            user.fam = user_data.fam
            user.name = user_data.name
            user.otc = user_data.otc
            user.phone = user_data.phone

        mountain_pass = MountainPass(
            beauty_title=submission.beauty_title,
            title=submission.title,
            other_titles=submission.other_titles,
            connect=submission.connect,
            add_time=submission.add_time,
            status="new",
            user=user,
            coordinates=Coordinates(
                latitude=coordinates_data.latitude,
                longitude=coordinates_data.longitude,
                height=coordinates_data.height,
            ),
            level=PassLevel(
                winter=level_data.winter,
                summer=level_data.summer,
                autumn=level_data.autumn,
                spring=level_data.spring,
            ),
        )

        for image_data in submission.images or []:
            if image_data.data is None:
                continue
            mountain_pass.images.append(
                PassImage(data=image_data.data, title=image_data.title)
            )

        self.session.add(mountain_pass)
        self.session.commit()
        self.session.refresh(mountain_pass)
        return mountain_pass.id

    def get_pass_by_id(self, pass_id: int) -> MountainPass | None:
        statement = (
            select(MountainPass)
            .where(MountainPass.id == pass_id)
            .options(
                selectinload(MountainPass.user),
                selectinload(MountainPass.coordinates),
                selectinload(MountainPass.level),
                selectinload(MountainPass.images),
            )
        )
        return self.session.scalar(statement)

    def get_passes_by_email(self, email: str) -> list[MountainPass]:
        statement = (
            select(MountainPass)
            .join(MountainPass.user)
            .where(User.email == email)
            .options(
                selectinload(MountainPass.user),
                selectinload(MountainPass.coordinates),
                selectinload(MountainPass.level),
                selectinload(MountainPass.images),
            )
            .order_by(MountainPass.id)
        )
        return list(self.session.scalars(statement).all())

    def update_pass(
        self, pass_id: int, submission: PassSubmission
    ) -> tuple[bool, str]:
        mountain_pass = self.get_pass_by_id(pass_id)
        if mountain_pass is None:
            return False, "Перевал с таким id не найден"

        if mountain_pass.status != "new":
            return False, "Нельзя редактировать перевал: его статус не new"

        mountain_pass.beauty_title = submission.beauty_title
        mountain_pass.title = submission.title
        mountain_pass.other_titles = submission.other_titles
        mountain_pass.connect = submission.connect
        mountain_pass.add_time = submission.add_time

        coordinates_data = submission.coords
        if mountain_pass.coordinates is None:
            mountain_pass.coordinates = Coordinates(
                latitude=coordinates_data.latitude,
                longitude=coordinates_data.longitude,
                height=coordinates_data.height,
            )
        else:
            mountain_pass.coordinates.latitude = coordinates_data.latitude
            mountain_pass.coordinates.longitude = coordinates_data.longitude
            mountain_pass.coordinates.height = coordinates_data.height

        level_data = submission.level
        if mountain_pass.level is None:
            mountain_pass.level = PassLevel(
                winter=level_data.winter,
                summer=level_data.summer,
                autumn=level_data.autumn,
                spring=level_data.spring,
            )
        else:
            mountain_pass.level.winter = level_data.winter
            mountain_pass.level.summer = level_data.summer
            mountain_pass.level.autumn = level_data.autumn
            mountain_pass.level.spring = level_data.spring

        mountain_pass.images = [
            PassImage(data=image.data, title=image.title)
            for image in submission.images or []
            if image.data is not None
        ]

        # Данные пользователя здесь намеренно не меняются.
        self.session.commit()
        return True, "Данные перевала успешно обновлены"
