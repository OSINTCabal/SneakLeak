#!/usr/bin/env python3
"""
SneakLeak.py - Advanced OSINT Breach Search Tool
Searches multiple breach databases and presents unified results
"""

import requests
import json
import re
import sys
import os
from datetime import datetime
from typing import Dict, List, Tuple, Any
from collections import defaultdict
import argparse

# ============================================================================
# API CONFIGURATIONS
# ============================================================================

API_CONFIGS = {
    'breach_bot': {
        'name': 'Breach Bot Telegram',
        'url': 'https://leakosintapi.com/',
        'key': '7716697356:jRmF1drs',  # Terrorbyte key for all searches
        'supports': ['email', 'phone', 'domain', 'username', 'name', 'ip'],
        'has_credits': False
    },
    'breach_directory': {
        'name': 'Breach Directory',
        'url': 'https://BreachDirectory.com/api_usage',
        'key': '30248df1771fd7a94a6ae5a84df77fcf',
        'supports': ['email', 'domain', 'username', 'ip', 'name'],
        'has_credits': False
    },
    'hibp': {
        'name': 'Have I Been Pwned',
        'url': 'https://haveibeenpwned.com/api/v3',
        'key': 'add6d4fe069149e29245414572afea44',
        'supports': ['email'],
        'has_credits': True
    },
    'leakinsight': {
        'name': 'LeakInsight API',
        'url': 'https://leakinsight-api.p.rapidapi.com/general/',
        'key': 'd4c94601b8msh79d994f9ac7e748p1b19b0jsnf9633ab98bc9',
        'host': 'leakinsight-api.p.rapidapi.com',
        'supports': ['email', 'phone', 'domain', 'username', 'name', 'ip', 'hash', 'password'],
        'has_credits': False
    }
}

# ============================================================================
# ASCII ART & BRANDING
# ============================================================================

TITLE = """  ██████  ███▄    █ ▓█████ ▄▄▄       ██ ▄█▀    ██▓    ▓█████ ▄▄▄       ██ ▄█▀
▒██    ▒  ██ ▀█   █ ▓█   ▀▒████▄     ██▄█▒    ▓██▒    ▓█   ▀▒████▄     ██▄█▒ 
░ ▓██▄   ▓██  ▀█ ██▒▒███  ▒██  ▀█▄  ▓███▄░    ▒██░    ▒███  ▒██  ▀█▄  ▓███▄░ 
  ▒   ██▒▓██▒  ▐▌██▒▒▓█  ▄░██▄▄▄▄██ ▓██ █▄    ▒██░    ▒▓█  ▄░██▄▄▄▄██ ▓██ █▄ 
▒██████▒▒▒██░   ▓██░░▒████▒▓█   ▓██▒▒██▒ █▄   ░██████▒░▒████▒▓█   ▓██▒▒██▒ █▄
▒ ▒▓▒ ▒ ░░ ▒░   ▒ ▒ ░░ ▒░ ░▒▒   ▓▒█░▒ ▒▒ ▓▒   ░ ▒░▓  ░░░ ▒░ ░▒▒   ▓▒█░▒ ▒▒ ▓▒
░ ░▒  ░ ░░ ░░   ░ ▒░ ░ ░  ░ ▒   ▒▒ ░░ ░▒ ▒░   ░ ░ ▒  ░ ░ ░  ░ ▒   ▒▒ ░░ ░▒ ▒░
░  ░  ░     ░   ░ ░    ░    ░   ▒   ░ ░░ ░      ░ ░      ░    ░   ▒   ░ ░░ ░ 
      ░           ░    ░  ░     ░  ░░  ░          ░  ░   ░  ░     ░  ░░  ░   
"""

