# Multi-Agent System for Scientific Paper Processing

This multi-agent system uses Google Agent Development Kit (ADK) with Model Context Protocol (MCP) to provide specialized agents for scientific paper processing and database management.

## 🏗️ Architecture

### Agents

1. **Orchestrator Agent** (`orchestrator_agent`)
   - Main routing agent that directs user queries to appropriate specialized agents
   - Provides system overview and guidance

2. **Database Agent** (`database_agent`) 
   - Connects to PostgreSQL database via MCP
   - Queries paper metadata, text sections, tables, images, and references
   - Provides data analysis and search capabilities

3. **Greeting Agent** (`greeting_agent`)
   - Handles initial user interactions
   - Provides casual conversation and system introduction

## 🚀 Quick Start

### Prerequisites

1. **PostgreSQL Database**: Ensure your database is running on the configured port
2. **Node.js**: Required for MCP server (`npx` command)
3. **Environment Variables**: Set up your `.env` file with database credentials

### Installation

```bash
# Install ADK if not already installed
pip install google-adk

# Install MCP server for PostgreSQL
npm install -g @modelcontextprotocol/server-postgres