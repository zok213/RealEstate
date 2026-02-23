# 🎯 CLIENT KEY DECISIONS CHECKLIST
## Critical Technical Requirements for Industrial Park AI System

**Date:** January 25, 2026  
**Version:** 1.0  
**Purpose:** Streamlined decision checklist for key technical requirements

---

## 📋 OVERVIEW

After a detailed technical analysis, we found this project to be **highly complex** with many in-depth analytical components. To deliver a quality solution that meets expectations and avoids deviations, we request that the Client clarify several key technical requirements below.

**Instructions:** Please check [✓] the boxes that apply to your preferences and requirements.

---

## � SECTION 1: TERMINOLOGY & INTERFACE LANGUAGE

### Q2: Standard terminology confirmation

**Context:** The system will use English for all technical field labels and terminology (consistent across all sites including Vietnam).

**Question:** Do you use any industry-specific terms that differ from standard IEAT/international usage?

**Please select ONE:**

- [ ] **No special terms** - Use standard IEAT/international terminology
- [ ] **Have custom terms** - We use organization-specific terminology (provide glossary)

**If you have custom terms that must appear in the interface, please provide a glossary (max 10 critical terms):**

**Example:**
```
Standard term → Your preferred term
"Salable Area" → "Leasable Area"
"Buffer Zone" → "Setback Zone"
```

**Your organization's preferred terms:**
```text
1. _______________________________________________
2. _______________________________________________
3. _______________________________________________
4. _______________________________________________
5. _______________________________________________
```

**Note:** All interface elements (buttons, labels, menus) will be in English for consistency across international clients.

---

## 🤖 SECTION 2: AI AUTONOMY & HUMAN OVERSIGHT

### Q4: AI automation level expectations

**Question:** What is your expectation for AI automation in design generation?

**Please select ONE primary option:**

- [ ] **(Option A) Fully autonomous AI-generated designs**
  - AI generates complete, construction-ready designs
  - Minimal human review required
  - Suitable for: Experienced users, standard projects
  - **Risk:** Higher liability if errors occur

- [ ] **(Option B) AI-generated with mandatory architect review**
  - AI generates complete designs
  - Licensed architect MUST review before finalization
  - System includes approval workflow
  - **Risk:** Moderate - shared responsibility

- [ ] **(Option C) AI-assisted design with human control**
  - AI suggests layouts and optimizations
  - Human architect makes final decisions at each step
  - Collaborative approach
  - **Risk:** Lower - human maintains control

- [ ] **(Option D) AI provides options, human selects**
  - AI generates 3-5 alternative designs
  - Human reviews and selects preferred option
  - Can request modifications
  - **Risk:** Lower - human makes key decisions

**Preferred workflow:** (Check one)
- [ ] Design → Review → Approve → Export
- [ ] Design → Auto-approve → Export (no review)
- [ ] Design → Review → Modify → Re-review → Approve
- [ ] Other: _______________________________________

### Q5: Legal responsibility and liability

**Question:** If the AI produces a design that inadvertently violates IEAT regulations or contains errors, who bears the legal and professional responsibility?

**Please select your position:**

- [ ] **Platform is fully responsible**
  - Platform guarantees correctness of AI designs
  - Platform provides professional liability insurance
  - **Note:** This will significantly increase costs

- [ ] **Client organization is fully responsible**
  - Platform is a tool only, Client validates all designs
  - Client must have licensed architects review
  - Platform provides disclaimers

- [ ] **Shared responsibility model**
  - Platform ensures algorithm correctness
  - Client ensures proper use and final validation
  - Clear division of responsibilities in agreement

- [ ] **Individual user/architect is responsible**
  - Each user (architect) signs off on designs they generate
  - Platform and Client provide framework only
  - Professional liability follows user

**Additional safeguard:**

Do you require a rule-based validation layer that double-checks all AI outputs?

