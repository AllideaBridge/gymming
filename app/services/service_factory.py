import boto3

from app.repositories.repository_change_ticket import ChangeTicketRepository
from app.repositories.repository_schedule import ScheduleRepository
from app.repositories.repository_trainer import TrainerRepository
from app.repositories.repository_trainer_availability import TrainerAvailabilityRepository
from app.repositories.repository_trainer_fcm_token import TrainerFcmTokenRepository
from app.repositories.repository_trainer_user import TrainerUserRepository
from app.repositories.repository_user_fcm_token import UserFcmTokenRepository
from app.repositories.repository_users import UserRepository
from app.services.service_change_ticket import ChangeTicketService
from app.services.service_image import ImageService
from app.services.service_schedule import ScheduleService
from app.services.service_trainer import TrainerService
from app.services.service_trainer_user import TrainerUserService
from app.services.service_user import UserService
from database import db


class ServiceFactory:
    @staticmethod
    def user_service():
        return UserService(
            user_repository=UserRepository(db=db),
            user_fcm_repository=UserFcmTokenRepository(db=db)
        )

    @staticmethod
    def change_ticket_service():
        return ChangeTicketService(
            change_ticket_repository=ChangeTicketRepository(db=db),
            schedule_repository=ScheduleRepository(db=db),
            schedule_service=ServiceFactory.schedule_service(),
            user_repository=UserRepository(db=db),
            trainer_user_repository=TrainerUserRepository(db=db),
            trainer_repository=TrainerRepository(db=db)
        )

    @staticmethod
    def trainer_service():
        return TrainerService(
            trainer_repository=TrainerRepository(db=db),
            trainer_availability_repository=TrainerAvailabilityRepository(db=db),
            trainer_fcm_repository=TrainerFcmTokenRepository(db=db)
        )

    @staticmethod
    def schedule_service():
        return ScheduleService(
            schedule_repository=ScheduleRepository(db=db),
            trainer_availability_repository=TrainerAvailabilityRepository(db=db),
            trainer_user_repository=TrainerUserRepository(db=db),
            trainer_repository=TrainerRepository(db=db)
        )

    @staticmethod
    def image_service():
        return ImageService(
            s3=boto3.client('s3'),
            bucket='gymming'
        )

    @staticmethod
    def trainer_user_service():
        return TrainerUserService(
            tu_repository=TrainerUserRepository(db=db),
            user_repository=UserRepository(db=db),
            trainer_repository=TrainerRepository(db=db),
            image_service=ServiceFactory.image_service()
        )
