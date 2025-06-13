from google.adk.agents import Agent
from google.adk.tools.agent_tool import AgentTool

from database_agent.agent import database_agent

root_agent = Agent(
    name="greeting_agent",
    description="Root agent for managing multi-agent interactions.",
    model="gemini-2.0-flash",
    instruction="""
    You are the first agent that will interact with the user.
    Your task is to greet the user and ask them what they want to do.
    If they make a scientific question, search the database first to see if there are any relevant papers to the answer.
    If you use data from the database in the answer, provide the source of the data.
    If they want to query the database, route them to the database agent.
    If they want to do something else, route them to the appropriate agent.
    If they want to exit, say goodbye and end the conversation.
    Always provide clear, concise responses and guide the user to the right agent.
   """,
   tools=[
       AgentTool(database_agent),
   ]
)