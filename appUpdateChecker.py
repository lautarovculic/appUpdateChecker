#!/usr/bin/env python3

import os
import sys
import argparse
from datetime import datetime, timedelta
import json
import time
import re
from typing import Dict, Optional, Tuple
from colorama import init, Fore, Style
import requests
from bs4 import BeautifulSoup

init(autoreset=True)
class AppUpdateChecker:
    def __init__(self):
        self.data_dir = os.path.expanduser("~/.local/share/appUpdateChecker")
        self.data_file = os.path.join(self.data_dir, "data.json")
        self.cache_duration = 300
        self.ensure_data_dir()
        self.setup_session()

    def setup_session(self):
        # HTTP Connection #########################################################################################################################
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        })

    def ensure_data_dir(self):
        # Directory ###############################################################################################################################
        try:
            os.makedirs(self.data_dir, exist_ok=True)
            if not os.path.exists(self.data_file):
                self.save_data({})
        except Exception as e:
            print(f"{Fore.RED}[!] Error creating directory: {e}{Fore.RESET}")
            sys.exit(1)

    def load_data(self) -> Dict:
        # Load data ###############################################################################################################################
        try:
            if os.path.exists(self.data_file):
                with open(self.data_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    return self.migrate_data_format(data)
            return {}
        except (FileNotFoundError, json.JSONDecodeError) as e:
            print(f"{Fore.YELLOW}[!] Warning: Error loading data, creating new file: {e}{Fore.RESET}")
            return {}

    def migrate_data_format(self, data: Dict) -> Dict:
        # Migrate #################################################################################################################################
        migrated = {}
        for package_name, info in data.items():
            if isinstance(info, dict):
                # packages
                migrated[package_name] = {
                    'check_date': info.get('check_date', datetime.now().isoformat()),
                    'last_update': info.get('last_update', ''),
                    'last_fetched': info.get('last_fetched', ''),
                    'fetch_count': info.get('fetch_count', 0),
                    'last_error': info.get('last_error', '')
                }
        return migrated

    def save_data(self, data: Dict):
        # Save info ###############################################################################################################################
        try:
            with open(self.data_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"{Fore.RED}[!] Error saving data: {e}{Fore.RESET}")

    def parse_play_store_date(self, date_str: str) -> Optional[datetime]:
        # Parse Play Store date ###################################################################################################################
            return None

        # Clean the date string #####
        date_str = date_str.strip()
        
        # Common date patterns ######
        patterns = [
            r'(\w+ \d{1,2}, \d{4})',
            r'(\d{1,2} \w+ \d{4})',
            r'(\w+ \d{4})',
            r'(\d{1,2}/\d{1,2}/\d{4})',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, date_str)
            if match:
                try:
                    date_part = match.group(1)
                    # Parsing formats #####
                    formats = ['%b %d, %Y', '%d %b %Y', '%b %Y', '%m/%d/%Y']
                    for fmt in formats:
                        try:
                            return datetime.strptime(date_part, fmt)
                        except ValueError:
                            continue
                except Exception:
                    continue
        
        return None

    def get_play_store_update_date(self, package_name: str) -> Tuple[Optional[str], Optional[str]]:
        # Get last update #########################################################################################################################
        try:
            url = f"https://play.google.com/store/apps/details?id={package_name}&hl=en&gl=us"
            
            # #Avoid rate limit ####
            time.sleep(1)
            
            response = self.session.get(url, timeout=30)
            
            if response.status_code == 404:
                return None, "App not found in Play Store"
            elif response.status_code != 200:
                return None, f"HTTP {response.status_code}"

            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Types of update ####
            update_date = None
            
            # Look for "Updated on" text ####
            updated_elem = soup.find(string=re.compile(r'Updated on|Last updated'))
            if updated_elem:
                parent = updated_elem.find_parent()
                if parent:
                    next_div = parent.find_next_sibling()
                    if next_div:
                        update_date = next_div.get_text(strip=True)
            
            # Look in structured data ####
            if not update_date:
                scripts = soup.find_all('script', type='application/ld+json')
                for script in scripts:
                    try:
                        data = json.loads(script.string)
                        if isinstance(data, dict) and 'dateModified' in data:
                            update_date = data['dateModified']
                            break
                    except:
                        continue
            
            # Look for date patterns in divs ####
            if not update_date:
                date_divs = soup.find_all('div', string=re.compile(r'\w+ \d{1,2}, \d{4}'))
                if date_divs:
                    update_date = date_divs[0].get_text(strip=True)
            
            if update_date:
                # Clean and validate the date ####
                parsed_date = self.parse_play_store_date(update_date)
                if parsed_date:
                    return update_date, None
                else:
                    return None, f"Could not parse date: {update_date}"
            else:
                return None, "Update date not found on page"
                    
        except requests.exceptions.Timeout:
            return None, "Request timeout"
        except requests.exceptions.RequestException as e:
            return None, f"Network error: {str(e)}"
        except Exception as e:
            return None, f"Parsing error: {str(e)}"

    def add_package(self, package_name: str):
        # Add a new package to track ##############################################################################################################
        data = self.load_data()
        current_time = datetime.now().isoformat()
        
        if package_name in data:
            print(f"{Fore.BLUE}[*] Info{Fore.RESET} - Package {Fore.BLUE}{package_name}{Fore.RESET} is already being tracked.\n")
            return

        print(f"{Fore.YELLOW}[*] Fetching info for {package_name}...{Fore.RESET}")
        update_date, error = self.get_play_store_update_date(package_name)
        
        if error:
            print(f"{Fore.RED}[!] Error{Fore.RESET} - Cannot get update date for package {Fore.RED}{package_name}{Fore.RESET}")
            print(f"{Fore.RED}    Reason: {error}{Fore.RESET}\n")
            return

        data[package_name] = {
            'check_date': current_time,
            'last_update': update_date,
            'last_fetched': current_time,
            'fetch_count': 1,
            'last_error': ''
        }
        
        self.save_data(data)
        print(f"{Fore.GREEN}[+] Success{Fore.RESET} - Package {Fore.GREEN}{package_name}{Fore.RESET} added successfully!")
        print(f"{Fore.BLUE}[*] Info{Fore.RESET} - Last update: {Fore.BLUE}{update_date}{Fore.RESET}")
        print(f"{Fore.BLUE}[*] Info{Fore.RESET} - Started tracking on: {Fore.BLUE}{datetime.now().strftime('%Y-%m-%d %H:%M')}{Fore.RESET}\n")

    def delete_package(self, package_name: str):
        # Delete a package from tracking ##########################################################################################################
        data = self.load_data()
        if package_name in data:
            del data[package_name]
            self.save_data(data)
            print(f"{Fore.GREEN}[+] Success{Fore.RESET} - Package {Fore.GREEN}{package_name}{Fore.RESET} deleted successfully!\n")
        else:
            print(f"{Fore.RED}[!] Error{Fore.RESET} - Package {Fore.RED}{package_name}{Fore.RESET} doesn't exist in database\n")

    def list_packages(self):
        # List all tracked packages ###############################################################################################################
        data = self.load_data()
        if not data:
            print(f"{Fore.BLUE}[*] Info{Fore.RESET} - No packages are being tracked\n")
            return

        print(f"{Fore.CYAN}Tracked Packages ({len(data)}):{Fore.RESET}")
        print("-" * 50)
        for package_name, info in data.items():
            check_date = datetime.fromisoformat(info['check_date']).strftime('%Y-%m-%d %H:%M')
            print(f"{Fore.WHITE}{package_name}{Fore.RESET}")
            print(f"  Last update: {Fore.BLUE}{info['last_update']}{Fore.RESET}")
            print(f"  Tracking since: {Fore.BLUE}{check_date}{Fore.RESET}")
            if info.get('last_error'):
                print(f"  Last error: {Fore.RED}{info['last_error']}{Fore.RESET}")
            print()

    def check_updates(self):
        # Check updates for all tracked packages ##################################################################################################
        data = self.load_data()
        if not data:
            print(f"{Fore.BLUE}[*] Info{Fore.RESET} - Package database is empty\n")
            return

        print(f"{Fore.CYAN}Checking {len(data)} packages for updates...{Fore.RESET}\n")
        
        updates_found = 0
        errors_found = 0

        for i, (package_name, info) in enumerate(data.items(), 1):
            print(f"{Fore.YELLOW}[{i}/{len(data)}] Checking {package_name}...{Fore.RESET}")
            
            try:
                # Get current update date from Play Store ####
                current_update, error = self.get_play_store_update_date(package_name)
                
                # Update fetch statistics ####
                info['fetch_count'] = info.get('fetch_count', 0) + 1
                info['last_fetched'] = datetime.now().isoformat()
                
                if error:
                    info['last_error'] = error
                    errors_found += 1
                    print(f"{Fore.RED}[!] Error - {package_name}{Fore.RESET} - {error}\n")
                    continue
                
                info['last_error'] = ''
                old_update = info.get('last_update', '')
                
                # Compare dates ####
                if current_update != old_update and old_update:
                    # Parse dates ####
                    old_date = self.parse_play_store_date(old_update)
                    new_date = self.parse_play_store_date(current_update)
                    
                    if new_date and old_date and new_date > old_date:
                        print(f"{Fore.GREEN}[+] NEW UPDATE!{Fore.RESET} - {Fore.GREEN}{package_name}{Fore.RESET}")
                        print(f"    Previous: {Fore.BLUE}{old_update}{Fore.RESET}")
                        print(f"    Current:  {Fore.GREEN}{current_update}{Fore.RESET}")
                        updates_found += 1
                        info['last_update'] = current_update
                    else:
                        print(f"{Fore.BLUE}[*] No updates - {package_name}{Fore.RESET}")
                        print(f"    Last update: {Fore.BLUE}{old_update}{Fore.RESET}")
                        if current_update != old_update:
                            info['last_update'] = current_update
                else:
                    print(f"{Fore.BLUE}[*] No updates - {package_name}{Fore.RESET}")
                    if current_update:
                        print(f"    Last update: {Fore.BLUE}{current_update}{Fore.RESET}")
                        info['last_update'] = current_update

            except Exception as e:
                error_msg = f"Unexpected error: {str(e)}"
                info['last_error'] = error_msg
                errors_found += 1
                print(f"{Fore.RED}[!] Error - {package_name}{Fore.RESET} - {error_msg}")
            
            print()
        
        # Save updated data ####
        self.save_data(data)
        
        # Summary ####
        print(f"{Fore.CYAN}Check completed!{Fore.RESET}")
        print(f"Updates found: {Fore.GREEN}{updates_found}{Fore.RESET}")
        print(f"Errors: {Fore.RED}{errors_found}{Fore.RESET}")
        print(f"Last check: {Fore.BLUE}{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}{Fore.RESET}\n")

def main():
    # Banner ####
    print(f"{Fore.RED}+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+{Fore.RESET}")
    print(f"{Fore.RED}-{Fore.RESET}{Fore.WHITE}App Update Checker v0.2.0 - https://lautarovculic.com {Fore.RESET}{Fore.RED}-{Fore.RESET}")
    print(f"{Fore.RED}+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+{Fore.RESET}\n")

    # Help panel ####
    parser = argparse.ArgumentParser(description='Enhanced App Update Checker for Android Apps')
    parser.add_argument('-a', '--add', help='Package name to add for tracking')
    parser.add_argument('-d', '--delete', help='Package name to remove from tracking')
    parser.add_argument('-l', '--list', action='store_true', help='List all tracked packages')
    parser.add_argument('-c', '--check', action='store_true', help='Check for updates (default action)')

    args = parser.parse_args()
    
    try:
        checker = AppUpdateChecker()

        if args.add:
            checker.add_package(args.add)
        elif args.delete:
            checker.delete_package(args.delete)
        elif args.list:
            checker.list_packages()
        else:
            # Default action is to check updates ####
            checker.check_updates()
            
    except KeyboardInterrupt:
        print(f"\n{Fore.YELLOW}[!] Operation cancelled by user{Fore.RESET}")
        sys.exit(0)
    except Exception as e:
        print(f"{Fore.RED}[!] Unexpected error: {e}{Fore.RESET}")
        sys.exit(1)

if __name__ == "__main__":
    main()
