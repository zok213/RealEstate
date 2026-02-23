# Full-Site API Testing Guide

## 🚀 Quick Start

### Step 1: Start Backend Server

Open a PowerShell terminal and run:

```powershell
.\start_server.ps1
```

The server will start on `http://localhost:8000`

Keep this terminal open while testing.

### Step 2: Test API Endpoints

Open a **NEW** PowerShell terminal and run:

```powershell
.\test_api.ps1
```

This will test all 4 endpoints:
1. Upload DWG and start analysis
2. Poll for completion
3. Select scenario and export
4. Download DXF file

## 📋 Expected Output

```
======================================================================
FULL-SITE API ENDPOINT TEST
======================================================================

Using file: Pilot_Existing Topo _ Boundary.dxf
Target plots: 200

======================================================================
STEP 1: Starting Full-Site Analysis
======================================================================

[OK] Analysis started
   Job ID: <uuid>
   Status: processing
   Message: Full-site analysis started

======================================================================
STEP 2: Waiting for Analysis Completion
======================================================================

   [0s] PROCESSING: 10% - Extracting site boundary...
   [2s] PROCESSING: 20% - Analyzing terrain...
   [6s] PROCESSING: 50% - Generating scenarios...
   [9s] COMPLETED: 100% - Full-site analysis complete!

   Site area: 191.00 ha
   Buildable zones: 12
   Optimal zones: 8
   Processing time: 9.3s

   Scenarios generated: 3

   --- Scenario A: Cost-Optimized ---
       Strategy: minimize_grading_cost
       Plots: 180
       Area: 150.0 ha
       Cost: $1,234,567

   --- Scenario B: Capacity-Maximized ---
       Strategy: maximize_plot_count
       Plots: 220
       Area: 170.0 ha
       Cost: $2,345,678

   --- Scenario C: Balanced ---
       Strategy: balanced
       Plots: 200
       Area: 160.0 ha
       Cost: $1,789,012

======================================================================
STEP 3: Selecting and Exporting Scenario
======================================================================

[OK] Export started
   Export Job ID: <uuid>
   Scenario: Balanced
   Plots: 200

======================================================================
STEP 4: Waiting for DXF Export
======================================================================

   [0s] PROCESSING: 20% - Preparing layout data...
   [1s] PROCESSING: 50% - Generating DXF file...
   [2s] COMPLETED: 100% - DXF export complete!

   DXF file: pilot_fullsite_scenario_C.dxf
   Download URL: /api/demo/download/pilot_fullsite_scenario_C.dxf
   Scenario: Balanced
   Plots: 200

======================================================================
TEST SUMMARY
======================================================================

[SUCCESS] All API endpoints working correctly!

Tested endpoints:
  1. POST /api/demo/analyze-full-site
  2. GET  /api/demo/scenarios/{job_id}
  3. POST /api/demo/select-scenario
  4. GET  /api/demo/job-status/{export_job_id}

Next steps:
  - Build frontend interface
  - Integrate with UI
  - Deploy to production
```

## 🔧 Manual Testing (Alternative)

If you prefer to test manually:

### 1. Start Server
```powershell
cd backend
python -m uvicorn api.main:app --reload --port 8000
```

### 2. Test with curl or Postman

**Upload and Start Analysis:**
```powershell
curl -X POST "http://localhost:8000/api/demo/analyze-full-site?target_plot_count=200" `
  -F "file=@sample-data/Pilot_Existing Topo _ Boundary.dxf"
```

**Check Status:**
```powershell
curl "http://localhost:8000/api/demo/scenarios/{job_id}"
```

**Select Scenario:**
```powershell
curl -X POST "http://localhost:8000/api/demo/select-scenario?job_id={job_id}&scenario_id=C"
```

**Download DXF:**
```powershell
curl "http://localhost:8000/api/demo/download/{filename}" -o output.dxf
```

## 📚 API Documentation

Once server is running, visit:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## ❓ Troubleshooting

### Server won't start
- Check if port 8000 is already in use
- Verify Python environment is activated
- Check for missing dependencies: `pip install -r requirements.txt`

### Test script fails
- Make sure server is running first
- Check if DXF file exists in `sample-data/` directory
- Verify file path is correct

### Timeout errors
- Large files may take longer to process
- Increase timeout in test script if needed
- Check server logs for errors

## 📁 File Locations

- Test script: `sample-data/test_fullsite_api.py`
- Sample DXF: `sample-data/Pilot_Existing Topo _ Boundary.dxf`
- Exported DXF: `backend/exports/pilot_fullsite_scenario_*.dxf`
- Server logs: Check terminal where server is running

## 🎯 Next Steps After Testing

1. ✅ Verify all endpoints work
2. 🎨 Build frontend UI
3. 🔗 Integrate API with React components
4. 🚀 Deploy to production
