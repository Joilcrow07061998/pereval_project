from sqlalchemy import select
from sqlalchemy.orm import Session

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
