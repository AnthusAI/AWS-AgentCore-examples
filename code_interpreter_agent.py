"""
Code Interpreter Agent - CSV Contact Extractor

This agent demonstrates the "Give an Agent a Tool" paradigm using AgentCore's
managed Code Interpreter. Instead of writing complex parsing logic for every
possible CSV format, we give the agent ONE tool (Code Interpreter) and let it
figure out how to extract contacts from any CSV format.

Inspired by: https://github.com/AnthusAI/Give-an-Agent-a-Tool

Traditional approach: Write if/else logic for every header variation, language, format
Agent approach: Give the agent Code Interpreter and let it adapt to any format

Example CSV formats this handles WITHOUT code changes:
- "First Name,Last Name,Email"
- "Last,First,Email" (reversed order)
- "Nombre,Apellidos,Correo" (Spanish)
- "Contact Info,Details" (messy legacy format)
- Any other variation you throw at it!
"""

import boto3
import json
from bedrock_agentcore import BedrockAgentCoreApp, RequestContext
from strands import Agent
from strands_tools.code_interpreter import AgentCoreCodeInterpreter
from botocore.exceptions import ClientError

app = BedrockAgentCoreApp()

# Initialize Code Interpreter (AgentCore's managed sandbox)
code_interpreter_tool = AgentCoreCodeInterpreter(region="us-west-2")

# System prompt that defines the agent's goal
SYSTEM_PROMPT = """You are a contact extraction assistant.

Your goal: Extract name and email from CSV data, regardless of format.

You have access to a Code Interpreter tool that can execute Python code in a secure sandbox.
Use it to:
1. Parse the CSV (handle any delimiter, any header names, any language)
2. Extract each person's name and email
3. Return a clean list of contacts

Be flexible:
- Headers might be "First Name,Last Name,Email" or "Last,First,Email" or "Nombre,Apellidos,Correo"
- Names might be split across columns or in a single column
- Emails might be in a column called "Email", "Work Email", "Correo", or mixed with other data
- The CSV might have extra columns you should ignore

Write Python code to handle whatever format you receive. Return results as a JSON list:
[{"name": "John Doe", "email": "john@example.com"}, ...]
"""

# Create the agent with Code Interpreter tool
agent = Agent(
    tools=[code_interpreter_tool.code_interpreter],
    system_prompt=SYSTEM_PROMPT
)

@app.entrypoint
def extract_contacts(request: RequestContext) -> dict:
    """
    Extract contacts from CSV data using Code Interpreter.
    
    The agent will write and execute Python code to parse any CSV format.
    """
    csv_data = request.get("csv", "")
    
    if not csv_data:
        return {
            "success": False,
            "message": "Please provide CSV data in the 'csv' field",
            "example": {
                "csv": "First Name,Last Name,Email\\nJohn,Doe,john@example.com"
            }
        }
    
    try:
        # Let the agent figure out how to parse this CSV
        prompt = f"""Extract contacts from this CSV data:

```csv
{csv_data}
```

Write Python code to parse this and extract name + email for each person.
Return the results as a JSON list."""

        # Agent decides how to parse, writes code, executes it
        response = agent(prompt)
        
        # Extract the agent's response
        # The response object has a message attribute with the content
        agent_response = str(response.message) if hasattr(response, 'message') else str(response)
        
        return {
            "success": True,
            "message": "Contacts extracted successfully using Code Interpreter",
            "agent_response": agent_response,
            "csv_preview": csv_data[:200] + "..." if len(csv_data) > 200 else csv_data,
            "paradigm": "Give an Agent a Tool - no hard-coded parsing logic needed!"
        }
        
    except Exception as e:
        return {
            "success": False,
            "message": f"Error: {str(e)}",
            "csv_preview": csv_data[:200] + "..." if len(csv_data) > 200 else csv_data
        }

if __name__ == "__main__":
    app.run()

