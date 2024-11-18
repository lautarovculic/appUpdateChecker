# App Update Checker

A simple Python script to track the update status of Android apps on the Google Play Store. This tool allows you to add, delete, and check updates for packages, storing the data locally.

## Features

- Add Android app packages to a tracking list.
- Check the last update date of apps on the Google Play Store.
- Automatically update tracking information for apps.

## Requirements

- Python 3.x
- pip (Python's package manager)
    - colorama
    - requests
    - beautifulsoup4

## Installation

To install the script and its dependencies, run the following command:
```bash
curl -sSL https://raw.githubusercontent.com/lautarovculic/appUpdateChecker/main/install.sh | bash
```

This will:

    Download the script to /usr/local/bin/appUpdateChecker

# Usage

## Run the script
After installation, you can execute the script using:
```bash
appUpdateChecker
```

### Options
```text
Argument	Description
-p, --package	Add a package to the tracker.
-d, --delete	Remove a package from tracking.
```

# Install Dependencies
If you have issues with requeriments (requests, colorama, beautifulsoup4)
Install the required Python libraries:
```bash
pip install -r requirements.txt
```

## Examples

### Add a package
```bash
appUpdateChecker -p com.example.myapp
```

### Delete a package
```bash
appUpdateChecker -d com.example.myapp
```

### Check for updates
Simply run the script without arguments:
```bash
appUpdateChecker
```
# File Structure
The script stores its data in:
```bash
~/.local/share/appUpdateChecker/data.json
```

This file contains information about the tracked packages, including their last update date and the date they were added.

# License
This project is licensed under the WTFPL License.