ART = """                                    ██████████████                            
                              ██▓▓▓▓▓▓▒▒▒▒▒▒▒▒░░▒▒▓▓▓▓██                      
                          ████▓▓░░░░▒▒░░░░░░▒▒░░░░░░▒▒░░████                  
                      ██▓▓▒▒▓▓▓▓▒▒▒▒░░░░░░▒▒░░▒▒░░░░░░▒▒░░▒▒▓▓▓▓              
                    ██▓▓▒▒▒▒▒▒▒▒░░▒▒░░░░░░░░░░░░▒▒░░░░▒▒░░░░▒▒░░██            
                  ██▓▓▓▓░░░░▒▒░░░░▒▒▒▒░░░░░░░░░░▒▒░░  ░░░░░░░░▒▒░░██          
                ██▓▓▓▓▓▓▓▓▓▓░░░░░░▒▒░░░░░░░░░░░░░░      ░░░░░░░░░░░░██        
              ██▓▓▒▒▒▒▒▒▒▒▒▒▒▒░░░░░░▒▒░░░░░░░░░░░░  ░░            ▒▒▒▒██      
              ██▓▓▒▒▒▒▒▒▒▒░░░░▒▒░░░░░░░░░░░░░░░░░░                ░░░░██      
            ▓▓▓▓▒▒▒▒▒▒▒▒▒▒░░░░░░▒▒░░░░░░░░░░░░░░░░░░▓▓▓▓▓▓▓▓▓▓    ░░  ▒▒▓▓    
            ██▒▒▒▒▒▒▒▒▒▒░░░░░░░░░░░░░░░░░░░░░░░░▓▓▓▓▒▒▒▒▒▒▒▒▓▓▓▓▓▓    ░░██    
          ▓▓▒▒▒▒▒▒▒▒▒▒░░░░░░░░░░░░░░░░░░░░    ▓▓▒▒▒▒▒▒▒▒░░░░▒▒▒▒▓▓▒▒  ░░▒▒▓▓  
          ██▓▓▒▒░░░░░░▒▒▒▒▒▒░░░░░░░░░░░░░░░░▓▓▒▒▒▒▒▒▒▒▒▒▒▒▒▒░░░░▒▒▓▓▓▓  ░░██  
          ██▓▓▓▓▒▒▒▒▒▒▒▒░░░░▒▒░░░░░░░░░░░░  ▒▒▒▒▒▒▒▒▒▒▒▒████▓▓░░░░▒▒▓▓  ░░██  
        ██▓▓▒▒▒▒▒▒▓▓▒▒▓▓░░░░░░░░░░░░░░░░░░▓▓▒▒▒▒░░▒▒▒▒████  ▒▒██░░▒▒▓▓▓▓  ░░██
        ██▒▒▒▒▒▒▒▒▒▒▒▒▒▒░░░░░░░░░░░░░░░░░░▓▓░░▒▒▒▒▒▒██████▒▒  ▓▓▓▓░░▓▓▓▓  ░░██
        ██▓▓▒▒▒▒░░▒▒▒▒▒▒░░░░░░░░░░░░░░░░░░▓▓▒▒░░▒▒░░████████▓▓  ██▓▓▒▒▓▓  ░░██
        ██▓▓▓▓▓▓▓▓▒▒▒▒▒▒░░░░░░▒▒░░░░░░░░░░▒▒░░▒▒░░▒▒██████████▒▒██▒▒▒▒▓▓  ░░██
        ██▓▓▒▒▒▒▒▒░░░░░░░░▒▒▒▒░░░░░░░░░░░░▒▒▒▒░░░░▒▒██▒▒██████  ██▒▒▒▒▓▓  ░░██
        ██▒▒▒▒▒▒░░▓▓▓▓▓▓▒▒░░░░░░░░░░░░░░░░▒▒░░  ▒▒░░██  ▒▒████▒▒██▒▒▒▒▓▓  ░░██
        ██▓▓▓▓▓▓▓▓░░▒▒▒▒░░▒▒░░░░░░░░░░░░░░▒▒▒▒░░░░░░▒▒██  ██████▒▒▒▒▒▒▓▓░░░░██
      ██▓▓██▓▓▒▒▒▒▓▓░░░░▒▒░░░░░░░░░░░░░░░░░░▒▒▒▒░░▒▒░░▒▒██████▒▒▒▒▒▒▓▓  ░░██  
      ██▓▓██▒▒▒▒▒▒▒▒▓▓▓▓▒▒░░░░░░░░░░░░░░░░░░▒▒░░▒▒░░▒▒░░▒▒░░▒▒▒▒▒▒▒▒▓▓░░░░██  
    ██▒▒▓▓██▓▓▒▒▒▒▒▒▒▒▒▒▒▒░░░░░░░░░░░░░░░░░░░░▒▒░░▒▒░░░░░░▒▒▒▒▒▒▒▒▓▓  ░░░░██  
    ██▒▒▒▒▓▓██▓▓▓▓▒▒▒▒▒▒▒▒░░░░░░░░▒▒░░░░░░░░░░░░▒▒▒▒▒▒░░▒▒▒▒▒▒▓▓▓▓  ░░░░██    
  ▓▓▓▓▒▒▒▒▓▓██▓▓▒▒▒▒▒▒░░░░▒▒▒▒░░▒▒░░░░░░░░░░░░░░░░░░▒▒▒▒▓▓▓▓▓▓░░░░░░░░▒▒██    
  ██▒▒▒▒▓▓▒▒▓▓██▒▒▒▒▒▒▒▒▓▓▒▒▒▒▒▒░░░░░░░░░░░░░░░░░░░░░░░░░░░░  ░░  ░░░░██      
██▒▒▒▒▓▓░░▒▒▒▒██▓▓▓▓▓▓▒▒▒▒▒▒▒▒▓▓▓▓░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░▒▒░░▒▒██      
██▒▒▒▒▓▓▒▒░░▓▓▒▒██▓▓▒▒▒▒▒▒▒▒░░▓▓▒▒▓▓▒▒░░░░▒▒░░░░░░░░░░░░░░░░░░░░░░▓▓██        
██▒▒▒▒▒▒░░▒▒▒▒▒▒▓▓██▓▓▒▒▒▒▒▒▓▓▒▒▒▒▒▒▒▒▒▒▓▓░░░░░░░░░░▒▒░░░░▒▒░░▒▒▒▒██          
██▒▒▒▒░░▒▒░░▒▒████  ██▓▓▓▓▓▓▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒░░▓▓▒▒▒▒▒▒▓▓▒▒██            
██▒▒▓▓░░▒▒░░▓▓        ████▓▓▒▒▓▓▒▒▒▒▒▒░░▒▒▒▒▒▒▒▒▓▓▒▒▒▒▒▒▒▒▒▒██▓▓              
██▒▒▒▒▒▒▒▒  ██            ████▓▓▒▒▓▓▓▓▓▓▒▒▒▒▒▒▒▒▓▓▒▒▒▒▒▒████                  
  ██▒▒▒▒▒▒▒▒░░██              ██████▓▓▒▒▒▒▒▒▒▒▓▓▓▓██████                      
  ██▒▒▒▒▒▒▒▒░░  ████                ██████████████                            
    ██▒▒▒▒▒▒▒▒░░  ░░████                                                      
      ████▒▒▒▒▒▒░░░░  ░░████                                                  
          ████▒▒▒▒▒▒░░░░  ░░██                                                
              ████▒▒▒▒▒▒░░  ░░██                                              
                  ██▓▓▒▒▒▒░░  ▒▒▓▓                                            
                      ████▒▒░░  ▒▒██                                          
                          ▓▓▒▒░░░░██                                          
                            ██░░  ██                                          
                      ▓▓██  ██░░░░██                                          
                    ██░░██  ██░░░░██                                          
                  ██░░██    ██░░▒▒██                                          
                  ██░░▒▒████░░▒▒██                                            
                    ▓▓▒▒▒▒▒▒▒▒▓▓                                              
                      ████████                                                
"""

# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

def clear_screen():
    """Clear the terminal screen"""
    os.system('cls' if os.name == 'nt' else 'clear')

def print_banner():
    """Display the title and ASCII art"""
    clear_screen()
    print("\033[96m" + ART + "\033[0m")  # Cyan color
    print("\033[93m" + TITLE + "\033[0m")  # Yellow color
    print("\033[92m" + "="*80 + "\033[0m")
    print("\033[92m" + "Advanced OSINT Breach Search Tool | Multi-API Intelligence Gathering".center(80) + "\033[0m")
    print("\033[92m" + "="*80 + "\033[0m\n")

def detect_input_type(query: str) -> str:
    """
    Auto-detect the type of input based on patterns
    
    Rules:
    - Email: contains @ with domain
    - IP: matches IP pattern
    - Phone: starts with + or all digits (10-15 chars)
    - Domain: contains . and looks like domain
    - Name: Two or more words (treated as full name)
    - Username: Single word (no spaces)
    """
    query = query.strip()
    
    # Email detection
    if re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', query):
        return 'email'
    
    # IP detection
    if re.match(r'^(\d{1,3}\.){3}\d{1,3}$', query):
        return 'ip'
    
    # Phone detection (starts with + or 10-15 digits)
    if re.match(r'^\+?\d{10,15}$', query.replace('-', '').replace(' ', '').replace('(', '').replace(')', '')):
        return 'phone'
    
    # Domain detection (has . and looks like domain)
    if '.' in query and not ' ' in query and re.match(r'^[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', query):
        return 'domain'
    
    # Name detection (2+ words)
    if len(query.split()) >= 2:
        return 'name'
    
    # Default to username for single word
    return 'username'

def format_phone(phone: str) -> str:
    """Format phone number for API requests"""
    return re.sub(r'[^0-9+]', '', phone)

def format_domain(domain: str) -> str:
    """Format domain for API requests"""
    domain = domain.lower()
    domain = re.sub(r'^https?://', '', domain)
    domain = re.sub(r'^www\.', '', domain)
    domain = domain.rstrip('/')
    return domain

# ============================================================================
# API SEARCH FUNCTIONS
# ============================================================================

def search_breach_bot(query: str, query_type: str, debug: bool = False) -> Dict[str, Any]:
    """Search using Breach Bot Telegram API"""
    result = {
        'api': 'Breach Bot Telegram',
        'success': False,
        'records': [],
        'error': None,
        'total_found': 0
    }
    
    try:
        headers = {'Content-Type': 'application/json'}
        payload = {
            'token': API_CONFIGS['breach_bot']['key'],
            'request': query,
            'limit': 10000,
            'lang': 'en'
        }
        
        if debug:
            print(f"\n[DEBUG] Breach Bot Request:")
            print(f"  URL: {API_CONFIGS['breach_bot']['url']}")
            print(f"  Payload: {json.dumps(payload, indent=2)}")
        
        response = requests.post(
            API_CONFIGS['breach_bot']['url'],
            headers=headers,
            json=payload,
            timeout=30
        )
        
        if debug:
            print(f"  Status: {response.status_code}")
            print(f"  Response (first 500 chars): {response.text[:500]}")
        
        if response.status_code == 200:
            try:
                # Get raw text for debugging
                response_text = response.text.strip()
                
                # Try to parse JSON
                data = response.json()
                
                if debug:
                    print(f"  Parsed JSON type: {type(data)}")
                    print(f"  JSON keys: {list(data.keys()) if isinstance(data, dict) else 'N/A (list)'}")
                    print(f"  Full response: {json.dumps(data, indent=2)[:1000]}")
                
                # Handle Breach Bot's specific structure: {"List": {"BreachName": {"Data": [...], "InfoLeak": "..."}}}
                if isinstance(data, dict) and 'List' in data:
                    breach_list = data['List']
                    all_records = []
                    
                    if debug:
                        print(f"  Found Breach Bot 'List' structure with {len(breach_list)} breaches")
                    
                    # Iterate through each breach in the List
                    for breach_name, breach_info in breach_list.items():
                        if isinstance(breach_info, dict) and 'Data' in breach_info:
                            breach_data = breach_info['Data']
                            info_leak = breach_info.get('InfoLeak', '')
                            
                            # Process each record in this breach
                            if isinstance(breach_data, list):
                                for record in breach_data:
                                    # Add breach metadata to each record
                                    enhanced_record = record.copy() if isinstance(record, dict) else {'data': record}
                                    enhanced_record['source'] = {
                                        'name': breach_name,
                                        'description': info_leak
                                    }
                                    all_records.append(enhanced_record)
                                    
                                if debug:
                                    print(f"    {breach_name}: {len(breach_data)} records")
                    
                    if len(all_records) > 0:
                        result['success'] = True
                        result['records'] = all_records
                        result['total_found'] = len(all_records)
                        if debug:
                            print(f"  Total records extracted: {len(all_records)}")
                    else:
                        result['success'] = True
                        result['total_found'] = 0
                        if debug:
                            print(f"  No records found in breach list")
                
                # Fallback: Try standard structure
                elif isinstance(data, dict):
                    # Check for explicit success indicators
                    if data.get('success') in [True, 'true', 1]:
                        # Try multiple field names for results
                        results = data.get('result') or data.get('results') or data.get('data') or data.get('records') or []
                        
                        if isinstance(results, list) and len(results) > 0:
                            result['success'] = True
                            result['records'] = results
                            result['total_found'] = len(results)
                        else:
                            # Success but no results
                            result['success'] = True
                            result['total_found'] = 0
                    # Check if success is explicitly False but has results
                    elif data.get('success') == False or data.get('success') == 'false':
                        # Even if success=false, check for results
                        results = data.get('result') or data.get('results') or data.get('data') or data.get('records') or []
                        if isinstance(results, list) and len(results) > 0:
                            result['success'] = True
                            result['records'] = results
                            result['total_found'] = len(results)
                        # Check for error message
                        elif data.get('error') or data.get('message'):
                            error_msg = data.get('error') or data.get('message')
                            # Treat "not found" as success with 0 results
                            if any(phrase in str(error_msg).lower() for phrase in ['not found', 'no results', 'no data', 'nothing found']):
                                result['success'] = True
                                result['total_found'] = 0
                            else:
                                result['error'] = error_msg
                        else:
                            result['success'] = True
                            result['total_found'] = 0
                    # No explicit success field but has data fields
                    elif any(key in data for key in ['result', 'results', 'data', 'records']):
                        results = data.get('result') or data.get('results') or data.get('data') or data.get('records') or []
                        if isinstance(results, list) and len(results) > 0:
                            result['success'] = True
                            result['records'] = results
                            result['total_found'] = len(results)
                        else:
                            result['success'] = True
                            result['total_found'] = 0
                    # Check for error messages
                    elif data.get('error') or data.get('message'):
                        error_msg = data.get('error') or data.get('message')
                        # Treat "not found" as success with 0 results
                        if any(phrase in str(error_msg).lower() for phrase in ['not found', 'no results', 'no data', 'nothing found']):
                            result['success'] = True
                            result['total_found'] = 0
                        else:
                            result['error'] = error_msg
                    # Empty response means no results
                    elif len(data) == 0:
                        result['success'] = True
                        result['total_found'] = 0
                    else:
                        # Unknown structure - treat as no results
                        result['success'] = True
                        result['total_found'] = 0
                        
                elif isinstance(data, list):
                    # Direct list response
                    if len(data) > 0:
                        result['success'] = True
                        result['records'] = data
                        result['total_found'] = len(data)
                    else:
                        result['success'] = True
                        result['total_found'] = 0
                else:
                    result['error'] = f"Unexpected response type: {type(data)}"
                    
            except json.JSONDecodeError as e:
                result['error'] = f"Invalid JSON response"
                if debug:
                    print(f"  JSON Error: {e}")
        elif response.status_code == 404:
            # Not found = no results
            result['success'] = True
            result['total_found'] = 0
        else:
            result['error'] = f"HTTP {response.status_code}"
            if debug:
                print(f"  Error response: {response.text[:200]}")
            
    except requests.exceptions.Timeout:
        result['error'] = "Request timeout (30s)"
    except requests.exceptions.ConnectionError as e:
        result['error'] = "Connection failed"
        if debug:
            print(f"  Connection Error: {e}")
    except requests.exceptions.RequestException as e:
        result['error'] = f"Request error: {str(e)}"
        if debug:
            print(f"  Request Error: {e}")
    except Exception as e:
        result['error'] = f"Unexpected error: {str(e)}"
        if debug:
            print(f"  Unexpected Error: {e}")
    
    return result