- [ ] **Yes - Mandatory rule engine validation**
  - All AI designs checked against hard-coded regulation database
  - Acts as safety net to catch AI errors
  - Adds complexity but reduces risk

- [ ] **Optional - Can be enabled/disabled by user**
  - Power users can skip for speed
  - New users get automatic validation

- [ ] **No - Trust AI with disclaimers**
  - AI is accurate enough
  - Human review is sufficient safeguard

---

## 🏭 SECTION 3: INDUSTRY-SPECIFIC REQUIREMENTS

### Q6: Target industries and special infrastructure needs

**Question:** What types of industries will your industrial parks primarily serve?

**Please rank in order of importance (1 = most important, 5 = least important):**

- [ ] Light manufacturing (automotive parts, electronics assembly) - Priority: _____
- [ ] Heavy industry (steel mills, chemical plants) - Priority: _____
- [ ] Logistics & warehousing (distribution centers, cold storage) - Priority: _____
- [ ] Food processing (requires hygiene, cold chain) - Priority: _____
- [ ] Other: _____________________________________ - Priority: _____

**Industry-specific infrastructure requirements:**

**Please check ALL infrastructure types that your projects typically require:**

**Loading & Transport:**
- [ ] Truck loading docks (specify: standard / refrigerated)
- [ ] Container loading facilities (20ft / 40ft)
- [ ] Rail spur access (railway connection)
- [ ] Oversized equipment clearances (for large machinery delivery)
- [ ] Heavy vehicle parking areas (truck yards)

**Specialized Storage:**
- [ ] Hazardous material storage zones (chemical, flammable)
- [ ] Cold storage facilities (temperature-controlled)
- [ ] Bonded warehouses (customs-controlled)
- [ ] High-ceiling warehouses (>10m height)
- [ ] Climate-controlled storage

**Utility Requirements:**
- [ ] High-voltage power supply (>22kV)
- [ ] Industrial water supply (separate from potable)
- [ ] Process water treatment
- [ ] Gas pipelines (natural gas / LPG)
- [ ] Compressed air systems
- [ ] Steam generation facilities

**Environmental & Safety:**
- [ ] Waste treatment facilities (industrial wastewater)
- [ ] Hazardous waste handling areas
- [ ] Fire water reservoirs (separate from potable)
- [ ] Emergency response stations
- [ ] Environmental monitoring stations

**Special Requirements:**
- [ ] Clean room environments (electronics, pharma)
- [ ] Vibration-free zones (precision manufacturing)
- [ ] EMI shielding areas (electromagnetic interference control)
- [ ] Explosion-proof zones (chemical processing)
- [ ] Other: _______________________________________

**Additional specifications:** (Please describe any unique requirements)
```
_____________________________________________________________________
_____________________________________________________________________
_____________________________________________________________________
```

---

## 💰 SECTION 4: COST VS ACCURACY TRADE-OFFS

### Q7: LLM provider strategy

**Question:** What is your strategic preference for AI language model infrastructure?

**Please select your primary approach:**

- [ ] **(Option A) Cost-effective solution**
  - Use local Ollama models (free, open-source)
  - Requires infrastructure investment (servers/GPUs)
  - **Pros:** No ongoing API costs, full data privacy
  - **Cons:** Lower accuracy, requires setup & maintenance
  - **Estimated cost:** $5K-15K hardware + $0/month API

- [ ] **(Option B) Higher accuracy & speed**
  - Use paid commercial APIs (Gemini, GPT-4, Claude)
  - Cloud-based, no infrastructure needed
  - **Pros:** Best accuracy, always updated, scalable
  - **Cons:** Ongoing API costs, data sent to external providers
  - **Estimated cost:** $500-2,000/month for 100 users

- [ ] **(Option C) Hybrid approach**
  - Use paid APIs for critical tasks (design generation)
  - Use local models for simple tasks (chat, clarification)
  - **Pros:** Balanced cost/performance, flexible
  - **Cons:** More complex to manage
  - **Estimated cost:** $200-800/month + $5K hardware

