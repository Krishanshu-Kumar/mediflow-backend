from app.services.ai_service import chat

result = chat(
    prompt="Run diagnoses of why my api is not working",
    system_prompt="You are a senior backend engineer. Be concise and structured.",
    temperature=0.3,
)
print("Test 3:", result)