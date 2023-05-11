name = """
┌┬┐┌─┐┌─┐┌┬┐┌┬┐┌─┐┬ ┬┌┐┌
│││├┤ ├┤  │  │││ │││││││
┴ ┴└─┘└─┘ ┴ ─┴┘└─┘└┴┘┘└┘
________________________
"""
import os
import getpass
import requests
import json
import argparse
import datetime
import markdown
from bs4 import BeautifulSoup

# Global
md_data = {}

now = datetime.datetime.now()
now.strftime("%m-%d-%Y-")

# Default config
config = {
    "debug": 0,
    "folder": f"{os.getcwd()}",
    "location": f"meetdown.md",
    "tmp": ".meetdown.md",
    "id": "👤",
    "desc": "👤 person",
    "prompt-main": "Select an option by number",
    "external": {
        "id": "jira",
        "url": "https://frontdeskhq.atlassian.net/jira/software/c/projects/FD/boards/7/backlog?view=detail&selectedIssue="
    },
    "ctx": [
        {"⬜":  "⬜ todo"},
        {"🛠️":  "🛠️ in-progress"},
        {"🔎":  "🔎 qa"},
        {"✅":  "✅ done"},
        {"🚫":  "🚫 blocked"},
    ],
    "ctx-itm-lbl-enabled": 0
}

default_username = getpass.getuser()
default_folder = config['folder']
default_location = config['location']
default_root_elements = []  # Default list of users or use  --users flag separated by commas

# Name of the temporary file
tmp_filename = config['tmp']

def itemTypes(config):
    dynamic_object_keys = []

    for obj in config['ctx']:
        for key in obj:
            dynamic_object_keys.append(key)

    return dynamic_object_keys

def generate_options():
    opts = []

    i = 0
    opts.append(f"{i+1}. Add")
    opts.append(f"{i+2}. Remove")
    opts.append(f"{i+3}. Toggle")
    opts.append(f"{i+4}. Load")
    opts.append(f"{i+5}. Save & Quit")
    
    if config['debug']:
      opts.append(f"{i+6}. Upload")
        
    return "\n".join(["\n".join(opts)])

def parse_arguments():
    parser = argparse.ArgumentParser(description='Process command-line arguments.')
    parser.add_argument('--title', type=str, default=f"standup-{now}", help='Title (default: aws-p13.md)')
    parser.add_argument('--entities', type=str, default='philipbroadway', help='List of entities separated by commas (example: pike13,aws-sales)')
    parser.add_argument('--out', type=str, default="", help='Save directory path (default: empty string)')

    args = parser.parse_args()

    if args.entities:
        args.entities = args.entities.split(',')

    return args

def clear_screen():
    if os.name == 'posix':
        os.system('clear')
    elif os.name == 'nt':
        os.system('cls')

def external():
    return config['external']['id']

def toTrackerMarkdownURL(ticket):
    return f"[{ticket}]({config['external']['url']}{ticket})"

def toggle():
    # First, create a flat list of all items
    all_items = []
    for entity, data in md_data.items():
        for category, items in data.items():
            for item in items:
                all_items.append((entity, category, item))

    # If there are no items, return
    if not all_items:
        print("No items to toggle.")
        return

    # Now, print all items and let the user select one
    for i, (entity, category, item) in enumerate(all_items, start=1):
        print(f"{i}. {entity} - {category} - {item['description']}")
    item_index = input(f"Toggle {entity} {category} to?: ")
    if item_index == '':  # if input is empty, return to main menu
        return
    item_index = int(item_index) - 1

    # Get the selected item and its details
    entity, from_category, item = all_items[item_index]

    # Now, let the user select the new category
    for i, ctx in enumerate(config['ctx'], start=1):
        print(f"{i}. {list(ctx.keys())[0]}")
    to_category_index = input("Select the new category of the item by entering the number: ")
    if to_category_index == '':  # if input is empty, return to main menu
        return
    to_category_index = int(to_category_index) - 1
    to_category = list(config['ctx'][to_category_index].keys())[0]

    # Now, remove the item from the old category and add it to the new one
    md_data[entity][from_category].remove(item)
    md_data[entity][to_category].append(item)
    print(f"Item toggled from {from_category} to {to_category}.")

