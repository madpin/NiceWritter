from typing import Optional
from pydantic import BaseModel
from logger import initialize_logger
import logging
from nicegui import app, ui, Client

logger = logging.getLogger(__name__)


class Section(BaseModel):
    id: str
    title: Optional[str]
    description: Optional[str]
    content: Optional[str]
    pages: Optional[int]


class Subchapter(BaseModel):
    id: str
    title: Optional[str]
    description: Optional[str]
    pages: Optional[int]
    sections: list[Section]


class Chapter(BaseModel):
    id: str
    title: Optional[str]
    description: str
    pages: Optional[int]
    subchapters: list[Subchapter]


class Book(BaseModel):
    id: str
    title: Optional[str]
    description: str
    pages: Optional[int]
    chapters: list[Chapter]


book = Book(
    id="The Tech Consultant's Guide: From Code to Consulting",
    description="A Practical Handbook for Aspiring Tech Consultants",
    chapters=[
        Chapter(
            id="1",
            description="Introduction to Tech Consulting - An overview of the tech consulting industry, the skills required, and the opportunities available. (20)",
            subchapters=[
                Subchapter(
                    id="1.1",
                    description="What is Tech Consulting? - A definition of tech consulting and its role in the modern business world. (10)",
                    sections=[
                        Section(
                            id="1.1.1",
                            description="The History of Tech Consulting - A brief look at the evolution of tech consulting and its impact on the industry. (5)",
                        ),
                        Section(
                            id="1.1.2",
                            description="The Benefits of Tech Consulting - An exploration of the advantages of hiring a tech consultant for your business. (5)",
                        ),
                    ],
                ),
                Subchapter(
                    id="1.2",
                    description="The Skills Required for Tech Consulting - An examination of the key skills and competencies needed to succeed as a tech consultant. (10)",
                    sections=[
                        Section(
                            id="1.2.1",
                            description="Technical Skills - A discussion of the technical skills required for tech consulting, including programming languages, software development tools, and data analysis techniques. (5)",
                        ),
                        Section(
                            id="1.2.2",
                            description="Soft Skills - An exploration of the soft skills that are essential for success in tech consulting, such as communication, problem-solving, and teamwork. (5)",
                        ),
                    ],
                ),
            ],
        ),
        # Rest of model omitted for brevity
    ],
)

obj = book.dict


@ui.page("/")
def main_page() -> None:
    ui.label(f"The Tech Consultant's Guide: From Code to Consulting").classes("text-h4")
    with ui.grid(columns=2):
        with ui.column():
            test = ui.button("test", on_click=lambda: exp.enable)
        with ui.expansion(
            "Expand!",
            icon="work",
            # on_click=lambda: ui.notify("Hi!", closeBtn="OK"),
        ).classes("w-full") as exp:
            ui.label("inside the expansion inside the expansion inside the expansion inside the expansion")
            ui.label("inside the expansion")
            ui.label("inside the expansion")
            ui.label("inside the expansion")


def show_section(section: Section) -> None:
    ui.label(f"Section {section.id}: {section.description}")


if __name__ in {"__main__", "__mp_main__"}:
    logger = initialize_logger(__name__)
    ui.run(storage_secret="THIS_NEEDS_TO_BE_CHANGED", port=81)
