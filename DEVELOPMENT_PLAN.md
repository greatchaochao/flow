# Development Plan: Cross-Border FX Payment Platform PoC

> **Stack:** Python + Streamlit + PostgreSQL  
> **Status:** Sandbox / Non-Production  
> **Target:** UK SME Market

---

##  Executive Summary

This document outlines the development approach for building a Proof of Concept (PoC) cross-border FX and payment automation platform. The PoC validates technical feasibility and product desirability for UK SMEs using sandbox-only integrations.

---

##  Technology Stack

### Core Technologies
- **Frontend:** Streamlit 1.30+
- **Backend:** Python 3.11+
- **Database:** PostgreSQL 15+
- **ORM:** SQLAlchemy 2.0+
- **API Integration:** httpx / requests
- **Authentication:** streamlit-authenticator or custom session management
- **Environment Management:** python-dotenv

### Development Tools
- **Version Control:** Git
- **Package Management:** Poetry or pip + requirements.txt
- **Code Quality:** Black, Flake8, mypy
- **Testing:** pytest, pytest-postgresql
- **Migration:** Alembic

---

##  Database Schema

### Tables

#### users
```sql
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    full_name VARCHAR(255),
    role VARCHAR(50) NOT NULL, -- 'admin', 'maker', 'approver'
    company_id INTEGER REFERENCES companies(id),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

#### companies
```sql
CREATE TABLE companies (
    id SERIAL PRIMARY KEY,
    company_name VARCHAR(255) NOT NULL,
    registered_country VARCHAR(2) NOT NULL, -- ISO 2-letter code
    industry_sector VARCHAR(100),
    fx_volume_band VARCHAR(50), -- 'small', 'medium', 'large'
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

#### beneficiaries
```sql
CREATE TABLE beneficiaries (
    id SERIAL PRIMARY KEY,
    company_id INTEGER NOT NULL REFERENCES companies(id),
    beneficiary_name VARCHAR(255) NOT NULL,
    beneficiary_type VARCHAR(50), -- 'individual', 'business'
    country VARCHAR(2) NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

#### beneficiary_bank_accounts
```sql
CREATE TABLE beneficiary_bank_accounts (
    id SERIAL PRIMARY KEY,
    beneficiary_id INTEGER NOT NULL REFERENCES beneficiaries(id),
    account_holder_name VARCHAR(255) NOT NULL,
    iban VARCHAR(34),
    swift_bic VARCHAR(11),
    bank_name VARCHAR(255),
    currency VARCHAR(3) NOT NULL,
    is_default BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

#### fx_quotes
```sql
CREATE TABLE fx_quotes (
    id SERIAL PRIMARY KEY,
    company_id INTEGER NOT NULL REFERENCES companies(id),
    quote_id VARCHAR(100) UNIQUE, -- External provider quote ID
    source_currency VARCHAR(3) NOT NULL,
    target_currency VARCHAR(3) NOT NULL,
    rate DECIMAL(18, 8) NOT NULL,
    markup_percentage DECIMAL(5, 4), -- e.g., 0.0050 for 0.5%
    final_rate DECIMAL(18, 8) NOT NULL,
    quote_expires_at TIMESTAMP NOT NULL,
    is_expired BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

#### payments
```sql
CREATE TABLE payments (
    id SERIAL PRIMARY KEY,
    company_id INTEGER NOT NULL REFERENCES companies(id),
    created_by_user_id INTEGER NOT NULL REFERENCES users(id),
    beneficiary_id INTEGER NOT NULL REFERENCES beneficiaries(id),
    beneficiary_bank_account_id INTEGER NOT NULL REFERENCES beneficiary_bank_accounts(id),
    fx_quote_id INTEGER REFERENCES fx_quotes(id),
    
    source_currency VARCHAR(3) NOT NULL,
    target_currency VARCHAR(3) NOT NULL,
    source_amount DECIMAL(18, 2),
    target_amount DECIMAL(18, 2),
    fx_rate DECIMAL(18, 8),
    fee_amount DECIMAL(18, 2),
    total_debit DECIMAL(18, 2),
    
    payment_reference VARCHAR(255),
    execution_date DATE,
    
    status VARCHAR(50) NOT NULL DEFAULT 'draft', 
    -- 'draft', 'pending_approval', 'approved', 'rejected', 
    -- 'submitted', 'processing', 'completed', 'failed'
    
    external_payment_id VARCHAR(100), -- Provider payment ID
    failure_reason TEXT,
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

#### payment_approvals
```sql
CREATE TABLE payment_approvals (
    id SERIAL PRIMARY KEY,
    payment_id INTEGER NOT NULL REFERENCES payments(id),
    approver_user_id INTEGER REFERENCES users(id),
    action VARCHAR(50) NOT NULL, -- 'submitted', 'approved', 'rejected'
    comments TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

#### audit_logs
```sql
CREATE TABLE audit_logs (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    entity_type VARCHAR(50) NOT NULL, -- 'payment', 'beneficiary', etc.
    entity_id INTEGER NOT NULL,
    action VARCHAR(50) NOT NULL, -- 'created', 'updated', 'deleted', etc.
    old_values JSONB,
    new_values JSONB,
    ip_address VARCHAR(45),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### Indexes
```sql
CREATE INDEX idx_payments_company_id ON payments(company_id);
CREATE INDEX idx_payments_status ON payments(status);
CREATE INDEX idx_payments_created_at ON payments(created_at);
CREATE INDEX idx_fx_quotes_expires_at ON fx_quotes(quote_expires_at);
CREATE INDEX idx_audit_logs_entity ON audit_logs(entity_type, entity_id);
```

---

##  Application Architecture

### Directory Structure
```
flow/
 .github/
    copilot-instructions.md
 app/
    __init__.py
    main.py                    # Streamlit entry point
    config.py                  # Configuration management
    database/
       __init__.py
       connection.py          # DB connection pool
       models.py              # SQLAlchemy models
       migrations/            # Alembic migrations
    services/
       __init__.py
       auth_service.py        # Authentication logic
       fx_service.py          # FX quote integration
       payment_service.py     # Payment logic
       beneficiary_service.py
       approval_service.py
       notification_service.py
    repositories/
       __init__.py
       user_repository.py
       payment_repository.py
       fx_repository.py
       audit_repository.py
    integrations/
       __init__.py
       fx_provider.py         # Mock/sandbox FX API
       payment_provider.py    # Mock/sandbox payment API
    utils/
       __init__.py
       validators.py          # IBAN/SWIFT validation
       formatters.py
       security.py            # Password hashing
    ui/
        __init__.py
        pages/
           1__Company_Profile.py
           2__Beneficiaries.py
           3__FX_Quotes.py
           4__Payments.py
           5__Approvals.py
           6__Reports.py
        components/
            auth.py
            forms.py
            tables.py
 tests/
    __init__.py
    conftest.py
    test_services/
    test_repositories/
    test_integrations/
 scripts/
    init_db.py                 # Database initialization
    seed_data.py               # Seed test data
 .env.example
 .gitignore
 requirements.txt
 pyproject.toml                 # Poetry config (optional)
 README.md
 DEVELOPMENT_PLAN.md
 docker-compose.yml             # PostgreSQL + optional pgAdmin
```

---

##  Development Phases

### Phase 1: Foundation (Week 1)
**Goal:** Set up core infrastructure

#### Tasks
- [ ] Initialize Git repository
- [ ] Set up Python virtual environment
- [ ] Configure PostgreSQL database (local or Docker)
- [ ] Create database schema and run initial migrations
- [ ] Implement database connection pooling
- [ ] Set up SQLAlchemy models
- [ ] Create configuration management (dev/prod environments)
- [ ] Implement basic Streamlit app structure
- [ ] Set up authentication (email + password)
- [ ] Create seed script for test users

**Deliverables:**
- Running PostgreSQL instance
- Basic Streamlit app with login page
- Database with schema in place
- Test users can log in

---

### Phase 2: User & Company Management (Week 1-2)
**Goal:** Basic user and company profile functionality

#### Tasks
- [ ] Implement user repository and service
- [ ] Create company profile page in Streamlit
- [ ] Add/edit company details form
- [ ] Implement role-based access control (Admin, Maker, Approver)
- [ ] Add session state management
- [ ] Create audit logging service
- [ ] Implement password hashing with bcrypt

**Deliverables:**
- Users can create/edit company profile
- Role-based navigation in Streamlit
- Basic audit trail

---

### Phase 3: Beneficiary Management (Week 2)
**Goal:** Add and manage payment beneficiaries

#### Tasks
- [ ] Implement beneficiary repository and service
- [ ] Create beneficiary list page
- [ ] Build add/edit beneficiary form
- [ ] Add bank account details (IBAN, SWIFT)
- [ ] Implement IBAN validation logic
- [ ] Implement SWIFT/BIC validation
- [ ] Add beneficiary search and filtering
- [ ] Enable/disable beneficiary functionality

**Deliverables:**
- Users can add/edit/disable beneficiaries
- Bank account validation working
- Beneficiary list with search

---

### Phase 4: FX Quote Integration (Week 2-3)
**Goal:** Fetch and display real-time FX quotes

#### Tasks
- [ ] Research and select FX sandbox API (e.g., CurrencyCloud, Wise sandbox)
- [ ] Implement FX provider integration
- [ ] Create FX quote service with markup logic
- [ ] Build FX quote request page
- [ ] Display quote with breakdown (rate, markup, expiry)
- [ ] Implement quote expiry countdown timer
- [ ] Store quotes in database
- [ ] Handle expired quotes gracefully

**Deliverables:**
- FX quote page showing live rates
- Quote expiry handling (60-120s)
- Stored quotes in database

---

### Phase 5: Payment Creation (Week 3)
**Goal:** Create payment instructions with FX

#### Tasks
- [ ] Implement payment repository and service
- [ ] Create payment creation form
- [ ] Integrate FX quote selection
- [ ] Calculate amounts (send vs receive logic)
- [ ] Add fee calculation
- [ ] Implement payment draft saving
- [ ] Create payment list page
- [ ] Add payment status filtering
- [ ] Implement "Submit for Approval" action

**Deliverables:**
- Payment creation workflow complete
- Payment list with status filters
- Payments move to "Pending Approval" state

---

### Phase 6: Maker-Checker Approval (Week 3-4)
**Goal:** Implement approval workflow

#### Tasks
- [ ] Implement approval service
- [ ] Create approvals dashboard page
- [ ] Build payment review interface
- [ ] Implement approve/reject actions
- [ ] Add approval comments
- [ ] Prevent maker from approving own payments
- [ ] Create payment approval history view
- [ ] Update audit logs for approvals

**Deliverables:**
- Approver can review pending payments
- Approve/reject workflow functional
- Audit trail for all approval actions

---

### Phase 7: Payment Execution (Week 4)
**Goal:** Submit payments to sandbox payment rails

#### Tasks
- [ ] Research and select payment sandbox API (e.g., Modulr, Railsbank sandbox)
- [ ] Implement payment provider integration
- [ ] Create payment submission logic
- [ ] Handle payment status webhooks (or polling)
- [ ] Update payment status in database
- [ ] Implement error handling for failed payments
- [ ] Create payment status tracking page
- [ ] Add payment detail view

**Deliverables:**
- Approved payments submitted to sandbox
- Payment status updates working
- Failed payment error handling

---

### Phase 8: Notifications (Week 4-5)
**Goal:** Notify users of key events

#### Tasks
- [ ] Implement notification service
- [ ] Add email configuration (SendGrid/SMTP/local)
- [ ] Create notification templates
- [ ] Send "Payment Pending Approval" emails
- [ ] Send "Payment Approved" emails
- [ ] Send "Payment Failed" emails
- [ ] Add in-app notification badge (optional)

**Deliverables:**
- Email notifications for key events
- Configurable notification settings

---

### Phase 9: Reporting & Dashboard (Week 5)
**Goal:** Basic reporting for demo purposes

#### Tasks
- [ ] Create dashboard page with key metrics
- [ ] Display total FX volume
- [ ] Show payment count by status
- [ ] Calculate simulated fee revenue
- [ ] Create payment history report
- [ ] Add date range filtering
- [ ] Export payment list to CSV (optional)
- [ ] Add basic charts (Plotly or Altair)

**Deliverables:**
- Dashboard with summary metrics
- Payment history with filters
- Basic visualizations

---

### Phase 10: Polish & Testing (Week 5-6)
**Goal:** Bug fixes, testing, and demo preparation

#### Tasks
- [ ] Write unit tests for services
- [ ] Write integration tests for repositories
- [ ] Test end-to-end user journey
- [ ] Fix critical bugs
- [ ] Improve UI/UX based on testing
- [ ] Add loading states and error messages
- [ ] Document setup and usage in README
- [ ] Prepare demo data and script
- [ ] Security review (basic)

**Deliverables:**
- Test coverage > 60%
- End-to-end demo working smoothly
- Documentation complete

---

##  Testing Strategy

### Unit Tests
- Service layer logic (FX calculation, approval rules)
- Validation functions (IBAN, SWIFT)
- Security utilities (password hashing)

### Integration Tests
- Database repository operations
- API integrations (with mocked responses)

### Manual Testing
- End-to-end user journey
- Role-based access control
- Error scenarios (expired quotes, failed payments)

### Test Data
- Seed script with:
  - 3 users (Admin, Maker, Approver)
  - 1 company profile
  - 5 beneficiaries
  - Sample payments at various stages

---

##  Security Considerations (PoC Level)

- Password hashing with bcrypt
- Session management with Streamlit
- SQL injection prevention via SQLAlchemy ORM
- Input validation for all forms
- HTTPS in deployment (even for PoC)
- Environment variables for secrets
- No hardcoded credentials

**Note:** Full production security out of scope for PoC.

---

##  Deployment Approach

### Local Development
```bash
# PostgreSQL via Docker
docker-compose up -d

# Python environment
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Database migrations
alembic upgrade head

# Seed data
python scripts/seed_data.py

# Run Streamlit
streamlit run main.py
```

### PoC Deployment Options
1. **Streamlit Cloud** (easiest)
   - Free tier for prototypes
   - Connect to external PostgreSQL (e.g., Neon, Supabase)

2. **Railway / Render**
   - Simple Python + PostgreSQL deployment
   - Free tier available

3. **Heroku**
   - Mature platform
   - Easy PostgreSQL addon

**Recommendation:** Streamlit Cloud + Neon PostgreSQL for zero-cost PoC.

---

##  Success Metrics

### Technical
- [ ] End-to-end payment flow completes successfully
- [ ] FX quotes refresh within 2-3 seconds
- [ ] Approval workflow prevents maker self-approval
- [ ] Payment status updates within 5 seconds of sandbox response

### User Experience
- [ ] Clear visibility of FX rates and fees
- [ ] Intuitive navigation between pages
- [ ] Meaningful error messages
- [ ] Audit trail is human-readable

### Business Validation
- [ ] Demonstrates value over manual banking
- [ ] Shows transparency in FX pricing
- [ ] Validates maker-checker control model

---

##  Key Risks & Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| Sandbox API unreliable | High | Implement fallback mock responses |
| Streamlit session state issues | Medium | Use st.session_state carefully; test edge cases |
| Database schema changes | Medium | Use Alembic migrations from day 1 |
| Scope creep | High | Strictly adhere to PoC scope; defer nice-to-haves |
| FX quote expiry handling | Medium | Clear UI messaging; refresh mechanism |

---

##  Documentation Requirements

1. **README.md** - Setup instructions, architecture overview
2. **API_INTEGRATION.md** - Sandbox API configuration
3. **DATABASE.md** - Schema explanation and migrations
4. **DEMO_SCRIPT.md** - Step-by-step demo walkthrough
5. **LIMITATIONS.md** - What's NOT in scope

---

## ⏱ Timeline Summary

| Phase | Duration | Key Deliverable |
|-------|----------|----------------|
| 1. Foundation | Week 1 | Running app + DB |
| 2. User Management | Week 1-2 | User roles working |
| 3. Beneficiaries | Week 2 | Beneficiary CRUD |
| 4. FX Quotes | Week 2-3 | Live FX quotes |
| 5. Payment Creation | Week 3 | Payment forms |
| 6. Approvals | Week 3-4 | Maker-checker flow |
| 7. Payment Execution | Week 4 | Sandbox integration |
| 8. Notifications | Week 4-5 | Email alerts |
| 9. Reporting | Week 5 | Dashboard |
| 10. Polish & Testing | Week 5-6 | Demo-ready |

**Total Estimated Duration:** 5-6 weeks (1 developer, full-time)

---

##  Next Steps

1. Review and approve this plan
2. Set up development environment
3. Create GitHub/GitLab repository
4. Begin Phase 1: Foundation
5. Schedule weekly demo checkpoints

---

##  Stakeholder Communication

- **Weekly demos** of completed phases
- **Daily standups** (if team > 1)
- **Blocker escalation** within 24 hours
- **Scope change requests** via formal review

---

**Last Updated:** 11 January 2026  
**Document Owner:** Engineering Lead  
**Status:** Draft - Pending Approval
