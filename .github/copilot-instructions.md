# Copilot Instructions

## 📚 Required Context

**Always reference these files when assisting with this project:**
- [README.md](../README.md) - PoC objectives, functional scope, and project overview
- [DEVELOPMENT_PLAN.md](../DEVELOPMENT_PLAN.md) - Complete development roadmap, database schema, architecture, and implementation details

These files contain critical context about the project's goals, architecture, timeline, and technical decisions. Review them before making suggestions or implementing features.

---

## 🎯 Project Overview

**Cross-Border FX Digital Payment Automation Platform (PoC)**

- **Target Market:** UK SMEs
- **Stack:** Python 3.11+ | Streamlit 1.30+ | PostgreSQL 15+
- **Status:** Pre-regulatory, sandbox-only prototype
- **Purpose:** Validate technical feasibility and product desirability

---

## 🏗️ Key Architecture Principles

### Technology Stack
- **Frontend:** Streamlit for rapid prototyping
- **Backend:** Python with SQLAlchemy ORM
- **Database:** PostgreSQL with Alembic migrations
- **Integrations:** Sandbox APIs only (FX + Payment providers)

### Directory Structure
```
flow/
├── app/
│   ├── main.py                    # Streamlit entry point
│   ├── config.py                  # Configuration management
│   ├── database/                  # Models, connection, migrations
│   ├── services/                  # Business logic layer
│   ├── repositories/              # Data access layer
│   ├── integrations/              # External API wrappers
│   ├── utils/                     # Validators, formatters, security
│   └── ui/                        # Streamlit pages & components
├── tests/                         # pytest test suite
├── scripts/                       # DB initialization & seeding
└── .env                          # Environment variables (not in git)
```

---

## 🎨 Code Style Guidelines

### Python
- **Formatter:** Black (line length 88)
- **Linter:** Flake8
- **Type Hints:** Use mypy for static type checking
- **Naming:**
  - Classes: `PascalCase`
  - Functions/variables: `snake_case`
  - Constants: `UPPER_SNAKE_CASE`
  - Private methods: `_leading_underscore`

### SQLAlchemy Models
- Use declarative base
- Include `__tablename__` explicitly
- Add `__repr__` for debugging
- Use type hints with SQLAlchemy 2.0 style

### Streamlit Pages
- Numbered prefix for navigation order: `1_🏢_Company_Profile.py`
- Use `st.session_state` for state management
- Implement proper error handling with `st.error()`
- Add loading states with `st.spinner()`

---

## 🔒 Security Best Practices

### Authentication
- Hash passwords with bcrypt (min 12 rounds)
- Use session-based authentication via `st.session_state`
- Implement RBAC: Admin, Maker, Approver roles
- No hardcoded credentials (use environment variables)

### Database
- Use SQLAlchemy ORM to prevent SQL injection
- Validate all user inputs
- Sanitize data before storage
- Use prepared statements

### API Integrations
- Store API keys in environment variables
- Use HTTPS for all external calls
- Implement retry logic with exponential backoff
- Log API errors without exposing secrets

---

## 📊 Database Guidelines

### Schema Design
- Follow the schema defined in [DEVELOPMENT_PLAN.md](../DEVELOPMENT_PLAN.md)
- Use Alembic for all schema changes
- Add indexes for frequently queried columns
- Use JSONB for flexible metadata storage

### Migrations
```bash
# Create a new migration
alembic revision --autogenerate -m "Description"

# Apply migrations
alembic upgrade head

# Rollback
alembic downgrade -1
```

### Naming Conventions
- Tables: plural lowercase with underscores (`beneficiary_bank_accounts`)
- Columns: lowercase with underscores (`created_by_user_id`)
- Indexes: `idx_table_column` pattern
- Foreign keys: `table_id` pattern

---

## 🧪 Testing Standards

### Test Coverage
- Target: >60% for PoC
- Focus on services and repositories
- Mock external API calls
- Use pytest fixtures for database setup

### Test Structure
```python
def test_function_name_should_expected_behavior():
    # Arrange
    setup_data()
    
    # Act
    result = function_under_test()
    
    # Assert
    assert result == expected_value
```

### Running Tests
```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app --cov-report=html

# Run specific test file
pytest tests/test_services/test_payment_service.py
```

---

## 🚀 Development Workflow

### Before Starting Work
1. Review [DEVELOPMENT_PLAN.md](../DEVELOPMENT_PLAN.md) for current phase
2. Pull latest changes from main branch
3. Create feature branch: `feature/description` or `fix/bug-description`
4. Check for open issues or blockers

