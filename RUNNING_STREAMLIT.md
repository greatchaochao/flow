# Running the Streamlit Application

##  Quick Start

### 1. Install Dependencies

```bash
# Make sure you're in the project root directory
cd /Users/greatchaochao/flow

# Install required packages
pip install -r requirements.txt
```

### 2. Run the Application

```bash
# Start the Streamlit server (from project root)
PYTHONPATH=. streamlit run app/main.py
```

The application will open automatically in your browser at `http://localhost:8501`

---

##  Access from Other Devices

### Local Network Access

To allow other developers to access the app on your local network:

```bash
# Run with network access enabled
PYTHONPATH=. streamlit run app/main.py --server.address 0.0.0.0
```

Then share your local IP address (e.g., `http://192.168.1.100:8501`)

### Find Your IP Address

**macOS:**
```bash
ipconfig getifaddr en0
```

**Or check System Preferences → Network**

---

##  Demo Credentials

The UI includes mock authentication. Use these credentials to log in:

| Role | Email | Password |
|------|-------|----------|
| **Admin** | admin@uksmb.com | admin123 |
| **Maker** | maker@uksmb.com | maker123 |
| **Approver** | approver@uksmb.com | approver123 |

---

##  UI Features Implemented

###  Completed Pages

1. ** Home / Dashboard**
   - Login functionality
   - Role-based dashboard
   - Key metrics overview
   - Recent activity feed

2. ** Company Profile**
   - Company information management
   - User management (Admin only)
   - Role-based permissions

3. ** Beneficiaries**
   - Beneficiary list with filters
   - Add/edit beneficiary forms
   - Bank account details
   - IBAN/SWIFT validation hints
   - Statistics and insights

4. ** FX Quotes**
   - Real-time quote request form
   - Mock quote generation
   - Rate breakdown transparency
   - Quote expiry countdown (120s)
   - Recent quotes history

5. ** Payments**
   - Payment list with filters
   - Create payment workflow
   - Payment details view
   - FX quote integration
   - Cost breakdown

6. ** Approvals**
   - Pending approvals queue
   - Detailed payment review
   - Approve/reject functionality
   - Approval checklist
   - Maker-checker enforcement
   - Audit trail

7. ** Reports & Analytics**
   - Dashboard with metrics
   - Payment volume trends
   - FX analysis and charts
   - Beneficiary reports
   - Export functionality (mock)

---

##  Role-Based Features

### Admin
- Full access to all pages
- Manage company profile
- Manage users
- Create and approve payments
- View all reports

### Maker
- Create payments
- Manage beneficiaries
- Request FX quotes
- View own payments
- Cannot approve payments

### Approver
- Approve/reject payments
- View payment details
- Cannot create payments
- Cannot approve own payments (maker-checker)

---

##  Configuration

### Streamlit Configuration

The app uses `.streamlit/config.toml` for theming and settings:

```toml
[theme]
primaryColor = "#0066cc"
backgroundColor = "#ffffff"
secondaryBackgroundColor = "#f0f2f6"
textColor = "#262730"
font = "sans serif"

[server]
port = 8501
enableCORS = false
```

### Environment Variables

Copy `.env.example` to `.env` for configuration (not required for UI-only demo):

```bash
cp .env.example .env
```

---

##  Notes

- **No Backend**: The UI is fully functional but uses mock data
- **No Database**: No PostgreSQL connection required for UI demo
- **Mock Authentication**: Login validation is client-side only
- **Session State**: User sessions are managed by Streamlit
- **Auto-refresh**: Some pages (like FX Quotes) auto-refresh for countdown timers

---

##  Troubleshooting

### Port Already in Use

If port 8501 is already in use:

```bash
PYTHONPATH=. streamlit run app/main.py --server.port 8502
```

### Dependencies Issues

Make sure you have Python 3.11+ installed:

```bash
python --version
```

Reinstall dependencies if needed:

```bash
pip install --upgrade -r requirements.txt
```

### Can't Access from Other Devices

1. Check firewall settings
2. Ensure you're using `--server.address 0.0.0.0`
3. Verify all devices are on the same network
4. Try the IP address instead of hostname

---

##  Next Steps

After UI review:

1. **Phase 2**: Implement backend services
2. **Phase 3**: Connect to PostgreSQL database
3. **Phase 4**: Integrate real authentication
4. **Phase 5**: Add FX provider API integration
5. **Phase 6**: Implement payment provider integration

---

##  Support

For issues or questions:
- Check the browser console for errors
- Review Streamlit logs in terminal
- Ensure all dependencies are installed correctly
