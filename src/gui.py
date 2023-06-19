#!/usr/bin/env python3
"""This is just a very simple authentication example.

Please see the `OAuth2 example at FastAPI <https://fastapi.tiangolo.com/tutorial/security/simple-oauth2/>`_  or
use the great `Authlib package <https://docs.authlib.org/en/v0.13/client/starlette.html#using-fastapi>`_ to implement a classing real authentication system.
Here we just demonstrate the NiceGUI integration.
"""
import json
import time
from fastapi.responses import RedirectResponse
from typing import List, Tuple

from langchain.chains import ConversationChain
from langchain.chat_models import ChatOpenAI

from nicegui import app, ui, Client
from dotenv import load_dotenv, find_dotenv
import requests

# from src.llm import get_completion
from llm import get_completion
import os
import logging
from logger import initialize_logger

logger = logging.getLogger(__name__)

# in reality users passwords would obviously need to be hashed
passwords = {"m": "p", "user2": "pass2"}

_ = load_dotenv(find_dotenv())  # read local .env file

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "not-set")

llm = ConversationChain(
    llm=ChatOpenAI(model_name="gpt-3.5-turbo", openai_api_key=OPENAI_API_KEY)
)

messages: List[Tuple[str, str, str]] = []
thinking: bool = False


@ui.refreshable
async def chat_messages() -> None:
    for name, text in messages:
        ui.chat_message(text=text, name=name, sent=name == "You")
    if thinking:
        ui.spinner(size="3rem").classes("self-center")
    await ui.run_javascript(
        "window.scrollTo(0, document.body.scrollHeight)", respond=False
    )


@ui.page("/")
def main_page() -> None:
    if not app.storage.user.get("authenticated", False):
        return RedirectResponse("/login")
    with ui.column().classes("absolute-center items-center"):
        ui.label(f'Hello {app.storage.user["username"]}!').classes("text-2xl")
        ui.button(
            # on_click=lambda: (app.storage.user.clear(), ui.open("/login"))
            on_click=lambda: ui.open("/page_layout")
        ).props("outline round icon=logout")


@ui.page("/login")
def login() -> None:
    def try_login() -> (
        None
    ):  # local function to avoid passing username and password as arguments
        if passwords.get(username.value) == password.value:
            app.storage.user.update({"username": username.value, "authenticated": True})
            ui.open("/")
        else:
            ui.notify("Wrong username or password", color="negative")

    if app.storage.user.get("authenticated", False):
        return RedirectResponse("/")
    with ui.card().classes("absolute-center"):
        username = ui.input("Username").on("keydown.enter", try_login)
        password = (
            ui.input("Password").on("keydown.enter", try_login).props("type=password")
        )
        ui.button("Log in", on_click=try_login)


