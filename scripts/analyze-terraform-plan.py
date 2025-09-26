#!/usr/bin/env python3
"""
Terraform Plan Analysis using Azure OpenAI
Analyzes Terraform plan output and provides AI-powered insights using Azure OpenAI Service
"""

import os
import sys
import json
import subprocess
import requests
from typing import Dict, Any

def get_terraform_plan_text() -> str:
    """Generate human-readable Terraform plan output"""
    try:
        # Run terraform show to get human-readable plan
        result = subprocess.run(
            ['terraform', 'show', '-no-color', 'tfplan'],
            capture_output=True,
            text=True,
            check=True
        )
        return result.stdout
    except subprocess.CalledProcessError as e:
        print(f"Error generating plan text: {e}")
        print(f"stderr: {e.stderr}")
        return ""

def analyze_plan_with_azure_openai(plan_text: str, api_key: str, endpoint: str, deployment_name: str, api_version: str = "2024-02-15-preview") -> Dict[str, Any]:
    """Send Terraform plan to Azure OpenAI for analysis"""
    
    system_prompt = """You are a Terraform infrastructure expert and security analyst. 
Analyze the provided Terraform plan and provide insights on:

1. SECURITY ANALYSIS:
   - Security vulnerabilities or misconfigurations
   - Network security recommendations
   - Access control issues
   - Password/secrets management concerns

2. COST OPTIMIZATION:
   - Resource sizing recommendations
   - Cost-saving opportunities
   - Over-provisioned resources

3. BEST PRACTICES:
   - Terraform best practices violations
   - Azure-specific recommendations
   - Resource naming and tagging

4. RISK ASSESSMENT:
   - High-risk changes
   - Potential downtime or service disruption
   - Dependencies and impact analysis

5. RECOMMENDATIONS:
   - Specific actionable improvements
   - Alternative approaches
   - Future considerations

Format your response in clear sections with bullet points. Be concise but thorough.
Focus on actionable insights that would help in a DevOps pipeline review. Keep response under 3500 characters for file output. Use plain text format only - no markdown formatting."""

    user_prompt = f"""Please analyze this Terraform plan for Azure infrastructure deployment:

```
{plan_text}
```

Provide your analysis following the structure requested in the system prompt."""

    # Azure OpenAI uses api-key header instead of Authorization Bearer
    headers = {
        'api-key': api_key,
        'Content-Type': 'application/json'
    }
    
    payload = {
        'messages': [
            {'role': 'system', 'content': system_prompt},
            {'role': 'user', 'content': user_prompt}
        ],
        'max_tokens': 1500,
        'temperature': 0.1
    }
    
    # Construct Azure OpenAI endpoint URL
    url = f"https://tf-open-ai.openai.azure.com/openai/deployments/gpt-4/chat/completions?api-version=2025-01-01-preview"
    
    try:
        response = requests.post(
            url,
            headers=headers,
            json=payload,
            timeout=60
        )
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error calling Azure OpenAI API: {e}")
        if hasattr(e, 'response') and e.response is not None:
            print(f"Response status: {e.response.status_code}")
            print(f"Response text: {e.response.text}")
        return {}

def format_analysis_output(analysis_response: Dict[str, Any]) -> str:
    """Format the Azure OpenAI analysis response for pipeline output"""
    
    if not analysis_response or 'choices' not in analysis_response:
        return "❌ Failed to get analysis from Azure OpenAI"
    
    analysis_text = analysis_response['choices'][0]['message']['content']
    
    # Format for Azure DevOps pipeline display
    formatted_output = f"""
##[section]🤖 AI-Powered Terraform Plan Analysis

{analysis_text}

---
💡 Analysis completed using Azure OpenAI Service
⚠️  Please review recommendations carefully before deployment
"""
    
    return formatted_output

def save_analysis_to_file(analysis: str, filename: str = "terraform-analysis.txt"):
    """Save analysis to file for artifact publishing"""
    try:
        # Extract plain text content from analysis (remove Azure DevOps formatting)
        plain_text = analysis.replace("##[section]🤖 AI-Powered Terraform Plan Analysis\n\n", "")
        plain_text = plain_text.replace("\n\n---\n💡 Analysis completed using Azure OpenAI Service\n⚠️  Please review recommendations carefully before deployment\n", "")
        
        # Limit content to 4000 characters total
        header = f"Terraform Plan Analysis\n\nGenerated: {subprocess.run(['date'], capture_output=True, text=True).stdout.strip()}\n\n"
        max_content_length = 4000 - len(header)
        
        if len(plain_text) > max_content_length:
            plain_text = plain_text[:max_content_length-50] + "\n\n[Content truncated to fit 4000 character limit]"
        
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(header)
            f.write(plain_text)
        print(f"Analysis saved to {filename} (max 4000 characters)")
    except Exception as e:
        print(f"Error saving analysis to file: {e}")

def main():
    """Main function to run the Terraform plan analysis"""
    
    # Get Azure OpenAI configuration from environment
    api_key = os.getenv('AZURE_OPENAI_API_KEY')
    endpoint = os.getenv('AZURE_OPENAI_ENDPOINT')
    deployment_name = os.getenv('AZURE_OPENAI_DEPLOYMENT_NAME', 'gpt-4')
    api_version = os.getenv('AZURE_OPENAI_API_VERSION', '2024-02-15-preview')
    
    # Validate required environment variables
    if not api_key:
        print("##[error]AZURE_OPENAI_API_KEY environment variable not set")
        print("##[warning]Skipping AI analysis. Set AZURE_OPENAI_API_KEY variable in pipeline.")
        return 0
    
    if not endpoint:
        print("##[error]AZURE_OPENAI_ENDPOINT environment variable not set")
        print("##[warning]Skipping AI analysis. Set AZURE_OPENAI_ENDPOINT variable in pipeline.")
        return 0
    
    # Ensure endpoint has proper format
    if not endpoint.startswith('https://'):
        endpoint = f"https://{endpoint}"
    if endpoint.endswith('/'):
        endpoint = endpoint.rstrip('/')
    
    print("##[section]🔍 Analyzing Terraform Plan with Azure OpenAI...")
    print(f"Using endpoint: {endpoint}")
    print(f"Using deployment: {deployment_name}")
    
    # Get the Terraform plan text
    plan_text = get_terraform_plan_text()
    if not plan_text:
        print("##[error]Failed to generate Terraform plan text")
        return 1
    
    # Truncate plan if too long (Azure OpenAI has token limits)
    if len(plan_text) > 10000:
        plan_text = plan_text[:10000] + "\n... (truncated for analysis)"
        print("##[warning]Plan output truncated for AI analysis")
    
    # Analyze with Azure OpenAI
    analysis_response = analyze_plan_with_azure_openai(plan_text, api_key, endpoint, deployment_name, api_version)
    
    if not analysis_response:
        print("##[error]Failed to get analysis from Azure OpenAI")
        return 1
    
    # Format and display analysis
    formatted_analysis = format_analysis_output(analysis_response)
    print(formatted_analysis)
    
    # Save analysis to file for artifact
    save_analysis_to_file(formatted_analysis)
    
    # Check for critical security issues in the analysis
    analysis_text = analysis_response.get('choices', [{}])[0].get('message', {}).get('content', '').lower()
    
    critical_keywords = ['critical', 'severe', 'high risk', 'security vulnerability', 'exposed']
    if any(keyword in analysis_text for keyword in critical_keywords):
        print("##[warning]⚠️ Critical issues detected in analysis. Please review carefully!")
    
    print("##[section]✅ AI Analysis Complete")
    return 0

if __name__ == "__main__":
    sys.exit(main())
