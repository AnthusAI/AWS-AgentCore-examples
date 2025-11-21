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

---

## Short-Term Memory Agent

**File**: `memory_stm_agent.py`  
**Status**: Active  
**SDK**: bedrock-agentcore 1.0.6
**Memory**: STM (Short-Term Memory)

### Overview

This agent demonstrates how to actually USE AgentCore's short-term memory. Unlike the earlier examples that had memory resources but didn't use them, this agent actively stores and retrieves conversation history.

### How It Works

1. Gets session_id from AgentCore context
2. Creates/retrieves a memory session
3. Retrieves last 5 conversation turns
4. Provides context to Claude
5. Stores user message in memory
6. Stores Claude's response in memory

### Memory Operations

```python
# Get recent turns
recent_turns = session.get_last_k_turns(k=5)

# Add user message
session.add_turns(messages=[
    ConversationalMessage(user_message, MessageRole.USER)
])

# Add assistant response  
session.add_turns(messages=[
    ConversationalMessage(agent_message, MessageRole.ASSISTANT)
])
```

### Testing

The agent maintains conversation context within a session:

```bash
# First message
{"prompt": "My name is Alice"}
# Response: "Nice to meet you, Alice!"

# Second message (same session)
{"prompt": "What is my name?"}
# Response: "Your name is Alice!"
```

### Configuration

- Memory mode: STM_ONLY (default)
- Works with any AgentCore memory resource
- Session-based (same session_id = same conversation)

---

## Long-Term Memory Agent

**File**: `memory_ltm_agent.py`  
**Status**: Active  
**SDK**: bedrock-agentcore 1.0.6
**Memory**: LTM (Long-Term Memory with Semantic Strategy)

### Overview

This agent demonstrates AgentCore's long-term memory with semantic strategy. It automatically extracts facts and preferences from conversations and stores them for future retrieval.

### How It Works

1. Stores conversation turns (same as STM)
2. **Semantic strategy automatically extracts insights** (happens in background)
3. Searches long-term memories relevant to current query
4. Provides both recent context AND long-term facts to Claude
5. Agent responds with knowledge from past sessions

### Memory Operations

```python
# Get recent turns (STM)
recent_turns = session.get_last_k_turns(k=5)

# Search long-term memories (LTM)
long_term_memories = session.search_long_term_memories(
    query=user_message,
    namespace_prefix="/",
    top_k=3
)

# Both contexts provided to Claude
```

### Key Difference from STM

**Code**: Nearly identical!  
**Configuration**: Uses semantic strategy instead of STM_ONLY  
**Behavior**: Automatically extracts and stores facts

### Semantic Strategy

When enabled, AgentCore:
- Analyzes conversation turns
- Extracts key facts (names, preferences, etc.)
- Stores them in searchable format
- Takes ~30 seconds after conversation
- Persists across sessions

### Example

**Session 1:**
```
User: "My name is Alice, I work at Anthus"
Agent: "Nice to meet you, Alice!"
[Semantic strategy extracts: name=Alice, company=Anthus]
```

**Session 2 (days later):**
```
User: "Where do I work?"
Agent: "You work at Anthus!"
[Retrieved from long-term memory]
```

### Configuration

Must be deployed with semantic strategy:

```bash
agentcore configure --entrypoint memory_ltm_agent.py
# Choose: "Create new memory with STM + LTM (semantic strategy)"
```

---

## Code Interpreter Agent

**File**: `code_interpreter_agent.py`  
**Status**: Active  
**SDK**: bedrock-agentcore 1.0.6, strands-agents 1.17.0  
**Tool**: Code Interpreter (AgentCore managed service)

### Overview

This agent demonstrates the **"Give an Agent a Tool"** paradigm using AgentCore's managed Code Interpreter. Instead of writing complex parsing logic for every possible CSV format, we give the agent ONE tool (Code Interpreter) and let it figure out how to solve the problem.