def search_breach_directory(query: str, query_type: str) -> Dict[str, Any]:
    """Search using Breach Directory API"""
    result = {
        'api': 'Breach Directory',
        'success': False,
        'records': [],
        'error': None,
        'total_found': 0
    }
    
    # Map query types to BD method
    method_map = {
        'email': 'email',
        'domain': 'domain',
        'username': 'username',
        'ip': 'ip',
        'name': 'general'
    }
    
    method = method_map.get(query_type, 'general')
    
    try:
        params = {
            'method': method,
            'key': API_CONFIGS['breach_directory']['key'],
            'query': query
        }
        
        response = requests.get(
            API_CONFIGS['breach_directory']['url'],
            params=params,
            timeout=30
        )
        
        if response.status_code == 200:
            # Get raw response text
            response_text = response.text.strip()
            
            # Handle completely empty responses
            if not response_text:
                result['success'] = True
                result['total_found'] = 0
                return result
            
            # Check if response is HTML (error page)
            if response_text.lower().startswith('<!doctype') or response_text.lower().startswith('<html'):
                result['error'] = "API returned HTML error page (service may be unavailable)"
                return result
            
            # Check for plain text error messages
            if len(response_text) < 100 and 'error' in response_text.lower():
                # Treat common errors as "no results"
                if any(phrase in response_text.lower() for phrase in ['not found', 'no results', 'no data']):
                    result['success'] = True
                    result['total_found'] = 0
                else:
                    result['error'] = f"API error: {response_text}"
                return result
            
            # Try to parse as JSON
            try:
                data = response.json()
                
                if isinstance(data, dict):
                    # Check for success or found indicators
                    found_count = data.get('found', 0)
                    
                    if data.get('success') in [True, 'true', 1] or found_count > 0:
                        results = data.get('result') or data.get('results') or data.get('data') or data.get('records') or []
                        
                        if isinstance(results, list) and len(results) > 0:
                            result['success'] = True
                            result['records'] = results
                            result['total_found'] = found_count if found_count > 0 else len(results)
                        else:
                            # Success but no results
                            result['success'] = True
                            result['total_found'] = 0
                    # Check for error messages
                    elif data.get('error') or data.get('message'):
                        error_msg = data.get('error') or data.get('message')
                        # Some APIs return "not found" as an error, treat as success with 0 results
                        if any(phrase in str(error_msg).lower() for phrase in ['not found', 'no results', 'no data']):
                            result['success'] = True
                            result['total_found'] = 0
                        else:
                            result['error'] = error_msg
                    else:
                        # No explicit indicators - treat as no results
                        result['success'] = True
                        result['total_found'] = 0
                        
                elif isinstance(data, list):
                    if len(data) > 0:
                        result['success'] = True
                        result['records'] = data
                        result['total_found'] = len(data)
                    else:
                        result['success'] = True
                        result['total_found'] = 0
                else:
                    # Unknown data type - treat as no results
                    result['success'] = True
                    result['total_found'] = 0
                    
            except json.JSONDecodeError as e:
                # JSON parsing completely failed
                # This likely means the API is returning malformed data
                # Treat as "no results" rather than hard error
                result['success'] = True
                result['total_found'] = 0
                # Optionally can uncomment below to see what failed
                # result['error'] = f"JSON parse failed (treating as no results): {response_text[:100]}"
                
        elif response.status_code == 404:
            # Not found = no results
            result['success'] = True
            result['total_found'] = 0
        elif response.status_code == 429:
            result['error'] = "Rate limit exceeded"
        elif response.status_code >= 500:
            result['error'] = f"API server error (HTTP {response.status_code})"
        else:
            result['error'] = f"HTTP {response.status_code}"
            
    except requests.exceptions.Timeout:
        result['error'] = "Request timeout (30s)"
    except requests.exceptions.ConnectionError:
        result['error'] = "Connection failed"
    except requests.exceptions.RequestException as e:
        result['error'] = f"Request error: {str(e)}"
    except Exception as e:
        result['error'] = f"Unexpected error: {str(e)}"
    
    return result

