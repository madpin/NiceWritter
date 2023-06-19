from sqlalchemy import Column, ForeignKey, Integer, String, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.orm import sessionmaker

engine = create_engine("sqlite:///content.db")
Session = sessionmaker(bind=engine)
session = Session()

Base = declarative_base()


class Book(Base):
    __tablename__ = "books"

    id = Column(Integer, primary_key=True)
    title = Column(String)
    subtitle = Column(String)
    description = Column(String)
    short_description = Column(String)

    chapters = relationship("Chapter", back_populates="book")


class Chapter(Base):
    __tablename__ = "chapters"

    id = Column(Integer, primary_key=True)
    title = Column(String)
    subtitle = Column(String)
    description = Column(String)
    short_description = Column(String)

    book_id = Column(Integer, ForeignKey("books.id"))
    book = relationship("Book", back_populates="chapters")
    subchapters = relationship("Subchapter", back_populates="chapter")


class Subchapter(Base):
    __tablename__ = "subchapters"

    id = Column(Integer, primary_key=True)
    title = Column(String)
    subtitle = Column(String)
    description = Column(String)
    short_description = Column(String)

    chapter_id = Column(Integer, ForeignKey("chapters.id"))
    chapter = relationship("Chapter", back_populates="subchapters")
    sections = relationship("Section", back_populates="subchapter")


class Section(Base):
    __tablename__ = "sections"

    id = Column(Integer, primary_key=True)
    title = Column(String)
    subtitle = Column(String)
    description = Column(String)
    short_description = Column(String)
    content = Column(String)

    subchapter_id = Column(Integer, ForeignKey("subchapters.id"))
    subchapter = relationship("Subchapter", back_populates="sections")


Base.metadata.create_all(engine)
