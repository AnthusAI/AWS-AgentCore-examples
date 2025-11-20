"""
Claude-Powered Agent for AWS AgentCore

This agent adds AI capabilities to the AgentCore structure.
It uses Claude (via AWS Bedrock) to generate intelligent responses.

This shows how to combine:
- AgentCore (infrastructure/deployment framework)
- Bedrock (AI model access)
- Claude (the actual LLM)
"""

import json
import boto3
from bedrock_agentcore import BedrockAgentCoreApp

# Initialize the AgentCore application
app = BedrockAgentCoreApp()

# Initialize Bedrock client for calling Claude
bedrock_runtime = boto3.client(
    service_name='bedrock-runtime',
    region_name='us-east-1'
)


@app.entrypoint
def agent_handler(payload: dict) -> dict:
    """
    AgentCore entrypoint that uses Claude to generate responses.
    
    Args:
        payload: The incoming request
        
    Returns:
        dict: Response from Claude
    """
    user_message = payload.get("prompt", "Hello!")
    
    try:
        # Call Claude via Bedrock
        body = json.dumps({
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": 500,
            "messages": [
                {
                    "role": "user",
                    "content": f"You are a helpful AI assistant running on AWS AgentCore. Respond to: {user_message}"
                }
            ]
        })
        
        response = bedrock_runtime.invoke_model(
            modelId='anthropic.claude-3-haiku-20240307-v1:0',
            body=body
        )
        
        # Parse Claude's response
        response_body = json.loads(response['body'].read())
        agent_message = response_body['content'][0]['text']
        
        return {
            "success": True,
            "message": agent_message,
            "model": "claude-3-haiku",
            "framework": "AWS AgentCore"
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "message": "Error calling Claude. Check AWS credentials and Bedrock access."
        }


if __name__ == "__main__":
    print("=" * 60)
    print("Claude-Powered AgentCore Agent")
    print("=" * 60)
    print("\nThis agent combines:")
    print("  - AgentCore (deployment framework)")
    print("  - Bedrock (AI model access)")
    print("  - Claude 3 Haiku (the LLM)")
    print("\nStarting on http://localhost:8080")
    print("\nTest it:")
    print('  curl -X POST http://localhost:8080/invocations \\')
    print('    -H "Content-Type: application/json" \\')
    print('    -d \'{"prompt": "Explain what AgentCore is"}\'')
    print("\nPress Ctrl+C to stop.\n")
    
    app.run()

