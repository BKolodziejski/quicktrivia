from sqlalchemy import (
    Column,
    Boolean,
    Integer,
    Text,
    ForeignKey,
)

from sqlalchemy.orm import relationship

from .meta import Base

class Answer(Base):
    __tablename__ = 'answers'
    id = Column(Integer, primary_key=True)
    content = Column(Text)
    is_correct = Column(Boolean(name='correct'))

    question_id = Column(ForeignKey('questions.id'), nullable=False)
    question = relationship('Question', backref='answers')
