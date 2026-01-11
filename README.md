# Cross-Border FX Digital Payment Automation Platform (PoC)

> **UK SME Market | Sandbox Only**

**Status:** Pre-regulatory, non-production prototype  
**Purpose:** Validate technical feasibility & product desirability  
**Audience:** Engineering, Architecture, Product  
**Environment:** Sandbox / Test only (no real customer funds)

---

## 🚀 Overview

This Proof of Concept (PoC) validates the core workflow for a **cross-border FX and payment automation platform** targeting UK SMEs.

The PoC focuses on:
- FX quote transparency
- Maker–checker payment approvals
- End-to-end payment lifecycle (sandbox)
- Clear, auditable workflows

⚠️ **This repository is not production-ready and must not be used with real funds.**

---

## 🎯 PoC Objectives

### What We Are Proving

#### Technical Feasibility
- Integration with FX quote APIs (sandbox)
- Integration with payment APIs (sandbox)
- Real-time FX pricing and quote expiry handling

#### Workflow Validation
- SME-friendly payment creation flow
- Maker–checker approval model
- Status tracking and auditability

#### Value Proposition
- Transparency of FX pricing and fees
- Automation vs manual banking processes
- Clear UI communication of risk and status

---

### Explicitly Out of Scope

The following are **intentionally excluded**:

- ❌ Production reliability or SLAs  
- ❌ Real funds movement  
- ❌ Full compliance / regulatory framework  
- ❌ Full accounting or ERP integrations  
- ❌ Scalability or performance tuning  

---

## 🔁 End-to-End User Journey

1. User logs in  
2. User creates a mock SME profile  
3. User adds a beneficiary  
4. User requests an FX quote  
5. User creates a payment instruction  
6. Approver reviews and approves payment  
7. System submits payment to sandbox rails  
8. Payment status updates are displayed  
9. User views basic FX & payment reporting  

---

## 🧩 Functional Scope

### Authentication & Roles
- Email + password login
- Session-based authentication
- Roles: Admin, Maker, Approver
- Optional MFA (nice-to-have)

---

### SME Profile (Mocked)
- Company name
- Registered country
- Industry sector
- FX volume band (self-declared)

No KYB / onboarding checks. Minimal personal data only.

---

### Beneficiary Management
- Add / edit / disable beneficiaries
- IBAN and BIC/SWIFT syntax validation

---

### FX Quote Engine
- Real-time sandbox FX quotes
- Configurable markup
- Quote expiry (60–120 seconds)

---

### Payment Creation
- Source currency
- Beneficiary
- Amount (send or receive)
- Execution date
- Automatic FX & fee calculation

States: Draft → Pending Approval

---

### Maker–Checker Approval
- Submit / approve / reject
- Comments supported
- Full audit trail
- Maker cannot approve own payment

---

### Payment Execution (Sandbox)
- Submit to payment API sandbox
- Status tracking: Submitted → Processing → Completed / Failed
- No real funds movement

---

### Reporting & Logs
- Payment list with filters
- FX volume, payment count, simulated fees

---

### Notifications
- Payment pending approval
- Payment approved
- Payment failed

---

## ⚙️ Non-Functional Requirements

- Business-hours availability
- < 2–3s page load
- TLS + hashed passwords
- UK / EU data residency preferred
- Centralised basic logging
- UK GDPR-aware

---

## 🗄️ Minimal Data Model

- users
- companies
- beneficiaries
- beneficiary_bank_accounts
- fx_quotes
- payments
- payment_approvals
- audit_logs

---

## 🏗️ High-Level Architecture

- Web frontend (SPA)
- Backend API
- FX provider (sandbox)
- Payment provider (sandbox)
- Database
- Notification service

---

## ✅ Success Criteria

- End-to-end workflow completes
- FX quotes retrieved reliably
- Approval controls reflect SME reality
- Clear user perception of transparency & control

---

## ⚠️ Disclaimer

This repository represents a **non-production Proof of Concept** and must not be used with real customers or real funds.
