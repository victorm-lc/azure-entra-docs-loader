"""
LangGraph ReAct Agent example using modular Azure Blob Storage tools.
Demonstrates composable, scalable approach to Azure document management.
"""

import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langgraph.prebuilt import create_react_agent
from modular_azure_tools import MODULAR_AZURE_TOOLS

# Load environment variables
load_dotenv()

def create_modular_azure_agent():
    """Create a ReAct agent with modular Azure Blob Storage tools."""
    
    # Initialize LLM
    llm = ChatOpenAI(
        model="gpt-4o",
    )
    
    # Create the agent with modular Azure tools
    agent = create_react_agent(
        model=llm, 
        tools=MODULAR_AZURE_TOOLS,
        prompt="""You are a helpful Azure Blob Storage document assistant with modular, composable tools.

Your tools follow a discovery → search → load → summarize workflow:

1. **list_available_containers** - Discover what containers/collections are available
2. **list_documents_in_container** - Browse documents in a specific container
3. **search_documents_by_metadata** - Search documents by filename, type, date, size
4. **load_document_from_blob** - Load and parse a specific document
5. **summarize_document** - Load and summarize a document (overview, detailed, key_points)

Best practices:
- Start with discovery tools when users don't know what's available
- Use search tools to filter before loading
- For document content, prefer summarize_document over load_document_from_blob unless users need full text
- When users load documents, automatically provide summaries and key insights
- Always be helpful and provide next steps

Example workflows:
- User: "What's available?" → list_available_containers → list_documents_in_container
- User: "Find PDFs about reports" → search_documents_by_metadata → summarize_document
- User: "Load report.pdf" → summarize_document (provide overview first) → load_document_from_blob (if they need full content)

IMPORTANT: When users request to load a document, use summarize_document first to give them an overview, then offer to load full content if needed."""
    )
    
    return agent

def main():
    """Main function to run the demo workflow."""
    demo_workflow()

def demo_workflow():
    """Demonstrate the modular workflow programmatically."""
    print("🎬 Demo: Modular Azure Blob Storage Workflow")
    print("=" * 50)
    
    agent = create_modular_azure_agent()
    storage_account = os.getenv("AZURE_STORAGE_ACCOUNT_NAME", "langchaintesting1")
    
    # Step 1: Discover containers
    print("Step 1: Discovering available containers...")
    response1 = agent.invoke({"messages": [("user", f"List all containers in {storage_account}")]})
    print(f"Result: {response1['messages'][-1].content}")
    print()
    
    # Step 2: Browse documents in a container
    print("Step 2: Browsing documents in 'docs' container...")
    response2 = agent.invoke({"messages": [("user", f"List documents in the docs container in {storage_account}")]})
    print(f"Result: {response2['messages'][-1].content}")
    print()
    
    # Step 3: Search for specific files
    print("Step 3: Searching for PDF files...")
    response3 = agent.invoke({"messages": [("user", f"Search for PDF files in docs container in {storage_account}")]})
    print(f"Result: {response3['messages'][-1].content}")
    print()
    
    # Step 4: Summarize a specific document
    print("Step 4: Summarizing a specific document...")
    response4 = agent.invoke({"messages": [("user", f"Summarize the example_study.pdf document from docs container in {storage_account}")]})
    print(f"Result: {response4['messages'][-1].content[:500]}...")
    print()
    
    print("✅ Demo complete! This shows the modular, composable approach.")

if __name__ == "__main__":
    # Check for required environment variables
    required_vars = ["AZURE_CLIENT_ID", "AZURE_TENANT_ID", "AZURE_CLIENT_SECRET"]
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    
    if missing_vars:
        print("❌ Missing required environment variables:")
        for var in missing_vars:
            print(f"  - {var}")
        print("\nPlease set these in your .env file or environment.")
        exit(1)
    
    if not os.getenv("OPENAI_API_KEY"):
        print("❌ Missing OPENAI_API_KEY environment variable")
        print("Please set this in your .env file or environment.")
        exit(1)
    
    # Run the demo workflow
    main()