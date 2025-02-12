import chainlit as cl
from phi.agent import Agent
from phi.model.google import Gemini
from phi.tools.tavily import TavilyTools
import os

# Load environment variables
TAVILY_API_KEY = "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"

# Define system prompt and instructions for the agent
system_prompt = """
You are a bot that compares product prices listed on OLX and Quikr. Your task is to find the price details of a specific product (e.g., location, seller, mileage, date) provided by the user from both websites and present a simple comparison of the prices or any specific details respective to the product.
"""

instructions = """
1. Search for the specified product on OLX.
   - Extract the price or any specific details respective to the product details for all relevant listings.
2. Search for the same product on Quikr.
   - Extract the price, location, seller, or any specific details respective to the product details for all relevant listings.
3. Compare the prices from both platforms.
   - Identify the lowest and highest prices on each platform.
4. Present the comparison in a simple table format:
   - Include columns for platform, price or any specific details respective to the product, and example listings (if available).
5. Provide the source link for each listing.
"""

# Initialize Gemini model
gemini_model = Gemini(
    model="gemini-pro",
    api_key=os.getenv("GEMINI_API_KEY")
)

# Initialize Agent
agent = Agent(
    model=gemini_model,
    system_prompt=system_prompt,
    instructions=instructions,
    tools=[TavilyTools(api_key=TAVILY_API_KEY)],
    include_domains=["https://www.olx.in/en-in", "https://www.quikr.com/"],
    markdown=True,
    verbose=0
)

# Define Chainlit app logic
@cl.on_message
async def main(message: cl.Message):
    """
    Handles user input and fetches response from the agent.
    """
    try:
        # Send an initial loading message
        loading_message = cl.Message(content="Fetching data... Please wait.")
        await loading_message.send()

        # Fetch response from agent
        raw_response = agent.run(message.content)

        # Extract content from RunResponse object
        if hasattr(raw_response, "content"):  # Check if 'content' attribute exists
            response_content = raw_response.content  # Extract content
        else:
            response_content = str(raw_response)  # Fallback to string conversion

        # Update loading message with final content
        if response_content:
            loading_message.content = response_content
            await loading_message.update()
        else:
            loading_message.content = "Sorry, I couldn't retrieve any results. Please try again."
            await loading_message.update()
    
    except Exception as e:
        error_message = cl.Message(content=f"An error occurred: {str(e)}")
        await error_message.send()
