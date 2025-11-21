"""
Browser Tool Agent - Web Research Assistant

This agent demonstrates AgentCore's managed Browser Tool - a key feature that
distinguishes AgentCore from just "running Playwright in Lambda."

WHAT AGENTCORE PROVIDES:
- Secure, cloud-based browser runtime (you don't provision browsers)
- VM-level isolation (each session is isolated)
- Automatic session management (timeouts, cleanup)
- Built-in observability (monitor browser sessions)
- Production-ready infrastructure (scaling, security)

WITHOUT AGENTCORE, YOU'D BUILD:
- Browser infrastructure (EC2 instances, containers)
- Session management (timeouts, cleanup, pooling)
- Security isolation (prevent cross-session contamination)
- Monitoring and logging
- Scaling logic

WITH AGENTCORE:
- Call browser_session() and get a secure browser
- AWS handles all the infrastructure
- Focus on what the browser should DO, not HOW to run it

This is the "Give an Agent a Tool" paradigm:
- Traditional: Write custom scraping logic for each website
- Agent: Give the agent a browser and let it adapt
"""

import boto3
import json
from bedrock_agentcore import BedrockAgentCoreApp, RequestContext
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeout
from bedrock_agentcore.tools.browser_client import browser_session
from botocore.exceptions import ClientError

app = BedrockAgentCoreApp()

BEDROCK_RUNTIME = boto3.client(
    service_name="bedrock-runtime",
    region_name="us-west-2"
)

@app.entrypoint
def research_website(request: RequestContext) -> dict:
    """
    Research a website and extract information using AgentCore's Browser Tool.
    
    The agent will navigate to the URL and extract the requested information.
    """
    url = request.get("url", "")
    question = request.get("question", "What is this website about?")
    
    if not url:
        return {
            "success": False,
            "message": "Please provide a URL to research",
            "example": {
                "url": "https://example.com",
                "question": "What is the main topic of this website?"
            }
        }
    
    try:
        # Use AgentCore's managed Browser Tool
        # KEY: browser_session() connects to AgentCore's cloud-based browser runtime
        # You don't provision browsers - AWS provides secure, isolated browser sessions
        with sync_playwright() as playwright:
            with browser_session('us-west-2') as client:
                # AgentCore provides the browser endpoint and auth headers
                ws_url, headers = client.generate_ws_headers()
                
                # Connect to AgentCore's managed browser (not your local browser!)
                browser = playwright.chromium.connect_over_cdp(ws_url, headers=headers)
                context = browser.contexts[0]
                page = context.pages[0]
                
                try:
                    # Navigate to the URL
                    page.goto(url, timeout=30000)
                    page.wait_for_load_state('networkidle', timeout=10000)
                    
                    # Extract page content
                    title = page.title()
                    content = page.inner_text('body')
                    
                    # Limit content size for Claude
                    if len(content) > 5000:
                        content = content[:5000] + "... (content truncated)"
                    
                    # Ask Claude to analyze the page content
                    prompt = f"""I visited the website: {url}

Page Title: {title}

Page Content:
{content}

Question: {question}

Please provide a clear, concise answer based on the page content."""

                    response = BEDROCK_RUNTIME.invoke_model(
                        modelId="anthropic.claude-3-haiku-20240307-v1:0",
                        contentType="application/json",
                        accept="application/json",
                        body=json.dumps({
                            "anthropic_version": "bedrock-2023-05-31",
                            "max_tokens": 1000,
                            "messages": [
                                {"role": "user", "content": prompt}
                            ]
                        })
                    )
                    
                    response_body = json.loads(response.get("body").read())
                    answer = response_body["content"][0]["text"]
                    
                    return {
                        "success": True,
                        "url": url,
                        "page_title": title,
                        "question": question,
                        "answer": answer,
                        "paradigm": "Give an Agent a Tool - browser automation without custom scraping logic!"
                    }
                    
                except PlaywrightTimeout:
                    return {
                        "success": False,
                        "message": f"Timeout loading {url}. The page took too long to load.",
                        "url": url
                    }
                except Exception as e:
                    return {
                        "success": False,
                        "message": f"Error navigating to website: {str(e)}",
                        "url": url
                    }
                finally:
                    browser.close()
                    
    except Exception as e:
        return {
            "success": False,
            "message": f"Error: {str(e)}",
            "url": url
        }

if __name__ == "__main__":
    app.run()

