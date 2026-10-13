# CreatorXDR 🛡️

### Blockchain-Backed Creator Identity & Cybersecurity Platform

CreatorXDR is a cybersecurity and digital identity platform designed to protect content creators from **identity impersonation, phishing, suspicious logins, unknown devices, credential-related threats, and other account-security risks**.

The platform combines **identity verification, blockchain-backed verification proofs, security monitoring, threat detection, risk assessment, and actionable alerts** into a single creator-focused security dashboard.

---

## 📌 Table of Contents

* [Overview](#-overview)
* [Problem Statement](#-problem-statement)
* [Proposed Solution](#-proposed-solution)
* [Objectives](#-objectives)
* [Key Features](#-key-features)
* [System Workflow](#-system-workflow)
* [System Architecture](#-system-architecture)
* [Modules](#-modules)
* [Technology Stack](#-technology-stack)
* [Project Structure](#-project-structure)
* [Team Responsibilities](#-team-responsibilities)
* [Database Design](#-database-design)
* [API Design](#-api-design)
* [Threat Detection](#-threat-detection-model)
* [Blockchain Design](#-blockchain-design)
* [Security & Privacy](#-security--privacy)
* [Installation](#-installation)
* [Running the Project](#-running-the-backend)
* [Testing](#-testing)
* [Development Roadmap](#-development-roadmap)
* [Future Enhancements](#-future-enhancements)
* [Contribution Guidelines](#-contribution-guidelines)
* [License](#-license)
* [Disclaimer](#-disclaimer)

---

# 🔎 Overview

Content creators increasingly depend on digital platforms for their identity, communication, business relationships, and income.

This also makes creator accounts attractive targets for:

* Account impersonation
* Phishing
* Credential theft
* Account takeover
* Suspicious logins
* Unknown devices
* Fake sponsorship messages
* Malicious links
* Identity misuse
* Social engineering

Existing creator verification systems generally focus on proving that an account is authentic, while conventional cybersecurity tools are often designed for organizations rather than individual creators.

**CreatorXDR bridges these two areas.**

It provides a unified platform where a creator can:

1. Verify their identity.
2. Register their original account.
3. Generate a blockchain-backed verification proof.
4. Monitor account-security events.
5. Detect suspicious activity.
6. Analyze potentially malicious URLs.
7. Identify possible impersonation.
8. Receive risk-based alerts.
9. View recommended security actions.
10. Maintain a tamper-evident security/audit history.

---

# ❗ Problem Statement

Creators can face multiple digital-security threats simultaneously.

For example:

```text
Creator
   │
   ├── Fake account impersonating them
   │
   ├── Phishing link sent as a sponsorship offer
   │
   ├── Login from an unknown device
   │
   ├── Multiple failed authentication attempts
   │
   └── Potential credential exposure
```

These events are usually handled separately.

CreatorXDR aims to bring these security signals together and provide the creator with a centralized view of their digital security.

---

# 💡 Proposed Solution

CreatorXDR combines:

```text
Identity Verification
        +
Original Account Registration
        +
Blockchain Verification
        +
Security Monitoring
        +
Threat Detection
        +
Risk Assessment
        +
Actionable Alerts
        +
Audit Trail
```

The result is a creator-focused security platform that provides both **identity credibility** and **cybersecurity monitoring**.

---

# 🎯 Objectives

The primary objectives of CreatorXDR are:

* Establish a verified creator identity.
* Associate the verified identity with an original account.
* Provide tamper-evident verification through blockchain.
* Detect suspicious login behavior.
* Monitor unknown devices.
* Identify potential phishing URLs.
* Detect possible impersonation.
* Calculate security risk based on multiple indicators.
* Generate actionable security alerts.
* Maintain a security event history.
* Protect sensitive identity information.
* Provide a centralized creator-security dashboard.

---

# ✨ Key Features

## 1. Creator Identity Verification

Allows a creator to establish a verified identity within CreatorXDR.

The prototype separates identity verification from blockchain storage.

Sensitive identity information is **not stored directly on the blockchain**.

---

## 2. Original Account Registration

A verified creator can register their original social-media account.

Example:

```text
Creator
   │
   └── Verified Identity
            │
            └── Original Account
                    │
                    └── CreatorXDR Profile
```

---

## 3. Blockchain Verification

A cryptographic verification credential/hash can be recorded on a blockchain.

The blockchain provides:

* Integrity
* Timestamping
* Verification proof
* Tamper resistance
* Auditability

---

## 4. Login Monitoring

CreatorXDR can analyze login events using indicators such as:

* Device
* Location indicator
* Login time
* Failed authentication attempts
* Known/unknown device status

---

## 5. Device Monitoring

The system maintains information about devices associated with the creator.

Example:

```text
Laptop       → Known
Phone        → Known
New Device   → Unknown
```

An unknown device can contribute to the overall risk assessment.

---

## 6. Phishing Detection

CreatorXDR can analyze URLs and identify potentially suspicious links.

Possible indicators include:

* Suspicious domain
* URL structure
* Login-related keywords
* Domain reputation
* Known malicious indicators
* Model-based classification

Example:

```text
URL
 ↓
Feature Extraction
 ↓
Threat Analysis
 ↓
Risk Level
 ↓
CreatorXDR Alert
```

---

## 7. Impersonation Detection

The platform can identify accounts that may be attempting to impersonate a verified creator.

Potential signals include:

* Username similarity
* Display-name similarity
* Profile information
* Profile-image similarity
* Other creator-identifying information

The result can be classified as:

```text
LOW
MEDIUM
HIGH
```

This classification is an indicator for investigation rather than definitive proof of malicious intent.

---

## 8. Threat Detection Engine

The threat engine combines multiple security indicators.

```text
Login Anomaly
      +
Unknown Device
      +
Phishing Indicator
      +
Impersonation Indicator
      +
Credential Indicator
      ↓
Threat Engine
      ↓
Risk Assessment
```

---

## 9. Risk Scoring

CreatorXDR can assign a risk score based on detected indicators.

Example prototype model:

```text
New Device              +25
Unusual Location        +25
Multiple Failed Logins  +30
Suspicious URL          +40
High Impersonation      +50
```

The resulting score can be mapped to a risk category:

```text
0–29      LOW
30–59     MEDIUM
60–100    HIGH
```

These values are configurable prototype parameters and are not intended as a universal cybersecurity standard.

---

## 10. Security Alerts

When suspicious activity is detected, CreatorXDR generates an alert.

Example:

```text
HIGH-RISK EVENT

Suspicious login detected.

Indicators:
• Unknown device
• Unusual login location
• Multiple failed attempts

Recommended actions:
• Review active sessions
• Revoke unknown device
• Change credentials if necessary
• Enable MFA
```

---

## 11. Recommended Actions

CreatorXDR is designed to provide actionable information instead of simply reporting an event.

Possible actions include:

* Review login
* Review active sessions
* Revoke unknown device
* Change password
* Enable MFA
* Avoid suspicious URLs
* Report potential impersonation
* Review account activity

---

## 12. Security Audit Trail

Security events can be recorded with:

* Event ID
* Creator ID
* Event type
* Timestamp
* Risk level
* Event hash
* Blockchain reference

This provides a tamper-evident history for relevant security events.

---

# 🔄 System Workflow

The complete CreatorXDR workflow is:

```text
                    CREATOR
                       │
                       ▼
              ┌─────────────────┐
              │    REGISTER     │
              └────────┬────────┘
                       │
                       ▼
              ┌─────────────────┐
              │    VERIFY       │
              │    IDENTITY     │
              └────────┬────────┘
                       │
                       ▼
              Verification Proof
                       │
                       ▼
              ┌─────────────────┐
              │   BLOCKCHAIN    │
              └────────┬────────┘
                       │
                       ▼
              Register Original
                   Account
                       │
                       ▼
              ┌─────────────────┐
              │     SECURITY    │
              │    MONITORING   │
              └────────┬────────┘
                       │
          ┌────────────┼────────────┐
          ▼            ▼            ▼
       Login        Device       Phishing
      Analysis      Analysis      Analysis
          │            │            │
          └────────────┼────────────┘
                       ▼
              ┌─────────────────┐
              │ THREAT ENGINE   │
              └────────┬────────┘
                       ▼
              ┌─────────────────┐
              │  RISK SCORING   │
              └────────┬────────┘
                       ▼
              ┌─────────────────┐
              │     ALERT       │
              └────────┬────────┘
                       ▼
              Recommended Action
                       │
                       ▼
              Security Audit Log
```

---

# 🏗️ System Architecture

```text
                         CREATORXDR
                             │
                 ┌───────────┴───────────┐
                 │                       │
                 ▼                       ▼
             FRONTEND                 BACKEND
                 │                       │
          ┌──────┼──────┐          ┌─────┼─────┐
          │      │      │          │     │     │
       Login  Dashboard Alerts    APIs Threat Auth
                                  │     Engine
                                  │
                                  ▼
                              DATABASE
                                  │
                    ┌─────────────┴─────────────┐
                    │                           │
                    ▼                           ▼
              THREAT SERVICES              BLOCKCHAIN
                    │                           │
             ┌──────┼──────┐             Identity Proof
             │      │      │             Audit Integrity
          Phishing Login  Device
             │
             ▼
       Impersonation
```

---

# 🧩 Modules

## Module 1 — Identity Verification

Responsible for:

* Creator registration
* Identity verification
* Verification status
* Credential generation

---

## Module 2 — Blockchain Identity

Responsible for:

* Credential hashing
* Smart contract interaction
* Blockchain transaction
* Verification proof
* Audit integrity

---

## Module 3 — Original Account

Responsible for:

* Account registration
* Platform information
* Original-account association
* Creator profile

---

## Module 4 — Login Monitoring

Responsible for:

* Login events
* Failed attempts
* Login anomaly indicators
* Risk contribution

---

## Module 5 — Device Monitoring

Responsible for:

* Known devices
* Unknown devices
* Device history
* Device risk indicators

---

## Module 6 — Phishing Detection

Responsible for:

* URL analysis
* Feature extraction
* Phishing classification
* Risk assessment

---

## Module 7 — Impersonation Detection

Responsible for:

* Candidate account analysis
* Username similarity
* Profile similarity
* Potential impersonation alerts

---

## Module 8 — Threat Engine

Responsible for:

* Combining security signals
* Threat classification
* Risk calculation
* Severity determination

---

## Module 9 — Alert System

Responsible for:

* Alert generation
* Severity
* Threat description
* Recommended actions

---

## Module 10 — Audit Trail

Responsible for:

* Security-event history
* Event hashes
* Timestamps
* Blockchain references

---

# 🛠️ Technology Stack

## Frontend

Recommended:

* React
* JavaScript / TypeScript
* HTML
* CSS
* REST API integration

---

## Backend

Recommended:

* Python
* Flask
* REST APIs

---

## Database

Recommended:

* PostgreSQL

For an initial prototype, SQLite can also be used.

---

## Cybersecurity / Machine Learning

Possible technologies:

* Python
* scikit-learn
* Pandas
* NumPy
* BeautifulSoup
* URL feature extraction
* Threat-intelligence feeds

---

## Blockchain

Recommended:

* Solidity
* Ethereum-compatible blockchain
* Hardhat
* Web3 / Ethers
* MetaMask for development/testing

A local blockchain or test network should be used during development.

---

## Development Tools

* Git
* GitHub
* VS Code
* Postman
* Docker
* GitHub Actions

---

# 📁 Project Structure

The intended project structure is:

```text
CreatorXDR/
│
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   ├── pages/
│   │   ├── services/
│   │   └── App.jsx
│   │
│   ├── package.json
│   └── README.md
│
├── backend/
│   ├── app.py
│   │
│   ├── routes/
│   │   ├── auth.py
│   │   ├── creator.py
│   │   ├── verification.py
│   │   ├── threats.py
│   │   └── alerts.py
│   │
│   ├── models/
│   │   ├── creator.py
│   │   ├── account.py
│   │   ├── device.py
│   │   ├── threat.py
│   │   └── alert.py
│   │
│   ├── services/
│   │   ├── blockchain.py
│   │   ├── threat_engine.py
│   │   └── notification.py
│   │
│   ├── database/
│   ├── requirements.txt
│   └── .env.example
│
├── threat_engine/
│   ├── risk_engine.py
│   ├── login_detection.py
│   ├── device_detection.py
│   └── impersonation.py
│
├── phishing/
│   ├── model/
│   ├── feature_extraction.py
│   ├── predictor.py
│   └── requirements.txt
│
├── blockchain/
│   ├── contracts/
│   │   └── CreatorIdentity.sol
│   │
│   ├── scripts/
│   ├── test/
│   ├── hardhat.config.js
│   └── package.json
│
├── tests/
│   ├── backend/
│   ├── phishing/
│   ├── blockchain/
│   └── integration/
│
├── docs/
│   ├── architecture/
│   ├── diagrams/
│   ├── api/
│   └── reports/
│
├── .gitignore
├── README.md
└── LICENSE
```

---

# 👥 Team Responsibilities

| Team Member | Primary Responsibility                                                         |
| ----------- | ------------------------------------------------------------------------------ |
| **Anusha**  | System architecture, integration, cybersecurity workflow, project coordination |
| **Tanishq** | Blockchain and smart contract                                                  |
| **Aditi**   | Cybersecurity and threat-detection logic                                       |
| **Sheetal** | Backend, APIs and database                                                     |
| **Shlok**   | Frontend and dashboard                                                         |
| **Ujwala**  | Threat intelligence, phishing/impersonation datasets and testing               |

### Integration dependency

```text
                 Anusha
                   │
        ┌──────────┼──────────┐
        ▼          ▼          ▼
     Sheetal    Tanishq     Aditi
    Backend    Blockchain  Security
        │          │          │
        └──────────┼──────────┘
                   ▼
                 Shlok
               Frontend
                   │
                   ▼
                Ujwala
           Threat Testing
```

---

# 🗄️ Database Design

## Creator

```text
creator_id
name
email
verification_status
credential_hash
created_at
```

## Account

```text
account_id
creator_id
platform
username
account_identifier
is_original
created_at
```

## Device

```text
device_id
creator_id
device_identifier
first_seen
last_seen
status
```

## Login Event

```text
login_id
creator_id
device_id
timestamp
location_indicator
failed_attempts
risk_score
status
```

## Threat

```text
threat_id
creator_id
threat_type
severity
description
timestamp
status
```

## Alert

```text
alert_id
creator_id
threat_id
risk_level
message
recommended_action
timestamp
```

## Audit Event

```text
event_id
creator_id
event_type
timestamp
event_hash
blockchain_reference
```

---

# 🔌 API Design

## Authentication

```http
POST /api/register
POST /api/login
```

## Identity

```http
POST /api/verify
GET /api/verification/<creator_id>
```

## Creator

```http
GET /api/creator/<creator_id>
POST /api/account
```

## Security

```http
POST /api/login-event
POST /api/analyze-url
GET /api/threats/<creator_id>
```

## Alerts

```http
GET /api/alerts/<creator_id>
POST /api/alerts/<alert_id>/resolve
```

## Audit

```http
GET /api/audit/<creator_id>
```

The exact endpoints may change during implementation.

---

# 🧠 Threat Detection Model

CreatorXDR initially uses a **rule-based risk engine**.

Example:

```python
risk_score = 0

if new_device:
    risk_score += 25

if unusual_location:
    risk_score += 25

if failed_attempts >= 5:
    risk_score += 30

if suspicious_url:
    risk_score += 40

if high_impersonation_similarity:
    risk_score += 50
```

Risk classification:

```python
if risk_score >= 60:
    severity = "HIGH"
elif risk_score >= 30:
    severity = "MEDIUM"
else:
    severity = "LOW"
```

This architecture allows a machine-learning model to replace or supplement individual detection components later.

---

# 🔗 Blockchain Design

CreatorXDR does **not** store sensitive identity information directly on the blockchain.

Instead:

```text
Identity Verification
        ↓
Verification Result
        ↓
Credential / Hash
        ↓
Smart Contract
        ↓
Blockchain
```

Possible blockchain record:

```text
creatorHash
verificationHash
timestamp
transactionId
```

The application database can store the transaction reference needed to verify the proof.

---

# 🔐 Security & Privacy

CreatorXDR follows these principles:

### Sensitive data

Sensitive identity information should remain off-chain.

### Password security

Passwords must never be stored in plaintext.

Use:

* Password hashing
* Secure authentication
* Session/token security

### Blockchain

Blockchain should be used for:

* Proof
* Integrity
* Timestamping
* Auditability

It should not replace the application's normal database.

### Secrets

API keys, database credentials and blockchain private keys must never be committed to Git.

Use environment variables:

```text
.env
```

and provide:

```text
.env.example
```

instead.

---

# ⚙️ Installation

## 1. Clone the repository

```bash
git clone https://github.com/<YOUR-USERNAME>/CreatorXDR.git

cd CreatorXDR
```

---

## 2. Backend setup

```bash
cd backend

python -m venv venv
```

### Windows

```bash
venv\Scripts\activate
```

### Linux/macOS

```bash
source venv/bin/activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

---

## 3. Configure environment variables

Create:

```text
.env
```

Example:

```env
FLASK_ENV=development
SECRET_KEY=change-this
DATABASE_URL=sqlite:///creatorxdr.db

BLOCKCHAIN_RPC_URL=
BLOCKCHAIN_CONTRACT_ADDRESS=
BLOCKCHAIN_PRIVATE_KEY=
```

Never commit the real `.env` file.

---

# ▶️ Running the Backend

From:

```text
backend/
```

run:

```bash
python app.py
```

The API should become available at the configured local server address.

---

# ▶️ Running the Frontend

From:

```text
frontend/
```

install dependencies:

```bash
npm install
```

Run:

```bash
npm run dev
```

---

# ⛓️ Running the Blockchain

From:

```text
blockchain/
```

install dependencies:

```bash
npm install
```

Compile:

```bash
npx hardhat compile
```

Run tests:

```bash
npx hardhat test
```

Deploy using the project's configured development/test network.

---

# 🧪 Testing

CreatorXDR should include unit, integration and security tests.

## Backend tests

Test:

* Registration
* Authentication
* Creator creation
* Account registration
* Threat creation
* Alert creation

## Threat-engine tests

Test:

```text
Known device
Unknown device
Normal login
Multiple failed logins
Suspicious URL
Potential impersonation
Multiple simultaneous indicators
```

## Blockchain tests

Test:

* Credential registration
* Credential lookup
* Transaction generation
* Verification
* Invalid credential handling

## Integration tests

Test the complete workflow:

```text
Registration
     ↓
Verification
     ↓
Blockchain
     ↓
Account
     ↓
Security Event
     ↓
Threat Engine
     ↓
Risk
     ↓
Alert
     ↓
Audit
```

---

# 🚀 Development Roadmap

## Phase 1 — Foundation

* [ ] Repository setup
* [ ] Git branching strategy
* [ ] Backend setup
* [ ] Database schema
* [ ] Frontend skeleton

---

## Phase 2 — Identity

* [ ] Creator registration
* [ ] Identity verification prototype
* [ ] Verification credential
* [ ] Original account registration

---

## Phase 3 — Blockchain

* [ ] Smart contract
* [ ] Credential hashing
* [ ] Blockchain deployment
* [ ] Backend integration
* [ ] Verification proof

---

## Phase 4 — Security Monitoring

* [ ] Login-event model
* [ ] Device model
* [ ] Unknown-device detection
* [ ] Login anomaly detection

---

## Phase 5 — Threat Detection

* [ ] Phishing detection
* [ ] URL analysis
* [ ] Impersonation detection
* [ ] Threat engine
* [ ] Risk scoring

---

## Phase 6 — Dashboard

* [ ] Creator dashboard
* [ ] Security status
* [ ] Threat page
* [ ] Alert page
* [ ] Device page
* [ ] Verification page
* [ ] Audit page

---

## Phase 7 — Integration

* [ ] Frontend ↔ Backend
* [ ] Backend ↔ Database
* [ ] Backend ↔ Blockchain
* [ ] Backend ↔ Threat Engine
* [ ] End-to-end workflow

---

## Phase 8 — Testing & Documentation

* [ ] Unit testing
* [ ] Integration testing
* [ ] Security testing
* [ ] Documentation
* [ ] Screenshots
* [ ] Architecture diagrams
* [ ] Final demonstration

---

# 🔮 Future Enhancements

Possible future improvements include:

* Real-time security monitoring
* More advanced behavioral anomaly detection
* Machine-learning-based risk scoring
* Additional threat-intelligence sources
* Browser extension for phishing detection
* Mobile application
* Multi-platform creator monitoring
* Advanced impersonation analysis
* Automated incident-response workflows
* Hardware/security-key support
* Decentralized identity standards
* More sophisticated blockchain-based credentials

---

# 🤝 Contribution Guidelines

Each team member should work on a separate branch.

Example:

```text
main
│
├── feature/frontend
├── feature/backend
├── feature/blockchain
├── feature/threat-engine
├── feature/phishing
└── feature/testing
```

## Workflow

```bash
git checkout -b feature/<feature-name>

git add .

git commit -m "Add <feature>"

git push origin feature/<feature-name>
```

Create a Pull Request into `main`.

Do not directly push experimental changes to `main`.

---

# 📋 Commit Convention

Use descriptive commits.

Examples:

```text
feat: add creator registration API
feat: implement phishing URL analyzer
feat: add blockchain identity contract
feat: create security dashboard

fix: correct login risk calculation
fix: resolve alert API issue

docs: update architecture documentation
test: add threat engine tests

refactor: reorganize backend services
```

---

# 🌿 Branch Strategy

```text
main
  │
  ├── develop
  │
  ├── feature/frontend
  ├── feature/backend
  ├── feature/blockchain
  ├── feature/threat-engine
  ├── feature/phishing
  └── feature/testing
```

`main` should contain stable versions.

Feature branches should be merged only after testing/review.

---

# 📊 Example End-to-End Scenario

A creator registers with CreatorXDR.

```text
1. Creator registers
        ↓
2. Identity is verified
        ↓
3. Verification credential is generated
        ↓
4. Credential proof is recorded on blockchain
        ↓
5. Creator registers original account
        ↓
6. Creator receives suspicious login
        ↓
7. New device is detected
        ↓
8. Multiple failed login attempts occur
        ↓
9. Threat engine calculates risk
        ↓
10. HIGH-risk alert generated
        ↓
11. Creator receives recommended actions
        ↓
12. Security event is stored in audit history
```

---

# 🧪 Example Dashboard

```text
┌──────────────────────────────────────────────┐
│                 CREATORXDR                   │
├──────────────────────────────────────────────┤
│                                              │
│ Creator: Example Creator                     │
│ Identity: ✓ VERIFIED                         │
│                                              │
│ SECURITY STATUS                              │
│                                              │
│              🟢 LOW RISK                     │
│                                              │
├──────────────────────────────────────────────┤
│ THREATS        ALERTS        DEVICES         │
│    2              1             3            │
├──────────────────────────────────────────────┤
│ RECENT ACTIVITY                              │
│                                              │
│ ✓ Known device login                        │
│ ⚠ Unknown device detected                   │
│ ✓ Blockchain verification                   │
│                                              │
├──────────────────────────────────────────────┤
│ QUICK ACTIONS                                │
│                                              │
│ [View Threats] [View Devices] [Audit Log]   │
│                                              │
└──────────────────────────────────────────────┘
```

---

# 📜 License

This project is intended for academic and research purposes.

The final repository should include an appropriate open-source license after reviewing the licenses of any third-party repositories, datasets, libraries, or models incorporated into the project.

Third-party code must retain its original license and attribution requirements.

---

# ⚠️ Disclaimer

CreatorXDR is an academic/prototype cybersecurity project.

It is not intended to provide guaranteed protection against real-world cyberattacks.

Threat scores and detection rules are prototype mechanisms and should not be interpreted as definitive proof that an account, URL, device, or individual is malicious.

Identity verification functionality should use appropriate authorized verification mechanisms in any real-world deployment.

Sensitive identity information should not be placed on public blockchains.

---

# 👥 Team

### CreatorXDR Development Team

| Member  | Role                              |
| ------- | --------------------------------- |
| Anusha  | System Architecture & Integration |
| Tanishq | Blockchain Development            |
| Aditi   | Cybersecurity & Threat Detection  |
| Sheetal | Backend & Database                |
| Shlok   | Frontend Development              |
| Ujwala  | Threat Intelligence & Testing     |

---

# ⭐ Project Vision

CreatorXDR aims to provide creators with a unified security layer that combines:

```text
          TRUST
            +
         IDENTITY
            +
        BLOCKCHAIN
            +
        MONITORING
            +
       THREAT DETECTION
            +
        RISK ANALYSIS
            +
          ALERTS
            +
       AUDITABILITY
```

### CreatorXDR

**Verify. Monitor. Detect. Respond. Protect.**
