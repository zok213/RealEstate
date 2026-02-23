"""Check where Python is importing from."""
import pipeline.land_redistribution
import inspect

file_location = inspect.getfile(pipeline.land_redistribution.LandRedistributionPipeline)
print(f"Importing LandRedistributionPipeline from: {file_location}")

# Check if it has our debug log
source = inspect.getsource(pipeline.land_redistribution.LandRedistributionPipeline.run_stage2)
if "[RUN_STAGE2]" in source:
    print("✓ Source HAS debug log [RUN_STAGE2]")
else:
    print("✗ Source DOES NOT have debug log [RUN_STAGE2]")
    print("First 500 chars of run_stage2:")
    print(source[:500])