- [ ] **(Option D) Multi-provider strategy**
  - Primary: Paid API (Gemini)
  - Fallback: Alternative APIs (DeepSeek, Groq)
  - Emergency: Local Ollama
  - **Pros:** Maximum reliability, cost optimization
  - **Cons:** Most complex setup
  - **Estimated cost:** $300-1,000/month + $5K hardware

**Budget allocation:**

What is your monthly budget for LLM API calls?

- [ ] Under $500/month (cost-sensitive, use free/cheap models)
- [ ] $500-1,000/month (moderate usage, ~50-100 users)
- [ ] $1,000-2,000/month (standard usage, ~100-200 users)
- [ ] $2,000-5,000/month (heavy usage, ~200-500 users)
- [ ] $5,000+/month (enterprise usage, unlimited)
- [ ] No budget constraint - prioritize quality over cost

---

## 🔐 SECTION 5: DATA PRIVACY & COMPLIANCE

### Q8: Data privacy and security requirements

**Question:** Do you have data privacy or compliance concerns about sending project data to external LLM providers?

**Project data includes:**
- DXF/DWG files (site boundaries, topography)
- Site information (location, size, characteristics)
- Financial data (costs, pricing, ROI projections)
- Client/tenant information
- Design parameters and requirements

**Please select ALL that apply:**

**Privacy Concerns:**
- [ ] **High concern** - Project data is highly confidential
- [ ] **Moderate concern** - Some projects are sensitive
- [ ] **Low concern** - Data is not particularly sensitive
- [ ] **No concern** - Public or non-confidential projects only

**Regulatory Requirements:**
- [ ] **MUST comply with PDPA** (Thailand Personal Data Protection Act)
- [ ] **MUST comply with GDPR** (European Union)
- [ ] **MUST comply with local data residency laws**
- [ ] **Industry-specific regulations** (specify): _________________
- [ ] **No specific regulatory requirements**

**Data Handling Preferences:**
- [ ] **Data must stay on-premise** - Cannot send to external APIs
- [ ] **Data can go to cloud** - But only within Thailand/ASEAN
- [ ] **Data can go to global cloud** - With proper security measures
- [ ] **No restrictions** - Can use any provider

**Required approach based on concerns:**

If you have HIGH privacy concerns, you MUST select:

- [ ] **Deploy local LLM models on-premise**
  - All data processing happens on your servers
  - Zero data leaves your infrastructure
  - **Trade-off:** Higher setup cost, lower AI accuracy
  - **Estimated cost:** $10K-20K hardware + maintenance

- [ ] **Use private cloud with data encryption**
  - Dedicated cloud instance (not shared)
  - End-to-end encryption
  - Data residency guaranteed
  - **Trade-off:** Higher monthly cost
  - **Estimated cost:** +50-100% cloud costs

- [ ] **Acceptable to use public APIs with agreements**
  - Standard commercial APIs (Gemini, GPT-4)
  - Sign data processing agreements (DPA)
  - Accept provider terms of service
  - **Trade-off:** Data sent to external parties
  - **Estimated cost:** Standard API pricing

---

## 👥 SECTION 6: USER TECHNICAL SOPHISTICATION

### Q9: Target user profiles and expertise levels

**Question:** What is the technical sophistication level of your typical users?

**Please check ALL user types that will use the system:**

**User Type A: Licensed Architects/Engineers**
- [ ] **Primary users** (>50% of user base)
- [ ] **Some users** (20-50% of user base)
- [ ] **Few users** (<20% of user base)
- [ ] **Not applicable**

**Characteristics:**
- Understand technical specifications (ROW, setbacks, clearances)
- Read engineering drawings fluently
- Know regulatory requirements (IEAT standards)
- Can validate AI outputs professionally

