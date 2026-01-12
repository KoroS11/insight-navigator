# Neuro-Symbolic Security Operations Center (SOC)

A modern, AI-powered Security Operations Center dashboard built with React, TypeScript, and Tailwind CSS. This application provides security analysts with real-time threat detection, explainable AI decisions, and comprehensive governance controls.

## 🎯 Project Overview

This SOC platform combines neural network-based anomaly detection with symbolic rule engines to provide:

- **Real-time Security Monitoring**: Track security events, threats, and system performance
- **AI-Powered Decision Support**: Confidence indicators and action recommendations
- **Explainable AI**: Understand why the system made specific decisions
- **Governance & Compliance**: Audit trails, autonomy boundaries, and emergency protocols

## 🛠️ Technology Stack

| Category | Technology |
|----------|------------|
| **Frontend** | React 18, TypeScript |
| **Styling** | Tailwind CSS, shadcn/ui |
| **State Management** | TanStack React Query |
| **Routing** | React Router v6 |
| **Backend** | Lovable Cloud (Supabase) |
| **Animations** | Framer Motion |
| **Charts** | Recharts |
| **Icons** | Lucide React |

## 📁 Project Structure

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
│   │   │   ├── AnalystNotes.tsx          # Analyst note-taking component
│   │   │   └── ConfidenceIndicator.tsx   # AI confidence visualization
│   │   ├── explainability/
│   │   │   ├── CounterfactualPanel.tsx   # "What-if" scenario analysis
│   │   │   ├── EventSummary.tsx          # Event details summary
│   │   │   └── ExplanationTree.tsx       # Decision tree visualization
│   │   ├── governance/
│   │   │   ├── AuditTrail.tsx            # System audit logs
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
│   │       ├── client.ts                 # Supabase client configuration
│   │       └── types.ts                  # Database type definitions
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
│   ├── index.css                         # Tailwind CSS imports
│   └── main.tsx                          # Application entry point
├── supabase/
│   └── config.toml                       # Supabase configuration
├── .env                                  # Environment variables
├── tailwind.config.ts                    # Tailwind configuration
├── vite.config.ts                        # Vite build configuration
└── package.json                          # Dependencies and scripts
```

## 🚀 Getting Started

### Prerequisites

- Node.js 18+ 
- npm or bun

### Installation

```bash
# Clone the repository
git clone <YOUR_GIT_URL>

# Navigate to project directory
cd <YOUR_PROJECT_NAME>

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

## 📱 Pages

### Dashboard (`/`)
Main security operations dashboard displaying:
- Key performance metrics
- Recent security events
- Active investigations
- System performance summary

### Decisions (`/decisions`)
Analyst decision support interface with:
- AI confidence indicators
- Action recommendation matrix
- Analyst notes and observations
- Relevant playbook references

### Explainability (`/explainability`)
AI decision explanation center featuring:
- Event summaries and timelines
- Explanation trees for decision logic
- Counterfactual "what-if" analysis
- Evidence strength indicators

### Governance (`/governance`)
Compliance and control management:
- Autonomy boundary controls
- Emergency override protocols
- Complete audit trail
- Security policy management

### Architecture (`/architecture`)
System architecture documentation:
- Neuro-symbolic processing pipeline
- Layer specifications and performance
- Integration points and protocols

## 🔐 Backend Integration

This project uses **Lovable Cloud** for backend services:
- **Database**: PostgreSQL with Row Level Security
- **Authentication**: Built-in user management
- **Storage**: Secure file handling
- **Edge Functions**: Serverless backend logic

## 📝 Changelog

All notable changes to this project will be documented in this section.

### [2025-01-12]

#### Added
- ✅ Enabled Lovable Cloud backend integration
- ✅ Added comprehensive README documentation
- ✅ Documented complete project structure

#### Fixed
- 🐛 Fixed TypeScript error in Decisions.tsx (removed unused `recommendedAction` prop)

---

## 📄 License

This project is private and proprietary.

## 🤝 Contributing

1. Create a feature branch from `main`
2. Make your changes
3. Submit a pull request for review

---

*Built with [Lovable](https://lovable.dev) - The AI-powered web application builder*
