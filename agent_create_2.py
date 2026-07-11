from huggingface_hub import login
import os

from agent_create_1 import HF_TOKEN

# login()
os.environ["HTTP_PROXY"] = "http://127.0.0.1:7897"
os.environ["HTTPS_PROXY"] = "http://127.0.0.1:7897"



from smolagents import CodeAgent, DuckDuckGoSearchTool, FinalAnswerTool, InferenceClientModel, Tool, tool, VisitWebpageTool

import numpy as np
import time
import datetime

# agent = CodeAgent(tools=[DuckDuckGoSearchTool()], model=InferenceClientModel())
# agent.run("Search for the best music recommendations for a party at the Wayne's mansion.")


@tool
def suggest_menu(occasion: str)->str:
    """
        Suggests a menu based on the occasion.
        Args:
            occasion: The type of occasion for the party.
    """
    if occasion == "casual":
        return "Pizza, snacks, and drinks."
    elif occasion == "formal":
        return "3-course dinner with wine and dessert."
    elif occasion == "superhero":
        return "Buffet with high-energy and healthy food."
    else:
        return "Custom menu for the butler."

# agent = CodeAgent(tools=[suggest_menu], model=InferenceClientModel())
# agent.run("Prepare a formal menu for the party.")


@tool
def get_current_time() -> str:
    """
    Returns the current date and time.
    Use this tool when you need to know the current time to calculate deadlines or schedules.
    """
    return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
agent = CodeAgent(
    tools=[get_current_time],
    model=InferenceClientModel(),
    additional_authorized_imports=['datetime']
)

agent.run(
    """
    Alfred needs to prepare for the party. Here are the tasks:
    1. Prepare the drinks - 30 minutes
    2. Decorate the mansion - 60 minutes
    3. Set up the menu - 45 minutes
    4. Prepare the music and playlist - 45 minutes

    Total preparation time: 180 minutes (3 hours)

    You have access to the get_current_time() tool.
    Task: If we start right now, at what time will the party be ready?
    First, use get_current_time() to get the current time, then add 3 hours to calculate the completion time.
    """
)

@tool
def catering_service_tool(query: str) -> str:
    """
    This tool returns the highest-rated catering service in Gotham City.

    Args:
        query: A search term for finding catering services.
    """
    # 餐饮服务及其评分的示例列表
    services = {
        "Gotham Catering Co.": 4.9,
        "Wayne Manor Catering": 4.8,
        "Gotham City Events": 4.7,
    }

    # 找到评分最高的餐饮服务（模拟搜索查询过滤）
    best_service = max(services, key=services.get)

    return best_service


class SuperheroPartyThemeTool(Tool):
    name = "superhero_party_theme_generator"
    description = """
    This tool suggests creative superhero-themed party ideas based on a category.
    It returns a unique party theme idea."""

    inputs = {
        "category": {
            "type": "string",
            "description": "The type of superhero party (e.g., 'classic heroes', 'villain masquerade', 'futuristic Gotham').",
        }
    }

    output_type = "string"

    def forward(self, category: str):
        themes = {
            "classic heroes": "Justice League Gala: Guests come dressed as their favorite DC heroes with themed cocktails like 'The Kryptonite Punch'.",
            "villain masquerade": "Gotham Rogues' Ball: A mysterious masquerade where guests dress as classic Batman villains.",
            "futuristic Gotham": "Neo-Gotham Night: A cyberpunk-style party inspired by Batman Beyond, with neon decorations and futuristic gadgets."
        }

        return themes.get(category.lower(),
                          "Themed party idea not found. Try 'classic heroes', 'villain masquerade', or 'futuristic Gotham'.")


# 管家阿尔弗雷德，为派对准备菜单
agent = CodeAgent(
    tools=[
        DuckDuckGoSearchTool(),
        VisitWebpageTool(),
        suggest_menu,
        catering_service_tool,
        SuperheroPartyThemeTool()
    ],
    model=InferenceClientModel(),
    max_steps=10,
    verbosity_level=2
)

# agent.run("Give me best playlist for a party at the Wayne's mansion. The party idea is a 'villain masquerade' theme")