**Inspired by**: [Give an Agent a Tool](https://github.com/AnthusAI/Give-an-Agent-a-Tool)

### The Problem

You receive CSV files with varying formats:
- Different headers: "First Name,Last Name,Email" vs "Nombre,Apellidos,Correo"
- Different languages: English, Spanish, etc.
- Different column orders: "Last,First" vs "First,Last"
- Messy legacy formats with mixed data

**Traditional approach**: Write if/else logic for every variation (brittle, hard to maintain)  
**Agent approach**: Give the agent Code Interpreter and let it adapt (flexible, self-maintaining)

### How It Works

1. Agent receives CSV data as input
2. Agent analyzes the format (headers, language, structure)
3. Agent writes Python code to parse and extract contacts
4. Code Interpreter executes the code in AgentCore's secure sandbox
5. Agent returns structured contact data

**Key insight**: The SAME code handles English, Spanish, reversed columns, messy formats—no changes needed!

### Code Interpreter Tool

AgentCore's Code Interpreter is a **managed service**:
- Secure Python sandbox (isolated, ephemeral environments)
- Integrated with Bedrock (agent decides when to write/execute code)
- Production-ready (built-in monitoring, logging, observability)
- You don't build the sandbox—AgentCore provides it

### Testing Locally

```bash
# Install dependencies
pip install -r requirements.txt

# Run the agent
python code_interpreter_agent.py

# Test with English CSV
curl -X POST http://localhost:8080/invocations \
  -H "Content-Type: application/json" \
  -d '{"csv": "First Name,Last Name,Email\nJohn,Doe,john@example.com"}'

# Test with Spanish CSV - NO CODE CHANGES!
curl -X POST http://localhost:8080/invocations \
  -H "Content-Type: application/json" \
  -d '{"csv": "Nombre,Apellidos,Correo\nLuis,García,luis@empresa.es"}'
```

### Deploying to AWS

```bash
agentcore configure --entrypoint code_interpreter_agent.py --non-interactive
agentcore launch

# Test in the cloud
agentcore invoke '{"csv": "First Name,Last Name,Email\nJohn,Doe,john@example.com"}'
agentcore invoke '{"csv": "Nombre,Apellidos,Correo\nLuis,García,luis@empresa.es"}'
```

### Example Response

```json
{
  "success": true,
  "message": "Contacts extracted successfully using Code Interpreter",
  "agent_response": "Perfect! I've successfully extracted the contacts...\n[{\"name\": \"Luis García\", \"email\": \"luis@empresa.es\"}]",
  "paradigm": "Give an Agent a Tool - no hard-coded parsing logic needed!"
}
```

### Key Takeaway

This demonstrates the paradigm shift from traditional programming to agent-based programming:

**Traditional**: You must think of everything (every format, every edge case, every language)  
**Agent**: You provide ONE capability (Code Interpreter) and let intelligence emerge

When a new CSV format appears:
- Traditional: Add more if/else branches, risk breaking existing code
- Agent: Same code, agent adapts automatically

### What Makes This AgentCore-Specific

This isn't just "calling Claude with tool use"—it's using AgentCore's **managed Code Interpreter service**:

1. **You don't build the sandbox** - AgentCore provides secure Python execution
2. **Production-ready** - Built-in monitoring, logging, observability
3. **Integrated** - Works seamlessly with AgentCore Memory, Identity, etc.
4. **Managed** - AWS handles security, scaling, updates

---

## Browser Tool Agent

**File**: `browser_agent.py`  
**Status**: Active (local testing)  
**SDK**: bedrock-agentcore 1.0.6, playwright 1.56.0  
**Tool**: Browser Tool (AgentCore managed service)

### Overview

This agent demonstrates AgentCore's managed Browser Tool. Instead of writing custom web scraping logic for every website, we give the agent a browser and let it navigate and extract information.

**Inspired by**: [Give an Agent a Tool](https://github.com/AnthusAI/Give-an-Agent-a-Tool)

### What AgentCore Provides

The Browser Tool is a **managed service** that provides:

1. **Secure, cloud-based browser runtime** - You don't provision browser infrastructure
2. **VM-level isolation** - Each session is isolated for security
3. **Automatic session management** - Timeouts, cleanup, pooling handled by AWS
4. **Built-in observability** - Monitor browser sessions in real-time
5. **Production-ready** - Scaling, security, monitoring all managed

### Without AgentCore

You would need to build:
- Browser infrastructure (EC2 instances, Selenium Grid, containers)
- Session management and cleanup logic
- Security isolation between sessions
- Monitoring and logging systems
- Scaling and load balancing

### With AgentCore

```python
from bedrock_agentcore.tools.browser_client import browser_session

# That's it! AgentCore provides the secure browser
with browser_session('us-west-2') as client:
    ws_url, headers = client.generate_ws_headers()
    # Connect to AgentCore's managed browser
```

### How It Works

1. Agent receives a URL and question
2. Agent connects to AgentCore's secure browser session
3. Agent navigates to the URL using Playwright
4. Agent extracts page content
5. Agent uses Claude to analyze the content and answer the question

**Key insight**: The SAME code works for any website - no custom scraping logic!

### Example: Agent Explains AgentCore

The perfect meta-example - the agent visits the AWS AgentCore page and explains what AgentCore is:

```bash
curl -X POST http://localhost:8080/invocations \
  -H "Content-Type: application/json" \
  -d '{"url": "https://aws.amazon.com/bedrock/agentcore/", "question": "What is AWS AgentCore?"}'
```

**Response**: The agent successfully navigates to the AgentCore page, extracts content, and provides a comprehensive explanation:

> "Amazon Bedrock AgentCore is an agentic platform that allows users to build, deploy, and operate highly capable AI agents securely at scale... It is a suite of fully-managed services... works with any AI framework... Key capabilities include enhancing agents with tools, memory, and the ability to execute code securely..."

This demonstrates both the Browser Tool capability AND teaches about the platform itself!

### Testing Locally

```bash
# Install dependencies
pip install playwright nest-asyncio
playwright install chromium

# Run the agent
python browser_agent.py

# Test with any website
curl -X POST http://localhost:8080/invocations \
  -H "Content-Type: application/json" \
  -d '{"url": "https://example.com", "question": "What is this website about?"}'
```

### Deployment Note

The Browser Tool works perfectly for local testing. For production deployment to AWS AgentCore, there are additional configuration requirements for the browser runtime environment (Playwright binaries, permissions, etc.).

### Key Takeaway

This demonstrates the paradigm shift:

**Traditional**: Write custom scraping logic for each website structure  
**Agent**: Give the agent a browser and let it adapt to any website

The agent figures out how to navigate and extract information - you just provide the tool and the goal.

---

## Shared Agent Registry

Keep track of agents in this playground:

| Agent Name | File | Type | Status | Last Updated |
|------------|------|------|--------|--------------|
| Hello World | hello_agent.py | Simple AgentCore app | Active | 2025-11-20 |
| Claude Agent | claude_agent.py | AI-powered | Active | 2025-11-20 |
| STM Agent | memory_stm_agent.py | Short-term memory | Active | 2025-11-20 |
| LTM Agent | memory_ltm_agent.py | Long-term memory | Active | 2025-11-20 |
| Code Interpreter | code_interpreter_agent.py | Code execution tool | Active | 2025-11-21 |
| Browser Tool | browser_agent.py | Web automation tool | Active (local) | 2025-11-21 |

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
