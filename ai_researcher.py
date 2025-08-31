# Step1: Install & Import dependencies
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.prebuilt import create_react_agent
from arxiv_tool import arxiv_search
from read_pdf import read_pdf
from write_pdf import render_latex_pdf
import os
from dotenv import load_dotenv

load_dotenv()

# Step2: Setup LLM and tools
tools = [arxiv_search, read_pdf, render_latex_pdf]
model = ChatGoogleGenerativeAI(model="gemini-2.5-pro", api_key=os.getenv("GOOGLE_API_KEY"))

# Step3: Create the ReAct agent graph
graph = create_react_agent(model, tools=tools)

# Step4: Run the agent with an initial prompt

INITIAL_PROMPT = """
You are a research assistant. 
- Use arxiv.org via tools for papers.
- Discuss topic with me, then show latest papers. 
- After I choose, read paper and analyze future directions. 
- Then propose ideas, and when I pick one, write a LaTeX research paper with equations and references.
- Finally, render to PDF.
"""

def print_stream(stream):
    for s in stream:
        message = s["messages"][-1]
        print(f"Message received: {message.content[:200]}...")
        message.pretty_print()

while True:
    user_input = input("User: ")
    if user_input:
        messages = [
                    {"role": "system", "content": INITIAL_PROMPT},
                    {"role": "user", "content": user_input}
                ]
        input_data = {
            "messages" : messages
        }
        print_stream(graph.stream(input_data, stream_mode="values"))