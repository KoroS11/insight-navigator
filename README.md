# NSA-X: Neuro-Symbolic Autonomous Security Analyst

> **⚠️ DISCLAIMER**: This is a research prototype with a working **frontend UI** and **backend API**. However, **ML/Neural Network models are NOT implemented** - the system uses symbolic rule-based processing only. Real-time ML anomaly detection is planned for future development.

---

## 🚀 Quick Start

### Prerequisites

- **Node.js 18+** - [Download](https://nodejs.org)
- **Python 3.11+** - [Download](https://python.org)
- **Git** - [Download](https://git-scm.com)

### One-Command Setup

**Windows (PowerShell):**
```powershell
git clone https://github.com/KoroS11/insight-navigator.git
cd insight-navigator
.\setup.ps1
```

**Linux/macOS:**
```bash
git clone https://github.com/KoroS11/insight-navigator.git
cd insight-navigator
chmod +x setup.sh && ./setup.sh
```

### Running the Application

**Terminal 1 - Backend:**
```bash
cd backend
# Windows: .\venv\Scripts\Activate.ps1
# Linux/macOS: source venv/bin/activate
uvicorn app.main:app --reload
```

**Terminal 2 - Frontend:**
```bash
npm run dev
```

Open http://localhost:8080 and login with `admin` / `admin123`

---

## 1. Project Overview

NSA-X is a research-grade prototype for a neuro-symbolic security analysis system designed with the following principles:

- **Neuro-Symbolic Architecture**: Combines neural network-based anomaly detection with symbolic rule-based reasoning for more robust and interpretable threat analysis
- **Human-in-the-Loop by Design**: Security analysts remain the final decision authority; the system supports rather than replaces human judgment
- **Explainability-First**: Every detection, recommendation, and action must be traceable and justifiable
- **Governance-Aware**: Built-in audit trails, autonomy boundaries, and compliance controls

### What This Prototype Demonstrates

This prototype visualizes the intended user experience and workflow for security analysts interacting with a neuro-symbolic detection system. It serves as:

- A concept demonstration for stakeholders and mentors
- A design reference for future implementation
- A research artifact documenting the intended system behavior

---

## 2. What Is Implemented (Current State)

The following components exist today:

| Component | Status | Description |
|-----------|--------|-------------|
| **Frontend UI** | ✅ Complete | React + TypeScript + Tailwind CSS + shadcn/ui |
| **Backend API** | ✅ Complete | FastAPI + SQLAlchemy Async + JWT Auth |
| **Database** | ✅ Complete | SQLite (dev) / PostgreSQL (prod) |
| **Event Pipeline** | ✅ Complete | 7-layer processing pipeline (rule-based, no ML) |
| **Symbolic Reasoning** | ✅ Complete | Rule-based threat detection |
| **Explainability Engine** | ✅ Complete | Decision tree + counterfactuals |
| **Audit System** | ✅ Complete | Immutable audit trail |
| **Authentication** | ✅ Complete | JWT + OAuth2 password flow |
| **Test Coverage** | ✅ 87% | 192 tests passing |

### Technical Stack

| Layer | Technology |
|-------|------------|
| Frontend | React 18, TypeScript, TanStack Query, Tailwind CSS, shadcn/ui |
| Backend | FastAPI, Python 3.11+, Pydantic v2 |
| Database | SQLAlchemy 2.0 Async, SQLite/PostgreSQL |
| Auth | python-jose (JWT), passlib (bcrypt) |
| Testing | pytest, pytest-asyncio, 87% coverage |

### Important Clarifications

- **Frontend and Backend are fully connected** — Real API calls, not mocked
- **Data is persisted** — Events, alerts, decisions stored in database
- **Authentication works** — JWT-based login with admin/admin123
- **ML/Neural Networks NOT implemented** — Anomaly detection is rule-based only

---

## 3. What Is NOT Implemented

This section is critical for setting accurate expectations.

| Component | Status | Notes |
|-----------|--------|-------|
| **ML Detection Models** | ❌ Not implemented | No neural network anomaly detection |
| **Behavioral Baseline** | ❌ Not implemented | No learned user/entity behavior profiles |
| **Sequence Analysis** | ❌ Not implemented | No LSTM/Transformer for event sequences |
| **Real Anomaly Scoring** | ❌ Not implemented | Scores are rule-based, not ML-generated |
| **Data Normalization** | ❌ Not implemented | No CEF/STIX/OCSF parsing |
| **SIEM Integration** | ❌ Not implemented | No Splunk/Sentinel/Elastic connectors |
| **SOAR Integration** | ❌ Not implemented | No Phantom/XSOAR/Tines integration |
| **Ticketing Integration** | ❌ Not implemented | No Jira/ServiceNow connectivity |
| **Alert Correlation** | ❌ Not implemented | No event grouping or chaining |
| **Threat Intelligence** | ❌ Not implemented | No IOC enrichment |

### What the UI Shows vs. What Actually Happens

| UI Element | Visual State | Actual Behavior |
|------------|--------------|-----------------|
| Confidence Score | Shows percentage | Calculated from rules, not ML |
| Event Timeline | Shows events | Real events from database |
| Explanation Tree | Shows decision path | Generated from symbolic reasoning |
| Audit Trail | Shows log entries | Persisted to database |
| Analyst Notes | Accepts input | Saved to database |

---

##  Additional Implementations (Planned / To Be Done)

The following components are designed and scoped but pending full implementation or integration.

| Component | Planned Scope |
|-----------|---------------|
| **Neural Detection Layer** | Behavioral baseline, sequence analysis, anomaly scoring with ML models |
| **Frontend UI Prototype** | Full SOC-style React UI with TypeScript & Tailwind CSS |
| **Design System** | Dark theme, SOC-style layout, consistent component library |
| **Dashboard Layout** | Main navigation, sidebar, real-time status indicators |
| **Architecture Visualization** | Conceptual and interactive neuro-symbolic pipeline diagrams |
| **Mock Security Events** | Realistic synthetic event generation with proper identifiers |
| **Analyst Decision Interface** | Confidence indicators, action matrix, analyst notes panel |
| **Explainability UI** | Event summaries, explanation trees, counterfactual visualization |
| **Governance Interface** | Audit trail viewer, autonomy boundary controls |
| **Playbook Reference** | Static and dynamic playbook listing for analyst guidance |

---

## 4. Intended System Architecture (Conceptual)

The following describes the **target architecture**, not the current implementation.

```
┌─────────────────────────────────────────────────────────────────┐
│                      DATA INGESTION LAYER                        │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐        │
│  │   SIEM   │  │   EDR    │  │ Network  │  │   IAM    │        │
│  │  Events  │  │  Alerts  │  │  Flows   │  │   Logs   │        │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘  └────┬─────┘        │
│       └──────────────┴──────────────┴──────────────┘            │
│                              │                                   │
│                    ┌─────────▼─────────┐                        │
│                    │   Normalization   │                        │
│                    │   (CEF → OCSF)    │                        │
│                    └─────────┬─────────┘                        │
└──────────────────────────────┼──────────────────────────────────┘
                               │
┌──────────────────────────────▼──────────────────────────────────┐
│                     NEURAL DETECTION LAYER                       │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐ │
│  │ Behavioral      │  │ Sequence        │  │ Anomaly         │ │
│  │ Baseline        │  │ Analysis        │  │ Scoring         │ │
│  └────────┬────────┘  └────────┬────────┘  └────────┬────────┘ │
│           └─────────────────────┴─────────────────────┘         │
│                              │                                   │
│                    ┌─────────▼─────────┐                        │
│                    │ Detection Output  │                        │
│                    │ + Confidence      │                        │
│                    └─────────┬─────────┘                        │
└──────────────────────────────┼──────────────────────────────────┘
                               │
┌──────────────────────────────▼──────────────────────────────────┐
│                   SYMBOLIC REASONING LAYER                       │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐ │
│  │ Rule Engine     │  │ Policy DSL      │  │ Conflict        │ │
│  │ (Rete/CLIPS)    │  │ Evaluation      │  │ Resolution      │ │
│  └────────┬────────┘  └────────┬────────┘  └────────┬────────┘ │
│           └─────────────────────┴─────────────────────┘         │
│                              │                                   │
│                    ┌─────────▼─────────┐                        │
│                    │ Reasoned Decision │                        │
│                    │ + Rule Trace      │                        │
│                    └─────────┬─────────┘                        │
└──────────────────────────────┼──────────────────────────────────┘
                               │
┌──────────────────────────────▼──────────────────────────────────┐
│                    EXPLAINABILITY ENGINE                         │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐ │
│  │ Provenance      │  │ Evidence        │  │ Counterfactual  │ │
│  │ Tracking        │  │ Attribution     │  │ Generation      │ │
│  └────────┬────────┘  └────────┬────────┘  └────────┬────────┘ │
│           └─────────────────────┴─────────────────────┘         │
│                              │                                   │
│                    ┌─────────▼─────────┐                        │
│                    │ Human-Readable    │                        │
│                    │ Explanation       │                        │
│                    └─────────┬─────────┘                        │
└──────────────────────────────┼──────────────────────────────────┘
                               │
┌──────────────────────────────▼──────────────────────────────────┐
│                   ANALYST DECISION LAYER                         │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐ │
│  │ Decision        │  │ Escalation      │  │ Feedback        │ │
│  │ Interface       │  │ Workflow        │  │ Loop            │ │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
                               │
┌──────────────────────────────▼──────────────────────────────────┐
│                    GOVERNANCE & AUDIT                            │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐ │
│  │ Audit Trail     │  │ Autonomy        │  │ Compliance      │ │
│  │ (Immutable)     │  │ Boundaries      │  │ Reporting       │ │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
```

### Layer Descriptions

| Layer | Purpose | Key Components |
|-------|---------|----------------|
| Data Ingestion | Collect and normalize security telemetry | SIEM connectors, log parsers, OCSF normalization |
| Neural Detection | Identify anomalies using ML models | Behavioral baselines, sequence models, anomaly scorers |
| Symbolic Reasoning | Apply rules and policies to detections | Rule engine, policy DSL, conflict resolution |
| Explainability | Generate human-understandable explanations | Provenance graphs, evidence chains, counterfactuals |
| Analyst Decision | Present findings for human review | Decision UI, escalation workflows, feedback capture |
| Governance | Ensure accountability and compliance | Immutable audit logs, autonomy controls, reports |

---

## 5. MVP TODO List

### What Needs to Be Built to Reach MVP

This is the prioritized work required to transform the prototype into a functional minimum viable product.

---

#### 5.1 Backend Infrastructure

| Task | Why Needed | Complexity |
|------|------------|------------|
| Design database schema | Persist events, decisions, audit logs | Medium |
| Implement event ingestion API | Receive security events from sources | Medium |
| Build normalization service | Convert diverse formats to OCSF | High |
| Create alert generation logic | Transform anomalies into actionable alerts | Medium |
| Set up authentication system | Secure access, enable RBAC | Medium |
| Implement API layer | Connect frontend to backend services | Medium |
| Add logging and monitoring | Operational visibility | Low |

---

#### 5.2 Detection Capabilities

| Task | Why Needed | Complexity |
|------|------------|------------|
| Implement baseline anomaly detection | Core detection capability | High |
| Build feature extraction pipeline | Prepare data for ML models | High |
| Create model training workflow | Enable model updates | High |
| Implement drift detection | Detect when models degrade | Medium |
| Add detection confidence scoring | Quantify detection reliability | Medium |

---

#### 5.3 Symbolic Reasoning

| Task | Why Needed | Complexity |
|------|------------|------------|
| Select and integrate rule engine | Execute symbolic rules (Rete, CLIPS, Drools) | High |
| Design policy DSL | Allow analysts to define rules | High |
| Implement conflict resolution | Handle contradictory rules | Medium |
| Build rule versioning | Track policy changes | Low |
| Create rule testing framework | Validate rules before deployment | Medium |

---

#### 5.4 Explainability

| Task | Why Needed | Complexity |
|------|------------|------------|
| Implement provenance tracking | Trace data lineage | High |
| Build evidence attribution | Link conclusions to supporting data | High |
| Create explanation templates | Generate consistent explanations | Medium |
| Implement counterfactual generation | Show "what would change the outcome" | High |
| Add confidence breakdown | Explain score components | Medium |

---

#### 5.5 Analyst Workflows

| Task | Why Needed | Complexity |
|------|------------|------------|
| Persist analyst decisions | Save verdicts and justifications | Low |
| Implement escalation workflows | Route to appropriate responders | Medium |
| Build feedback capture | Enable model improvement | Medium |
| Add case management | Group related alerts | Medium |
| Create analyst performance metrics | Measure decision quality | Low |

---

#### 5.6 Governance

| Task | Why Needed | Complexity |
|------|------------|------------|
| Implement immutable audit log | Regulatory compliance | Medium |
| Build autonomy boundary enforcement | Prevent unauthorized automation | Medium |
| Create compliance reporting | Generate audit reports | Low |
| Add role-based access control | Restrict sensitive operations | Medium |

---

#### 5.7 Integrations

| Task | Why Needed | Complexity |
|------|------------|------------|
| SIEM connector (Splunk/Sentinel) | Ingest security events | High |
| EDR connector (CrowdStrike/Defender) | Endpoint telemetry | High |
| SOAR integration | Automate response actions | High |
| Ticketing integration (Jira/ServiceNow) | Track incidents | Medium |
| Threat intel feeds | Enrich with IOCs | Medium |

---

## 6. Roadmap

A realistic phased approach to reach production readiness.

### Phase 0: Frontend Prototype ✅ COMPLETE

- UI/UX design and component library
- Mock data and workflow visualization
- Architecture documentation
- Stakeholder demonstration

### Phase 1: Core Backend + Basic Detection

- Database schema and API layer
- Event ingestion and normalization
- Simple anomaly detection (threshold-based)
- Basic persistence (decisions, audit logs)
- Authentication and basic RBAC

**Exit Criteria**: System can ingest events, detect simple anomalies, and persist analyst decisions.

### Phase 2: Explainability + Analyst Workflows

- Rule engine integration
- Provenance tracking
- Evidence attribution
- Escalation workflows
- Feedback loop

**Exit Criteria**: Detections include explanations; analysts can review, decide, and provide feedback.

### Phase 3: Pilot-Ready System

- ML-based detection models
- Counterfactual generation
- SIEM/EDR integration
- Compliance reporting
- Performance optimization

**Exit Criteria**: System can be deployed in a controlled environment for analyst evaluation.

### Phase 4: Production Hardening (Future)

- High availability architecture
- Security audit and penetration testing
- Scalability testing
- Full RBAC implementation
- Enterprise integrations

---

## 7. Who This Is For

### Primary Audience

| Audience | Use Case |
|----------|----------|
| **SOC Analysts** | Evaluate the proposed workflow and provide feedback |
| **Security Architects** | Assess the system design and integration points |
| **Researchers** | Study neuro-symbolic approaches to security |
| **Mentors/Judges** | Evaluate the project's technical merit and feasibility |

### Not Intended For

- **End users seeking a production tool** — This is a research prototype
- **Organizations needing immediate deployment** — Significant development required
- **Non-technical stakeholders** — Documentation assumes security domain knowledge

---

## 8. Project Structure

```
├── public/
│   ├── favicon.ico
│   ├── placeholder.svg
│   └── robots.txt
├── src/
│   ├── components/
│   │   ├── architecture/
│   │   │   └── ArchitectureFlow.tsx      # System architecture diagram
│   │   ├── decisions/
│   │   │   ├── ActionMatrix.tsx          # Decision action recommendations
│   │   │   ├── AnalystNotes.tsx          # Analyst note-taking (not persisted)
│   │   │   └── ConfidenceIndicator.tsx   # AI confidence visualization
│   │   ├── explainability/
│   │   │   ├── CounterfactualPanel.tsx   # "What-if" scenarios (static)
│   │   │   ├── EventSummary.tsx          # Event details summary
│   │   │   └── ExplanationTree.tsx       # Decision tree visualization
│   │   ├── governance/
│   │   │   ├── AuditTrail.tsx            # Audit logs (mock data)
│   │   │   └── AutonomyBoundary.tsx      # AI autonomy controls
│   │   ├── layout/
│   │   │   ├── AppLayout.tsx             # Main application layout
│   │   │   ├── AppSidebar.tsx            # Navigation sidebar
│   │   │   └── StatusBar.tsx             # System status indicator
│   │   ├── shared/
│   │   │   ├── MetricCard.tsx            # Reusable metric display
│   │   │   └── StatusBadge.tsx           # Status indicator badge
│   │   ├── ui/                           # shadcn/ui components
│   │   └── NavLink.tsx                   # Navigation link component
│   ├── hooks/
│   │   ├── use-mobile.tsx                # Mobile detection hook
│   │   └── use-toast.ts                  # Toast notification hook
│   ├── integrations/
│   │   └── supabase/
│   │       ├── client.ts                 # Supabase client (not used yet)
│   │       └── types.ts                  # Database types (empty)
│   ├── lib/
│   │   └── utils.ts                      # Utility functions
│   ├── pages/
│   │   ├── Architecture.tsx              # System architecture page
│   │   ├── Decisions.tsx                 # Analyst decision interface
│   │   ├── Explainability.tsx            # AI explanation dashboard
│   │   ├── Governance.tsx                # Governance & compliance
│   │   ├── Index.tsx                     # Main dashboard
│   │   └── NotFound.tsx                  # 404 error page
│   ├── App.tsx                           # Root application component
│   ├── App.css                           # Global styles
│   ├── index.css                         # Tailwind CSS configuration
│   └── main.tsx                          # Application entry point
├── supabase/
│   └── config.toml                       # Supabase configuration
├── .env                                  # Environment variables
├── tailwind.config.ts                    # Tailwind configuration
├── vite.config.ts                        # Vite build configuration
└── package.json                          # Dependencies
```

---

## 9. Local Development

### Prerequisites

- Node.js 18+
- npm or bun

### Installation

```bash
# Clone the repository
git clone https://github.com/KoroS11/insight-navigator.git

# Navigate to project directory
cd insight-navigator

# Install dependencies
npm install

# Start development server
npm run dev
```

### Available Scripts

| Command | Description |
|---------|-------------|
| `npm run dev` | Start development server |
| `npm run build` | Build for production |
| `npm run preview` | Preview production build |
| `npm run lint` | Run ESLint |

---

## 10. Changelog

All notable changes to this project are documented here.

### [2026-01-12]

#### Documentation
- Complete README rewrite with honest assessment of current state
- Added detailed MVP TODO list with complexity ratings
- Documented intended vs. actual architecture
- Created phased roadmap

#### Added
- Enabled Lovable Cloud backend integration (not yet utilized)

#### Fixed
- Fixed TypeScript error in Decisions.tsx (removed unused `recommendedAction` prop)

### [Initial Commit]

#### Added
- Frontend UI prototype
- Dashboard, Decisions, Explainability, Governance, Architecture pages
- Component library with shadcn/ui
- Mock data for demonstration
- Dark theme design system

---

## 11. License

License not yet specified. All rights reserved.

---

## 12. Contributing

1. Create a feature branch from `main`
2. Make your changes
3. Submit a pull request for review

---

*This is a research prototype developed to explore neuro-symbolic approaches to security operations. It is not intended for production use without significant additional development.*
