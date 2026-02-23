"""
Test Gemini API directly with simple prompt
"""
import google.generativeai as genai
import time
from config import settings

print("Testing Gemini API...")
print(f"API Key: {settings.google_api_key[:20]}...")

# Configure Gemini
genai.configure(api_key=settings.google_api_key)

# Create model
model = genai.GenerativeModel('gemini-2.0-flash-exp')

print("\n=== Test 1: Simple greeting ===")
start = time.time()
try:
    response = model.generate_content(
        "Chào bạn!",
        generation_config={
            "max_output_tokens": 100,
            "temperature": 0.7
        }
    )
    elapsed = time.time() - start
    print(f"✓ Response in {elapsed:.2f}s:")
    print(response.text)
except Exception as e:
    elapsed = time.time() - start
    print(f"✗ Failed after {elapsed:.2f}s: {e}")

print("\n=== Test 2: Industrial park query ===")
start = time.time()
try:
    response = model.generate_content(
        "Tôi muốn thiết kế khu công nghiệp 100 hecta",
        generation_config={
            "max_output_tokens": 200,
            "temperature": 0.7
        }
    )
    elapsed = time.time() - start
    print(f"✓ Response in {elapsed:.2f}s:")
    print(response.text[:300])
except Exception as e:
    elapsed = time.time() - start
    print(f"✗ Failed after {elapsed:.2f}s: {e}")
