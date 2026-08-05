#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Utility script to query Russian Certificate Transparency (CT) logs
(ct.tlscc.ru and precert.ru) for a domain name.

Usage:
    python check_russian_ct.py [domain]

Example:
    python check_russian_ct.py securepay.tinkoff.ru
"""

import sys
import json
import urllib3
import requests

# Disable warnings for insecure requests if we run without custom CA bundle loaded
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


def get_django_ca_bundle():
    """Attempts to load the custom combined CA bundle directly from the file system."""
    import os
    base_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Check if combined_ca.pem exists
    combined_path = os.path.join(base_dir, 'tinkoff_merchant', 'certs', 'combined_ca.pem')
    if os.path.exists(combined_path):
        return combined_path
    
    # Otherwise check if russiantrustedca.pem exists
    custom_path = os.path.join(base_dir, 'tinkoff_merchant', 'certs', 'russiantrustedca.pem')
    if os.path.exists(custom_path):
        return custom_path
        
    return None


def query_ct_tlscc(domain, verify_ca=True):
    """
    Queries ct.tlscc.ru (the Russian equivalent of crt.sh, maintained by TCI).
    Supports &output=json for easy programmatic parsing.
    """
    url = f"https://ct.tlscc.ru/?q={domain}&output=json"
    print(f"[*] Querying ct.tlscc.ru for domain: '{domain}'...")
    
    try:
        # Use our combined CA bundle if available
        verify = verify_ca if isinstance(verify_ca, str) else verify_ca
        
        response = requests.get(url, timeout=15, verify=verify)
        if response.status_code == 200:
            try:
                return response.json()
            except json.JSONDecodeError:
                print("[-] Received invalid JSON from ct.tlscc.ru (it might be returning an HTML page).")
                return None
        else:
            print(f"[-] Received HTTP status {response.status_code} from ct.tlscc.ru.")
    except requests.exceptions.SSLError as e:
        print(f"[!] SSL verification failed: {e}")
        print("[!] Retrying with SSL verification disabled (verify=False)...")
        try:
            response = requests.get(url, timeout=15, verify=False)
            if response.status_code == 200:
                return response.json()
        except Exception as ex:
            print(f"[-] Query failed even without SSL verification: {ex}")
    except Exception as e:
        print(f"[-] Query failed: {e}")
    
    return None


def check_precert_ru(domain):
    """Provides a manual search URL and details for precert.ru."""
    url = f"https://precert.ru/?q={domain}"
    print(f"\n[*] Precert.ru search link for manual check:")
    print(f"    {url}")
    print("    (You can open this link in your browser to inspect detailed CT logs search results.)")


def main():
    # Default to securepay.tinkoff.ru if no domain is provided
    domain = sys.argv[1] if len(sys.argv) > 1 else "securepay.tinkoff.ru"
    
    print("======================================================================")
    print("              RUSSIAN CERTIFICATE TRANSPARENCY CHECKER                ")
    print("======================================================================")
    
    # Check if we can find and use the local combined CA bundle
    ca_bundle = get_django_ca_bundle()
    if ca_bundle:
        print(f"[+] Found local Django combined CA bundle at:\n    {ca_bundle}")
        verify_ca = ca_bundle
    else:
        print("[-] Local Django combined CA bundle not found. Using system certs.")
        verify_ca = True
        
    results = query_ct_tlscc(domain, verify_ca=verify_ca)
    
    if results:
        print(f"\n[+] SUCCESS: Found {len(results)} certificate(s) logged in ct.tlscc.ru!")
        print("\nListing the 10 most recent entries:")
        print(f"{'Log ID':<12} | {'Issuer Name':<45} | {'Logged At'}")
        print("-" * 85)
        
        # Sort by ID or entry date (newest first)
        # Often ct.tlscc.ru returns them ordered, but we'll show first 10
        for entry in results[:10]:
            log_id = entry.get("id", "N/A")
            issuer = entry.get("issuer_name", "N/A")
            # Truncate issuer for display
            if len(issuer) > 45:
                issuer = issuer[:42] + "..."
            entry_date = entry.get("not_before", "N/A")
            print(f"{log_id:<12} | {issuer:<45} | {entry_date}")
            
    else:
        print("\n[-] No entries returned or query failed. If ct.tlscc.ru is down, try manual check.")
        
    check_precert_ru(domain)
    
    print("\n[i] Note: Russian national certificates (issued by Mintsifry/Минцифры) are logged")
    print("    in the following active CT logs:")
    print("    - Yandex CT log: ct-agate.yandex.net")
    print("    - VK CT log:     ctlog2026.mail.ru")
    print("    - Mintsifry:     26.ctlog.digital.gov.ru")
    print("======================================================================")


if __name__ == "__main__":
    main()