**User Type B: Business Executives/Project Managers**
- [ ] **Primary users** (>50% of user base)
- [ ] **Some users** (20-50% of user base)
- [ ] **Few users** (<20% of user base)
- [ ] **Not applicable**

**Characteristics:**
- Think in high-level concepts (ROI, project scale, timeline)
- May not understand detailed technical specifications
- Focus on business metrics and feasibility
- Need simplified explanations

**User Type C: Real Estate Developers/Investors**
- [ ] **Primary users** (>50% of user base)
- [ ] **Some users** (20-50% of user base)
- [ ] **Few users** (<20% of user base)
- [ ] **Not applicable**

**Characteristics:**
- Focus on financial returns and market positioning
- Understand land use and zoning at high level
- May lack technical engineering knowledge
- Need clear visualizations and ROI analysis

**User Type D: CAD Technicians/Drafters**
- [ ] **Primary users** (>50% of user base)
- [ ] **Some users** (20-50% of user base)
- [ ] **Few users** (<20% of user base)
- [ ] **Not applicable**

**Characteristics:**
- Expert in CAD software and file formats
- Understand layer structure and drawing standards
- May lack design decision-making authority
- Focus on accurate technical documentation

**System communication style should be:**

Based on your user base, the AI should communicate:

- [ ] **Highly technical** - Use engineering terminology, specifications, codes
- [ ] **Business-focused** - Emphasize ROI, costs, benefits, risks
- [ ] **Mixed - adaptive** - Detect user level and adjust language
- [ ] **Simple/educational** - Explain concepts, avoid jargon

**User interface complexity:**

- [ ] **Advanced UI** - Many options, parameters, expert controls
- [ ] **Standard UI** - Balance of simplicity and flexibility
- [ ] **Simplified UI** - Minimal options, guided workflow
- [ ] **Wizard-based** - Step-by-step with explanations at each stage

---

## ⚖️ SECTION 7: CONSTRAINT PRIORITY HIERARCHY

### Q10: Establishing priority order for design constraints

**Question:** When trade-offs are necessary (site constraints prevent satisfying all requirements), what is your organization's priority order?

**Instructions:** Please RANK the following constraints from 1 (HIGHEST priority - cannot compromise) to 10 (LOWEST priority - can relax if needed)

**Regulatory Constraints:**

- [ ] **Fire safety regulations** (clearances, access, hydrants) - Rank: _____
- [ ] **IEAT green area requirements** (minimum 10% green space) - Rank: _____
- [ ] **IEAT salable area limits** (maximum 75-85% salable) - Rank: _____
- [ ] **Buffer zone requirements** (10m perimeter strip) - Rank: _____
- [ ] **Road width standards** (minimum 25m ROW for main roads) - Rank: _____

**Functional Constraints:**

- [ ] **Parking ratios** (parking spaces per building area) - Rank: _____
- [ ] **Utility access** (every lot must have utility connections) - Rank: _____
- [ ] **Building orientation** (preferred facing direction) - Rank: _____
- [ ] **Lot size targets** (achieving desired lot sizes) - Rank: _____
- [ ] **Road efficiency** (minimizing total road length) - Rank: _____

**Alternative approach - Category-based:**

Or, classify constraints into categories:

**HARD CONSTRAINTS (Absolutely non-negotiable):**

Check ALL constraints that CANNOT be relaxed under any circumstances:

- [ ] Fire safety regulations
- [ ] IEAT salable area limits
- [ ] IEAT green area minimums
- [ ] Buffer zone requirements
- [ ] Road width standards
- [ ] Parking ratios
- [ ] Utility access
- [ ] Building orientation
- [ ] Lot size targets
- [ ] Road efficiency
- [ ] Other: _______________________________________

**SOFT CONSTRAINTS (Can be relaxed in difficult sites):**

Check ALL constraints that CAN be adjusted if necessary:

