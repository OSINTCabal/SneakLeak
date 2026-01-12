#!/usr/bin/env python3
"""
SneakLeak - Credential breach and data leak checker
Searches multiple breach databases for compromised credentials
"""

import requests
import argparse
import json
import hashlib
import sys
from datetime import datetime
from typing import Dict, List, Optional

class SneakLeak:
    def __init__(self):
        # API Keys - Replace with your actual keys
        self.hibp_key = "YOUR_HIBP_API_KEY_HERE"
        self.dehashed_email = "YOUR_DEHASHED_EMAIL_HERE"
        self.dehashed_key = "YOUR_DEHASHED_API_KEY_HERE"
        self.leakcheck_key = "YOUR_LEAKCHECK_API_KEY_HERE"
        
        self.results = {}
        
    def check_hibp_email(self, email: str) -> Dict:
        """Check Have I Been Pwned for email breaches"""
        print(f"[*] Checking Have I Been Pwned for: {email}")
        
        if self.hibp_key == "YOUR_HIBP_API_KEY_HERE":
            return {"error": "HIBP API key not configured"}
        
        try:
            url = f"https://haveibeenpwned.com/api/v3/breachedaccount/{email}"
            headers = {
                "hibp-api-key": self.hibp_key,
                "user-agent": "SneakLeak-OSINT-Tool"
            }
            
            response = requests.get(url, headers=headers, timeout=10)
            
            if response.status_code == 200:
                breaches = response.json()
                return {
                    "email": email,
                    "breaches_found": len(breaches),
                    "breaches": [
                        {
                            "name": breach.get("Name"),
                            "domain": breach.get("Domain"),
                            "breach_date": breach.get("BreachDate"),
                            "added_date": breach.get("AddedDate"),
                            "pwn_count": breach.get("PwnCount"),
                            "data_classes": breach.get("DataClasses", [])
                        }
                        for breach in breaches
                    ]
                }
            elif response.status_code == 404:
                return {
                    "email": email,
                    "breaches_found": 0,
                    "status": "No breaches found"
                }
            else:
                return {"error": f"HIBP API error: {response.status_code}"}
        except Exception as e:
            return {"error": str(e)}
    
    def check_hibp_password(self, password: str) -> Dict:
        """Check Have I Been Pwned for password in breaches (k-anonymity)"""
        print(f"[*] Checking password against HIBP database...")
        
        try:
            # Hash the password
            sha1_hash = hashlib.sha1(password.encode()).hexdigest().upper()
            prefix = sha1_hash[:5]
            suffix = sha1_hash[5:]
            
            # Query HIBP API with k-anonymity
            url = f"https://api.pwnedpasswords.com/range/{prefix}"
            response = requests.get(url, timeout=10)
            
            if response.status_code == 200:
                hashes = response.text.split('\r\n')
                
                for hash_line in hashes:
                    hash_suffix, count = hash_line.split(':')
                    if hash_suffix == suffix:
                        return {
                            "password_compromised": True,
                            "times_seen": int(count),
                            "recommendation": "CRITICAL: Change this password immediately"
                        }
                
                return {
                    "password_compromised": False,
                    "times_seen": 0,
                    "status": "Password not found in breach databases"
                }
            else:
                return {"error": f"HIBP Passwords API error: {response.status_code}"}
        except Exception as e:
            return {"error": str(e)}
    
    def check_dehashed(self, query: str, query_type: str = "email") -> Dict:
        """Check Dehashed for leaked credentials"""
        print(f"[*] Checking Dehashed for: {query}")
        
        if self.dehashed_key == "YOUR_DEHASHED_API_KEY_HERE":
            return {"error": "Dehashed API key not configured"}
        
        try:
            url = "https://api.dehashed.com/search"
            params = {query_type: query}
            
            response = requests.get(
                url,
                params=params,
                auth=(self.dehashed_email, self.dehashed_key),
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                entries = data.get("entries", [])
                
                return {
                    "query": query,
                    "query_type": query_type,
                    "results_found": len(entries),
                    "entries": [
                        {
                            "email": entry.get("email"),
                            "username": entry.get("username"),
                            "password": entry.get("password"),
                            "hashed_password": entry.get("hashed_password"),
                            "name": entry.get("name"),
                            "database_name": entry.get("database_name")
                        }
                        for entry in entries[:10]  # Limit to first 10
                    ]
                }
            else:
                return {"error": f"Dehashed API error: {response.status_code}"}
        except Exception as e:
            return {"error": str(e)}
    
    def check_leakcheck(self, query: str) -> Dict:
        """Check LeakCheck for leaked credentials"""
        print(f"[*] Checking LeakCheck for: {query}")
        
        if self.leakcheck_key == "YOUR_LEAKCHECK_API_KEY_HERE":
            return {"error": "LeakCheck API key not configured"}
        
        try:
            url = "https://leakcheck.io/api/public"
            params = {
                "key": self.leakcheck_key,
                "check": query,
                "type": "email"
            }
            
            response = requests.get(url, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                
                if data.get("success"):
                    sources = data.get("sources", [])
                    return {
                        "query": query,
                        "found": data.get("found", False),
                        "sources_count": len(sources),
                        "sources": [
                            {
                                "name": source.get("name"),
                                "date": source.get("date")
                            }
                            for source in sources
                        ]
                    }
                else:
                    return {
                        "query": query,
                        "found": False,
                        "status": "No leaks found"
                    }
            else:
                return {"error": f"LeakCheck API error: {response.status_code}"}
        except Exception as e:
            return {"error": str(e)}
    
    def run_investigation(self, target: str, check_types: List[str], password: Optional[str] = None) -> Dict:
        """Run all enabled checks on the target"""
        print(f"\n[+] Starting breach investigation on: {target}")
        print(f"[+] Timestamp: {datetime.now().isoformat()}\n")
        
        results = {
            "target": target,
            "timestamp": datetime.now().isoformat(),
            "checks": {}
        }
        
        if "hibp" in check_types:
            results["checks"]["hibp_email"] = self.check_hibp_email(target)
        
        if "dehashed" in check_types:
            results["checks"]["dehashed"] = self.check_dehashed(target)
        
        if "leakcheck" in check_types:
            results["checks"]["leakcheck"] = self.check_leakcheck(target)
        
        if password and "password" in check_types:
            results["checks"]["hibp_password"] = self.check_hibp_password(password)
        
        return results
    
    def save_results(self, results: Dict, output_file: str):
        """Save results to JSON file"""
        with open(output_file, 'w') as f:
            json.dump(results, f, indent=2)
        print(f"\n[+] Results saved to: {output_file}")
    
    def print_results(self, results: Dict):
        """Print results to console"""
        print("\n" + "="*60)
        print("BREACH INVESTIGATION RESULTS")
        print("="*60)
        print(f"Target: {results['target']}")
        print(f"Timestamp: {results['timestamp']}")
        print("="*60)
        
        for check_name, data in results['checks'].items():
            print(f"\n[{check_name.upper()}]")
            if "error" in data:
                print(f"  Error: {data['error']}")
            else:
                # Pretty print based on check type
                if check_name == "hibp_email":
                    print(f"  Breaches found: {data.get('breaches_found', 0)}")
                    if data.get('breaches'):
                        for breach in data['breaches']:
                            print(f"\n  - {breach['name']}")
                            print(f"    Date: {breach['breach_date']}")
                            print(f"    Pwned: {breach['pwn_count']:,} accounts")
                            print(f"    Data: {', '.join(breach['data_classes'])}")
                
                elif check_name == "hibp_password":
                    if data.get('password_compromised'):
                        print(f"  ⚠️  PASSWORD COMPROMISED!")
                        print(f"  Seen {data['times_seen']:,} times in breaches")
                        print(f"  {data['recommendation']}")
                    else:
                        print(f"  ✓ Password not found in breach databases")
                
                elif check_name == "dehashed":
                    print(f"  Results found: {data.get('results_found', 0)}")
                    if data.get('entries'):
                        for entry in data['entries'][:5]:
                            print(f"\n  - Email: {entry.get('email', 'N/A')}")
                            print(f"    Username: {entry.get('username', 'N/A')}")
                            print(f"    Database: {entry.get('database_name', 'N/A')}")
                
                elif check_name == "leakcheck":
                    print(f"  Found: {data.get('found', False)}")
                    print(f"  Sources: {data.get('sources_count', 0)}")
                    if data.get('sources'):
                        for source in data['sources'][:5]:
                            print(f"    - {source['name']} ({source.get('date', 'Unknown date')})")
        
        print("\n" + "="*60)

def main():
    parser = argparse.ArgumentParser(
        description="SneakLeak - Credential breach and data leak checker",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument("email", help="Target email address to check")
    parser.add_argument(
        "-c", "--checks",
        nargs="+",
        choices=["hibp", "dehashed", "leakcheck", "password", "all"],
        default=["all"],
        help="Checks to perform (default: all)"
    )
    parser.add_argument(
        "-p", "--password",
        help="Password to check against breach databases (optional)"
    )
    parser.add_argument(
        "-o", "--output",
        help="Output file for JSON results"
    )
    
    args = parser.parse_args()
    
    # Determine which checks to run
    if "all" in args.checks:
        check_types = ["hibp", "dehashed", "leakcheck"]
        if args.password:
            check_types.append("password")
    else:
        check_types = args.checks
    
    # Run investigation
    leak_checker = SneakLeak()
    results = leak_checker.run_investigation(args.email, check_types, args.password)
    
    # Print results
    leak_checker.print_results(results)
    
    # Save if output file specified
    if args.output:
        leak_checker.save_results(results, args.output)

if __name__ == "__main__":
    main()
