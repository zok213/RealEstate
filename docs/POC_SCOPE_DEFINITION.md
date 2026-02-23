# 🎯 POC SCOPE DEFINITION
## Industrial Estate AI Master Planning System - Proof of Concept

**Date:** January 28, 2026  
**Version:** 1.0  
**Target Presentation:** Week of February 3, 2026  
**POC Duration:** 4-6 weeks

---

## 📋 EXECUTIVE SUMMARY

**POC Objective:** Demonstrate core AI-powered industrial estate planning capabilities with a focused, achievable scope that validates feasibility and value proposition.

**Success Criteria:**
- Generate regulation-compliant industrial park layouts from DXF site boundaries
- Collect design requirements via structured form inputs
- Apply IEAT regulations automatically (system enforces compliance)
- Produce exportable DXF/DWG design files
- Calculate basic financial metrics (salable area, road costs, ROI)

---

## 🎯 SCOPE INCLUSIONS (IN SCOPE)

### 1. CORE FUNCTIONALITY

#### A. Site Input & Processing
- ✅ **DXF/DWG Upload** - Accept AutoCAD file formats (R2018 or later)
- ✅ **Boundary Extraction** - Automatic detection of site perimeter
- ✅ **Terrain Data** - Basic elevation/contour processing
- ✅ **Site Area Calculation** - Automatic computation of total site area

#### B. Requirements Input
- ✅ **Form-Based Interface** - Structured input forms with dropdowns, sliders, and text fields
- ✅ **Guided Workflow** - Step-by-step parameter collection with validation
- ✅ **Key Parameters:**
  - Target lot sizes (number input: 1000-1500 sqm range)
  - Industry type (dropdown: light manufacturing, logistics, warehousing)
  - Infrastructure priorities (checkboxes: road width, green space, utilities)
  - Financial targets (sliders/inputs: salable area percentage, target pricing)
- ✅ **Language:** English interface for consistency across all sites

#### C. AI-Powered Design Generation
- ✅ **Road Network Layout** - Automatic generation of primary/secondary roads
- ✅ **Lot Subdivision** - Intelligent parcel subdivision based on requirements
- ✅ **Utility Planning** - Basic placement of utility corridors
- ✅ **Green Space Allocation** - Automatic distribution to meet regulations

#### D. Regulatory Compliance (IEAT Focus)
- ✅ **Salable Area Validation** - Check compliance with IEAT limits (typically 70-85% depending on zone type)
- ✅ **Green Area Requirements** - Enforce minimum 10% green space (IEAT standard)
- ✅ **Buffer Zones** - Apply 10m perimeter buffer strips
- ✅ **Road Standards** - Main roads ≥25m ROW, secondary ≥15m
- ✅ **Fire Safety** - Basic clearance requirements (6m access roads, hydrant spacing)
- ✅ **Automated Validation** - System checks all constraints before finalizing design

#### E. Output & Visualization
- ✅ **2D Plan View** - Web-based interactive map display
- ✅ **DXF/DWG Export** - AutoCAD-compatible file output with proper layer structure
- ✅ **Financial Summary** - Cost breakdown, salable area, projected revenue
- ✅ **Design Report** - PDF summary with key metrics and compliance checklist

---

### 2. SUPPORTED INDUSTRIAL TYPES (POC)

**Primary Focus:** Light to medium manufacturing

✅ **Tier 1 (Full Support):**
- Light manufacturing (electronics assembly, automotive parts)
- General warehousing & logistics
- Food processing (non-hazardous)

⚠️ **Tier 2 (Basic Support):**
- Heavy industry (simplified - no specialized hazmat handling)
- Cold storage logistics (standard utility requirements)

---

### 3. TECHNICAL SPECIFICATIONS (POC)

#### A. LLM Provider
- **Primary:** Gemini Pro 2.0 Flash (Google)
- **Reasoning:** Best cost/performance balance, handles complex spatial reasoning
- **API Budget:** ~$300/month for POC testing (reduced due to structured inputs)
- **Fallback:** None for POC (single provider to reduce complexity)

#### B. Deployment
- **Environment:** Docker containers (frontend + backend)
- **Hosting:** Cloud VM (AWS/GCP/Azure) or client on-premise server
- **Database:** PostgreSQL + PostGIS for spatial data
- **Storage:** Local file system for DXF/DWG files