@ui.page("/page_layout")
async def page_layout(client: Client):
    if not app.storage.user.get("authenticated", False):
        return RedirectResponse("/login")

    with ui.header(elevated=True).style("background-color: #3874c8").classes(
        "items-center justify-between"
    ):
        ui.button(on_click=lambda: left_drawer.toggle()).props(
            "flat color=white icon=menu"
        )
        ui.label("HEADER")
        ui.button(on_click=lambda: right_drawer.toggle()).props(
            "flat color=white icon=menu"
        )
    with ui.footer().style("background-color: #3874c8"):
        ui.label("FOOTER")

    with ui.left_drawer(fixed=False).style("background-color: #ebf1fa").props(
        "bordered"
    ) as left_drawer:
        ui.label("LEFT DRAWER")
    with ui.right_drawer(fixed=False).style("background-color: #ebf1fa").props(
        "bordered"
    ) as right_drawer:
        ui.label("RIGHT DRAWER")

    # with ui.row():
    txt_who = ui.textarea(
        label="Who he is:",
        value=(
            "You are an author, with cheesy humor, "
            "that writes about business, tech and consulting,"
            "focused on code examples language"
        ),
    ).style("width: 80%")
    txt_structure = ui.textarea(
        label="Structure:",
        value=(
            "Can you give the the chapters,"
            "subchapters and sections for a book "
            "about how to be a tech consultant, "
            "with aproximately 500 pages \n",
        ),
    ).style("width: 80%")
    txt_formatting = ui.textarea(
        label="Structure:",
        value=(
            "---\n"
            "The answer should be given in json format, "
            "using double quotes as delimiters \n"
            "with only the json content and nothing else, \n"
            "with the fields: \n"
            "\bbook_title as `bt`, subtitle as `ss`, "
            "chapters as `cs` (as a array), "
            "chapter_number as `cn`, chapter_title as `ct`, "
            "chapter_description as `cd`, chapter_pages as `cp`, "
            "subchapters as ss (as a array), "
            "subchapter_number(int) as `scn`, "
            "subchapter_title as `sct`, subchapter_description as `scd`, "
            "subchapter_pages as `scp`, sections (as a array) as `scs`,"
            "section_number(int) as `sn`, section_title as `st`, "
            "section_description as `sd`, section_pages as `sp`"
        ),
    ).style("width: 80%")

    def get_chapters():
        # return {
        #     "bt": "Book Title",
        #     "st": "Subtitle",
        #     "cs": [
        #         {
        #             "cn": 1,
        #             "ct": "Chapter 1",
        #             "cd": "Chapter 1 Description",
        #             "cp": 10,
        #             "ss": [
        #                 {
        #                     "scn": 1,
        #                     "sct": "Subchapter 1",
        #                     "scd": "Subchapter 1 Description",
        #                     "scp": 5,
        #                     "scs": [
        #                         {
        #                             "sn": 1,
        #                             "st": "Section 1",
        #                             "sd": "Section 1 Description",
        #                             "sp": 2,
        #                         },
        #                         {
        #                             "sn": 2,
        #                             "st": "Section 2",
        #                             "sd": "Section 2 Description",
        #                             "sp": 3,
        #                         },
        #                     ],
        #                 }
        #             ],
        #         },
        #         {
        #             "cn": 2,
        #             "ct": "Chapter 2",
        #             "cd": "Chapter 2 Description",
        #             "cp": 15,
        #             "ss": [],
        #         },
        #     ],
        # }

        response = """
        {
  "bt": "The Tech Consultant's Guide to Success",
  "ss": "A Comprehensive Handbook for Business and Technology Professionals",
  "cs": [
    {
      "cn": 1,
      "ct": "Introduction to Tech Consulting",
      "cd": "An overview of the tech consulting industry and the skills required to succeed.",
      "cp": 20,
      "ss": [
        {
          "scn": 1,
          "sct": "Defining Tech Consulting",
          "scd": "What is tech consulting and why is it important?",
          "scp": 10,
          "scs": [
            {
              "sn": 1,
              "st": "The Role of the Tech Consultant",
              "sd": "A detailed look at the responsibilities and expectations of a tech consultant.",
              "sp": 5
            },
            {
              "sn": 2,
              "st": "The Benefits of Tech Consulting",
              "sd": "Exploring the advantages of a career in tech consulting.",
              "sp": 5
            }
          ]
        },
        {
          "scn": 2,
          "sct": "Essential Skills for Tech Consultants",
          "scd": "A breakdown of the most important skills for success in tech consulting.",
          "scp": 10,
          "scs": [
            {
              "sn": 1,
              "st": "Technical Expertise",
              "sd": "Why a strong technical foundation is critical for tech consultants.",
              "sp": 5
            },
            {
              "sn": 2,
              "st": "Communication Skills",
              "sd": "How to effectively communicate with clients and team members.",
              "sp": 5
            }
          ]
        }
      ]
    
  }
]
}
"""
        re = requests.get("http://ifconfig.me")
        message_openai = f"{txt_who.value}\n\n{txt_structure.value}\n\n{txt_formatting.value}"
        logger.debug(f"Sending message: {message_openai}")

        response2 = get_completion(message_openai)
        logger.debug(f"Got response: {response}")
        # try:
        return json.loads(response)
        # except Exception as e:
        #     print(e)
        #     return {"cs": []}

    def chapters_to_tree(chapters):
        logger.debug("Converting chapters to tree")
        chapters_tree = []
        for chapter in chapters["cs"]:
            chapter_node = {
                "id": str(chapter["cn"]),
                # "description": chapter["ct"],
                "description": (
                    f"{chapter['ct']} - {chapter['cd']} " f"({chapter['cp']})"
                ),
                "children": [],
            }
            if chapter["ss"]:
                for subchapter in chapter["ss"]:
                    subchapter_node = {
                        "id": str(chapter["cn"]) + "." + str(subchapter["scn"]),
                        # "description": subchapter["sct"],
                        "description": (
                            f"{subchapter['sct']} - {subchapter['scd']} "
                            f"({subchapter['scp']})"
                        ),
                        "children": [],
                    }

                    if subchapter["scs"]:
                        for section in subchapter["scs"]:
                            section_node = {
                                "id": f"{chapter['cn']}.{subchapter['scn']}.{section['sn']}",
                                "description": (
                                    f"{section['st']} - {section['sd']} "
                                    f"({section['sp']})"
                                ),
                            }
                            subchapter_node["children"].append(section_node)
                    chapter_node["children"].append(subchapter_node)
            chapters_tree.append(chapter_node)
        return [
            {
                "id": str(chapters["bt"]),
                "description": chapters["ss"],
                "children": chapters_tree,
            }
        ]

    def update_tree():
        print("Building the Book!")
        tree_container.clear()
        logger.info("Building the Book!")
        ui.notify("Building the Book!")
        # message = f"{txt_who.value}\n\n{txt_structure.value}\n\n{txt_formatting.value}"

        # response = get_completion(message)
        # print(response)
        logger.debug("Getting chapters")

        logger.debug("This is the one that works")
        working_tree_array = [
            {
                "id": "The Tech Consultant's Guide: From Code to Consulting",
                "description": "A Practical Handbook for Aspiring Tech Consultants",
                "children": [
                    {
                        "id": "1",
                        "description": "Introduction to Tech Consulting - An overview of the tech consulting industry, the skills required, and the opportunities available. (20)",
                        "children": [
                            {
                                "id": "1.1",
                                "description": "What is Tech Consulting? - A definition of tech consulting and its role in the modern business world. (10)",
                                "children": [
                                    {
                                        "id": "1.1.1",
                                        "description": "The History of Tech Consulting - A brief look at the evolution of tech consulting and its impact on the industry. (5)",
                                    },
                                    {
                                        "id": "1.1.2",
                                        "description": "The Benefits of Tech Consulting - An exploration of the advantages of hiring a tech consultant for your business. (5)",
                                    },
                                ],
                            },
                            {
                                "id": "1.2",
                                "description": "The Skills Required for Tech Consulting - An examination of the key skills and competencies needed to succeed as a tech consultant. (10)",
                                "children": [
                                    {
                                        "id": "1.2.1",
                                        "description": "Technical Skills - A discussion of the technical skills required for tech consulting, including programming languages, software development tools, and data analysis techniques. (5)",
                                    },
                                    {
                                        "id": "1.2.2",
                                        "description": "Soft Skills - An exploration of the soft skills that are essential for success in tech consulting, such as communication, problem-solving, and teamwork. (5)",
                                    },
                                ],
                            },
                        ],
                    },
                    {
                        "id": "2",
                        "description": "Building Your Tech Consulting Business - A guide to starting and growing your own tech consulting business, including marketing, sales, and client management. (100)",
                        "children": [
                            {
                                "id": "2.1",
                                "description": "Setting Up Your Business - A step-by-step guide to setting up your tech consulting business, including legal and financial considerations. (20)",
                                "children": [
                                    {
                                        "id": "2.1.1",
                                        "description": "Choosing a Business Structure - An overview of the different legal structures available for your tech consulting business, and the pros and cons of each. (5)",
                                    },
                                    {
                                        "id": "2.1.2",
                                        "description": "Managing Your Finances - A guide to managing your finances as a tech consultant, including budgeting, invoicing, and taxes. (5)",
                                    },
                                    {
                                        "id": "2.1.3",
                                        "description": "Marketing Your Business - A crash course in marketing for tech consultants, including branding, social media, and content creation. (10)",
                                    },
                                ],
                            },
                            {
                                "id": "2.2",
                                "description": "Finding and Managing Clients - A comprehensive guide to finding and managing clients as a tech consultant, including sales techniques, client communication, and project management. (80)",
                                "children": [
                                    {
                                        "id": "2.2.1",
                                        "description": "Sales Techniques for Tech Consultants - An overview of the sales process for tech consultants, including prospecting, lead generation, and closing deals. (20)",
                                    },
                                    {
                                        "id": "2.2.2",
                                        "description": "Client Communication and Management - A guide to communicating effectively with clients and managing their expectations throughout the project lifecycle. (30)",
                                    },
                                    {
                                        "id": "2.2.3",
                                        "description": "Project Management for Tech Consultants - An introduction to project management principles and techniques for tech consultants, including agile methodologies and project planning tools. (30)",
                                    },
                                ],
                            },
                        ],
                    },
                    {
                        "id": "3",
                        "description": "Advanced Tech Consulting Techniques - A deep dive into advanced tech consulting techniques, including data analysis, machine learning, and cloud computing. (200)",
                        "children": [
                            {
                                "id": "3.1",
                                "description": "Data Analysis for Tech Consultants - An in-depth look at data analysis techniques for tech consultants, including data visualization, statistical analysis, and predictive modeling. (50)",
                                "children": [
                                    {
                                        "id": "3.1.1",
                                        "description": "Data Visualization Techniques - An exploration of the different data visualization tools and techniques available for tech consultants, including charts, graphs, and dashboards. (20)",
                                    },
                                    {
                                        "id": "3.1.2",
                                        "description": "Statistical Analysis for Tech Consultants - A guide to statistical analysis techniques for tech consultants, including hypothesis testing, regression analysis, and variance analysis. (20)",
                                    },
                                    {
                                        "id": "3.1.3",
                                        "description": "Predictive Modeling for Tech Consultants - An introduction to predictive modeling techniques for tech consultants, including machine learning algorithms and data mining tools. (10)",
                                    },
                                ],
                            },
                            {
                                "id": "3.2",
                                "description": "Cloud Computing for Tech Consultants - A guide to cloud computing technologies and their applications for tech consultants, including infrastructure as a service, platform as a service, and software as a service. (50)",
                                "children": [
                                    {
                                        "id": "3.2.1",
                                        "description": "Infrastructure as a Service - An overview of infrastructure as a service (IaaS) and its applications for tech consultants, including cloud storage, virtual machines, and networking. (20)",
                                    },
                                    {
                                        "id": "3.2.2",
                                        "description": "Platform as a Service - A guide to platform as a service (PaaS) and its applications for tech consultants, including cloud development platforms and database services. (20)",
                                    },
                                    {
                                        "id": "3.2.3",
                                        "description": "Software as a Service - An introduction to software as a service (SaaS) and its applications for tech consultants, including cloud-based productivity tools and enterprise software solutions. (10)",
                                    },
                                ],
                            },
                            {
                                "id": "3.3",
                                "description": "Emerging Technologies for Tech Consultants - A look at emerging technologies that are shaping the future of tech consulting, including blockchain, artificial intelligence, and the internet of things. (100)",
                                "children": [
                                    {
                                        "id": "3.3.1",
                                        "description": "Blockchain for Tech Consultants - An overview of blockchain technology and its applications for tech consultants, including smart contracts, decentralized applications, and cryptocurrency. (30)",
                                    },
                                    {
                                        "id": "3.3.2",
                                        "description": "Artificial Intelligence for Tech Consultants - A guide to artificial intelligence technologies and their applications for tech consultants, including natural language processing, computer vision, and machine learning. (30)",
                                    },
                                    {
                                        "id": "3.3.3",
                                        "description": "The Internet of Things for Tech Consultants - An introduction to the internet of things (IoT) and its applications for tech consultants, including smart homes, connected cars, and industrial automation. (40)",
                                    },
                                ],
                            },
                        ],
                    },
                ],
            }
        ]

        # chapters_raw = get_chapters()
        # tree_array = chapters_to_tree(chapters_raw)
        tree_array = ""

        def print_dict_types(d, key=None, level=0):
            indent = "-" * level
            logger.debug(f"{indent}Key: {key}, Type: {type(d)}")
            if isinstance(d, dict):
                for k, v in d.items():
                    print_dict_types(v, k, level + 1)
            elif isinstance(d, list):
                for i, item in enumerate(d):
                    print_dict_types(item, i, level + 1)

        # print_dict_types(tree_array)
        logger.debug(f"Tree Array\n\n\n {tree_array}\n\n\n")
        logger.debug(f"Working Tree Array\n\n\n {working_tree_array}\n\n\n")
        logger.debug(f"tree array type: {type(tree_array)}")
        try:
            logger.debug(f"tree array and childs type: {type(tree_array[0])}")
        except Exception:
            pass
        logger.debug("Tree arrary done")
        # time.sleep(1)
        with tree_container:
            logger.debug("with tree_container")
            global book_tree
            book_tree = ui.tree(
                working_tree_array,
                label_key="id",
            ).add_slot(
                "default-body",
                '<span :props="props">Description: "{{ props.node.description }}"</span>',
            )
            logger.debug("Did it show? The tree?")

        # book_tree = None
        # entire_answer_container.clear()
        # with entire_answer_container:
        #     ui.label(response)

    def expand_all():
        book_tree.tree.expand_all()

    ui.button("Expand All", on_click=expand_all)
    ui.button("Build Chapters!", on_click=update_tree)
    tree_container = ui.row()

    # entire_answer_container = ui.row()


if __name__ in {"__main__", "__mp_main__"}:
    ui.run(storage_secret="THIS_NEEDS_TO_BE_CHANGED", port=81)
    logger = initialize_logger(__name__)
