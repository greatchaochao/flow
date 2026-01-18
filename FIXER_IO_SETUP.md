# Fixer.io Integration Setup

## Overview

This application integrates with [Fixer.io](https://fixer.io) for real delayed FX rates. The integration automatically falls back to a mock provider if no API key is configured, making it easy to develop and test without requiring an API key.

---

## Getting Your Fixer.io API Key

### Free Tier (Recommended for PoC)
- **Requests:** 100 requests/month
- **Data Delay:** ~60 minutes
- **Currencies:** 170+ supported
- **Cost:** FREE

### Steps:

1. Visit [https://fixer.io/product](https://fixer.io/product)
2. Click on "Get Free API Key" or select the Free plan
3. Sign up with your email
4. Verify your email address
5. Access your dashboard to find your API key
6. Copy your API access key

---

## Configuration

### 1. Update `.env` File

Open the `.env` file in the project root and add your Fixer.io API key:

```bash
# FX Provider (Fixer.io)
# Get your free API key at https://fixer.io/product (100 requests/month free)
# Leave FX_PROVIDER_API_KEY empty to use mock provider for testing
FX_PROVIDER_API_KEY=your_actual_api_key_here
FX_PROVIDER_API_URL=http://data.fixer.io/api
FX_MARKUP_PERCENTAGE=0.005
```

**Important:** Replace `your_actual_api_key_here` with your actual API key from Fixer.io.

### 2. Restart Streamlit

After updating the `.env` file, restart your Streamlit application:

```bash
# Stop the current Streamlit session (Ctrl+C)
# Then restart:
streamlit run main.py
```

---

## How It Works

### Provider Selection

The application automatically selects the FX provider based on configuration:

```python
# If FX_PROVIDER_API_KEY is set → Use Fixer.io
# If FX_PROVIDER_API_KEY is empty → Use Mock provider
```

### Rate Caching

To minimize API calls and stay within the free tier limit:

- **Rate Cache Duration:** 30 minutes per currency pair (since free tier has ~60 min delay)
- **Currency List Cache:** 24 hours (currencies rarely change)
- **Fallback Strategy:** Uses cached data or common currencies when rate limited
- **Request Limit:** 100/month (free tier)

### Provider Indicator

The FX Quotes page displays which provider is active:

- **Mock Provider:** Blue info banner with setup instructions
- **Fixer.io:** Green success banner confirming real rates

---

## API Endpoints Used

### Latest Rates
```
GET http://data.fixer.io/api/latest
Parameters:
  - access_key: Your API key
  - base: Source currency (e.g., GBP)
  - symbols: Target currency (e.g., EUR)
```

### Supported Currencies
```
GET http://data.fixer.io/api/symbols
Parameters:
  - access_key: Your API key
```

---

## Rate Accuracy

### Free Tier (Delayed Rates)
- **Update Frequency:** Every ~60 minutes
- **Base Currency:** EUR only (cross-rates calculated automatically)
- **Rate Limiting:** Can experience rate limits during testing
- **Use Case:** PoC demos, testing, development
- **NOT suitable for:** Production, real-time trading

### Paid Tiers (Real-Time Rates)
- **Update Frequency:** Every few seconds
- **Use Case:** Production applications
- **Pricing:** Starting at $10/month for 1,000 requests

---

## Monitoring API Usage

### Check Your Usage
1. Log in to [Fixer.io Dashboard](https://fixer.io/dashboard)
2. View current month's usage
3. Monitor remaining requests

### Usage Tips
- Cache is enabled (5 min) to reduce API calls
- Each quote request = 1 API call (unless cached)
- Consider upgrading if you exceed 100 requests/month

---

## Error Handling

The application handles common errors gracefully:

### No API Key Configured
- **Behavior:** Falls back to Mock provider
- **User Message:** "Using Mock FX Provider for testing"

### Invalid API Key
- **Behavior:** Falls back to Mock provider
- **User Message:** Shows error in console, continues with mock data

### API Rate Limit Exceeded
- **Behavior:** Returns cached rates if available
- **User Message:** Error shown in console

### Network Errors
- **Behavior:** Returns None, graceful degradation
- **User Message:** "Unable to fetch FX quote. Please try again."

---

## Comparison: Mock vs Fixer.io

| Feature | Mock Provider | Fixer.io |
|---------|--------------|----------|
| **Cost** | Free | Free (100 req/month) |
| **Rate Accuracy** | ±0.5% fluctuation | Real market rates (~60 min delay) |
| **Currencies** | 13 (common pairs) | 170+ |
| **Update Frequency** | Every request | ~60 minutes (free tier) |
| **Rate Limits** | None | 100 requests/month |
| **Use Case** | Testing, development | Demo, PoC validation |

---

## Troubleshooting

### Issue: "Using Mock FX Provider" message persists

**Solution:**
1. Verify API key is correctly set in `.env`
2. Check for extra spaces or quotes around the key
3. Ensure `.env` file is in project root
4. Restart Streamlit (`Ctrl+C` then `streamlit run main.py`)

### Issue: API calls not working

**Solution:**
1. Check internet connection
2. Verify API key at [Fixer.io Dashboard](https://fixer.io/dashboard)
3. Check console for error messages
4. Ensure you haven't exceeded rate limits (100 req/month)

### Issue: Rates seem outdated

**Solution:**
- This is expected with free tier (~60 min delay)
- Consider upgrading to a paid plan for real-time rates
- For PoC purposes, delayed rates are sufficient

---

## Upgrading to Paid Plan

If you need real-time rates or more requests:

1. Visit [Fixer.io Pricing](https://fixer.io/product)
2. Select a paid plan:
   - **Basic:** $10/month, 1,000 requests
   - **Professional:** $50/month, 50,000 requests
   - **Professional Plus:** $150/month, 200,000 requests
3. Update your subscription
4. No code changes needed! Just keep using the same API key

---

## Security Best Practices

### Never Commit API Keys
- API keys are in `.env` (which is in `.gitignore`)
- Never commit `.env` to version control
- Use `.env.example` as a template for team members

### Rotate Keys Regularly
- Generate new API keys periodically
- Revoke old keys in Fixer.io dashboard
- Update `.env` with new key

### Environment-Specific Keys
- Use different API keys for dev/staging/production
- Track usage per environment separately

---

## Alternative Providers

If Fixer.io doesn't meet your needs, consider:

1. **ExchangeRate-API** - Free tier: 1,500 req/month
2. **Frankfurter.app** - Free, open-source, ECB data
3. **CurrencyLayer** - Free tier: 100 req/month
4. **Open Exchange Rates** - Free tier: 1,000 req/month

To switch providers, modify `app/integrations/fx_provider.py` to add a new provider class.

---

## Questions?

For Fixer.io support:
- Documentation: [https://fixer.io/documentation](https://fixer.io/documentation)
- Support: contact@fixer.io

For this integration:
- Check `app/integrations/fx_provider.py` for implementation details
- Review `app/services/fx_service.py` for provider selection logic

---

**Last Updated:** 17 January 2026