def search_hibp(query: str, query_type: str) -> Dict[str, Any]:
    """Search using Have I Been Pwned API"""
    result = {
        'api': 'Have I Been Pwned',
        'success': False,
        'records': [],
        'error': None,
        'total_found': 0
    }
    
    # HIBP only supports email
    if query_type != 'email':
        result['error'] = 'Only supports email queries'
        return result
    
    try:
        headers = {
            'hibp-api-key': API_CONFIGS['hibp']['key'],
            'user-agent': 'SneakLeak-OSINT-Tool'
        }
        
        url = f"{API_CONFIGS['hibp']['url']}/breachedaccount/{query}?truncateResponse=false"
        
        response = requests.get(url, headers=headers, timeout=30)
        
        if response.status_code == 200:
            data = response.json()
            result['success'] = True
            result['records'] = data
            result['total_found'] = len(data)
        elif response.status_code == 404:
            result['success'] = True
            result['total_found'] = 0
        else:
            result['error'] = f"HTTP {response.status_code}"
            
    except Exception as e:
        result['error'] = str(e)
    
    return result

def search_leakinsight(query: str, query_type: str) -> Dict[str, Any]:
    """Search using LeakInsight API"""
    result = {
        'api': 'LeakInsight API',
        'success': False,
        'records': [],
        'error': None,
        'total_found': 0
    }
    
    # Map query types to LeakInsight types
    type_map = {
        'email': 'email',
        'phone': 'phone_number',
        'domain': 'domain',
        'username': 'username',
        'name': 'full_name',
        'ip': 'ip_address',
        'hash': 'hash',
        'password': 'password'
    }
    
    leak_type = type_map.get(query_type)
    if not leak_type:
        result['error'] = f'Unsupported query type: {query_type}'
        return result
    
    try:
        headers = {
            'x-rapidapi-host': API_CONFIGS['leakinsight']['host'],
            'x-rapidapi-key': API_CONFIGS['leakinsight']['key']
        }
        
        params = {
            'query': query,
            'type': leak_type,
            'offset': 0,
            'limit': 100
        }
        
        response = requests.get(
            API_CONFIGS['leakinsight']['url'],
            headers=headers,
            params=params,
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                result['success'] = True
                result['records'] = data.get('results', [])
                result['total_found'] = data.get('found', 0)
                result['databases'] = data.get('databases', 0)
        else:
            result['error'] = f"HTTP {response.status_code}"
            
    except Exception as e:
        result['error'] = str(e)
    
    return result

def check_hibp_credits() -> Dict[str, Any]:
    """Check HIBP API subscription status"""
    try:
        headers = {
            'hibp-api-key': API_CONFIGS['hibp']['key'],
            'user-agent': 'SneakLeak-OSINT-Tool'
        }
        
        response = requests.get(
            f"{API_CONFIGS['hibp']['url']}/subscription/status",
            headers=headers,
            timeout=10
        )
        
        if response.status_code == 200:
            return response.json()
        return {'error': f'HTTP {response.status_code}'}
    except Exception as e:
        return {'error': str(e)}

# ============================================================================
# RESULT PROCESSING
# ============================================================================

def deduplicate_results(all_results: List[Dict]) -> List[Dict]:
    """
    Deduplicate results and track which APIs found each record
    Also merges fields from the same breach found by different APIs
    """
    unique_records = {}
    
    for api_result in all_results:
        if not api_result['success'] or api_result['total_found'] == 0:
            continue
            
        api_name = api_result['api']
        
        for record in api_result['records']:
            # Create unique key based on available fields
            key_parts = []
            
            # Try different field names across APIs for common identifiers
            email = (record.get('email_address') or record.get('email') or 
                    record.get('Email') or record.get('login') or '').lower()
            username = (record.get('user_name') or record.get('username') or 
                       record.get('Username') or record.get('NickName') or 
                       record.get('Nickname') or '').lower()
            phone = (record.get('phone') or record.get('Phone') or 
                    record.get('phone_number') or '').lower()
            password = (record.get('password') or record.get('Password') or 
                       record.get('Password(bcrypt)') or record.get('Password(Hash)') or 
                       record.get('Password(SHA1+Salt)') or '')
            source = (record.get('source', {}).get('name') if isinstance(record.get('source'), dict) 
                     else record.get('source') or record.get('Name') or '').lower()
            
            # Build key with available identifiers
            if email:
                key_parts.append(f"e:{email}")
            if username:
                key_parts.append(f"u:{username}")
            if phone:
                key_parts.append(f"p:{phone}")
            if source:
                key_parts.append(f"s:{source}")
            
            # If we still don't have enough to make it unique, use password hash or full record hash
            if len(key_parts) < 2:
                if password:
                    # Use first 20 chars of password to help differentiate
                    key_parts.append(f"pw:{password[:20]}")
                else:
                    # Last resort: hash the entire record
                    key_parts.append(f"h:{hash(json.dumps(record, sort_keys=True))}")
            
            # Create unique key
            unique_key = '|'.join(key_parts) if key_parts else str(hash(json.dumps(record, sort_keys=True)))
            
            if unique_key in unique_records:
                # Merge with existing record - combine all fields
                existing = unique_records[unique_key]
                
                # Add API to sources list
                if api_name not in existing['_sources']:
                    existing['_sources'].append(api_name)
                
                # Merge all fields from new record into existing
                for key, value in record.items():
                    if key not in existing or not existing[key] or existing[key] == '':
                        # Field doesn't exist or is empty in existing record
                        existing[key] = value
                    elif key == 'source' and isinstance(value, dict) and isinstance(existing[key], dict):
                        # Merge source dictionaries
                        for sub_key, sub_value in value.items():
                            if sub_key not in existing[key] or not existing[key][sub_key]:
                                existing[key][sub_key] = sub_value
                    elif isinstance(value, list) and isinstance(existing[key], list):
                        # Merge lists
                        for item in value:
                            if item not in existing[key]:
                                existing[key].append(item)
            else:
                # New record
                record['_sources'] = [api_name]
                unique_records[unique_key] = record
    
    return list(unique_records.values())

def format_result_display(records: List[Dict], query_type: str) -> str:
    """Format deduplicated results for terminal display - shows ALL fields"""
    if not records:
        return "\n\033[93m[!] No results found\033[0m\n"
    
    output = []
    output.append(f"\n\033[92m{'='*80}\033[0m")
    output.append(f"\033[92m UNIFIED SEARCH RESULTS - {len(records)} Unique Records Found \033[0m")
    output.append(f"\033[92m{'='*80}\033[0m\n")
    
    # Field name mappings for better display
    field_labels = {
        'email': 'Email',
        'email_address': 'Email',
        'login': 'Email/Login',
        'username': 'Username',
        'user_name': 'Username',
        'Username': 'Username',
        'password': 'Password',
        'Password': 'Password',
        'name': 'Name',
        'full_name': 'Full Name',
        'Name': 'Breach Name',
        'first_name': 'First Name',
        'last_name': 'Last Name',
        'phone': 'Phone',
        'phone_number': 'Phone',
        'ip': 'IP Address',
        'ip_address': 'IP Address',
        'hash': 'Hash',
        'address': 'Address',
        'city': 'City',
        'state': 'State',
        'country': 'Country',
        'zip': 'ZIP Code',
        'zipcode': 'ZIP Code',
        'postal_code': 'Postal Code',
        'dob': 'Date of Birth',
        'birth_date': 'Date of Birth',
        'birthday': 'Birthday',
        'age': 'Age',
        'gender': 'Gender',
        'vin': 'VIN',
        'car_number': 'License Plate',
        'license_plate': 'License Plate',
        'telegram_id': 'Telegram ID',
        'telegram_username': 'Telegram Username',
        'facebook_id': 'Facebook ID',
        'vk_id': 'VK ID',
        'instagram_id': 'Instagram ID',
        'instagram_username': 'Instagram Username',
        'twitter_id': 'Twitter ID',
        'twitter_username': 'Twitter Username',
        'social_media': 'Social Media',
        'website': 'Website',
        'url': 'URL',
        'company': 'Company',
        'job_title': 'Job Title',
        'occupation': 'Occupation',
        'education': 'Education',
        'school': 'School',
        'university': 'University',
        'ssn': 'SSN',
        'passport': 'Passport',
        'driver_license': 'Driver License',
        'credit_card': 'Credit Card',
        'bank_account': 'Bank Account',
        'bitcoin': 'Bitcoin Address',
        'wallet': 'Wallet',
        'domain': 'Domain',
        'breach_date': 'Breach Date',
        'BreachDate': 'Breach Date',
        'added_date': 'Added Date',
        'modified_date': 'Modified Date',
        'line': 'Database Line',
        'database': 'Database',
        'source': 'Source',
        'breach': 'Breach',
        'data_classes': 'Data Classes',
        'IsVerified': 'Verified',
        'IsFabricated': 'Fabricated',
        'IsSensitive': 'Sensitive',
        'IsRetired': 'Retired',
        'IsSpamList': 'Spam List',
        'IsMalware': 'Malware',
        'Description': 'Description',
        'PwnCount': 'Pwn Count',
    }
    
    # Fields to skip (internal/meta fields)
    skip_fields = {'_sources', 'ModifiedDate', 'AddedDate', 'LogoPath', 'Title'}
    
    for idx, record in enumerate(records, 1):
        sources = record.pop('_sources', ['Unknown'])
        
        output.append(f"\033[96m[Record #{idx}]\033[0m")
        output.append(f"\033[90m  Found by: {', '.join(sources)}\033[0m")
        output.append(f"  {'-'*76}")
        
        # First, handle source/breach info specially
        source_info = record.get('source')
        breach_name = None
        breach_date = None
        
        if isinstance(source_info, dict):
            breach_name = source_info.get('name')
            breach_date = source_info.get('breach_date')
        elif record.get('Name'):
            breach_name = record.get('Name')
            breach_date = record.get('BreachDate')
        
        # Display ALL fields dynamically
        displayed_fields = set()
        
        for key, value in sorted(record.items()):
            # Skip empty values, internal fields, and already handled source info
            if key in skip_fields:
                continue
            if key == 'source' and isinstance(value, dict):
                continue  # Already handled above
            if key in ['Name', 'BreachDate'] and (breach_name or breach_date):
                continue  # Will display separately
            if not value or value == '' or value == []:
                continue
            
            # Get display label
            label = field_labels.get(key, key.replace('_', ' ').title())
            
            # Format the value
            if isinstance(value, dict):
                # Handle nested dictionaries
                output.append(f"  \033[93m{label}:\033[0m")
                for sub_key, sub_value in value.items():
                    if sub_value and sub_value != '':
                        sub_label = field_labels.get(sub_key, sub_key.replace('_', ' ').title())
                        output.append(f"    • {sub_label}: {sub_value}")
            elif isinstance(value, list):
                # Handle lists
                if len(value) > 0:
                    output.append(f"  \033[93m{label}:\033[0m {', '.join(str(v) for v in value)}")
            else:
                # Regular field
                output.append(f"  \033[93m{label}:\033[0m {value}")
            
            displayed_fields.add(key)
        
        # Display breach info at the end if available
        if breach_name:
            output.append(f"  \033[92m{'─'*76}\033[0m")
            output.append(f"  \033[93mBreach Source:\033[0m {breach_name}")
            if breach_date:
                output.append(f"  \033[93mBreach Date:\033[0m {breach_date}")
        
        output.append("")
    
    return '\n'.join(output)

def create_session_summary(all_results: List[Dict], query: str, query_type: str, 
                          start_time: datetime) -> str:
    """Create search session summary"""
    end_time = datetime.now()
    duration = (end_time - start_time).total_seconds()
    
    output = []
    output.append(f"\n\033[92m{'='*80}\033[0m")
    output.append(f"\033[92m SEARCH SESSION SUMMARY \033[0m")
    output.append(f"\033[92m{'='*80}\033[0m")
    output.append(f"\n  \033[93mQuery:\033[0m {query}")
    output.append(f"  \033[93mDetected Type:\033[0m {query_type}")
    output.append(f"  \033[93mSearch Duration:\033[0m {duration:.2f} seconds")
    output.append(f"  \033[93mTimestamp:\033[0m {start_time.strftime('%Y-%m-%d %H:%M:%S')}")
    
    # API Status
    output.append(f"\n  \033[96mAPIs Used:\033[0m")
    for result in all_results:
        status = "✓ SUCCESS" if result['success'] else "✗ FAILED"
        color = "\033[92m" if result['success'] else "\033[91m"
        output.append(f"    {color}{status}\033[0m - {result['api']}")
        if result['success']:
            output.append(f"      Records: {result['total_found']}")
        if result.get('error'):
            output.append(f"      Error: {result['error']}")
    
    # Credit Status
    output.append(f"\n  \033[96mAPI Credits:\033[0m")
    
    # Check HIBP credits
    hibp_status = check_hibp_credits()
    if 'error' not in hibp_status:
        output.append(f"    HIBP: {hibp_status.get('SubscriptionName', 'Unknown')} - "
                     f"{hibp_status.get('Description', 'Active')}")
    else:
        output.append(f"    HIBP: Unable to check credits")
    
    output.append(f"    Breach Bot: No credit tracking")
    output.append(f"    Breach Directory: No credit tracking")
    output.append(f"    LeakInsight: No credit tracking")
    
    output.append(f"\n\033[92m{'='*80}\033[0m\n")
    
    return '\n'.join(output)

# ============================================================================
# EXPORT FUNCTIONS
# ============================================================================

def export_json(records: List[Dict], filename: str, query: str, query_type: str):
    """Export results to JSON file"""
    data = {
        'query': query,
        'query_type': query_type,
        'timestamp': datetime.now().isoformat(),
        'total_records': len(records),
        'records': records
    }
    
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    
    print(f"\n\033[92m[✓] Exported {len(records)} records to {filename}\033[0m")

def export_txt(records: List[Dict], filename: str, query: str, query_type: str):
    """Export results to TXT file"""
    with open(filename, 'w', encoding='utf-8') as f:
        f.write("="*80 + "\n")
        f.write(f"SNEAKLEAK SEARCH RESULTS\n")
        f.write("="*80 + "\n")
        f.write(f"Query: {query}\n")
        f.write(f"Type: {query_type}\n")
        f.write(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"Total Records: {len(records)}\n")
        f.write("="*80 + "\n\n")
        
        for idx, record in enumerate(records, 1):
            sources = record.pop('_sources', ['Unknown'])
            f.write(f"[Record #{idx}]\n")
            f.write(f"Found by: {', '.join(sources)}\n")
            f.write("-"*80 + "\n")
            
            for key, value in record.items():
                if value and not key.startswith('_'):
                    f.write(f"{key}: {value}\n")
            f.write("\n")
    
    print(f"\n\033[92m[✓] Exported {len(records)} records to {filename}\033[0m")

def export_pdf(records: List[Dict], filename: str, query: str, query_type: str):
    """Export results to PDF file (requires reportlab)"""
    try:
        from reportlab.lib.pagesizes import letter
        from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib import colors
        from reportlab.lib.units import inch
        
        doc = SimpleDocTemplate(filename, pagesize=letter)
        elements = []
        styles = getSampleStyleSheet()
        
        # Title
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#00FF00'),
            spaceAfter=30,
        )
        
        elements.append(Paragraph("SneakLeak Search Results", title_style))
        elements.append(Spacer(1, 0.2*inch))
        
        # Metadata
        meta_data = [
            ["Query:", query],
            ["Type:", query_type],
            ["Timestamp:", datetime.now().strftime('%Y-%m-%d %H:%M:%S')],
            ["Total Records:", str(len(records))]
        ]
        
        meta_table = Table(meta_data, colWidths=[2*inch, 5*inch])
        meta_table.setStyle(TableStyle([
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
        ]))
        
        elements.append(meta_table)
        elements.append(Spacer(1, 0.3*inch))
        
        # Records
        for idx, record in enumerate(records, 1):
            sources = record.pop('_sources', ['Unknown'])
            
            record_title = Paragraph(f"<b>Record #{idx}</b> (Found by: {', '.join(sources)})", 
                                    styles['Heading2'])
            elements.append(record_title)
            
            record_data = []
            for key, value in record.items():
                if value and not key.startswith('_'):
                    record_data.append([key, str(value)])
            
            if record_data:
                record_table = Table(record_data, colWidths=[2*inch, 5*inch])
                record_table.setStyle(TableStyle([
                    ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
                    ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, -1), 9),
                    ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
                    ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
                    ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                ]))
                
                elements.append(record_table)
            
            elements.append(Spacer(1, 0.2*inch))
        
        doc.build(elements)
        print(f"\n\033[92m[✓] Exported {len(records)} records to {filename}\033[0m")
        
    except ImportError:
        print("\n\033[91m[!] PDF export requires 'reportlab' library\033[0m")
        print("\033[93m[!] Install with: pip install reportlab\033[0m")
        print("\033[93m[!] Falling back to TXT export...\033[0m")
        export_txt(records, filename.replace('.pdf', '.txt'), query, query_type)

