
import sys
import os
from pathlib import Path
import pytest

# Add backend directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))
# Add docker directory to path so 'core' can be found?
sys.path.insert(0, str(Path(__file__).parent.parent / "docker"))

try:
    from core.optimization.optimized_pipeline_integrator import OptimizedPipelineIntegrator
    print("✅ Imported OptimizedPipelineIntegrator from core.optimization")
except ImportError:
    try:
        from backend.docker.core.optimization.optimized_pipeline_integrator import OptimizedPipelineIntegrator
        print("✅ Imported OptimizedPipelineIntegrator from backend.docker.core.optimization")
    except ImportError as e:
        print(f"❌ Failed to import OptimizedPipelineIntegrator: {e}")
        # sys.exit(1)

try:
    from optimization.utility_router import UtilityNetworkDesigner
    print("✅ Imported UtilityNetworkDesigner from optimization.utility_router")
except ImportError:
    print("❌ Failed to import UtilityNetworkDesigner")

try:
    from optimization.financial_optimizer import FinancialModel
    print("✅ Imported FinancialModel from optimization.financial_optimizer")
except ImportError:
    print("❌ Failed to import FinancialModel")

def test_imports():
    pass

if __name__ == "__main__":
    test_imports()