def addable_items():
    # First, create a flat list of all items
    all_items = []
    for entity, data in md_data.items():
        for category, items in data.items():
            for item in items:
                all_items.append((entity, category, item))
    return all_items

def add():
    # Get the list of all types of items
    item_types = itemTypes(config)
    item_count = 1
    # Print all item types and let the user select one
    items = []
    print(f"______________\n\nAdd\n")
    for i, item_type in enumerate(item_types, start=1):
        for n, entity in enumerate(default_root_elements, start=1):
          if item_count == 1:
            items = [{"index": 1, "entity": entity, "item_type": item_type}]
          item_count += 1
          print(f"{item_count}. {entity}-{item_type}")
          items.append({"index": i, "entity": entity, "item_type": item_type})
    item_count += 1
    print(f"{item_count}. {config['id']}")
    items.append({"index": i+1, "entity": config['id'], "item_type": config['id']})
    
    item_type_index = input("\nEnter number: ")
    if item_type_index == '':  # if input is empty, return to main menu
        return

    item = items[int(item_type_index) - 1]
    
    selected_entity = item['entity']
    selected_item_type = item['item_type']
    selected_item_index = item['index']

    if selected_entity == config['id']:
      new_root = input(f"Enter name for {config['desc']}: ")
      # Initialize an empty list for each category in config's context
      md_data[new_root] = {list(ctx.keys())[0]: [] for ctx in config['ctx']}
      default_root_elements.append(new_root)
      print(f"➕  '{new_root}'")

    else:
      # Ask for the details of the new item
      is_tracker = input(f"Is this a {external().capitalize()} ticket? (y/n): ").lower() 
      if is_tracker == 'y':
          tracker_ticket = input(f"Enter {external().capitalize()} ID (ex: FD-12234): ")
      else:
          tracker_ticket = ''
      description = input(f"Enter {selected_item_type} description: ")
      if description == '':  # if input is empty, return to main menu
          return

      # Add the new item to the selected category for the selected entity
      md_data[selected_entity][selected_item_type].append({
          "tracker_ticket": tracker_ticket,
          "description": description
      })

      print(f"New {selected_item_type} item added for {selected_entity}.")

def remove():
    # Get the list of all types of items
    item_types = itemTypes(config)
    item_count = 0
    # Print all item types and let the user select one
    items = []
    for i, item_type in enumerate(item_types, start=1):
        for n, entity in enumerate(default_root_elements, start=1):
          item_count += 1
          print(f"{item_count}. Remove {item_type} for {entity}")
          items.append({"index": i, "entity": entity, "item_type": item_type})
    item_count += 1
    print(f"{item_count}. Remove {config['id']}")
    items.append({"index": i+1, "entity": config['id'], "item_type": config['id']})
    
    item_type_index = input("Enter the number of the action to perform: ")
    if item_type_index == '':  # if input is empty, return to main menu
        return

    item = items[int(item_type_index) - 1]
    
    selected_entity = item['entity']
    selected_item_type = item['item_type']
    selected_item_index = item['index']

    if selected_entity == config['id']:
      entity_index = select_root()
      if entity_index is None:
          return
      selected_entity = default_root_elements[entity_index]
      default_root_elements.pop(entity_index)
      md_data.pop(selected_entity)
      print(f"➖  '{selected_entity}'")
      # remove_root()

    else:
      # Ask for the details of the new item
      is_tracker = input(f"Is this a {external().capitalize()} ticket? (y/n): ").lower() 
      if is_tracker == 'y':
          tracker_ticket = input(f"Enter {external().capitalize()} ID (ex: FD-12234): ")
      else:
          tracker_ticket = ''
      description = input(f"Enter {selected_item_type} description: ")
      if description == '':  # if input is empty, return to main menu
          return

      # Add the new item to the selected category for the selected entity
      md_data[selected_entity][selected_item_type].append({
          "tracker_ticket": tracker_ticket,
          "description": description
      })

      print(f"New {selected_item_type} item added for {selected_entity}.")


