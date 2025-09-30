"""
LangChain-based Product Search Agent - DEMO VERSION
Interacts with v1 and v3 product search APIs using natural language

DEMO INSTRUCTIONS:
1. First run: Only Tool 1 (v1 API) is active - Try: "Find me laptops"
2. Uncomment Tool 2 below (line 68-98) and the tools list entry (line 109)
3. Second run: Both tools active - Try: "Find me laptops that are in stock"
"""

import os
import json
import requests
from dotenv import load_dotenv
from langchain.tools import tool
from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain_anthropic import ChatAnthropic
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

# Load environment variables from .env file
load_dotenv()


# ============================================================================
# TOOL 1 - Basic Product Search (v1 API) - ACTIVE
# ============================================================================

@tool
def search_products_v1(query: str, category: str = "") -> str:
    """
    Search for products in the v1 database (basic search).
    
    Args:
        query: The search query for products (e.g., 'laptop', 'chair')
        category: Product category - 'electronics', 'furniture', or empty string for all categories
    
    Returns:
        JSON string with search results from v1 API
    """
    try:
        url = "https://product-search-mcp-api.replit.app/v1/products/search"
        payload = {
            "query": query,
            "category": category
        }
        
        print(f"\n📞 Calling v1 API: query='{query}', category='{category}'")
        
        response = requests.post(
            url,
            headers={"Content-Type": "application/json"},
            json=payload,
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            return json.dumps(data, indent=2)
        else:
            return f"Error: API v1 returned status code {response.status_code}"
            
    except Exception as e:
        return f"Error calling API v1: {str(e)}"


# ============================================================================
# TOOL 2 - Advanced Product Search with Inventory (v3 API) - COMMENTED OUT
# UNCOMMENT THE LINES BELOW FOR PART 2 OF DEMO
# ============================================================================

# @tool
# def search_products_v3(query: str, category: str = "", in_stock: bool = None) -> str:
#     """
#     Search for products in the v3 database with inventory filtering (newer version).
    
#     Args:
#         query: The search query for products (e.g., 'laptop', 'chair')
#         category: Product category - 'electronics', 'furniture', or empty string for all categories
#         in_stock: Filter by inventory status - True for in-stock only, False for out-of-stock only, None for all products
    
#     Returns:
#         JSON string with search results from v3 API
#     """
#     try:
#         url = "https://product-search-mcp-api.replit.app/v3/products/search"
#         payload = {
#             "query": query,
#             "category": category
#         }
        
#         # Only add in_stock parameter if explicitly provided
#         if in_stock is not None:
#             payload["in_stock"] = in_stock
        
#         print(f"\n📞 Calling v3 API: query='{query}', category='{category}', in_stock={in_stock}")
        
#         response = requests.post(
#             url,
#             headers={"Content-Type": "application/json"},
#             json=payload,
#             timeout=10
#         )
        
#         if response.status_code == 200:
#             data = response.json()
#             return json.dumps(data, indent=2)
#         else:
#             return f"Error: API v3 returned status code {response.status_code}"
            
#     except Exception as e:
#         return f"Error calling API v3: {str(e)}"


def create_agent():
    """Create the LangChain agent with tools"""
    
    # Initialize the LLM (Claude)
    llm = ChatAnthropic(
        model="claude-sonnet-4-20250514",
        temperature=0,
        api_key=os.environ.get("ANTHROPIC_API_KEY")
    )
    
    # ========================================================================
    # TOOLS LIST - Uncomment search_products_v3 for Part 2 of Demo
    # ========================================================================
    tools = [
        search_products_v1,
        search_products_v3,  # <-- UNCOMMENT THIS LINE FOR PART 2
    ]
    
    # Create prompt template
    prompt = ChatPromptTemplate.from_messages([
        ("system", """You are a friendly and conversational AI assistant that can help with product searches.

You have access to product search tools:
- search_products_v1: Basic product search (v1 database)
- search_products_v3: Advanced product search with inventory filtering (v3 database) - if available

You can:
✅ Chat naturally about any topic - be friendly, helpful, and engaging
✅ Answer questions about products, shopping, or general topics
✅ Search for products when users ask (extract query, category, and in_stock parameters)
✅ Compare products from different databases
✅ Provide recommendations and advice

Remember:
- Be conversational and warm - you're having a chat, not just executing commands
- Only use search tools when the user actually wants to search for products
- You can discuss products, give shopping advice, or just have a friendly conversation
- If users greet you, greet them back warmly
- If they ask how you are or chat casually, respond naturally
- Present search results in a clear, friendly format

Categories available: 'electronics', 'furniture', or leave empty for all
For v3: Use in_stock=True for available items, False for out-of-stock, None for all"""),
        MessagesPlaceholder(variable_name="chat_history", optional=True),
        ("human", "{input}"),
        MessagesPlaceholder(variable_name="agent_scratchpad")
    ])
    
    # Create agent
    agent = create_tool_calling_agent(llm, tools, prompt)
    
    # Create agent executor
    agent_executor = AgentExecutor(
        agent=agent,
        tools=tools,
        verbose=True,
        handle_parsing_errors=True
    )
    
    return agent_executor


def main():
    """Main chat loop"""
    print("=" * 70)
    print("🤖 Product Search AI Agent - DEMO VERSION")
    print("=" * 70)
    print("\n💬 I'm your friendly AI assistant! I can:")
    print("   • Chat with you about anything")
    print("   • Search for products when you need them")
    print("   • Help with shopping advice and recommendations")
    print("\n📋 DEMO SCRIPT:")
    print("   Part 1: Tool 1 only - Try: 'Hello!' or 'Find me laptops'")
    print("   Part 2: Uncomment Tool 2, restart - Try: 'Find laptops that are in stock'")
    print("\nType 'quit' or 'exit' to end.\n")
    
    # Check for API key
    if not os.environ.get("ANTHROPIC_API_KEY"):
        print("⚠️  WARNING: ANTHROPIC_API_KEY environment variable not set!")
        print("Please set it with: export ANTHROPIC_API_KEY='your-api-key'\n")
        return
    
    # Create agent
    try:
        agent_executor = create_agent()
        print(f"✅ Agent initialized with {len(agent_executor.tools)} tool(s)\n")
    except Exception as e:
        print(f"❌ Error creating agent: {e}")
        return
    
    # Chat history
    chat_history = []
    
    # Chat loop
    while True:
        try:
            # Get user input
            user_input = input("\n👤 You: ").strip()
            
            if not user_input:
                continue
                
            if user_input.lower() in ['quit', 'exit', 'bye']:
                print("\n👋 Thanks for watching the demo!")
                break
            
            # Invoke agent
            print("\n🤖 Agent: ")
            print("-" * 70)
            
            response = agent_executor.invoke({
                "input": user_input,
                "chat_history": chat_history
            })
            
            # Print response
            print("-" * 70)
            output = response.get("output", "I encountered an error processing your request.")
            print(f"\n{output}\n")
            
            # Update chat history
            chat_history.append(("human", user_input))
            chat_history.append(("ai", output))
            
            # Keep history manageable
            if len(chat_history) > 20:
                chat_history = chat_history[-20:]
                
        except KeyboardInterrupt:
            print("\n\n👋 Demo ended!")
            break
        except Exception as e:
            print(f"\n❌ Error: {e}")
            continue


if __name__ == "__main__":
    main()