import requests
import json
import re

def fetch_mod_info(mod_id):
    url = f"https://reforger.armaplatform.com/workshop/{mod_id}"
    try:
        response = requests.get(url)
        response.raise_for_status()
    except requests.RequestException as e:
        print(f"Error fetching mod info: {e}")
        return None, None

    content = response.text
    start = content.find('<script id="__NEXT_DATA__" type="application/json">') + len('<script id="__NEXT_DATA__" type="application/json">')
    end = content.find('</script>', start)
    
    if start == -1 or end == -1:
        return None, None
    
    json_data = content[start:end].strip()
    try:
        data = json.loads(json_data)
        version = data['props']['pageProps']['asset']['currentVersionNumber']
        name = data['props']['pageProps']['asset']['name']
        return name, version
    except (json.JSONDecodeError, KeyError) as e:
        return None, None

def add_mod(config):
    mod_id = input("Enter the mod ID to add: ")
    name, version = fetch_mod_info(mod_id)
    if name is None or version is None:
        print("Failed to add mod. Please try again.")
        return

    new_mod = {
        "modId": mod_id,
        "name": name,
        "version": version
    }
    config['game']['mods'].append(new_mod)
    print(f"Added new mod: {name} with version {version}")

def update_mods(config):
    mods = config['game']['mods']
    for mod in mods:
        if not mod['version']:
            name, version = fetch_mod_info(mod['modId'])
            if name is None or version is None:
                print(f"Failed to update mod {mod['modId']}. Skipping.")
                continue
            mod['version'] = version
            mod['name'] = name
            print(f"Updated {mod['modId']} to version {version} and name {name}")

def load_config(config_file):
    try:
        with open(config_file, 'r') as file:
            return json.load(file)
    except FileNotFoundError:
        print("File not found. Please try again.")
        return None
    except json.JSONDecodeError as e:
        print(f"Error reading JSON file: {e}")
        return None

def save_config(config, config_file):
    try:
        with open(config_file, 'w') as file:
            json.dump(config, file, indent=4)
    except IOError as e:
        print(f"Error saving config file: {e}")

def parse_gproj_file(gproj_file):
    try:
        with open(gproj_file, 'r') as file:
            content = file.read()
        mod_ids = re.findall(r'"\b[0-9A-F]+\b"', content)
        return [mod_id.strip('"') for mod_id in mod_ids]
    except FileNotFoundError:
        print("gproj file not found. Please try again.")
        return None

def create_config_from_gproj(config, gproj_file):
    mod_ids = parse_gproj_file(gproj_file)
    if mod_ids is None:
        return
    
    for mod_id in mod_ids:
        name, version = fetch_mod_info(mod_id)
        if name is None or version is None:
            print(f"Failed to fetch info for mod ID {mod_id}. Skipping.")
            continue

        new_mod = {
            "modId": mod_id,
            "name": name,
            "version": version
        }
        config['game']['mods'].append(new_mod)
        print(f"Added mod: {name} with version {version}")

def update_config_json():
    config = None
    while config is None:
        config_file = input("Please enter the server config file name: ")
        config = load_config(config_file)
        if config is None:
            continue

    while True:
        print("\nChoose an option:")
        print("1. Add a mod by ID")
        print("2. Update mod versions and names")
        print("3. Add mod dependencies from gproj file to config")
        print("4. Exit")
        choice = input("Enter your choice (1, 2, 3, or 4): ")

        if choice == '1':
            add_mod(config)
        elif choice == '2':
            update_mods(config)
        elif choice == '3':
            gproj_file = input("Enter the gproj file name: ")
            create_config_from_gproj(config, gproj_file)
        elif choice == '4':
            save_config(config, config_file)
            print("Exiting")
            break
        else:
            print("Invalid choice, Try again.")

        save_config(config, config_file)

update_config_json()
