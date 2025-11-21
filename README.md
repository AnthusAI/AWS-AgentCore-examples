# AWS AgentCore Examples

> A hands-on introduction to building AI agents with AWS AgentCore

This repository contains working examples of AWS AgentCore agents, from basic structure to AI-powered applications. Created by the team at [Anthus](https://anthus.ai) as we explore AgentCore capabilities. All examples are tested and deployed to AWS.

## "Give an Agent a Tool" 🛠️

This playground demonstrates the **["Give an Agent a Tool"](https://github.com/AnthusAI/Give-an-Agent-a-Tool)** paradigm - a fundamental shift in how we write software:

> _"Give a man a fish and you feed him for a day. Teach a man to fish and you feed him for a lifetime. **Give an agent a tool and nobody has to fish.**"_

**Traditional programming**: Anticipate every scenario, write explicit logic for each case  
**Agent programming**: Provide tools and goals, let intelligence emerge

Our examples progress from basic structure to sophisticated agents that use AgentCore's managed services (Memory, Code Interpreter) to solve real problems without hard-coded logic.

## What is AWS AgentCore?

AWS AgentCore is a **platform for building and deploying AI agents**. At first glance, it looks similar to AWS Lambda (you write a handler function, it runs in the cloud), but it's specifically designed for the unique needs of AI agents.

### AgentCore vs Lambda: What's Different?

| Feature | Lambda | AgentCore |
|---------|--------|-----------|
| **Execution Time** | 15 minutes max | **8 hours max** (for long-running agent tasks) |
| **State Management** | Stateless (you manage state externally) | **Built-in Memory service** (conversation history, long-term memory) |
| **Identity** | IAM roles only | **OAuth-based Identity** (act on behalf of users, access GitHub/Slack/etc.) |
| **Tools** | You build everything | **Built-in tools** (Code Interpreter, Browser, custom tools) |
| **Purpose** | General event-driven functions | **AI agents specifically** (multi-turn conversations, tool use, memory) |
| **Observability** | CloudWatch | **Agent-specific dashboards** (trace reasoning, tool calls, memory access) |

### Why AgentCore for Agents?

AI agents have unique requirements that Lambda wasn't designed for:

1. **Long-running sessions** - Agents might need to think, use tools, and iterate for hours
2. **Stateful conversations** - Agents need to remember context across turns
3. **Tool orchestration** - Agents need to call multiple tools and reason about results
4. **User identity** - Agents need to act on behalf of users (read their emails, access their repos)
5. **Observability** - You need to see *why* an agent made a decision, not just logs

**AgentCore provides all of this out of the box.**

### What AgentCore Includes

- **Runtime** - Serverless environment optimized for agents (up to 8 hours)
- **Memory** - Short-term (conversation) and long-term (facts) memory
- **Identity** - OAuth for accessing user data across services
- **Gateway** - Turn any API into an agent-compatible tool
- **Tools** - Code Interpreter, Browser, custom tools
- **Observability** - Agent-specific monitoring and debugging

You write a Python function with `@app.entrypoint`, and AgentCore handles the infrastructure, state management, and agent-specific capabilities.

---

## Example 1: Hello World (Understanding the Structure)

**File**: `hello_agent.py`

This is the simplest possible AgentCore application. **No AI yet** - just the framework structure.

### What it demonstrates:

- How to define an AgentCore entrypoint
- Request/response pattern
- Local development
- What AgentCore handles for you (HTTP server, serialization, deployment)

### The code:

```python
from bedrock_agentcore import BedrockAgentCoreApp

app = BedrockAgentCoreApp()

@app.entrypoint
def agent_handler(payload: dict) -> dict:
    user_message = payload.get("prompt", "Hello!")
    return {
        "message": f"You said: '{user_message}'",
        "agent": "Hello World"
    }

if __name__ == "__main__":
    app.run()
```

### Running it:

```bash
conda activate agentcore-playground
python hello_agent.py
```

### Testing it:

```bash
curl -X POST http://localhost:8080/invocations \
  -H "Content-Type: application/json" \
  -d '{"prompt": "Hello!"}'
```

**Response:**
```json
{
  "message": "You said: 'Hello!'",
  "agent": "Hello World",
  "framework": "AWS AgentCore"
}
```

### Key takeaway:

AgentCore is like Lambda - you write a handler function, it handles the infrastructure. The `@app.entrypoint` decorator marks your function as the request handler. AgentCore gives you:
- HTTP server (local development)
- Deployment to AWS (with `agentcore launch`)
- Scaling and monitoring
- Integration with Memory, Identity, Tools, etc.

---

## Example 2: Claude-Powered Agent (Adding AI)

**File**: `claude_agent.py`

Now we add intelligence by calling Claude (via AWS Bedrock) inside our AgentCore handler.

### What it demonstrates:

- Combining AgentCore (framework) + Bedrock (AI access) + Claude (LLM)
- How to make your agent actually intelligent
- Same deployment model, now with AI

### The code:

```python
from bedrock_agentcore import BedrockAgentCoreApp
import boto3
import json

app = BedrockAgentCoreApp()
bedrock_runtime = boto3.client('bedrock-runtime', region_name='us-east-1')

@app.entrypoint
def agent_handler(payload: dict) -> dict:
    user_message = payload.get("prompt", "Hello!")
    
    # Call Claude via Bedrock
    response = bedrock_runtime.invoke_model(
        modelId='anthropic.claude-3-haiku-20240307-v1:0',
        body=json.dumps({
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": 500,
            "messages": [{"role": "user", "content": user_message}]
        })
    )
    
    # Parse and return Claude's response
    response_body = json.loads(response['body'].read())
    return {
        "message": response_body['content'][0]['text'],
        "model": "claude-3-haiku"
    }

if __name__ == "__main__":
    app.run()
```

### Running it:

```bash
conda activate agentcore-playground
python claude_agent.py
```

### Testing it:

```bash
curl -X POST http://localhost:8080/invocations \
  -H "Content-Type: application/json" \
  -d '{"prompt": "Explain what AgentCore is"}'
```

**Response:**
```json
{
  "success": true,
  "message": "AgentCore is a framework for building and deploying intelligent software agents on AWS that can interact with users, access data, and perform tasks autonomously.",
  "model": "claude-3-haiku",
  "framework": "AWS AgentCore"
}
```

### Key takeaway:

AgentCore provides the **infrastructure and deployment**, Bedrock provides **access to AI models**, and Claude provides the **intelligence**. You combine them to build production AI agents.

---

## The Progression

1. **AgentCore alone** (`hello_agent.py`) - Just the framework structure
2. **AgentCore + Bedrock + Claude** (`claude_agent.py`) - Add AI intelligence
3. **Next steps** - Add Memory, Tools, Identity for more capabilities

---

## Getting Started

### Prerequisites

1. **Python 3.10 or higher**
2. **Conda** (Anaconda or Miniconda)
3. **AWS Account** with:
   - AgentCore access
   - Bedrock access (with Claude models enabled)
4. **AWS CLI** configured:
   ```bash
   aws configure
   ```

### Setup

#### 1. Clone and Navigate

```bash
cd ~/Projects
git clone https://github.com/AnthusAI/AWS-AgentCore-examples.git
cd AWS-AgentCore-examples
```

#### 2. Create Environment

```bash
conda create -n agentcore-playground python=3.11 -y
conda activate agentcore-playground
```

#### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

This installs:
- `bedrock-agentcore` - AgentCore SDK
- `bedrock-agentcore-starter-toolkit` - CLI tools
- `boto3` - AWS SDK (for calling Bedrock)

#### 4. Enable Bedrock Models

In AWS Console:
1. Go to Bedrock → Model access
2. Enable `Claude 3 Haiku`
3. Wait for approval (usually instant)

#### 5. Run an Example

```bash
# Simple structure example
python hello_agent.py

# Or AI-powered example
python claude_agent.py
```

---

## Deploying to AWS

Both examples can be deployed to AWS AgentCore:

### 1. Configure

```bash
agentcore configure --entrypoint hello_agent.py
# or
agentcore configure --entrypoint claude_agent.py
```

This sets up IAM roles, ECR repository, and configuration.

### 2. Deploy

```bash
agentcore launch
```

This:
- Builds a container with your agent
- Pushes to Amazon ECR
- Deploys to AgentCore Runtime
- Returns an endpoint URL

### 3. Invoke

```bash
agentcore invoke '{"prompt": "Hello from AWS!"}'
```

Or use the HTTP endpoint:

```bash
curl -X POST https://your-endpoint.amazonaws.com/invocations \
  -H "Content-Type: application/json" \
  -d '{"prompt": "Hello!"}'
```

### 4. Check Status

```bash
agentcore status
```

### 5. Clean Up

```bash
agentcore destroy
```

---

## AgentCore CLI Reference

### Runtime
- `agentcore launch` - Deploy your agent
- `agentcore status` - Check deployment status
- `agentcore invoke` - Invoke your agent
- `agentcore destroy` - Delete resources

### Memory
- `agentcore memory create` - Create memory resource
- `agentcore memory list` - List memories
- `agentcore memory get` - Get memory details
- `agentcore memory delete` - Delete memory

### Identity
- `agentcore identity` - Manage OAuth and permissions

### Gateway
- `agentcore gateway` - Manage API gateways

---

## Project Structure

```
AWS-AgentCore-examples/
├── hello_agent.py              # Example 1: Basic structure
├── claude_agent.py             # Example 2: AI-powered
├── memory_stm_agent.py         # Example 3: Short-term memory
├── memory_ltm_agent.py         # Example 4: Long-term memory
├── code_interpreter_agent.py   # Example 5: Code Interpreter (Give an Agent a Tool)
├── browser_agent.py            # Example 6: Browser Tool (Give an Agent a Tool)
├── requirements.txt            # Dependencies
├── AGENTS.md                   # Detailed documentation
├── LICENSE.md                  # MIT License
├── .gitignore                  # Git ignore patterns
└── README.md                   # This file
```

---

### Example 3: Short-Term Memory Agent 🧠

**File**: `memory_stm_agent.py`

This agent demonstrates how to actually USE AgentCore's short-term memory to maintain conversation context.

**What it demonstrates:**
- Storing conversation turns in memory
- Retrieving recent context
- Providing context to Claude for continuity
- Session-based conversations

**The key difference from previous examples:**
Our earlier agents had memory resources created, but didn't use them. This agent actively stores and retrieves conversation history.

**Running it locally:**

```bash
# First create a memory resource
agentcore memory create stm_test_memory

# Run with the memory ID
BEDROCK_AGENTCORE_MEMORY_ID=stm_test_memory-XXXXXXXXXX python memory_stm_agent.py
```

**Testing it locally:**

```bash
# First message
curl -X POST http://localhost:8080/invocations \
  -H "Content-Type: application/json" \
  -d '{"prompt": "My name is Alice and I love Python"}'

# Second message - it remembers!
curl -X POST http://localhost:8080/invocations \
  -H "Content-Type: application/json" \
  -d '{"prompt": "What is my name and what do I love?"}'
```

**Response:**
```json
{
  "success": true,
  "message": "Your name is Alice and you love Python!",
  "session_id": "default_session",
  "turns_in_memory": 4,
  "memory_type": "STM (Short-Term Memory)"
}
```

**Deploying to AWS:**

```bash
# Configure and deploy
agentcore configure --entrypoint memory_stm_agent.py --non-interactive
agentcore launch

# Test in the cloud
agentcore invoke '{"prompt": "Hi! My name is Frank and I love building agents."}'

# Test memory in same session (use session ID from previous response)
agentcore invoke '{"prompt": "What is my name?"}' --session-id YOUR_SESSION_ID
```

**Cloud response:**
```json
{
  "success": true,
  "message": "Your name is Frank, and you expressed a love for building agents.",
  "session_id": "8e878648-bd6e-4d16-91eb-0d4939c2f878",
  "turns_in_memory": 4,
  "memory_type": "STM (Short-Term Memory)"
}
```

**Key takeaway:** Short-term memory stores conversation turns within a session. Same session_id = same conversation. The agent retrieves recent turns and provides them as context to Claude, enabling natural conversation flow.

---

### Example 4: Long-Term Memory Agent 💾

**File**: `memory_ltm_agent.py`

This agent demonstrates AgentCore's LONG-TERM MEMORY with semantic strategy - it automatically extracts and stores persistent facts.

**What it demonstrates:**
- Short-term memory (conversation turns)
- PLUS automatic extraction of facts/preferences
- Searching long-term memories across sessions
- Learning from past interactions

**The magic:** The code is nearly identical to the STM agent! The difference is in the configuration - LTM agents use "semantic strategy" which tells AgentCore to automatically extract insights.

**How it works:**
1. You have a conversation
2. AgentCore's semantic strategy extracts key facts (name, preferences, etc.)
3. Facts are stored in searchable long-term memory
4. In future sessions, agent searches and retrieves relevant facts
5. Agent responds with knowledge from past conversations

**Running it locally:**

```bash
# Create a memory resource WITH semantic strategy
agentcore memory create ltm_test_memory \
  --strategies '[{"semanticMemoryStrategy": {"name": "Facts"}}]' \
  --wait

# Run with the memory ID
BEDROCK_AGENTCORE_MEMORY_ID=ltm_test_memory-XXXXXXXXXX python memory_ltm_agent.py
```

**Testing it locally:**

```bash
# Have a conversation with facts
curl -X POST http://localhost:8080/invocations \
  -H "Content-Type: application/json" \
  -d '{"prompt": "My name is Emma, I work at Anthus, and I love Python and Rust"}'

# Wait 30 seconds for semantic extraction
sleep 30

# Query what it knows
curl -X POST http://localhost:8080/invocations \
  -H "Content-Type: application/json" \
  -d '{"prompt": "What do you know about me?"}'
```

**Response:**
```json
{
  "success": true,
  "message": "You are Emma, you work at Anthus building AI agents, and you love Python and Rust!",
  "long_term_memories_found": 3,
  "turns_in_memory": 4,
  "memory_type": "LTM (Long-Term Memory with Semantic Strategy)"
}
```

**Deploying to AWS:**

```bash
# First create a memory with semantic strategy
agentcore memory create my_ltm_memory \
  --strategies '[{"semanticMemoryStrategy": {"name": "Facts"}}]' \
  --wait

# Configure (you'll need to manually edit .bedrock_agentcore.yaml to use your memory)
agentcore configure --entrypoint memory_ltm_agent.py --non-interactive

# Edit .bedrock_agentcore.yaml:
# Change memory.mode to: STM_AND_LTM
# Change memory.memory_id to: my_ltm_memory-XXXXXXXXXX

# Deploy
agentcore launch

# Test with facts
agentcore invoke '{"prompt": "Hi! My name is Grace, I work at Anthus, and I love Rust and TypeScript."}'

# Wait 30 seconds for extraction
sleep 30

# Query in a new session
agentcore invoke '{"prompt": "What do you know about Grace?"}'
```

**Cloud response:**
```json
{
  "success": true,
  "message": "Grace works at Anthus building AI agents and loves Rust and TypeScript!",
  "long_term_memories_found": 3,
  "turns_in_memory": 2,
  "memory_type": "LTM (Long-Term Memory with Semantic Strategy)"
}
```

**Key takeaway:** Long-term memory transforms agents from having conversations to building relationships. The semantic strategy automatically identifies and stores important information, making agents truly remember users across sessions.

---

### Example 5: Code Interpreter Agent 🔧

**File**: `code_interpreter_agent.py`

This agent demonstrates the **"Give an Agent a Tool"** paradigm using AgentCore's managed Code Interpreter. Instead of writing complex parsing logic for every possible CSV format, we give the agent ONE tool and let it figure out how to solve the problem.

> **Inspired by**: [Give an Agent a Tool](https://github.com/AnthusAI/Give-an-Agent-a-Tool) - A demonstration of the paradigm shift from hard-coded logic to intelligent delegation.

**What it demonstrates:**
- AgentCore's managed Code Interpreter (secure Python sandbox)
- The "Give an Agent a Tool" paradigm
- Agent autonomously writing and executing code
- Handling varying data formats WITHOUT code changes

**The Problem** (from the Give an Agent a Tool project):
You receive CSV files with varying formats:
- Different headers: "First Name,Last Name" vs "Nombre,Apellidos"
- Different languages: English, Spanish, etc.
- Different column orders: "Last,First" vs "First,Last"
- Messy legacy formats

**Traditional approach**: Write if/else logic for every variation  
**Agent approach**: Give the agent Code Interpreter and let it adapt

**Running it locally:**

```bash
# Install dependencies (includes strands-agents for Code Interpreter)
pip install -r requirements.txt

# Run the agent
python code_interpreter_agent.py
```

**Testing with different formats:**

```bash
# English CSV
curl -X POST http://localhost:8080/invocations \
  -H "Content-Type: application/json" \
  -d '{"csv": "First Name,Last Name,Email\nJohn,Doe,john@example.com"}'

# Spanish CSV - NO CODE CHANGES NEEDED!
curl -X POST http://localhost:8080/invocations \
  -H "Content-Type: application/json" \
  -d '{"csv": "Nombre,Apellidos,Correo\nLuis,García,luis@empresa.es"}'
```

**Response:**
```json
{
  "success": true,
  "message": "Contacts extracted successfully using Code Interpreter",
  "agent_response": "Perfect! I've successfully extracted the contacts...\n[{\"name\": \"Luis García\", \"email\": \"luis@empresa.es\"}]",
  "paradigm": "Give an Agent a Tool - no hard-coded parsing logic needed!"
}
```

**Deploying to AWS:**

```bash
# Configure and deploy
agentcore configure --entrypoint code_interpreter_agent.py --non-interactive
agentcore launch

# Test with English format
agentcore invoke '{"csv": "First Name,Last Name,Email\nJohn,Doe,john@example.com"}'

# Test with Spanish format - SAME CODE!
agentcore invoke '{"csv": "Nombre,Apellidos,Correo\nLuis,García,luis@empresa.es"}'
```

**Key takeaway:** This is the paradigm shift. The traditional approach requires anticipating every format and writing explicit logic for each. The agent approach provides ONE capability (Code Interpreter) and lets intelligence emerge. When a new format appears, you don't patch code—you reuse the same tool, and the agent adapts.

**What makes this AgentCore-specific:**
- **Code Interpreter is a managed service** - You don't build the Python sandbox
- **Secure execution** - Code runs in isolated, ephemeral environments
- **Integrated with Bedrock** - Agent decides when to write/execute code
- **Production-ready** - Built-in monitoring, logging, and observability

---

### Example 6: Browser Tool Agent 🌐

**File**: `browser_agent.py`

This agent demonstrates AgentCore's managed Browser Tool - another example of the **"Give an Agent a Tool"** paradigm. Instead of writing custom web scraping logic for every website, we give the agent a browser and let it navigate and extract information.

**What AgentCore provides:**
- **Secure, cloud-based browser runtime** - You don't provision browser infrastructure
- **VM-level isolation** - Each session is isolated for security
- **Automatic session management** - Timeouts, cleanup, pooling handled by AWS
- **Built-in observability** - Monitor browser sessions in real-time
- **Production-ready** - Scaling, security, monitoring all managed

**Without AgentCore, you'd build:**
- Browser infrastructure (EC2, containers, Selenium Grid)
- Session management and cleanup
- Security isolation between sessions
- Monitoring and logging
- Scaling logic

**With AgentCore:**
- Call `browser_session()` and get a secure browser
- Focus on WHAT the browser should do, not HOW to run it

**Running it locally:**

```bash
# Install Playwright
pip install playwright
playwright install chromium

# Run the agent
python browser_agent.py
```

**Testing - Let the agent explain what AgentCore is:**

```bash
curl -X POST http://localhost:8080/invocations \
  -H "Content-Type: application/json" \
  -d '{"url": "https://aws.amazon.com/bedrock/agentcore/", "question": "What is AWS AgentCore?"}'
```

**Response:**
```json
{
  "success": true,
  "url": "https://aws.amazon.com/bedrock/agentcore/",
  "page_title": "Amazon Bedrock AgentCore- AWS",
  "question": "What is AWS AgentCore?",
  "answer": "Amazon Bedrock AgentCore is an agentic platform that allows users to build, deploy, and operate highly capable AI agents securely at scale. Key points:\n\n1. It is a suite of fully-managed services that can be used together or independently to enhance, deploy, and monitor AI agents.\n\n2. It works with any AI framework (e.g. CrewAI, LangGraph, LlamaIndex) and any foundation model, providing flexibility and interoperability.\n\n3. Key capabilities include:\n   - Enhancing agents with tools, memory, and the ability to execute code securely\n   - Deploying agents on secure, serverless infrastructure with low-latency and extended runtimes\n   - Monitoring agent behavior through intuitive dashboards\n\n4. Key benefits include faster time to value, flexibility, and enterprise-grade security and reliability.\n\n5. AgentCore is designed to address the critical business challenges of deploying production-ready AI agents at scale, without the need for infrastructure management.\n\nIn summary, AgentCore is an AWS service that provides a comprehensive platform to build, deploy, and operate highly capable AI agents across various frameworks and models, with a focus on security, scalability, and operational excellence.",
  "paradigm": "Give an Agent a Tool - browser automation without custom scraping logic!"
}
```

**Key takeaway:** The agent visited the AWS AgentCore page and explained what AgentCore is - demonstrating both the Browser Tool capability AND teaching about the platform itself! The same code works for any website - no custom scraping logic needed.

**Note:** The Browser Tool works locally for testing. For production deployment to AWS, there are additional configuration requirements for the browser runtime environment.

---

## Important Notes

### Cleaning Up

To avoid ongoing AWS charges, destroy your agents when done experimenting:

```bash
agentcore destroy
```

This removes:
- Agent runtimes
- Memory resources
- IAM roles
- S3 deployment packages

### Cost Management

- **Local development**: Free
- **Deployed agents**: Charges accrue even when idle
- **Best practice**: Destroy agents after testing, redeploy when needed
- Deployment takes ~3-4 minutes, so it's quick to spin up/down

---

## Cost Considerations

- **Local development**: Free
- **Deployed to AWS**:
  - Runtime charges (per hour)
  - Invocation charges (per request)
  - Model charges (Claude usage)
  - Memory/storage charges

Development/testing should cost pennies. Check [aws.amazon.com/bedrock/pricing](https://aws.amazon.com/bedrock/pricing/) for current rates.

---

## Troubleshooting

### Agent won't start

- Check Python version: `python --version` (need 3.10+)
- Verify packages: `pip list | grep bedrock`
- Check port 8080: `lsof -i :8080`

### Claude agent fails

- Verify AWS credentials: `aws sts get-caller-identity`
- Check Bedrock model access in AWS Console
- Ensure Claude 3 Haiku is enabled

### Deployment fails

- Check IAM permissions
- Review CloudFormation logs
- Verify region supports AgentCore

---

## Resources

- [AWS AgentCore Documentation](https://docs.aws.amazon.com/bedrock-agentcore/)
- [AgentCore Python SDK](https://github.com/aws/bedrock-agentcore-sdk-python)
- [AgentCore Starter Toolkit](https://aws.github.io/bedrock-agentcore-starter-toolkit/)
- [AWS Bedrock Documentation](https://docs.aws.amazon.com/bedrock/)

---

## Contributing

Found an issue or have an improvement? Pull requests welcome!

## About Anthus

This repository is maintained by [Anthus](https://anthus.ai), where we're building the future of AI-powered conversation intelligence.

## License

MIT License - See `LICENSE.md`

---

Happy agent building! 🚀