def add_root():
    new_root = input("Enter name of new entity: ")
    # Initialize an empty list for each category in config's context
    md_data[new_root] = {list(ctx.keys())[0]: [] for ctx in config['ctx']}
    default_root_elements.append(new_root)
    print(f"➕  '{new_root}'")

def select_root():
    for i, entity in enumerate(default_root_elements, start=1):
        print(f"{i}. {entity}")
    entity_index = input(f"Select a {config['desc']} by entering the number, or press Enter to return to main menu: ")
    if entity_index == '':  # if entity input is empty, return to main menu
        return None
    entity_index = int(entity_index) - 1
    if entity_index < 0 or entity_index >= len(default_root_elements):
        print("⛔ Invalid selection.")
        return None
    return entity_index

def save_to_file():
    save_location = input(f"Enter save location (default: meetdown-{now}.md): ") or f"meetdown-{now}.md"
    with open(f"{default_folder}{save_location}", "w") as file:
        interval = 0
        for entity, data in md_data.items():
            new_line = "\n" if interval > 0 else ""
            file.write(f"{new_line}## {entity}\n\n")
            file.write(f"| Category | {external().capitalize()} Ticket | Description |\n")
            file.write("|----------|-------------|-------------|\n")
            no_items = True
            for category, items in data.items():
                  for item in items:
                      no_items = False
                      tracker_ticket = toTrackerMarkdownURL(item["tracker_ticket"]) if item["tracker_ticket"] else ""
                      file.write(f"| {category} | {tracker_ticket} | {item['description']} |\n")
            file.write("\n")
            interval += 1
    print(f"\n💾:\n{default_folder}{save_location}\n")

def load_from_markdown(file_path):
    global md_data, default_root_elements, config

    if not os.path.isfile(file_path.strip()):
      print(f"Error: No such file or directory: '{file_path.strip()}'")
      return

    with open(file_path, 'r') as file:
        md = file.read()

    html = markdown.markdown(md, extensions=['tables'])
    soup = BeautifulSoup(html, features="html.parser")

    data = {}
    default_root_elements = []

    current_entity = None
    for h2 in soup.find_all('h2'):
        entity = h2.get_text()
        default_root_elements.append(entity)

        # Initialize data[entity] based on the config's ctx
        data[entity] = {list(ctx.keys())[0]: [] for ctx in config['ctx']}
        current_entity = entity

        table = h2.find_next_sibling('table')
        if table is None:
            print(f"Warn: No table found for entity {current_entity}. Skipping...")
            continue

        for row in table.find_all('tr')[1:]:
            cells = row.find_all('td')
            status = cells[0].get_text().strip()

            # If status not in data[current_entity], add it dynamically
            if status not in data[current_entity]:
                print(f"Info: New status '{status}' found for entity {current_entity}. Adding it...")
                config['ctx'].append({status: status})
                data[current_entity][status] = []

            jira_ticket = cells[1].get_text().strip()
            description = cells[2].get_text().strip()

            data[current_entity][status].append({
                "jira_ticket": jira_ticket if jira_ticket != '-' else '',
                "description": description
            })
    md_data = data
    return data, default_root_elements




def save_to_markdown(filename):
    with open(filename, "w") as file:
        # First, write the default_root_elements
        # file.write(f"default_root_elements: {', '.join(default_root_elements)}\n\n")
        interval = 0
        for entity, data in md_data.items():
            new_line = "\n\n" if interval > 0 else ""
            file.write(f"{new_line}## {entity}\n\n")
            file.write(f"| Category | {external().capitalize()} Ticket | Description |\n")
            file.write("|----------|-------------|-------------|\n")
            no_items = True
            for category, items in data.items():
                for item in items:
                    no_items = False
                    tracker_ticket = toTrackerMarkdownURL(item["tracker_ticket"]) if item["tracker_ticket"] else ""
                    file.write(f"| {category.capitalize()} | {tracker_ticket} | {item['description']} |\n")
            
    print(f"\nkthx👋\n")

