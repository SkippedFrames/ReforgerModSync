import requests
import json

def fetch_mod_info(mod_id):
    url = f"https://reforger.armaplatform.com/workshop/{mod_id}"
    response = requests.get(url)
    content = response.text
    start = content.find('<script id="__NEXT_DATA__" type="application/json">') + len('<script id="__NEXT_DATA__" type="application/json">')
    end = content.find('</script>', start)
    json_data = content[start:end].strip()
    data = json.loads(json_data)
    version = data['props']['pageProps']['asset']['currentVersionNumber']
    name = data['props']['pageProps']['asset']['name']
    return name, version

def add_mod(config):
    mod_id = input("Enter the mod ID to add: ")
    name, version = fetch_mod_info(mod_id)
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
        if mod['version'] == "":
            name, version = fetch_mod_info(mod['modId'])
            mod['version'] = version
            mod['name'] = name
            print(f"Updated {mod['modId']} to version {version} and name {name}")

def update_config_json():
    while True:
        try:
            config_file = input("Please enter the server config file name: ")
            with open(config_file, 'r') as file:
                config = json.load(file)
            break
        except FileNotFoundError:
            print("File not found. Please try again.")
        except KeyboardInterrupt:
            print("\nProgram terminated")
            return

    while True:
        print("\nChoose an option:")
        print("1. Add a mod by ID")
        print("2. Update mod versions and names")
        print("3. Exit")
        choice = input("Enter your choice (1, 2, or 3): ")

        if choice == '1':
            add_mod(config)
        elif choice == '2':
            update_mods(config)
        elif choice == '3':
            print("Exiting")
            break
        else:
            print("Invalid choice, Try again.")

        with open(config_file, 'w') as file:
            json.dump(config, file, indent=4)

update_config_json()
