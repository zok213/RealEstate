"""
Test offline fallback response
"""
import sys
sys.path.insert(0, '.')

from ai.llm_orchestrator import IndustrialParkLLMOrchestrator

print("=== Testing Offline Fallback ===\n")

orchestrator = IndustrialParkLLMOrchestrator()

# Test 1: Simple greeting
print("1. Testing simple greeting...")
response = orchestrator._generate_offline_response("Chào bạn!")
print(f"Response: {response[:200]}...\n")

# Test 2: Design request
print("2. Testing design request...")
response = orchestrator._generate_offline_response(
    "Tôi muốn thiết kế khu công nghiệp 100 hecta"
)
print(f"Response: {response[:300]}...\n")

print("✓ Offline mode works!")