# ============================================================================
# MAIN SEARCH FUNCTION
# ============================================================================

def run_search(query: str, query_type: str = None, debug: bool = False) -> Tuple[List[Dict], List[Dict]]:
    """
    Run search across all applicable APIs
    Returns: (deduplicated_records, all_api_results)
    """
    # Auto-detect type if not provided
    if not query_type:
        query_type = detect_input_type(query)
    
    # Format query based on type
    if query_type == 'phone':
        query = format_phone(query)
    elif query_type == 'domain':
        query = format_domain(query)
    
    print(f"\n\033[96m[*] Searching for: {query}\033[0m")
    print(f"\033[96m[*] Detected type: {query_type}\033[0m")
    print(f"\033[96m[*] Running searches...\033[0m\n")
    
    all_results = []
    
    # Run searches based on what each API supports
    for api_key, api_config in API_CONFIGS.items():
        if query_type in api_config['supports']:
            print(f"\033[90m  → Querying {api_config['name']}...\033[0m")
            
            if api_key == 'breach_bot':
                result = search_breach_bot(query, query_type, debug=debug)
            elif api_key == 'breach_directory':
                result = search_breach_directory(query, query_type)
            elif api_key == 'hibp':
                result = search_hibp(query, query_type)
            elif api_key == 'leakinsight':
                result = search_leakinsight(query, query_type)
            else:
                continue
            
            all_results.append(result)
    
    # Deduplicate results
    deduplicated = deduplicate_results(all_results)
    
    return deduplicated, all_results

