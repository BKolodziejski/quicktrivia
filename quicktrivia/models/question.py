from sqlalchemy import (
    Column,
    Integer,
    Text,
)

from .meta import Base
import os

class Question(Base):
    __tablename__ = 'questions'
    id = Column(Integer, primary_key=True)
    img_name = Column(Text)
    content = Column(Text)

    @property
    def get_img(self):
        if self.img_name:
            return os.path.join('media', self.img_name)
        else:
            return None

    @property
    def get_correct_answer(self):
        for i in self.answers:
            if i.is_correct:
                return i
