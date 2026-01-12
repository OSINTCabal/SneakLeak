# SneakLeak

A credential breach and data leak detection tool for professional investigators and security researchers.

## Description

SneakLeak checks multiple breach databases to identify compromised credentials and data leaks. It helps investigators determine if email addresses, usernames, or passwords have been exposed in known data breaches.

## Features

- **Multi-source breach aggregation** - Search 4+ databases simultaneously
- **OSINTCabal Breach Bot integration** - Access comprehensive Telegram-based breach data
- Automatic query type detection (email, username, phone, etc.)
- Smart deduplication across APIs
- Dynamic field display (shows ALL available data)
- Password breach checking with k-anonymity
- JSON export for further analysis
- Beautiful ASCII art interface
- Comprehensive result formatting

## Sources/APIs

This tool integrates with the following breach databases:

1. **OSINTCabal Breach Bot (Telegram)** - Comprehensive breach search via Telegram
   - **Sign up required**: https://t.me/Cabal_Breach_bot?start=Et18TP4
   - Access via Telegram bot interface
   - API endpoint: https://leakosintapi.com/
   - Supports: email, phone, domain, username, name, IP
   - Note: You must register through the Telegram bot to get API access

2. **Breach Directory** - Public breach database
   - API Documentation: https://breachdirectory.com/
   - Sign up: https://breachdirectory.com/
   - Supports: email, domain, username, IP, name
   - Free tier available

3. **Have I Been Pwned (HIBP)** - Email breach database
   - API Documentation: https://haveibeenpwned.com/API/v3
   - Get API Key: https://haveibeenpwned.com/API/Key
   - Paid API ($3.50/month)
   - Supports: email only

4. **Have I Been Pwned - Pwned Passwords** - Password breach checking
   - API Documentation: https://haveibeenpwned.com/API/v3#PwnedPasswords
   - No API key required (uses k-anonymity)
   - Free

5. **LeakInsight (via RapidAPI)** - Multi-source breach aggregator
   - API Documentation: https://rapidapi.com/
   - Sign up: https://rapidapi.com/
   - Supports: email, phone, domain, username, name, IP, hash, password
   - Paid service with free tier

## Installation

### Prerequisites

- Python 3.7 or higher
- pip package manager

### Setup

1. Clone the repository:
```bash
git clone https://github.com/yourusername/sneakleak.git
cd sneakleak
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Configure API keys:

Edit `sneakleak.py` and replace the placeholder values with your actual API keys:

```python
'breach_bot': {
    'key': 'YOUR_BREACH_BOT_API_KEY_HERE',  # Get from OSINTCabal Breach Bot
```

**Getting API Keys:**

- **OSINTCabal Breach Bot**: Visit https://t.me/Cabal_Breach_bot?start=Et18TP4 and register through Telegram
- **Breach Directory**: Sign up at https://breachdirectory.com/
- **HIBP**: Purchase API key at https://haveibeenpwned.com/API/Key ($3.50/month)
- **LeakInsight**: Sign up at https://rapidapi.com/ and subscribe to LeakInsight API

## Usage

### Basic Usage

Check an email across all databases:
```bash
python sneakleak.py user@example.com
```

### Check Specific Sources

Only check Have I Been Pwned:
```bash
python sneakleak.py user@example.com -c hibp
```

### Password Checking

Check if a password has been compromised:
```bash
python sneakleak.py user@example.com -c password -p "MyPassword123"
```

**Note**: Password checking uses k-anonymity and never sends your full password to the API.

### Save Results

Output results to JSON file:
```bash
python sneakleak.py user@example.com -o results.json
```

### Command-Line Options

```
usage: sneakleak.py [-h] [-c {hibp,dehashed,leakcheck,password,all} [...]] [-p PASSWORD] [-o OUTPUT] email

positional arguments:
  email                 Target email address to check

optional arguments:
  -h, --help            show this help message and exit
  -c, --checks          Checks to perform (default: all)
  -p, --password        Password to check against breach databases
  -o, --output OUTPUT   Output file for JSON results
```

## Examples

### Check email in all databases
```bash
python sneakleak.py john.doe@example.com
```

### Check email and password
```bash
python sneakleak.py john.doe@example.com -p "SecretPassword" -c hibp password
```

### Save results to file
```bash
python sneakleak.py investigate@target.com -o breach_report.json
```

### Use specific databases
```bash
python sneakleak.py user@domain.com -c hibp leakcheck
```

## Output Format

Results are provided in JSON format:

```json
{
  "target": "user@example.com",
  "timestamp": "2025-01-11T12:00:00",
  "checks": {
    "hibp_email": {
      "breaches_found": 3,
      "breaches": [
        {
          "name": "Adobe",
          "breach_date": "2013-10-04",
          "pwn_count": 152445165,
          "data_classes": ["Email addresses", "Passwords"]
        }
      ]
    },
    "hibp_password": {
      "password_compromised": true,
      "times_seen": 47205,
      "recommendation": "CRITICAL: Change this password immediately"
    }
  }
}
```

## Privacy and Security

### Password Checking

SneakLeak uses the k-anonymity model for password checking:
- Only the first 5 characters of the SHA-1 hash are sent to the API
- Your full password is NEVER transmitted
- The API returns all hashes matching the prefix
- Local matching determines if your password was breached

This ensures your password remains private while checking against millions of known breached passwords.

## Legal and Ethical Use

**IMPORTANT**: This tool is intended for legitimate security research and investigations only. Users must:

- Have proper authorization before investigating individuals
- Comply with all applicable laws and regulations
- Respect API terms of service
- Use responsibly and ethically
- Only investigate targets you have legal authority to investigate
- Not use discovered credentials for unauthorized access

The author is not responsible for misuse of this tool.

## API Rate Limits

Be aware of rate limits for each service:
- **HIBP**: Rate limiting applies (check API documentation)
- **Dehashed**: Rate limits based on subscription tier
- **LeakCheck**: Rate limits based on subscription tier

## License

MIT License - See LICENSE file for details

## Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## Support

For issues and questions:
- Open an issue on GitHub
- Check existing issues for solutions

## Disclaimer

This tool is provided "as-is" without warranty. Use at your own risk. Always ensure you have proper authorization before conducting investigations. Accessing accounts with discovered credentials without authorization is illegal.

## Author

Created for professional OSINT investigators and security researchers.

## Changelog

### Version 1.0.0
- Initial release
- HIBP email and password checking
- Dehashed integration
- LeakCheck integration
- JSON output support
- K-anonymity password checking
