import anthropic
import os
from typing import Optional


class AIService:
    """Service for AI-powered features using Claude"""
    
    def __init__(self):
        api_key = os.getenv("ANTHROPIC_API_KEY")
        if not api_key:
            raise ValueError("ANTHROPIC_API_KEY not found in environment variables")
        
        self.client = anthropic.Anthropic(api_key=api_key)
    
    def generate_slug(self, tenant_name: str) -> str:
        """
        Auto-generate a URL-friendly slug from tenant name
        Example: "My Company LLC" -> "my-company-llc"
        """
        message = self.client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=100,
            messages=[
                {
                    "role": "user",
                    "content": f"Convert this to a URL-friendly slug (lowercase, hyphens only, no special chars): '{tenant_name}'. Return ONLY the slug, nothing else."
                }
            ]
        )
        
        slug = message.content[0].text.strip()
        return slug


# Create a singleton instance
ai_service = AIService()