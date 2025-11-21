"""
Long-Term Memory Agent for AWS AgentCore

This agent demonstrates AgentCore's LONG-TERM MEMORY (LTM) with semantic strategy.
It maintains conversation context AND automatically extracts persistent insights.

Key differences from STM:
- Uses semantic strategy (configured during deployment)
- Automatically extracts facts, preferences, summaries
- Can search long-term memories across sessions
- Learns from past interactions

The code is nearly identical to STM - the magic happens in the configuration!
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
    Agent that uses long-term memory to remember facts across sessions.
    
    Args:
        payload: {"prompt": "user message", "actor_id": "optional_user_id"}
        
    Returns:
        dict: Response with message and memory insights
    """
    user_message = payload.get("prompt", "Hello!")
    actor_id = payload.get("actor_id", "default_user")
    
    try:
        # Get session ID from AgentCore context
        session_id = BedrockAgentCoreContext.get_session_id()
        if not session_id:
            session_id = "default_session"
        
        # Initialize memory session manager
        # If MEMORY_ID is None, we'll use a test ID
        memory_manager = MemorySessionManager(
            memory_id=MEMORY_ID or "test-memory-local",
            region_name="us-west-2"
        )
        
        # Create or get existing session
        session = memory_manager.create_memory_session(
            actor_id=actor_id,
            session_id=session_id
        )
        
        # Get recent conversation history (short-term memory)
        # get_last_k_turns returns List[List[EventMessage]]
        recent_turns = session.get_last_k_turns(k=5)
        
        # Search long-term memories relevant to this query
        # This searches facts/preferences extracted from past conversations
        try:
            long_term_memories = session.search_long_term_memories(
                query=user_message,
                namespace_prefix="/",
                top_k=3
            )
            ltm_context = "\n".join([
                f"- {mem.get('content', '')}" 
                for mem in long_term_memories
            ]) if long_term_memories else "No long-term memories yet"
        except:
            ltm_context = "Long-term memory search not available (requires semantic strategy)"
        
        # Build context from recent turns
        conversation_context = []
        if recent_turns and len(recent_turns) > 0:
            for turn in recent_turns:  # Each turn is a list of messages
                for message in turn:  # Each message in the turn
                    if isinstance(message, dict):
                        role = "user" if message.get('role') == 'USER' else "assistant"
                        content = message.get('content', '')
                    else:
                        role = "user" if message.role == MessageRole.USER else "assistant"
                        content = message.content
                    conversation_context.append(f"{role}: {content}")
        
        context_str = "\n".join(conversation_context) if conversation_context else "No previous context"
        
        # Add user's message to memory
        session.add_turns(
            messages=[ConversationalMessage(user_message, MessageRole.USER)]
        )
        
        # Call Claude with BOTH short-term and long-term context
        prompt = f"""You are a helpful AI assistant with long-term memory. You remember facts about users across conversations.

Long-term memories (facts/preferences from past sessions):
{ltm_context}

Recent conversation (current session):
{context_str}

Current user message: {user_message}

Respond naturally, using both recent context and long-term memories when relevant."""

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
        # With semantic strategy, AgentCore will automatically extract insights
        session.add_turns(
            messages=[ConversationalMessage(agent_message, MessageRole.ASSISTANT)]
        )
        
        return {
            "success": True,
            "message": agent_message,
            "session_id": session_id,
            "actor_id": actor_id,
            "turns_in_memory": len(recent_turns) + 2,
            "long_term_memories_found": len(long_term_memories) if 'long_term_memories' in locals() else 0,
            "memory_type": "LTM (Long-Term Memory with Semantic Strategy)"
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "message": "Error using memory. Ensure agent is deployed with semantic strategy."
        }


if __name__ == "__main__":
    print("=" * 60)
    print("Long-Term Memory Agent - AWS AgentCore")
    print("=" * 60)
    print("\nThis agent demonstrates LONG-TERM MEMORY:")
    print("  - Remembers conversation within a session (STM)")
    print("  - PLUS extracts facts/preferences automatically (LTM)")
    print("  - Searches relevant memories across sessions")
    print("  - Learns from past interactions")
    print("\nHow it works:")
    print("  1. You have a conversation")
    print("  2. AgentCore extracts key facts (name, preferences, etc.)")
    print("  3. Next session, agent remembers those facts")
    print("\nExample:")
    print('  Session 1: "My name is Alice, I love Python"')
    print('  Session 2: "What do you know about me?"')
    print('  Agent: "You are Alice and you love Python!"')
    print("\nStarting on http://localhost:8080")
    print("\nNote: Long-term memory extraction takes ~30 seconds")
    print("      after conversation ends.")
    print("\nPress Ctrl+C to stop.\n")
    
    app.run()

