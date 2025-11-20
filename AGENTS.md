# Agents Documentation

This document describes all agents in the AWS AgentCore playground, their capabilities, and how to use them.

## Hello World Agent

**File**: `hello_agent.py`  
**Status**: Active  
**SDK**: bedrock-agentcore 1.0.6

### Overview

The Hello World Agent is the simplest possible AgentCore example. It demonstrates the basic structure of an AgentCore application and serves as a starting point for building more complex agents.

### Purpose

This agent serves as:
- A starting point for learning AgentCore
- A template for building more complex agents
- A test bed for understanding the AgentCore SDK
- A reference implementation for the playground

### How It Works

1. Initializes a `BedrockAgentCoreApp` instance
2. Defines an entrypoint function with `@app.entrypoint`
3. Accepts incoming requests as dictionaries
4. Returns responses as dictionaries
5. AgentCore handles all HTTP server setup, serialization, and infrastructure

### Request Format

The agent accepts HTTP POST requests to `/invocations`:

```json
{
  "prompt": "Your message here"
}
```

**Fields**:
- `prompt` (string, optional): The user's message. Defaults to "Hello!" if not provided.

### Response Format

```json
{
  "message": "Hello from AWS AgentCore! You said: 'Your message here'",
  "agent_type": "AgentCore Hello World",
  "sdk_version": "1.0.6"
}
```

### Usage

**Local Development:**

```bash
# Start the agent
python hello_agent.py

# In another terminal, test it
curl -X POST http://localhost:8080/invocations \
  -H "Content-Type: application/json" \
  -d '{"prompt": "Hello!"}'
```

**Deploy to AWS:**

```bash
# Configure deployment
agentcore configure --entrypoint hello_agent.py

# Deploy
agentcore launch

# Invoke
agentcore invoke '{"prompt": "Hello from the cloud!"}'
```

### Configuration

**SDK Version**: `bedrock-agentcore 1.0.6`
- Local development on port 8080
- Automatic health checks
- Built-in logging and monitoring
- Container-based deployment to AWS

### Key Concepts

**BedrockAgentCoreApp**: The main application class that handles:
- HTTP server setup
- Request routing
- Response serialization
- Health checks
- Logging

**@app.entrypoint**: Decorator that marks your function as the main handler:
- Receives payload as a dictionary
- Must return a dictionary
- AgentCore handles all serialization

**Local vs Deployed**: 
- Locally: Runs on localhost:8080 for development
- Deployed: Runs on AWS infrastructure with auto-scaling, monitoring, etc.

### Error Handling

The agent includes basic error handling:
- Missing fields default to sensible values
- Exceptions are caught and logged
- AgentCore provides health check endpoints

### Extending This Agent

To build on this foundation:

1. **Add Bedrock Integration**: Call Claude or other models
   ```python
   import boto3
   bedrock = boto3.client('bedrock-runtime')
   # Use bedrock.invoke_model() in your handler
   ```

2. **Add Memory**: Use AgentCore Memory service
   ```bash
   agentcore memory create --name my-memory
   ```

3. **Add Tools**: Define tools your agent can use
   ```python
   @app.tool
   def my_tool(params):
       return result
   ```

4. **Add Identity**: Connect to external services
   ```bash
   agentcore identity configure
   ```

### Limitations

Current limitations:
- No conversation history (stateless)
- No AI model integration yet
- No tool/function calling
- Single-turn request/response only

These are intentional - this is a minimal example to understand the AgentCore structure.

### Cost Considerations

- **Local development**: Free (runs on your machine)
- **Deployed to AWS**: 
  - Runtime charges per hour
  - Invocation charges per request
  - Minimal for testing/development

---

## Ideas for Future Agents

Here are some ideas for additional agents to build in this playground:

### 1. Conversational Agent with Memory
- Use AgentCore Memory service
- Maintain conversation context
- Remember user preferences
- Multi-turn conversations

### 2. Claude-Powered Agent
- Integrate AWS Bedrock
- Use Claude for natural language understanding
- Streaming responses
- Tool use with Claude

### 3. Multi-Tool Agent
- Code Interpreter tool
- Browser automation tool
- Custom API tools
- Autonomous tool selection

### 4. Identity-Enabled Agent
- OAuth integration
- Access user's GitHub repos
- Send Slack messages
- Read/write to Google Drive

### 5. Document Analyzer Agent
- Upload documents to S3
- Use Bedrock to analyze
- Extract key information
- Answer questions about documents

### 6. RAG (Retrieval Augmented Generation) Agent
- Vector database integration
- Semantic search
- Context-aware responses
- Cite sources

### 7. Multi-Agent Orchestrator
- Coordinate multiple specialized agents
- Route requests to appropriate agent
- Combine results
- Handle complex workflows

### 8. Observability Demo Agent
- Demonstrate AgentCore Observability
- Custom metrics
- Trace visualization
- Performance monitoring

## Agent Development Guidelines

When creating new agents for this playground:

1. **Start Simple**: Begin with the hello world pattern
2. **Document Everything**: Add detailed documentation to this file
3. **Error Handling**: Always include proper error handling
4. **Cost Awareness**: Be mindful of AWS costs
5. **Testing**: Test locally before deploying
6. **Naming**: Use descriptive names (e.g., `claude_chat_agent.py`)
7. **Configuration**: Make settings configurable
8. **Logging**: Use proper logging for debugging
9. **Security**: Never commit credentials

## Testing Checklist

Before deploying a new agent:

- [ ] Local testing completed
- [ ] Error handling verified
- [ ] Documentation updated in this file
- [ ] README.md updated if needed
- [ ] Costs estimated
- [ ] Security review done
- [ ] Teammate notified

## Shared Agent Registry

Keep track of agents in this playground:

| Agent Name | File | Type | Status | Last Updated |
|------------|------|------|--------|--------------|
| Hello World | hello_agent.py | Simple AgentCore app | Active | 2025-11-20 |

Update this table when creating new agents or making changes.

---

## AgentCore Services Reference

Quick reference for AgentCore services you can integrate:

### Runtime
- Managed execution environment
- Auto-scaling
- Health checks
- Logging

### Memory
- Short-term memory (conversation context)
- Long-term memory (user preferences, facts)
- Automatic persistence
- Query and retrieval APIs

### Identity
- OAuth 2.0 integration
- AWS service access
- Third-party service access (GitHub, Slack, etc.)
- Secure credential management

### Tools
- **Code Interpreter**: Execute Python code securely
- **Browser**: Interact with web pages
- **Custom Tools**: Define your own tools

### Gateway
- API gateway for your agents
- Rate limiting
- Authentication
- Request routing

### Observability
- CloudWatch integration
- Custom metrics
- Distributed tracing
- Performance monitoring

---

## Resources

- [AgentCore Python SDK](https://github.com/aws/bedrock-agentcore-sdk-python)
- [AgentCore Starter Toolkit](https://aws.github.io/bedrock-agentcore-starter-toolkit/)
- [AWS AgentCore Documentation](https://docs.aws.amazon.com/bedrock-agentcore/)
- [AWS Bedrock Documentation](https://docs.aws.amazon.com/bedrock/)
