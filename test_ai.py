from dotenv import load_dotenv
import os

load_dotenv()  # Load environment variables from .env

# Check if API key is loaded
api_key = os.getenv("ANTHROPIC_API_KEY")
print(f"API Key loaded: {api_key[:20]}..." if api_key else "API Key NOT found!")

from app.services.ai_service import ai_service

# Test the slug generation
tenant_name = "MediFlow Healthcare Solutions LLC"
print(f"\nOriginal name: {tenant_name}")

try:
    slug = ai_service.generate_slug(tenant_name)
    print(f"Generated slug: {slug}")
except Exception as e:
    print(f"Error: {e}")