def upload_to_gist(filename, description=""):
    with open(filename, 'r') as file:
        content = file.read()

    gist = {
        "description": description,
        "public": True,
        "files": {
            filename: {
                "content": content
            }
        }
    }

    # Make a POST request to the Gists API
    response = requests.post(
        'https://api.github.com/gists',
        headers={
            'Authorization': 'token your_token'
        },
        data=json.dumps(gist)
    )

    if response.status_code == 201:
        print(f"Gist created successfully! URL: {response.json()['html_url']}")
    else:
        print(f"⛔ Error while creating gist, status code: {response.status_code}")

def ensure_default_ctx_items_exist_in_md_data():
  global md_data, default_records
  for record in md_data:
    for ctx in config['ctx']:
        category = list(ctx.keys())[0]
        if category not in md_data[record]:
            md_data[record][category] = []

def meetdown(args):
    global md_data, default_root_elements
    md_data = {entity: {list(ctx.keys())[0]: [] for ctx in config['ctx']} for entity in args.entities}
    default_root_elements = args.entities
    while True:
        ensure_default_ctx_items_exist_in_md_data()
        os.system('clear')
        print(f"{name}")
        # Preview
        if config["ctx-itm-lbl-enabled"]:
            print(f"\n@{default_location}\n")
            print(f"#{now}\n")
        for entity, data in md_data.items():
            print(f"\n## {entity}\n")
            print(f"| Status | {external().capitalize()} | Description |")
            print("|----------|-------------|-------------|")
            no_items = True
            for category, items in data.items():
                for item in items:
                    no_items = False
                    tracker_ticket = toTrackerMarkdownURL(item["tracker_ticket"]) if item["tracker_ticket"] else ""
                    print(f"| {category.capitalize()} | {tracker_ticket} | {item['description']} |")
            if no_items:
                print("| - | - | - |")

        # Prompt user for an option
        print(f"________________________\n\nOptions:\n\n{generate_options()}\n") 
        selected_option = input(f"{config['prompt-main']}: ")
        
         # If user hits return with no input, save the temporary file and exit
        if not selected_option:
            ensure_default_ctx_items_exist_in_md_data()
            save_to_markdown(config['tmp'])
            break
        
        try:
            selected_option = int(selected_option)
        except ValueError:
            print("Invalid option. Please try again.")
            continue
        
        ctx_length = len(config['ctx'])
        if selected_option == 1:
            # Add ctx item
            add()
        elif selected_option == 2:
            # Remove ctx item
            remove()
        elif selected_option == 3:
            # Toggle item
            toggle()
        elif selected_option == 4:
            # Load ctx from markdown
            file_path = input("Enter the path of the Markdown file to load: ")
            load_from_markdown(file_path)
        elif selected_option == 5:
            # Save ctx to markdown
            save_to_file()
            break
        elif selected_option == 6:
            # Save ctx & upload to gist
            gist_desc = input("Enter a description for your `gist`: ")
            save_to_markdown(config['tmp'])
            upload_to_gist(config['tmp'], gist_desc)
        else:
            print(f"`${selected_option}` is an invalid option. \nEnter any number 1-{2*ctx_length+5} and hit return or hit return again to stash & exit")


def main():
    args = parse_arguments()

    # Initialize tmp_file_found and tmp_file_action
    tmp_file_found = False
    tmp_file_action = 0

    # Check for temp file at the start of the program
    if os.path.exists(tmp_filename):
        tmp_file_found = True
        print(f"Temporary file {tmp_filename} found.")
        print("1. Load from temporary file")
        print("2. Delete temporary file")
        tmp_file_action = int(input("Select an option by entering the number: "))
        if tmp_file_action == 1:
            md_data, default_root_elements = load_from_markdown(tmp_filename)
        elif tmp_file_action == 2:
            os.remove(tmp_filename)

    if tmp_file_found and tmp_file_action == 1:
        md_data, default_root_elements = load_from_markdown(tmp_filename)
    else:
        md_data = {entity: {list(ctx.keys())[0]: [] for ctx in config['ctx']} for entity in args.entities}
        default_root_elements = args.entities
        default_location = args.title
        default_folder = args.out

    clear_screen()

    meetdown(args)

if __name__ == "__main__":
    main()