# ============================================================================
# MAIN PROGRAM
# ============================================================================

def main():
    parser = argparse.ArgumentParser(
        description='SneakLeak - Advanced OSINT Breach Search Tool',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument('query', nargs='?', help='Search query (email, username, phone, etc.)')
    parser.add_argument('-t', '--type', choices=['email', 'username', 'phone', 'ip', 'domain', 'name'],
                       help='Force specific query type (auto-detected if not specified)')
    parser.add_argument('-e', '--export', choices=['json', 'txt', 'pdf'],
                       help='Export results to file')
    parser.add_argument('-o', '--output', help='Output filename (default: sneakleak_[timestamp].[ext])')
    parser.add_argument('-q', '--quiet', action='store_true', help='Suppress banner')
    parser.add_argument('-d', '--debug', action='store_true', help='Enable debug output for API calls')
    
    args = parser.parse_args()
    
    # Show banner
    if not args.quiet:
        print_banner()
    
    # Interactive mode if no query provided
    if not args.query:
        try:
            query = input("\033[96mEnter search query: \033[0m").strip()
            if not query:
                print("\033[91m[!] No query provided. Exiting.\033[0m")
                sys.exit(1)
        except KeyboardInterrupt:
            print("\n\033[91m[!] Search cancelled.\033[0m")
            sys.exit(0)
    else:
        query = args.query
    
    # Start search
    start_time = datetime.now()
    
    try:
        records, all_results = run_search(query, args.type, debug=args.debug)
        
        # Display results
        query_type = args.type or detect_input_type(query)
        print(format_result_display(records, query_type))
        
        # Display session summary
        print(create_session_summary(all_results, query, query_type, start_time))
        
        # Export if requested
        if args.export and records:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            
            if args.output:
                filename = args.output
            else:
                filename = f"sneakleak_{timestamp}.{args.export}"
            
            if args.export == 'json':
                export_json(records, filename, query, query_type)
            elif args.export == 'txt':
                export_txt(records, filename, query, query_type)
            elif args.export == 'pdf':
                export_pdf(records, filename, query, query_type)
        
        # Interactive export prompt
        elif records and not args.quiet:
            try:
                export_choice = input("\n\033[96mExport results? (json/txt/pdf/n): \033[0m").strip().lower()
                
                if export_choice in ['json', 'txt', 'pdf']:
                    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                    filename = f"sneakleak_{timestamp}.{export_choice}"
                    
                    if export_choice == 'json':
                        export_json(records, filename, query, query_type)
                    elif export_choice == 'txt':
                        export_txt(records, filename, query, query_type)
                    elif export_choice == 'pdf':
                        export_pdf(records, filename, query, query_type)
            except KeyboardInterrupt:
                print("\n")
        
    except KeyboardInterrupt:
        print("\n\033[91m[!] Search interrupted.\033[0m")
        sys.exit(0)
    except Exception as e:
        print(f"\n\033[91m[!] Error: {str(e)}\033[0m")
        sys.exit(1)

if __name__ == '__main__':
    main()
