# AWS AgentCore Examples

> A hands-on introduction to building AI agents with AWS AgentCore

This repository contains working examples of AWS AgentCore agents, from basic structure to AI-powered applications. Created by the team at [Anthus](https://anthus.ai) as we explore AgentCore capabilities. All examples are tested and deployed to AWS.

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
├── hello_agent.py          # Example 1: Basic structure
├── claude_agent.py         # Example 2: AI-powered
├── requirements.txt        # Dependencies
├── AGENTS.md              # Detailed documentation
├── LICENSE.md             # MIT License
├── .gitignore             # Git ignore patterns
└── README.md              # This file
```

---

## What's Next?

### Add AgentCore Memory

Use the built-in Memory service to maintain conversation context:

```bash
# Create a memory resource
agentcore memory create --name my-agent-memory

# Use it in your agent code
from bedrock_agentcore.memory import Memory
memory = Memory("my-agent-memory")
```

### Add Tools

Integrate AgentCore tools:
- **Code Interpreter** - Execute Python code
- **Browser** - Interact with web pages
- **Custom tools** - Your own functions

### Add Identity

Connect to external services:
- GitHub repositories
- Slack workspaces
- Gmail accounts
- Custom OAuth apps

### Multi-Agent Systems

Build multiple specialized agents and coordinate them.

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
