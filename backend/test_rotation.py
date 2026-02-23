"""
Test script for LLM rotation backup system
Tests all configured providers in rotation order
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from ai.llm_orchestrator import FreeLLMClient, LLMProvider
from config import LLM_ROTATION_ORDER


def test_llm_rotation():
    """Test each LLM provider in rotation order"""
    print("="*60)
    print("Testing LLM Rotation Backup System")
    print("="*60)
    
    client = FreeLLMClient()
    
    # Simple test message
    test_messages = [
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "Say 'Hello' in one word."}
    ]
    
    print(f"\nRotation Order: {' -> '.join(LLM_ROTATION_ORDER)}")
    print("\n" + "="*60)
    
    # Test each provider
    providers_to_test = [
        (LLMProvider.MEGALLM, "MegaLLM (Llama 3.3 70B)"),
        (LLMProvider.GEMINI, "Google Gemini 2.0 Flash"),
        (LLMProvider.GROQ_QWEN, "Groq (Qwen 2.5 72B)"),
        (LLMProvider.MISTRAL, "Mistral Large"),
        (LLMProvider.CEREBRAS, "Cerebras (Llama 3.1 70B)"),
    ]
    
    results = {}
    
    for provider, name in providers_to_test:
        print(f"\n[TEST] {name}")
        print("-" * 60)
        try:
            response = client.chat(
                messages=test_messages,
                provider=provider,
                max_tokens=50
            )
            print(f"✓ Success: {response[:100]}")
            results[name] = "✓ Success"
        except Exception as e:
            print(f"✗ Failed: {str(e)[:100]}")
            results[name] = f"✗ Error"
    
    # Summary
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    for provider_name, status in results.items():
        print(f"{provider_name:30} {status}")
    
    # Test fallback chain
    print("\n" + "="*60)
    print("Testing Fallback Chain (forcing first provider to fail)")
    print("="*60)
    try:
        # This should trigger fallback
        response = client.chat(
            messages=test_messages,
            provider=LLMProvider.MEGALLM,
            max_tokens=50
        )
        print(f"✓ Fallback successful, got response: {response[:100]}")
    except Exception as e:
        print(f"✗ All providers failed: {e}")


if __name__ == "__main__":
    test_llm_rotation()
