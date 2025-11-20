"""
Hello World Agent for AWS AgentCore

This is the simplest possible AgentCore application.
It demonstrates the basic structure: define an entrypoint, accept a request, return a response.

Think of this like a Lambda function, but with AgentCore handling the infrastructure,
deployment, scaling, and monitoring for you.
"""

from bedrock_agentcore import BedrockAgentCoreApp

# Initialize the AgentCore application
app = BedrockAgentCoreApp()


@app.entrypoint
def agent_handler(payload: dict) -> dict:
    """
    This is your agent's entrypoint - the function that handles requests.
    
    Args:
        payload: The incoming request (a dictionary)
        
    Returns:
        dict: Your response (also a dictionary)
    """
    # Extract data from the request
    user_message = payload.get("prompt", "Hello!")
    
    # Do something (for now, just echo it back)
    response = {
        "message": f"You said: '{user_message}'",
        "agent": "Hello World",
        "framework": "AWS AgentCore"
    }
    
    return response


if __name__ == "__main__":
    print("=" * 60)
    print("AWS AgentCore Hello World")
    print("=" * 60)
    print("\nThis is the simplest AgentCore application.")
    print("It's like a Lambda function, but AgentCore handles:")
    print("  - HTTP server setup")
    print("  - Request/response handling")
    print("  - Deployment to AWS")
    print("  - Scaling and monitoring")
    print("\nStarting on http://localhost:8080")
    print("\nTest it:")
    print('  curl -X POST http://localhost:8080/invocations \\')
    print('    -H "Content-Type: application/json" \\')
    print('    -d \'{"prompt": "Hello!"}\'')
    print("\nPress Ctrl+C to stop.\n")
    
    # Run the AgentCore application
    app.run()
