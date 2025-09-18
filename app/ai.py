"""
AI integration module for Helpdesk-AI.
Handles LLM-based decision making for user queries.
"""

import json
import httpx
from typing import Dict, Any, Optional
from .config import settings
from .schemas import TicketCreate


async def call_groq_api(message: str) -> Dict[str, Any]:
    """
    Call Groq API to analyze user message and decide action.
    
    Returns dict with: action, confidence, short_title, reply_text
    Raises exception if API fails or no API key configured.
    """
    if not settings.groq_api_key:
        raise ValueError("GROQ_API_KEY not configured")
    
    system_prompt = """You are Helpdesk-AI. Reply only in JSON matching: {"action":"answer|escalate","confidence":number,"short_title":string,"reply_text":string}

For common IT issues (password resets, basic troubleshooting, software questions), provide helpful answers with high confidence (0.8-1.0).
For complex, specific, or unclear issues, choose "escalate" with a descriptive short_title for the ticket."""

    payload = {
        "model": settings.groq_model,
        "temperature": 0,
        "response_format": {"type": "json_object"},
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": message}
        ]
    }
    
    headers = {
        "Authorization": f"Bearer {settings.groq_api_key}",
        "Content-Type": "application/json"
    }
    
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                "https://api.groq.com/openai/v1/chat/completions",
                json=payload,
                headers=headers
            )
            response.raise_for_status()
            
            data = response.json()
            content = data["choices"][0]["message"]["content"]
            
            # Parse the JSON response
            result = safe_parse_json(content)
            if not result:
                raise Exception("Failed to parse AI response as JSON")
            
            # Normalize and validate fields
            if not isinstance(result.get("action"), str):
                result["action"] = "escalate"
            else:
                result["action"] = result["action"].lower()
                
            if not isinstance(result.get("confidence"), (int, float)):
                result["confidence"] = 0.0
            
            if not isinstance(result.get("reply_text"), str):
                result["reply_text"] = ""
                
            if not isinstance(result.get("short_title"), str):
                result["short_title"] = "Support Issue"
            
            return result
            
    except httpx.HTTPStatusError as e:
        raise Exception(f"Groq API error: {e.response.status_code} - {e.response.text}")
    except httpx.TimeoutException:
        raise Exception("Groq API timeout")
    except Exception as e:
        raise Exception(f"Failed to call Groq API: {str(e)}")


def safe_parse_json(content: str) -> Dict[str, Any] | None:
    """
    Safely parse JSON content, handling code fences and malformed JSON.
    Returns None if parsing fails completely.
    """
    if not isinstance(content, str):
        return None
    
    # Strip code fences if present
    content = content.strip()
    content = content.replace("```json", "").replace("```", "").strip()
    
    try:
        return json.loads(content)
    except json.JSONDecodeError:
        # Try to extract first {...} block
        import re
        match = re.search(r'\{[^}]*\}', content)
        if match:
            try:
                return json.loads(match.group())
            except json.JSONDecodeError:
                pass
    
    # Return None to indicate parsing failure
    return None


def should_answer_directly(decision: Dict[str, Any]) -> bool:
    """
    Determine if we should provide AI answer or escalate to ticket.
    """
    action = decision.get("action", "").lower()
    confidence = decision.get("confidence", 0.0)
    
    return (
        action == "answer" and 
        confidence >= settings.confidence_threshold
    )


def create_ticket_from_decision(original_message: str, decision: Dict[str, Any]) -> TicketCreate:
    """
    Create a TicketCreate object from the AI decision and original message.
    """
    title = decision.get("short_title", "Support Issue")
    if not title or title.strip() == "":
        title = "Support Issue"
        
    return TicketCreate(
        title=title,
        description=original_message
    )
