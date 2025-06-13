"""
Multi-Agent System for Scientific Paper Processing and Database Management

This system provides specialized agents for different aspects of scientific paper
processing and database interaction using Google ADK and MCP.
"""
import asyncio
import os
import sys
from pathlib import Path
from dotenv import load_dotenv
from google.genai import types
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.adk.artifacts.in_memory_artifact_service import InMemoryArtifactService

# Add the multi_agents directory to the path
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

# Import all agents
from greeting_agent.agent import root_agent as greeting_agent
from database_agent.agent import database_agent
from orchestrator_agent.agent import orchestrator_agent

# Load environment variables from parent directory
load_dotenv(dotenv_path=current_dir.parent / '.env')

class MultiAgentSystem:
    """
    Multi-agent system orchestrator for scientific paper processing.
    """
    
    def __init__(self):
        self.agents = {
            'greeting': greeting_agent,
            'database': database_agent,
            'orchestrator': orchestrator_agent
        }
        self.session_service = InMemorySessionService()
        self.artifacts_service = InMemoryArtifactService()
        self.current_agent = 'orchestrator'  # Start with orchestrator
    
    async def initialize_session(self, user_id: str = "user_001"):
        """Initialize a new session for the multi-agent system."""
        session = await self.session_service.create_session(
            state={'current_agent': self.current_agent}, 
            app_name='multi_agent_paper_system', 
            user_id=user_id
        )
        return session
    
    async def run_query(self, query: str, agent_name: str = None, session_id: str = None):
        """
        Run a query through the specified agent or the current agent.
        
        Args:
            query: User query/message
            agent_name: Name of agent to use ('greeting', 'database', 'orchestrator')
            session_id: Session ID to use
        """
        if agent_name and agent_name in self.agents:
            agent = self.agents[agent_name]
        else:
            agent = self.agents[self.current_agent]
        
        content = types.Content(role='user', parts=[types.Part(text=query)])
        
        runner = Runner(
            app_name='multi_agent_paper_system',
            agent=agent,
            artifact_service=self.artifacts_service,
            session_service=self.session_service,
        )
        
        print(f"\n🤖 Using {agent.name} to process: '{query}'")
        print("=" * 60)
        
        events_async = runner.run_async(
            session_id=session_id,
            user_id="user_001",
            new_message=content
        )
        
        responses = []
        async for event in events_async:
            print(f"📩 Event: {event}")
            responses.append(event)
        
        return responses
    
    async def interactive_session(self):
        """Run an interactive session with the multi-agent system."""
        print("\n🚀 Welcome to the Scientific Paper Multi-Agent System!")
        print("Available agents:")
        print("  - orchestrator: Main routing agent (default)")
        print("  - database: PostgreSQL database queries")
        print("  - greeting: Casual conversation and greetings")
        print("\nType 'quit' to exit, 'switch <agent>' to change agents")
        print("=" * 60)
        
        session = await self.initialize_session()
        
        while True:
            try:
                user_input = input(f"\n[{self.current_agent}] 💬 You: ").strip()
                
                if user_input.lower() == 'quit':
                    print("👋 Goodbye!")
                    break
                
                if user_input.lower().startswith('switch '):
                    new_agent = user_input[7:].strip()
                    if new_agent in self.agents:
                        self.current_agent = new_agent
                        print(f"🔄 Switched to {new_agent} agent")
                        continue
                    else:
                        print(f"❌ Unknown agent: {new_agent}")
                        continue
                
                if not user_input:
                    continue
                
                await self.run_query(user_input, session_id=session.id)
                
            except KeyboardInterrupt:
                print("\n👋 Session interrupted. Goodbye!")
                break
            except Exception as e:
                print(f"❌ Error: {e}")

async def main():
    """Main entry point for the multi-agent system."""
    system = MultiAgentSystem()
    
    # Test database connectivity first
    print("🔧 Testing database connectivity...")
    try:
        test_responses = await system.run_query(
            "List all schemas in the database", 
            agent_name='database'
        )
        print("✅ Database agent is working!")
    except Exception as e:
        print(f"⚠️  Database connectivity issue: {e}")
        print("Please ensure PostgreSQL is running and credentials are correct")
    
    # Start interactive session
    await system.interactive_session()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except Exception as e:
        print(f"💥 System error: {e}")