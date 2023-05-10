desc = """
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
now.strftime("%m-%d-%y")

# Default config
config = {
    "folder": "",
    "location": f"meetdown-{now}.md",
    "tmp": "meetdown-tmp.md",
    "id": "👤",
    "desc": "👤 person",
    "tracker": {
        "id": "jira",
        "url": "https://frontdeskhq.atlassian.net/jira/software/c/projects/FD/boards/7/backlog?view=detail&selectedIssue="
    },
    "ctx": [
        {"[ ]":  "[ ] in-progress"},
        {"✅":  "✅ completed"},
        {"❌":  "❌ blocker"},
        {"💩":  "💩 bs"}
    ],
    "ctx-itm-lbl-enabled": 0, # 0 = disabled, 1 = enabled shows lbls
}
default_username = getpass.getuser()
default_folder = config['folder']
default_location = config['location']
default_root_elements = []  # Default list of users or use  --users flag separated by commas

# Name of the temporary file
tmp_filename = config['tmp']

def generate_options():
    add_opts = []
    remove_opts = []
    other_opts = []

    if config['ctx-itm-lbl-enabled']:
      for i, ctx in enumerate(config['ctx'], start=1):
          for symbol, description in ctx.items():
              add_opts.append(f"{i}. Add {description}")
      for i, ctx in enumerate(config['ctx'], start=i+1):
          for symbol, description in ctx.items():
              remove_opts.append(f"{i}. Remove {description}")
      
      other_opts.append(f"{i+1}.Save & Quit")
      other_opts.append(f"{i+2}.Load")
      other_opts.append(f"{i+3}.Upload")
    else:
      for i, ctx in enumerate(config['ctx'], start=1):
          for symbol, description in ctx.items():
              add_opts.append(f"{i}. Add {symbol}")
      for i, ctx in enumerate(config['ctx'], start=i+1):
          for symbol, description in ctx.items():
              remove_opts.append(f"{i}. Remove {symbol}")
      
      other_opts.append(f"{i+1}.Save & Quit")
      other_opts.append(f"{i+2}.Load")
      other_opts.append(f"{i+3}.Upload")
      
    return "\n".join(["\t".join(add_opts), "\t".join(remove_opts), "\t".join(other_opts)])

opts = f"\n________________________\n\n{generate_options()}\n"

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

def toTrackerMarkdownURL(ticket):
    return f"[{ticket}]({config['tracker']['url']}{ticket})"

def add_root():
    new_root = input("Enter name of new entity: ")
    # Initialize an empty list for each category in config's context
    md_data[new_root] = {list(ctx.keys())[0]: [] for ctx in config['ctx']}
    default_root_elements.append(new_root)
    print(f"➕  '{new_root}'")

def remove_root():
    entity_index = select_root()
    if entity_index is None:
        return
    selected_entity = default_root_elements[entity_index]
    default_root_elements.pop(entity_index)
    md_data.pop(selected_entity)
    print(f"➖  '{selected_entity}'")

def select_root():
    for i, entity in enumerate(default_root_elements, start=1):
        print(f"{i}. {entity}")
    entity_index = input(f"Select a ${entity} by entering the number, or press Enter to return to main menu: ")
    if entity_index == '':  # if entity input is empty, return to main menu
        return None
    entity_index = int(entity_index) - 1
    if entity_index < 0 or entity_index >= len(default_root_elements):
        print("⛔ Invalid selection.")
        return None
    return entity_index

def add_item(category):
    entity_index = select_root()
    if entity_index is None:
        return
    selected_entity = default_root_elements[entity_index]
    
    is_jira = input("Is this a Jira ticket? (y/n, default: n): ").lower() 
    if is_jira == '':  # if entity input is empty, return to main menu
        return
    is_jira = is_jira == 'y'
    jira_ticket = ""
    if is_jira:
        jira_ticket = input("Enter Jira ticket name: ")
    description = input(f"Enter {category} description: ")
    if description == '':  # if entity input is empty, return to main menu
        return
    md_data[selected_entity][category].append({
        "jira_ticket": jira_ticket,
        "description": description
    })

def remove_item(category):
    entity_index = select_root()
    if entity_index is None:
        return
    selected_entity = default_root_elements[entity_index]
    items = md_data[selected_entity][category]
    if not items:
        print(f"No {category} items to remove.")
        return
    print(f"{selected_entity}'s {category} items:")
    for i, item in enumerate(items, start=1):
        print(f"{i}. {item['description']}")
    item_index = input(f"Enter the number of the {category} item to remove, or press Enter to return to main menu: ")
    if item_index == '':  # if entity input is empty, return to main menu
        return
    item_index = int(item_index) - 1
    items.pop(item_index)
    print(f"{category} item removed.")

def save_to_file():
    save_location = input(f"Enter save location (default: meetdown-{now}.md): ") or f"meetdown-{now}.md"
    with open(f"{default_folder}{save_location}", "w") as file:
        for entity, data in md_data.items():
            file.write(f"## {entity}\n\n")
            file.write("| Category | Jira Ticket | Description |\n")
            file.write("|----------|-------------|-------------|\n")
            no_items = True
            for category, items in data.items():
                  for item in items:
                      no_items = False
                      jira_ticket = toTrackerMarkdownURL(item["jira_ticket"]) if item["jira_ticket"] else ""
                      file.write(f"| {category} | {jira_ticket} | {item['description']} |\n")
            if no_items:
              file.write("| - | - | - |\n")
              
    print(f"Saved to:\n{default_folder}{save_location}\n")

def load_from_markdown(file_path):
    global md_data, default_root_elements

    if not os.path.isfile(file_path.strip()):
      print(f"Error: No such file or directory: '{file_path.strip()}'")
      return

    with open(file_path, 'r') as file:
        md = file.read()

    html = markdown.markdown(md, extensions=['tables'])
    soup = BeautifulSoup(html, features="html.parser")

    md_data = {}
    default_root_elements = []

    current_entity = None
    for h2 in soup.find_all('h2'):
        entity = h2.get_text()
        default_root_elements.append(entity)
        md_data[entity] = {"[ ]": [], "✅": [], "❌": []}
        current_entity = entity

        table = h2.find_next_sibling('table')
        if table is None:
            print(f"Warn: No table found for entity {current_entity}. Skipping...")
            continue

        for row in table.find_all('tr')[1:]:
            cells = row.find_all('td')
            status = cells[0].get_text().strip()
            if status not in md_data[current_entity]:
                print(f"Warn: Invalid status '{status}' for entity {current_entity}. Skipping...")
                continue

            jira_ticket = cells[1].get_text().strip()
            description = cells[2].get_text().strip()

            md_data[current_entity][status].append({
                "jira_ticket": jira_ticket if jira_ticket != '-' else '',
                "description": description
            })
    return md_data, default_root_elements

def save_to_markdown(filename):
    with open(filename, "w") as file:
        for entity, data in md_data.items():
            file.write(f"## {entity}\n\n")
            file.write("| Category | Jira Ticket | Description |\n")
            file.write("|----------|-------------|-------------|\n")
            no_items = True
            for category, items in data.items():
                for item in items:
                    no_items = False
                    jira_ticket = toTrackerMarkdownURL(item["jira_ticket"]) if item["jira_ticket"] else ""
                    file.write(f"| {category.capitalize()} | {jira_ticket} | {item['description']} |\n")
            if no_items:
                file.write("| - | - | - |\n")
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
        print(f"Error while creating gist, status code: {response.status_code}")

def ensure_default_ctx_items_exist_in_md_data():
  global md_data, default_records
  for record in md_data:
    for ctx in config['ctx']:
        category = list(ctx.keys())[0]
        if category not in md_data[record]:
            md_data[record][category] = []

def meetdown(args):
    global md_data, default_records
    while True:
        ensure_default_ctx_items_exist_in_md_data()
        os.system('clear')
        print(f"{desc}\n@{default_location}\n")
        # Preview
        print(f"# {now}\n")
        for entity, data in md_data.items():
            print(f"\n## {entity}\n")
            print("| Status | Jira Ticket | Description |")
            print("|----------|-------------|-------------|")
            no_items = True
            for category, items in data.items():
                for item in items:
                    no_items = False
                    jira_ticket = toTrackerMarkdownURL(item["jira_ticket"]) if item["jira_ticket"] else ""
                    print(f"| {category.capitalize()} | {jira_ticket} | {item['description']} |")
            if no_items:
                print("| - | - | - |")

        # Prompt user for an option
        print(opts) 
        selected_option = input("Select an option by entering the number: ")
        if not selected_option:
            save_to_markdown(config['tmp'])
            break
        try:
            selected_option = int(selected_option)
        except ValueError:
            print("Invalid option. Please try again.")
            continue
        
        ctx_length = len(config['ctx'])
        if 1 <= selected_option <= ctx_length:
            # Add ctx item
            ctx_idx = selected_option - 1
            category = list(config['ctx'][ctx_idx].keys())[0]
            add_item(category)
        elif ctx_length+1 <= selected_option <= 2*ctx_length:
            # Remove ctx item
            ctx_idx = selected_option - ctx_length - 1
            category = list(config['ctx'][ctx_idx].keys())[0]
            remove_item(category)
        elif selected_option == 2*ctx_length + 1:
             # Save ctx to markdown
            save_to_file()
            break
        elif selected_option == 2*ctx_length + 2:
             # Load ctx from markdown
            file_path = input("Enter the path of the Markdown file to load: ")
            md_data, default_records = load_from_markdown(file_path)
        elif selected_option == 2*ctx_length + 3:
             # Save ctx & upload to gist
            gist_desc = input("Enter a description for your `gist`: ")
            save_to_markdown(config['tmp'])
            upload_to_gist(config['tmp'], gist_desc)
        else:
            print(f"`${selected_option}` is an invalid option. \nEnter any number 1-{2*ctx_length+3} and hit return or hit return again to stash & exit")


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
    load_from_markdown(tmp_filename)
else:
    md_data = {entity: {list(ctx.keys())[0]: [] for ctx in config['ctx']} for entity in args.entities}
    default_root_elements = args.entities
    default_location = args.title
    default_folder = args.out

clear_screen()

meetdown(args)