#### C. User Capacity
- **Concurrent Users:** Up to 10 users simultaneously
- **Max Projects:** 50 projects total
- **File Size Limits:** DXF files up to 50MB

---

### 4. SAMPLE PROJECT SCENARIOS (POC)

**Scenario 1: Standard Light Manufacturing Park**
- Site: 20 hectares, flat terrain
- Requirements: 1,200 sqm average lot size, 50 lots minimum
- Infrastructure: Standard utilities, 10% green space
- Expected output: 55-60 lots, 75% salable area

**Scenario 2: Logistics Hub with Large Lots**
- Site: 30 hectares, moderate slope
- Requirements: 2,500 sqm average lots for warehouses
- Infrastructure: Wide roads (30m ROW), truck maneuvering areas
- Expected output: 35-40 lots, 72% salable area

**Scenario 3: Mixed-Use Industrial Estate**
- Site: 15 hectares, irregular boundary
- Requirements: Mix of small (800 sqm) and large (1,500 sqm) lots
- Infrastructure: Central utility zone, peripheral green buffer
- Expected output: 40-45 lots, 70% salable area

---

## 🚫 SCOPE EXCLUSIONS (OUT OF SCOPE FOR POC)

### 1. ADVANCED FEATURES

❌ **Complex Terrain Handling**
- Advanced earthwork calculations
- Cut/fill optimization
- Slope stability analysis
- **Reason:** Requires specialized civil engineering algorithms, high complexity

❌ **3D Building Design**
- Building envelope generation
- Multi-story building design
- Structural design
- **Reason:** Focus POC on site planning, not building architecture

❌ **Advanced Optimization**
- Multi-objective optimization (genetic algorithms)
- Real-time constraint satisfaction solver
- Scenario comparison with 5+ alternatives
- **Reason:** Can be added post-POC, basic optimization sufficient for demo

### 2. SPECIALIZED INDUSTRIES

❌ **Hazardous Industries**
- Chemical plants with specialized setbacks
- Explosive materials handling
- Radioactive material facilities
- **Reason:** Requires highly specialized compliance, low priority for initial market

❌ **Specialized Infrastructure**
- Rail spur design (railway connections)
- Port/dock facilities
- Airport adjacency planning
- **Reason:** Niche requirements, small market segment

### 3. ADVANCED UTILITIES

❌ **Detailed Utility Design**
- Pipe network sizing calculations
- Electrical load calculations
- Stormwater drainage design with flow analysis
- Wastewater treatment system design
- **Reason:** Requires MEP (mechanical/electrical/plumbing) engineering expertise

❌ **Energy Systems**
- Solar farm integration
- Microgrid design
- Battery storage planning
- **Reason:** Specialized domain, can be added as module later

### 4. ENTERPRISE FEATURES

❌ **Multi-User Collaboration**
- Real-time collaborative editing
- Version control with branching
- User roles and permissions (beyond basic admin/user)
- **Reason:** Adds significant technical complexity, not essential for POC

❌ **Integration with External Systems**
- ERP integration
- Government e-permitting systems
- GIS data feeds (live topographic updates)
- **Reason:** Requires API access and partnership agreements

❌ **Mobile App**
- Native iOS/Android applications
- Offline mode
- **Reason:** Web app sufficient for POC, mobile can follow based on demand

### 5. ADVANCED AI FEATURES

❌ **Computer Vision**
- Automatic building/structure detection from satellite imagery
- Photo-based site condition assessment
- **Reason:** Complex ML model training required

❌ **Predictive Analytics**
- Market demand forecasting
- Tenant matching algorithms
- Price prediction models
- **Reason:** Requires historical data and market research integration

---

## 📊 POC DELIVERABLES

### Week 1-2: Foundation
- [ ] Form-based input interface (English, with validation)
- [ ] DXF upload and boundary extraction
- [ ] Parameter validation and preprocessing

### Week 3-4: Core Generation
- [ ] Road network generation algorithm
- [ ] Lot subdivision logic
- [ ] IEAT regulation validation engine
- [ ] Basic financial calculations

### Week 5-6: Output & Polish
- [ ] DXF/DWG export with proper layers
- [ ] Web-based visualization (2D map)
- [ ] PDF report generation
- [ ] Testing with 3 sample projects

