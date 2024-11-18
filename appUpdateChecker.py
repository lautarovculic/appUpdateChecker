#!/usr/bin/env python3

import os
import sys
import argparse
from datetime import datetime
import json
from typing import Dict, Optional
from colorama import init, Fore
import requests
from bs4 import BeautifulSoup

class AppUpdateChecker:
    def __init__(self):
        self.data_dir = os.path.expanduser("~/.local/share/appUpdateChecker")
        self.data_file = os.path.join(self.data_dir, "data.json")
        self.ensure_data_dir()
        self.load_data()

    def ensure_data_dir(self):
        # Ensure the data directory exists
        if not os.path.exists(self.data_dir):
            os.makedirs(self.data_dir, exist_ok=True)
        if not os.path.exists(self.data_file):
            self.save_data({})

    def load_data(self) -> Dict:
        # Load package data from JSON file
        try:
            with open(self.data_file, 'r') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return {}

    def save_data(self, data: Dict):
        # Save package data to JSON file
        with open(self.data_file, 'w') as f:
            json.dump(data, f, indent=2)

    def get_play_store_update_date(self, package_name: str) -> Optional[str]:
        # Get the last update date of an app from Play Store
        try:
            url = f"https://play.google.com/store/apps/details?id={package_name}"
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            response = requests.get(url, headers=headers)
            if response.status_code != 200:
                print(f"{Fore.RED}[!] Error{Fore.RESET} - Cannot get information about {Fore.RED}{package_name}{Fore.RESET}")
                return None

            soup = BeautifulSoup(response.text, 'html.parser')
            update_text = soup.find('div', string='Updated on').find_next('div').text
            return update_text
        except Exception as e:
            print(f"{Fore.RED}[!] Error{Fore.RESET} - Cannot get update date: {Fore.RED}{e}{Fore.RESET}\n")
            return None

    def add_package(self, package_name: str):
        # Add a new package to track
        data = self.load_data()
        current_date = datetime.now().strftime('%b %d, %Y')
        
        if package_name in data:
            print(f"{Fore.BLUE}[*] Info{Fore.RESET} - Package {Fore.BLUE}{package_name}{Fore.RESET} are already managed.\n")
            return

        update_date = self.get_play_store_update_date(package_name)
        if not update_date:
            print(f"{Fore.RED}[!] Error{Fore.RESET} - Cannot get update date for package {Fore.RED}{package_name}{Fore.RESET}\n")
            return

        data[package_name] = {
            'check_date': current_date,  # Start date
            'last_update': update_date   # Last update date
        }
        
        self.save_data(data)
        print(f"{Fore.GREEN}[+] Sucess{Fore.RESET} - Package {Fore.GREEN}{package_name}{Fore.RESET} added successfully!")
        print(f"{Fore.BLUE}[*] Info{Fore.RESET} - Last update: {Fore.BLUE}{update_date}{Fore.RESET}")
        print(f"{Fore.BLUE}[*] Info{Fore.RESET} - Checking date since: {Fore.BLUE}{current_date}{Fore.RESET}\n")

    def delete_package(self, package_name: str):
        # Delete a package from tracking
        data = self.load_data()
        if package_name in data:
            del data[package_name]
            self.save_data(data)
            print(f"{Fore.GREEN}[+] Sucess{Fore.RESET} - Package {Fore.GREEN}{package_name}{Fore.RESET} deleted successfully!\n")
        else:
            print(f"{Fore.RED}[!] Error{Fore.RESET} - Package {Fore.RED}{package_name}{Fore.RESET} doesn't exists in database\n")

    def check_updates(self):
        # Check updates for all tracked packages
        data = self.load_data()
        if not data:
            print(f"{Fore.BLUE}[*] Info{Fore.RESET} - Package database empty\n")
            return

        for package_name, info in data.items():
            try:
                last_update = datetime.strptime(info['last_update'], '%b %d, %Y')
                check_date = datetime.strptime(info['check_date'], '%b %d, %Y')

                if last_update <= check_date:
                    print(f"{Fore.BLUE}[*] Info - {package_name}{Fore.RESET} - There aren't new updates since last tracking: {Fore.BLUE}({info['check_date']}){Fore.RESET}")
                    print(f"Last update: {Fore.BLUE}{info['last_update']}{Fore.RESET}\n")
                else:
                    print(f"{Fore.GREEN}[+] NEW!{Fore.RESET} - {Fore.GREEN}{package_name}{Fore.RESET} - New update available! Updated: {Fore.GREEN}{info['last_update']}{Fore.RESET}")
                    print(f"Last date that you has checked: {Fore.RED}{info['check_date']}{Fore.RESET}\n")

                

                # Update last date
                current_update = self.get_play_store_update_date(package_name)
                if current_update and current_update != info['last_update']:
                    info['last_update'] = current_update
                    self.save_data(data)

            except Exception as e:
                print(f"{Fore.RED}[!] Error{Fore.RESET} - Cannot verify {Fore.RED}{package_name}{Fore.RESET}: {e}")
        
        
        # Sync last check
        print(f"{Fore.BLUE}[*] Info - Updating last check date to today{Fore.RESET}\n")
        current_date = datetime.now().strftime('%b %d, %Y')
        for package_name in data.keys():
            data[package_name]['check_date'] = current_date
        self.save_data(data)
        print(f"{Fore.GREEN}[+] Success{Fore.RESET} - All packages updated with today's date: {Fore.GREEN}{current_date}{Fore.RESET}\n")
        

def main():
    # Banner
    print(f"{Fore.RED}+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+{Fore.RESET}")
    print(f"{Fore.RED}-{Fore.RESET}{Fore.WHITE}App Update Checker v0.1.0 - Lautaro V. Culic' (lautarovculic.com){Fore.RESET}{Fore.RED}-{Fore.RESET}")
    print(f"{Fore.RED}+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+{Fore.RESET}\n")

    # Help panel
    parser = argparse.ArgumentParser(description='App Update Checker for Android Apps')
    parser.add_argument('-p', '--package', help='Package name to add')
    parser.add_argument('-d', '--delete', help='Package name to delete')

    args = parser.parse_args()
    checker = AppUpdateChecker()

    if args.package:
        checker.add_package(args.package)
    elif args.delete:
        checker.delete_package(args.delete)
    else:
        checker.check_updates()
    
    
##################### MAIN
if __name__ == "__main__":
    main()
