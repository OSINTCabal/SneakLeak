# SneakLeak API Setup Guide

Complete guide to setting up all API keys for SneakLeak.

## Required APIs

### 1. OSINTCabal Breach Bot (Telegram) ⭐ RECOMMENDED

**Why use this?**
- This bot has many mirrors but this is the most powerful key of the bunch. Worth the money!

**Setup Steps:**
1. Visit: https://t.me/Cabal_Breach_bot?start=Et18TP4
2. Start the bot in Telegram
3. Follow registration instructions
4. Get your API key from the bot
5. Add to `sneakleak.py`:
   ```python
   'breach_bot': {
       'key': 'YOUR_API_KEY_FROM_TELEGRAM_BOT',
   ```

**Supported Queries:**
- ✅ Email addresses
- ✅ Phone numbers
- ✅ Domains
- ✅ Usernames
- ✅ Full names
- ✅ IP addresses

---

### 2. Breach Directory

**Setup:**
1. Visit: https://breachdirectory.com/
2. Create account
3. Navigate to API section
4. Copy your API key
5. Add to `sneakleak.py`:
   ```python
   'breach_directory': {
       'key': 'YOUR_BREACH_DIRECTORY_KEY',
   ```

**Free Tier:** Yes
**Supports:** email, domain, username, IP, name

---

### 3. Have I Been Pwned (HIBP)

**Setup:**
1. Visit: https://haveibeenpwned.com/API/Key
2. Purchase API key ($3.50/month)
3. Receive key via email
4. Add to `sneakleak.py`:
   ```python
   'hibp': {
       'key': 'YOUR_HIBP_API_KEY',
   ```

**Cost:** $3.50/month
**Supports:** Email only
**Note:** Highly reputable, maintained by Troy Hunt

---

### 4. LeakInsight (via RapidAPI)

**Setup:**
1. Visit: https://rapidapi.com/
2. Create account
3. Search for "LeakInsight API"
4. Subscribe to API
5. Copy your RapidAPI key
6. Add to `sneakleak.py`:
   ```python
   'leakinsight': {
       'key': 'YOUR_RAPIDAPI_KEY',
   ```

**Free Tier:** Limited
**Supports:** email, phone, domain, username, name, IP, hash, password

---

## Configuration Example

After getting all keys, your `API_CONFIGS` section should look like:

```python
API_CONFIGS = {
    'breach_bot': {
        'name': 'Breach Bot Telegram',
        'url': 'https://leakosintapi.com/',
        'key': 'abc123xyz789...',  # From OSINTCabal bot
        'supports': ['email', 'phone', 'domain', 'username', 'name', 'ip'],
        'has_credits': False
    },
    'breach_directory': {
        'name': 'Breach Directory',
        'url': 'https://BreachDirectory.com/api_usage',
        'key': 'def456uvw...',  # From Breach Directory
        'supports': ['email', 'domain', 'username', 'ip', 'name'],
        'has_credits': False
    },
    'hibp': {
        'name': 'Have I Been Pwned',
        'url': 'https://haveibeenpwned.com/api/v3',
        'key': 'ghi789rst...',  # From HIBP
        'supports': ['email'],
        'has_credits': True
    },
    'leakinsight': {
        'name': 'LeakInsight API',
        'url': 'https://leakinsight-api.p.rapidapi.com/general/',
        'key': 'jkl012mno...',  # From RapidAPI
        'host': 'leakinsight-api.p.rapidapi.com',
        'supports': ['email', 'phone', 'domain', 'username', 'name', 'ip', 'hash', 'password'],
        'has_credits': False
    }
}
```

## Testing Your Setup

Run a test search:
```bash
python sneakleak.py test@example.com
```

Each API will be queried and you'll see which ones are configured correctly.

## Troubleshooting

### "API key not configured" error
- Make sure you replaced `YOUR_XXXX_API_KEY_HERE` with your actual key
- Check for typos in the key

### "Connection failed" error
- Check your internet connection
- Verify the API service is not down
- Check if you've exceeded rate limits

### "HTTP 401/403" error
- Invalid API key
- API key expired
- Need to renew subscription

## Cost Summary

| API | Cost | Free Tier |
|-----|------|-----------|
| OSINTCabal Breach Bot | Varies | Check with bot |
| Breach Directory | Free | Yes |
| HIBP | $3.50/month | No |
| LeakInsight | Varies | Limited |

**Minimum to get started:** Just OSINTCabal Breach Bot + Breach Directory (both have free options)

## Support

- **OSINTCabal Breach Bot**: Contact through Telegram bot
- **Breach Directory**: Check their website
- **HIBP**: https://haveibeenpwned.com/
- **LeakInsight**: RapidAPI support