### During Development
1. Follow the phase tasks in DEVELOPMENT_PLAN.md
2. Write tests alongside implementation
3. Run linters: `black app/ && flake8 app/`
4. Test locally before committing
5. Write clear, descriptive commit messages

### Before Committing
```bash
# Format code
black app/ tests/

# Check linting
flake8 app/ tests/

# Run tests
pytest

# Type checking
mypy app/
```

---

## 🎯 PoC Scope Reminders

### In Scope ✅
- Sandbox-only integrations
- Basic maker-checker workflow
- FX quote transparency
- Payment lifecycle tracking
- Minimal audit logging
- Email notifications (basic)

### Out of Scope ❌
- Production-grade reliability
- Real funds movement
- Full regulatory compliance (AML/KYC)
- ERP/accounting integrations
- Performance optimization
- Advanced monitoring/alerting
- Multi-tenancy

---

## 💡 Common Patterns

### Service Layer Pattern
```python
class PaymentService:
    def __init__(self, payment_repo: PaymentRepository):
        self.payment_repo = payment_repo
    
    def create_payment(self, data: dict) -> Payment:
        # Validation
        # Business logic
        # Repository call
        return self.payment_repo.create(data)
```

### Repository Pattern
```python
class PaymentRepository:
    def __init__(self, session: Session):
        self.session = session
    
    def get_by_id(self, payment_id: int) -> Payment:
        return self.session.query(Payment).filter_by(id=payment_id).first()
```

### Streamlit Page Structure
```python
import streamlit as st
from app.services import PaymentService

st.set_page_config(page_title="Payments", page_icon="💰")

# Authentication check
if 'user_id' not in st.session_state:
    st.error("Please log in")
    st.stop()

st.title("💰 Payments")

# Page logic here
```

---

## 🐛 Error Handling

### User-Facing Errors
- Use `st.error()` for validation failures
- Use `st.warning()` for non-critical issues
- Use `st.success()` for confirmations
- Provide clear, actionable error messages

### Backend Errors
- Log all exceptions with context
- Use try-except blocks for external API calls
- Store failure reasons in database
- Never expose internal errors to users

### Example
```python
try:
    result = fx_provider.get_quote(from_currency, to_currency, amount)
except ExternalAPIError as e:
    logger.error(f"FX API error: {e}")
    st.error("Unable to fetch FX quote. Please try again.")
    return None
```

---

## 📝 Documentation Requirements

### Code Documentation
- Docstrings for all public functions/classes
- Type hints for function parameters and returns
- Inline comments for complex logic only

### Docstring Format
```python
def calculate_fx_amount(
    source_amount: Decimal,
    fx_rate: Decimal,
    markup: Decimal
) -> Decimal:
    """
    Calculate target amount after applying FX rate and markup.
    
    Args:
        source_amount: Amount in source currency
        fx_rate: Base exchange rate
        markup: Markup percentage (e.g., 0.005 for 0.5%)
    
    Returns:
        Target amount in destination currency
    """
    final_rate = fx_rate * (1 + markup)
    return source_amount * final_rate
```

---

## 🔄 State Management (Streamlit)

### Session State Keys
- `user_id`: Logged-in user ID
- `user_role`: User's role (admin, maker, approver)
- `company_id`: Current company ID
- `current_page`: Active page name
- `selected_payment_id`: For payment detail views

### Best Practices
- Initialize session state at app start
- Use getter/setter functions for complex state
- Clear sensitive data on logout
- Avoid storing large objects in session state

---

## 🎬 Demo Preparation

### Seed Data Requirements
- 3 users (1 per role)
- 1 company profile
- 5-10 beneficiaries with bank accounts
- Sample FX quotes (various currency pairs)
- Sample payments at different stages
- Approval history records

### Demo Flow
Follow the end-to-end journey in [README.md](../README.md):
1. Login as Maker
2. View/edit company profile
3. Add beneficiary
4. Request FX quote
5. Create payment
6. Submit for approval
7. Login as Approver
8. Review and approve payment
9. View payment status
10. Check reports/dashboard

---

## ⚠️ Important Reminders

1. **Always reference README.md and DEVELOPMENT_PLAN.md** for project context
2. **This is a PoC** - prioritize rapid iteration over perfection
3. **Sandbox only** - no real customer data or funds
4. **Security basics** - even in PoC, protect credentials and validate inputs
5. **Follow the phases** - stick to DEVELOPMENT_PLAN.md sequence
6. **Test as you go** - easier than fixing everything at the end
7. **Document decisions** - especially API choices and workarounds

---

## 📞 Getting Help

- Check DEVELOPMENT_PLAN.md for technical decisions
- Check README.md for scope questions
- Review existing code for patterns
- Ask specific questions with context

---

**Last Updated:** 11 January 2026
