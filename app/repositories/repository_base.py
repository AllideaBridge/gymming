from typing import Generic, TypeVar, Type, Optional, List

from flask_sqlalchemy import SQLAlchemy

T = TypeVar('T')


class BaseRepository(Generic[T]):
    def __init__(self, model: Type[T], db: SQLAlchemy):
        self.model = model
        self.db = db

    def create(self, obj: T) -> T:
        self.db.session.add(obj)
        self.db.session.commit()
        self.db.session.refresh(obj)
        return obj

    def get(self, id: int) -> Optional[T]:
        return self.model.query.get(id)

    def get_all(self) -> List[T]:
        return self.model.query.all()

    def update(self, obj: T) -> T:
        self.db.session.commit()
        self.db.session.refresh(obj)
        return obj

    def delete(self, obj: T) -> bool:
        self.db.session.delete(obj)
        self.db.session.commit()
        return True