### Final Presentation Materials
- [ ] Live demo with real DXF file
- [ ] Comparison: Manual design (2-3 days) vs. AI design (5 minutes)
- [ ] Compliance checklist showing automatic validation
- [ ] Financial analysis dashboard
- [ ] Video walkthrough (5 minutes)

---

## 💰 POC COST ESTIMATE

**Development Time:** 4-6 weeks (1 developer full-time + 1 developer part-time)

**Infrastructure Costs (POC Duration):**
- Cloud hosting: $200/month × 2 months = $400
- LLM API (Gemini): $500/month × 2 months = $1,000
- Database & storage: $100/month × 2 months = $200
- **Total Infrastructure:** ~$1,600

**Development Costs:** [To be determined based on team allocation]

**Total POC Budget:** [Client to specify budget constraints]

---

## ✅ SUCCESS METRICS

**Functional Metrics:**
- [ ] Generate compliant design in <5 minutes (vs. 2-3 days manual)
- [ ] 100% IEAT regulation compliance (automatic validation)
- [ ] Support 3 different project types (manufacturing, logistics, mixed)
- [ ] Produce AutoCAD-compatible DXF output

**Quality Metrics:**
- [ ] Salable area within ±5% of optimal (compared to manual design)
- [ ] Road network efficiency >85% (minimize total road length)
- [ ] Lot usability score >90% (rectangular, accessible lots)

**User Experience:**
- [ ] Non-technical users can complete design without training
- [ ] English interface with clear tooltips and help text
- [ ] <30 seconds response time for form validation and submission
- [ ] <5 minutes total time to input all parameters

---

## 🔄 POST-POC ROADMAP (FUTURE PHASES)

**Phase 2 (Post-POC):**
- Advanced terrain optimization
- Multi-scenario generation (3-5 alternatives)
- Enhanced financial modeling (NPV, IRR, sensitivity analysis)
- User preference learning

**Phase 3:**
- 3D visualization
- Building placement and orientation
- Detailed utility network design
- Construction phasing

**Phase 4:**
- Multi-user collaboration
- Integration with government permitting
- Mobile app
- Predictive market analytics

---

## 📋 ASSUMPTIONS FOR POC

**Client-Side Requirements:**
- Client provides 3-5 sample DXF files for testing
- Client provides IEAT regulation documents (already received)
- Client has basic cloud infrastructure or can provision VM
- Client team available for weekly feedback sessions

**Technical Assumptions:**
- DXF files are properly formatted (valid AutoCAD format)
- Site boundaries are clearly defined in DXF layer
- Internet connectivity available for LLM API calls
- Users have modern web browsers (Chrome, Edge, Safari)

**Regulatory Assumptions:**
- IEAT regulations provided are current and complete
- POC focuses on general IEAT standards (not province-specific variations)
- Fire safety requirements use standard Thai building code minimums

---

## 🎯 CLIENT DECISION POINTS

**Before POC Kickoff, Client Must Decide:**

1. **Hosting Preference**
   - [ ] Cloud-hosted (we manage infrastructure)
   - [ ] On-premise (client provides server)
   - [ ] Hybrid (dev on cloud, production on-premise)

2. **Data Privacy Level**
   - [ ] Standard (use public Gemini API)
   - [ ] Enhanced (VPN + data processing agreement)
   - [ ] Maximum (requires on-premise LLM - significantly higher cost)

3. **Primary User Type**
   - [ ] Licensed architects/engineers (technical UI)
   - [ ] Business executives (simplified UI)
   - [ ] Mixed (adaptive interface)

4. **POC Test Projects**
   - Client provides 3 real project sites (DXF files)
   - Client provides typical requirements for each site
   - Client provides expected outcomes for validation

---

## 📞 NEXT STEPS

**Pre-Presentation (Before T3):**
1. Client reviews and approves POC scope
2. Client provides 3 sample DXF files for testing
3. Client confirms budget and timeline

**T3 Presentation:**
1. Present POC scope and deliverables
2. Demonstrate conceptual mockup/prototype
3. Discuss timeline and milestones
4. Finalize contract and kickoff date

**Post-Approval:**
1. Week 1: Environment setup + data preparation
2. Week 2-3: Core development
3. Week 4-5: Integration and testing
4. Week 6: Client UAT and final adjustments

---

**Document Status:** Ready for client review  
**Prepared by:** Technical Team  
**Date:** January 28, 2026
