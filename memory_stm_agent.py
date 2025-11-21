"""
Short-Term Memory Agent for AWS AgentCore

This agent demonstrates how to actually USE AgentCore's short-term memory (STM).
It maintains conversation context within a session by storing and retrieving turns.

Key concepts:
- MemorySessionManager: Manages memory sessions
- Session ID: Identifies a conversation session
- Actor ID: Identifies the user
- Turns: Individual messages in the conversation
"""

import json
import boto3
from bedrock_agentcore import BedrockAgentCoreApp, BedrockAgentCoreContext
from bedrock_agentcore.memory import MemorySessionManager
from bedrock_agentcore.memory.constants import ConversationalMessage, MessageRole

# Initialize the AgentCore application
app = BedrockAgentCoreApp()

# Initialize Bedrock client for Claude
bedrock_runtime = boto3.client(
    service_name='bedrock-runtime',
    region_name='us-east-1'
)

# Memory configuration
# When deployed to AgentCore, memory is auto-configured
# In local mode, memory features are limited
import os
MEMORY_ID = os.environ.get('BEDROCK_AGENTCORE_MEMORY_ID')


@app.entrypoint
def agent_handler(payload: dict) -> dict:
    """
    Agent that uses short-term memory to maintain conversation context.
    
    Args:
        payload: {"prompt": "user message", "actor_id": "optional_user_id"}
        
    Returns:
        dict: Response with message and conversation history
    """
    user_message = payload.get("prompt", "Hello!")
    actor_id = payload.get("actor_id", "default_user")
    
    try:
        # Get session ID from AgentCore context
        session_id = BedrockAgentCoreContext.get_session_id()
        if not session_id:
            session_id = "default_session"
        
        # Initialize memory session manager
        # If MEMORY_ID is None, we'll use a test ID and see what happens
        memory_manager = MemorySessionManager(
            memory_id=MEMORY_ID or "test-memory-local",
            region_name="us-west-2"
        )
        
        # Create or get existing session
        session = memory_manager.create_memory_session(
            actor_id=actor_id,
            session_id=session_id
        )
        
        # Get recent conversation history (last 5 turns)
        # get_last_k_turns returns List[List[EventMessage]] - list of turns, each turn is a list of messages
        recent_turns = session.get_last_k_turns(k=5)
        
        # Build context from recent turns
        conversation_context = []
        if recent_turns and len(recent_turns) > 0:
            for turn in recent_turns:  # Each turn is a list of messages
                for message in turn:  # Each message in the turn
                    # Handle both dict and object formats
                    if isinstance(message, dict):
                        role = "user" if message.get('role') == 'USER' else "assistant"
                        content = message.get('content', '')
                    else:
                        role = "user" if message.role == MessageRole.USER else "assistant"
                        content = message.content
                    conversation_context.append(f"{role}: {content}")
        
        context_str = "\n".join(conversation_context) if conversation_context else "No previous context"
        
        # Add user's message to memory BEFORE calling Claude
        session.add_turns(
            messages=[ConversationalMessage(user_message, MessageRole.USER)]
        )
        
        # Call Claude with conversation context
        prompt = f"""You are a helpful AI assistant with memory. You can remember the conversation.

Previous conversation:
{context_str}

Current user message: {user_message}

Respond naturally, referencing previous context when relevant."""

        body = json.dumps({
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": 500,
            "messages": [
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        })
        
        response = bedrock_runtime.invoke_model(
            modelId='anthropic.claude-3-haiku-20240307-v1:0',
            body=body
        )
        
        response_body = json.loads(response['body'].read())
        agent_message = response_body['content'][0]['text']
        
        # Add assistant's response to memory
        session.add_turns(
            messages=[ConversationalMessage(agent_message, MessageRole.ASSISTANT)]
        )
        
        return {
            "success": True,
            "message": agent_message,
            "session_id": session_id,
            "actor_id": actor_id,
            "turns_in_memory": len(recent_turns) + 2,  # +2 for the new turn
            "memory_type": "STM (Short-Term Memory)"
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "message": "Error using memory. In local mode, memory features are limited."
        }


if __name__ == "__main__":
    print("=" * 60)
    print("Short-Term Memory Agent - AWS AgentCore")
    print("=" * 60)
    print("\nThis agent demonstrates SHORT-TERM MEMORY:")
    print("  - Remembers conversation within a session")
    print("  - Stores message turns")
    print("  - Provides context to Claude")
    print("\nMemory is session-based:")
    print("  - Same session_id = same conversation")
    print("  - Different session_id = new conversation")
    print("\nStarting on http://localhost:8080")
    print("\nTest with:")
    print('  curl -X POST http://localhost:8080/invocations \\')
    print('    -H "Content-Type: application/json" \\')
    print('    -d \'{"prompt": "My name is Alice"}\'')
    print("\nThen ask:")
    print('  curl -X POST http://localhost:8080/invocations \\')
    print('    -H "Content-Type: application/json" \\')
    print('    -d \'{"prompt": "What is my name?"}\'')
    print("\nPress Ctrl+C to stop.\n")
    
    app.run()