- [ ] Fire safety regulations (can slightly reduce clearances with mitigation)
- [ ] IEAT green area (can apply for exemption to 8%)
- [ ] IEAT salable area (can be lower than maximum)
- [ ] Buffer zone (can reduce to 5m in urban sites)
- [ ] Road width (can use 20m ROW for secondary roads)
- [ ] Parking ratios (can reduce with shared parking strategy)
- [ ] Utility access (can use easements/crossings)
- [ ] Building orientation (flexible based on site)
- [ ] Lot size targets (can vary ±20%)
- [ ] Road efficiency (acceptable if improves other metrics)
- [ ] Other: _______________________________________

**Conflict resolution strategy:**

When constraints conflict, the system should:

- [ ] **Prioritize regulatory compliance** - Always meet legal requirements first
- [ ] **Prioritize financial optimization** - Maximize ROI even if affects other factors
- [ ] **Prioritize lot quality** - Ensure usable, well-shaped lots over quantity
- [ ] **Prioritize user preferences** - Follow user's specified priorities
- [ ] **Use AI judgment** - Let optimization algorithm balance trade-offs
- [ ] **Ask user to decide** - Present conflicts and let user choose

---

## 📝 SECTION 9: ADDITIONAL PREFERENCES

### Q11: Other important considerations

**Input format preferences:**

How would your users prefer to input requirements?

- [ ] **Pure conversational chat** - Free-form text, natural language
- [ ] **Guided step-by-step form** - Structured fields and dropdowns
- [ ] **Hybrid approach** - Chat with parameter review panel
- [ ] **Template-based** - Select industry template, customize parameters
- [ ] **File upload** - Import requirements from Excel/PDF
- [ ] **No preference** - System decides best approach

**Handling ambiguous inputs:**

When a user says "I want a large industrial park" without specifying size:

- [ ] **Auto-assume defaults** - System uses standard definition (e.g., 100ha)
- [ ] **Ask clarifying questions** - AI asks "By large, do you mean 50ha, 100ha, or 200ha?"
- [ ] **Provide multiple alternatives** - Generate designs at different scales
- [ ] **Use contextual clues** - Infer from other parameters provided

**Performance expectations:**

What is your acceptable waiting time for design generation?

- [ ] **<1 minute** - Very fast, may sacrifice optimization quality
- [ ] **1-5 minutes** - Fast, balanced approach
- [ ] **5-10 minutes** - Standard, thorough optimization
- [ ] **10-20 minutes** - Comprehensive, multi-objective optimization
- [ ] **>20 minutes acceptable** - Best quality, can run as background task
- [ ] **No specific expectation** - Quality more important than speed

---

## ✅ COMPLETION CHECKLIST

**Before submitting, please ensure:**

- [ ] All sections have been reviewed
- [ ] At least one option checked for each critical question (Sections 1-7)
- [ ] Rankings completed where requested (Section 7)
- [ ] Custom terms and requirements documented (Sections 2, 4)
- [ ] Budget expectations indicated (Section 5)
- [ ] Privacy/compliance requirements clarified (Section 6)

---

## 📧 SUBMISSION

**Client Information:**

- **Organization Name:** _______________________________________
- **Contact Person:** _______________________________________
- **Title/Position:** _______________________________________
- **Email:** _______________________________________
- **Phone:** _______________________________________
- **Date Completed:** _______________________________________

**Signature:** _______________________________________

---

## 📌 NEXT STEPS

Once you complete this checklist:

1. **Email to:** [Technical Team Email]
2. **Schedule follow-up call:** To discuss any questions or clarifications
3. **Timeline:** We'll provide technical proposal within 1 week of receiving completed checklist
4. **Questions:** Contact [Project Manager] at [Email/Phone]

---

**Thank you for providing these critical decisions. Your input will ensure we build a system that precisely meets your needs!**

---

**Document Version:** 1.0  
**Date:** January 25, 2026  
**Prepared by:** Technical Architecture Team
