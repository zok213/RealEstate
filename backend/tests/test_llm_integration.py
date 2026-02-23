
import sys
import os
from pathlib import Path
from unittest.mock import MagicMock

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from ai.llm_orchestrator import IndustrialParkLLMOrchestrator

def test_llm_parameter_extraction():
    """
    Verify that LLMOrchestrator correctly extracts parameters from JSON response.
    This test mocks the actual LLM call to ensure logic is correct without API keys.
    """
    print("\n" + "="*70)
    print("AI INTEGRATION TEST: LLM Orchestrator Logic")
    print("="*70)
    
    # 1. Initialize Orchestrator
    orchestrator = IndustrialParkLLMOrchestrator()
    
    # 2. Mock LLM Client
    # We want to simulate a response that contains the JSON structure
    mock_response = """
    Here is the design for your 100ha industrial park.
    
    ```json
    {
      "parameters": {
        "totalArea_ha": 100,
        "industryFocus": [
          {"type": "logistics", "percentage": 40},
          {"type": "manufacturing", "percentage": 60}
        ],
        "constraints": {
          "greenAreaMin_percent": 10
        }
      },
      "readyForGeneration": true
    }
    ```
    """
    
    # Mock the chat method to return this string
    orchestrator.llm_client.chat = MagicMock(return_value=mock_response)
    
    # 3. Send a message
    print("Sending user request: 'Design a 100ha park'...")
    response = orchestrator.chat("Design a 100ha park")
    
    # 4. Verify Extraction
    params = orchestrator.get_extracted_params()
    extracted_params = params.get('parameters', {})
    
    print(f"\nExtracted Parameters: {params}")
    
    assert extracted_params.get('totalArea_ha') == 100
    assert len(extracted_params.get('industryFocus')) == 2
    assert response.ready_for_generation == True
    
    print("\n✅ Extraction Logic SUCCESS: Parameters correctly parsed from JSON.")
    
    # 5. Verify IEAT Validation (Implicit in extraction/update, but let's check validation logic if exposed)
    # The orchestrator runs validation on update, check compliance
    validation = orchestrator._validate_ieat_compliance()
    print(f"\nCompliance Check: {validation['compliant']}")
    assert validation['compliant'] == True
    
    print("✅ Compliance Logic SUCCESS: Design passed IEAT checks.")

if __name__ == "__main__":
    try:
        test_llm_parameter_extraction()
        print("\nAll AI tests passed.")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ AI Test Failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
