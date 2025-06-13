import os
from google.adk.agents import LlmAgent
from google.adk.tools.mcp_tool import MCPToolset, StdioConnectionParams
from mcp.client.stdio import StdioServerParameters

# Load database configuration from environment variables
# These should match your existing .env file
postgres_config = {
    "host": os.environ.get("POSTGRES_HOST", "localhost"),
    "port": os.environ.get("POSTGRES_PORT", "8700"),
    "database": os.environ.get("POSTGRES_DB", "thedb"),
    "user": os.environ.get("POSTGRES_USER", "theuser"),
    "password": os.environ.get("POSTGRES_PASSWORD", "thepassword"),
}

# Construct the PostgreSQL connection string for the MCP server
postgres_url = f"postgresql://{postgres_config['user']}:{postgres_config['password']}@{postgres_config['host']}:{postgres_config['port']}/{postgres_config['database']}"

database_agent = LlmAgent(
    name="database_agent",
    description="Agent for interacting with the PostgreSQL database containing scientific paper metadata, text sections, tables, images, and references.",
    model="gemini-2.0-flash",
    instruction="""
    You are a specialized database agent that can interact with the PostgreSQL database 
    containing scientific paper research data. You have access to the following schemas and tables:
    
    - papers.paper_metadata: Contains paper metadata (titles, authors, abstracts, DOIs, etc.)
    - papers.text_sections: Contains extracted text sections from papers
    - papers.table_data: Contains extracted tables and their analysis
    - papers.paper_images: Contains extracted images and their descriptions
    - papers.references_data: Contains extracted references from papers

    You are a specialized database agent that can interact with the PostgreSQL database 
    containing scientific paper research data. You have access to the following schemas and tables:
    
    IMPORTANT SCHEMA INFORMATION:
    
    1. papers.paper_metadata (Primary table):
       - Primary key: id (bigint)
       - Key columns: title, authors[], journal, publication_date, doi, abstract, keywords[], source_file
       - Other columns: volume, issue, pages, extracted_at, funding_sources[], conflict_of_interest, etc.
    
    2. papers.text_sections:
       - Primary key: id (bigint)
       - Foreign key: paper_id (references paper_metadata.id)
       - Key columns: title, section_number, level, word_count, content, summary, keywords[]
    
    3. papers.table_data:
       - Primary key: id (bigint)
       - Foreign key: paper_id (references paper_metadata.id)
       - Key columns: table_number, title, column_count, row_count, raw_content, summary, context_analysis, statistical_findings
    
    4. papers.paper_images:
       - Primary key: id (bigint)
       - Foreign key: paper_id (references paper_metadata.id)
       - Key columns: image_number, alt_text, image_format, image_data, summary, graphic_analysis, statistical_analysis
    
    5. papers.paper_references:
       - Primary key: id (bigint)
       - Foreign key: paper_id (references paper_metadata.id)
       - Key columns: reference_list[], reference_count, extracted_at
    
    CRITICAL: 
    - Use "id" for paper_metadata table primary key, NOT "paper_id"
    - Use "paper_id" for foreign keys in other tables that reference paper_metadata.id
    - Authors and keywords are stored as arrays (use array operators like ANY())
    - Always use proper table aliases: pm for paper_metadata, ts for text_sections, etc.
    
    You can help users:
    1. Query paper metadata and statistics
    2. Search for papers by author, title, keywords, or DOI
    3. Analyze text sections and their content
    4. Examine table data and statistical findings
    5. Review image descriptions and their context
    6. Explore references and citation networks
    7. Generate reports and summaries of the research database
    
    Always provide clear, well-structured responses with relevant data.
  
    """,
    tools=[
        MCPToolset(
            connection_params=StdioConnectionParams(
                server_params=StdioServerParameters(
                    command='npx',
                    args=[
                        "-y",  # Auto-confirm install
                        "@modelcontextprotocol/server-postgres",
                        postgres_url,
                    ],
                    # Pass environment variables to the MCP server process
                    env={
                        "POSTGRES_HOST": postgres_config["host"],
                        "POSTGRES_PORT": postgres_config["port"],
                        "POSTGRES_DB": postgres_config["database"],
                        "POSTGRES_USER": postgres_config["user"],
                        "POSTGRES_PASSWORD": postgres_config["password"],
                    }
                )
            ),
            # Filter to only expose safe database operations
            tool_filter=[
                'query',
                'list_tables', 
                'describe_table',
                'list_schemas'
            ]
        )
    ],
)