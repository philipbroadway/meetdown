import time
import os
from meetdown_utils import MeetDownUtils
from meetdown_config import MeetDownConfig
from meetdown_parser import MeetDownParser
import redis
from bs4 import BeautifulSoup
import panflute as pf
import datetime
import argparse
import subprocess
ASCII = """
┌┬┐┌─┐┌─┐┌┬┐┌┬┐┌─┐┬ ┬┌┐┌
│││├┤ ├┤  │  │││ │││││││
┴ ┴└─┘└─┘ ┴ ─┴┘└─┘└┴┘┘└┘
________________________
"""
NAME = "#"


class MeetDown:
    @staticmethod
    def default_config():
        return MeetDownConfig.default_config()

    def __init__(self, config):
        self.config = config
        self.utils = MeetDownUtils(config)
        self.data = {}
        self.showing_help = True
        redis_host = os.environ.get('REDIS_HOST')
        redis_port = os.environ.get('REDIS_PORT')
        redis_password = os.environ.get('REDIS_PASSWORD')
        self.redis_client = redis.Redis(
            host=redis_host, port=redis_port, password=redis_password)

    def parse_arguments(self):
        now = self.utils.now()
        whoiam = self.utils.whoami()
        parser = argparse.ArgumentParser(
            description='Process command-line arguments.')
        parser.add_argument(
            '--title', type=str, default=f"meetdown-{now}", help='Title (default: aws-p13.md)')
        parser.add_argument('--entities', type=str, default=whoiam,
                            help='Comma separated people or entities (example: pike13,aws-sales)')
        parser.add_argument('--out', type=str, default=MeetDownUtils.pwd(),
                            help='Save directory path (default: empty string)')
        args = parser.parse_args()

        if args.entities:
            args.entities = args.entities.split(',')
        return args

    def states(self):
        # off, on, busy, warn, done, error
        return ["⚫", "⚪", "🔵", "🟡", "🟢", "🔴"]

    def status_types(self):
        types = []
        for obj in self.config['states']:
            for key in obj:
                types.append(key)
        return types

    def notify(self, message):
        if os.name == 'posix' and os.uname().sysname == 'Darwin':
            try:
                from pync import Notifier
            except ImportError:
                exit(1)

            # Need to know absolute path to script & mardown file
            # Notifier.notify('Is ? still ?', execute=python absolute/path/to/meetdown meetdown/file/path)'
            Notifier.notify(f"{message}")

        # else:
        #     print("This method is intended to run on macOS only.")

    def editables(self):
        result = []
        for entity in sorted(self.data.keys()):
            for category in self.data[entity].keys():
                category_index = 0
                for item in self.data[entity][category]:
                    result.append({
                        "entity": entity,
                        "category": category,
                        "item": item,
                        "category_index": category_index,
                        "external_ticket": item['external_ticket'],
                        "description": item['description']
                    })
                category_index += 1
        return result

    def external(self):
        return self.config['external']['id']

    def toMarkdownExternalURL(self, id):
        return f"[{id}]({self.config['external']['url']}{id})"

    def toggle_prompt(self):
        
        print("Toggle Options:\n\n1. Toggle owner\n2. Toggle status\n")
        selected_option = input("Enter a number: ")
        if not selected_option.isdigit():
            self.showing_help = True
            self.render_root_preview()
            return None
        
        if int(selected_option) == 1:
            self.showing_help = True
            self.render_root_preview()
            return self.reassign()

        # First, create a flat list of all items
        all_items = []
        for entity, data in sorted(self.data.items()):
            for category, items in data.items():
                for item in items:
                    all_items.append((entity, category, item))

        if not all_items:
            print("No items to toggle.")
            self.showing_help = True
            self.render_root_preview()
            return
        spacer = " "
        self.showing_help = False
        self.render_root_preview()
        print("Togglable items:\n")
        # Now, print all items and let the user select one
        for i, (entity, category, item) in enumerate(all_items, start=1):
            print(f"{spacer}{i}. {entity}-{category}-{item['description']}")

        item_index = input(f"\nToggle which item?: ")
        if item_index == '':  # if input is empty, return to main menu
            self.showing_help = True
            self.render_root_preview()
            return
        item_index = int(item_index) - 1

        # Get the selected item and its details
        entity, from_category, item = all_items[item_index]
        self.showing_help = False
        self.render_root_preview()
        # Now, let the user select the new category
        print(f"Toggle: {all_items[item_index][1]} {item['description']}\n")
        for i, states in enumerate(self.config['states'], start=1):
            


            print(f"{i}. {list(states.keys())[0]}")
        to_category_index = input(
            "\nSelect the new status by entering the number: ")
        if to_category_index == '':
            self.showing_help = True
            self.render_root_preview()
            return
        to_category_index = int(to_category_index) - 1
        to_category = list(self.config['states'][to_category_index].keys())[0]
        self.showing_help = True
        self.render_root_preview()
        self.toggle_status(entity, from_category, to_category, item)

    def toggle_status(self, entity, from_category, to_category, item):
        if to_category not in self.data[entity]:
            self.data[entity][to_category] = []
        if self.data[entity][from_category]:
            self.data[entity][from_category].remove(item)
        self.data[entity][to_category].append(item)

    def add_entity(self, entity):
        self.data[entity] = {list(states.keys())[0]: []
                             for states in self.config['states']}
        self.config['imported-states'].append(entity)
        if entity not in self.data:
            self.data[entity] = {}
            for category in self.config['states']:
                self.data[entity][list(category.keys())[0]] = []
        self.showing_help = True
        self.render_root_preview()

    def remove_entity(self, entity):
        if entity in self.data:
            del self.data[entity]

    def add_prompt(self):
        # Get the list of all types of items
        item_types = self.status_types()
        item_count = 0
        # Print all item types and let the user select one
        items = []
        print(f"{self.config['prompt-add']} options:\n")

        for i, item_type in enumerate(item_types, start=1):
            for n, entity in enumerate(sorted(self.data), start=1):
                item_count += 1
                print(f"{item_count}. {entity}-{item_type}")
                items.append(
                    {"index": item_count, "entity": entity, "item_type": item_type})
        item_count += 1
        print(f"{item_count}. {self.config['id']}")
        items.append({"index": item_count+1,
                     "entity": self.config['id'], "item_type": self.config['id']})

        item_type_index = input(f"\n{self.config['prompt-main']}: ")
        if item_type_index == '' or item_type_index.isdigit() == False:
            self.showing_help = True
            self.render_root_preview()
            return

        if int(item_type_index) - 1 > len(items):
            print(
                f"{self.config['invalid']}\nShould be between 1 and {len(items)}")
            self.showing_help = True
            self.render_root_preview()
            return
        self.showing_help = False
        self.render_root_preview()
        item = items[int(item_type_index) - 1]

        selected_entity = item['entity']
        selected_item_type = item['item_type']

        if selected_entity == self.config['id']:
            new_root = input(f"Enter name for {self.config['desc']}: ")
            # Initialize an empty list for each category in config's context
            self.add_entity(new_root)
            print(f"➕  '{new_root}'")

        else:
            # Ask for the details of the new item
            is_external = input(
                f"Is this a {self.external().capitalize()} ticket? (y/n): ").lower()
            if is_external == 'y':
                external_ticket = input(
                    f"Enter {self.external().capitalize()} ID (ex: FD-12234): ")
            else:
                external_ticket = ''
            description = input(f"Enter {selected_item_type} description: ")
            if description == '':  # if input is empty, return to main menu
                self.showing_help = True
                self.render_root_preview()
                return

            # Add the new item to the selected category for the selected entity
            self.add_item(selected_entity, selected_item_type,
                          external_ticket, description)

            print(f"New {selected_item_type} item added for {selected_entity}.")

    def add_item(self, entity, item_type, external_ticket, description):
        self.showing_help = True
        self.render_root_preview()
        self.data[entity][item_type].append({
            "external_ticket": external_ticket,
            "description": description
        })

    def edit_ticket_or_description(self, editable):
        ticket_or_description = input(
            "\nOptions:\n\n1. Edit Ticket\n2. Edit Description\n\nSelect an option by entering the number: ")
        if not ticket_or_description.isdigit():
            print("Invalid input. Please enter a number.")
            self.showing_help = True
            self.render_root_preview()
            return None, None, None
        ticket_or_description = 1 if int(ticket_or_description) == 1 else 2
        ticket_key = 'external_ticket' if ticket_or_description == 1 else 'description'
        self.showing_help = False
        self.render_root_preview()
        print(f"\nCurrent value: {editable[ticket_key]}")
        input_text = input(f"\nNew value: ")
        if input_text == '':
            self.showing_help = True
            self.render_root_preview()
            return None, None, None
        else:
            self.showing_help = True
            self.render_root_preview()
            return editable, ticket_or_description, input_text

    def edit_prompt(self):
        print("Edit Options:\n")
        for i, editable in enumerate(self.editables(), start=1):
            ticket = f"-{editable['external_ticket']}" if editable['external_ticket'] else ""
            print(
                f"{i}. {editable['entity']}-{editable['category']}{ticket}-{editable['description']}")

        selected_index = input(
            "\nSelect an editable item by entering the number: ")
        if not selected_index.isdigit():
            print(f"{self.config['invalid']}")
            self.showing_help = True
            self.render_root_preview()
            return None
        self.showing_help = False
        self.render_root_preview()
        selected_index = int(selected_index)
        if selected_index < 1 or selected_index > len(self.editables()):
            print(f"{self.config['invalid']}")
            self.showing_help = True
            self.render_root_preview()
            return None

        selected_editable = self.editables()[selected_index - 1]

        editable, ticket_or_description, input_text = self.edit_ticket_or_description(
            selected_editable)
        return self.edit(selected_editable, ticket_or_description, input_text)

    def edit(self, editable, option, new_value):
        data = self.data
        option_key = 'external_ticket' if option == 1 else 'description'
        print(f"Edit {option_key}: {editable[option_key]} -> {new_value}")
        for type in data[editable['entity']]:
            for i, item in enumerate(data[editable['entity']][type]):
                if item['external_ticket'] == editable['external_ticket'] and item['description'] == editable['description']:
                    print(
                        f"✅  {editable['entity']} - {type} - {new_value} -> {data[editable['entity']][type][i][option_key]}")
                    self.data[editable['entity']
                              ][type][i][option_key] = new_value
                    print(f"✅ {data[editable['entity']][type][i][option_key]}")
                    continue
        self.showing_help = True
        self.render_root_preview()
        return data, self.config

    def users(self):
        result = []
        for user in self.data:
            result.append(user)
        return result

    def reassign(self):
        self.showing_help = False
        self.render_root_preview()
        print("Togglable items:\n")
        for i, item in enumerate(self.editables(), start=1):
            print(
                f"{i}. {item['entity']}-{item['category']}-{item['description']}")

        selected_item_index = input(
            "\nEnter the number of the item to toggle: ")
        if not selected_item_index.isdigit():
            print(f"{self.config['invalid']}")
            self.showing_help = True
            self.render_root_preview()
            return None

        selected_item_index = int(selected_item_index)
        if selected_item_index < 1 or selected_item_index > len(self.editables()):
            print(f"{self.config['invalid']}")
            self.showing_help = True
            self.render_root_preview()
            return None

        selected_item = self.editables()[selected_item_index - 1]
        self.showing_help = False
        self.render_root_preview()
        print("Assignable Users:\n")
        for i, user in enumerate(self.users(), start=1):
            print(f"{i}. {user}")

        selected_user_index = input("\nSelect a user by entering the number: ")
        if not selected_user_index.isdigit():
            print(f"{self.config['invalid']}")
            self.showing_help = True
            self.render_root_preview()
            return None

        selected_user_index = int(selected_user_index)
        if selected_user_index < 1 or selected_user_index > len(self.data):
            print(f"{self.config['invalid']}")
            self.showing_help = True
            self.render_root_preview()
            return None

        selected_user = self.users()[selected_user_index - 1]

        self.assign_item_to_user(selected_item, selected_user)

    def assign_item_to_user(self, item, user):

        for key in self.data:
            for i in self.data[key][item['category']]:
                print(f"i: {i} item: {item}")
                if i == item['item']:
                    self.data[key][item['category']].remove(i)

        self.data[user][item['category']].append(item)
        self.showing_help = True

    def remove_prompt(self):
        # Prepare a list of all items, each entity and each entity's category items
        items = []
        item_count = 0
        padding = ""
        print(f"{self.config['prompt-remove']} options:\n")
        for entity, data in sorted(self.data.items()):
            # Append each entity to the list
            item_count += 1
            print(
                f"{padding}{padding}{item_count}. {self.config['id']} {entity}")
            items.append({
                "index": item_count,
                "entity": entity,
                "type": "entity"
            })

            # Append each entity's category items to the list
            for category, category_items in data.items():
                for category_index, item in enumerate(category_items):
                    item_count += 1
                    print(
                        f"{padding}{padding}{item_count}. {entity}-{category}-{item['description']}")
                    items.append({
                        "index": item_count,
                        "entity": entity,
                        "category": category,
                        "item": item,
                        "type": "item",
                        "category_index": category_index
                    })

        # Ask the user to select an item or entity to remove
        item_index = input("\nEnter the number of the item to remove: ")
        if item_index == '' or item_index.isdigit() == False:
            self.showing_help = True
            self.render_root_preview()
            return
        if self.config['debug']:
            print(f"data: {self.data}")
        item_index = int(item_index) - 1
        selected_item = items[item_index]

        if selected_item['type'] == 'entity':
            self.showing_help = True
            self.render_root_preview()
            self.remove_entity(selected_item['entity'])
        else:
            self.showing_help = True
            self.render_root_preview()
            self.remove_item(
                selected_item['entity'], selected_item['category'], selected_item['category_index'])

    def remove_item(self, entity, item_type, item_index):
        if self.data[entity][item_type][item_index] == None:
            self.showing_help = True
            self.render_root_preview()
            return
        self.data[entity][item_type].pop(item_index)

    def select_entity(self):
        for i, entity in enumerate(self.config['imported-states'], start=1):
            print(f"{i}. {entity}")
        entity_index = input(
            f"Select a {self.config['desc']} by entering the number, or press Enter to return to main menu: ")
        if entity_index == '':  # if entity input is empty, return to main menu
            return None
        entity_index = int(entity_index) - 1
        if entity_index < 0 or entity_index >= len(self.config['status-types']):
            print(self.config['error-invalid-entity'])
            return None
        return entity_index

    def save_to_file(self):
        now = self.utils.now()
        save_location = input(
            f"Enter filename (default: meetdown-{now}.md): ") or f"meetdown-{now}.md"

        if not save_location.endswith(".md"):
            save_location += ".md"
        self.ensure_default_states_items_exist_in_data()
        self.write(save_location, False)

    def save_to_redis(self):
        # Prompt user for Redis folder and filename
        folder_name = input("Enter Redis folder name: ")
        filename = input("Enter filename: ")

        # Save the Markdown data to Redis
        key = f"{folder_name}:{filename}"
        self.redis_client.set(key, self.data)

        print(f"Markdown data saved to Redis: {key}")

    def browse_redis(self):
        # Print the available Redis folders
        folders = self.redis_client.keys(pattern="*:*")
        folders = [folder.decode("utf-8").split(":")[0] for folder in folders]
        folders = sorted(set(folders))

        print("Available Redis folders:")
        for i, folder in enumerate(folders, start=1):
            print(f"{i}. {folder}")

        # Prompt user to select a folder
        folder_index = input("Enter the number of the folder to browse: ")
        if not folder_index:
            return

        folder_index = int(folder_index) - 1

        if folder_index < 0 or folder_index >= len(folders):
            print("Invalid folder index.")
            return

        selected_folder = folders[folder_index]

        # List the keys in the selected folder
        keys = self.redis_client.keys(pattern=f"{selected_folder}:*")

        print(f"\nKeys in folder '{selected_folder}':")
        for i, key in enumerate(keys, start=1):
            print(f"{i}. {key.decode('utf-8')}")

        # Prompt user to select a key
        key_index = input("Enter the number of the key to view: ")
        if not key_index:
            return

        key_index = int(key_index) - 1

        if key_index < 0 or key_index >= len(keys):
            print("Invalid key index.")
            return

        selected_key = keys[key_index].decode("utf-8")

        # Retrieve the Markdown data from Redis
        markdown_data = self.redis_client.get(selected_key)

        if markdown_data:
            self.data = markdown_data.decode("utf-8")
            print(f"\nMarkdown data for key '{selected_key}':\n")
            print(self.data)
        else:
            print("Markdown data not found.")

    def load_from_markdown(self, file_path):
        parser = MeetDownParser(self.config)
        data, config = parser.load_from_markdown(file_path)
        self.config = config
        self.data = data
        self.showing_help = True
        self.render_root_preview()
        return data, config

    def update_data_item_categories(self, data, category):
        if self.config['debug']:
            print(
                f"\n[before]update_data_item_categories:------\n\ndata: {data}")
            print(f"\ncategory: {category}")
        keys = [category]
        for entity in data.keys():
            entitity_keys = []
            for key in data[entity]:
                keys.append(key)
        unique_keys = set(keys)
        for entity in data.keys():
            for key in unique_keys:
                if key not in data[entity]:
                    data[entity][key] = []
        if self.config['debug']:
            print(
                f"\n[fater]update_data_item_categories:------\n\ndata: {data}")
            print(f"\ncategory: {category}")

    def kebob(self, text):
        return text.lower().replace(" ", "-")

    def toInternalLink(self, item):
        external_ticket = item["external_ticket"]
        if external_ticket:
            ref = self.kebob(external_ticket + "-ref")
            return f"[{external_ticket}][{ref}]"
        return ""

    def createInternalReferenceLink(self, item):
        external_ticket = item["external_ticket"]
        if external_ticket:
            ref = self.kebob(external_ticket + "-ref")
            return f"[{ref}]: {self.config['external']['url']}{external_ticket}"
        return ""

    def write(self, filename, buhbye=False):
        with open(filename, "w") as file:

            for line in self.preview(self.data):
                file.write(line)
        if buhbye:
            self.showing_help = False
            self.render_root_preview()
        subprocess.run("pbcopy", text=True,
                       input=f"{MeetDownUtils.pwd()}/{filename}")
        savetype = buhbye and "auto-saved" or "saved"
        print(
            f"({savetype}) 💾: {MeetDownUtils.pwd()}/{filename}\n")

    def ensure_default_states_items_exist_in_data(self):
        allkeys = self.states()
        for entity in self.data.keys():
            for key in self.data[entity]:
                allkeys.append(key)
        unique_keys = set(allkeys)

        for entity in self.data.keys():
            for key in unique_keys:
                if key not in self.data[entity]:
                    self.data[entity][key] = []
        args = self.parse_arguments()

        if args.entities:
            for entity in args.entities:
                if entity not in self.data.keys():
                    self.add_entity(entity)

        for record in args.entities:
            for entity in self.data.keys():
                if record not in self.data[entity]:
                    if self.config['debug']:
                        print(f"Adding {record} to {entity}")
                    self.data[entity][record] = []

    def preview(self, data, compact=False):
        now = self.utils.now()
        spacer = " " if compact else ""
        result = []
        if compact:
            result = [
                f"{self.states()[1]} MeetDown://{self.config['title']}{now}", ""]
        else:
            result = [f"{NAME} {self.config['title']} @ {now}", "\n\n"]
        interval = 0
        refs = []
        for entity, data in sorted(data.items()):
            new_line = "" if interval > 0 else ""
            result.append(f"{new_line}## {entity}")
            if not compact:
                result.append("\n")
                result.append("\n")
            has_items = False
            for category, items in data.items():
                if len(items) > 0:
                    has_items = True
                    break
            if has_items or not compact:
                result.append(
                    f"{spacer}| State | {self.external().capitalize()} Ticket | Description |\n")
                result.append(f"{spacer}{self.config['table-separator']}\n")

            for category, items in data.items():
                for item in items:
                    if item.get("external_ticket"):
                        refs.append(self.createInternalReferenceLink(item))
                        external_ticket = self.toInternalLink(item)
                        ticket = f"[{item['external_ticket']}]" if compact else external_ticket
                        if self.config['debug']:
                            print(
                                f"external_ticket: {external_ticket} item: {item}")
                        result.append(
                            f"{spacer}| {category} | {ticket} | {item['description']} |\n")
                    else:
                        result.append(
                            f"{spacer}| {category} |  | {item['description']} |\n")
            result.append("\n")
            interval += 1
        if len(refs) > 0:
            if not compact:
                result.append("### References\n\n")
                uniq_refs = list(set(refs))
                for ref in uniq_refs:
                    result.append(f"{ref}\n")
        return result

    def render_terminal_preview(self, config, data, compact=False):
        result = []

        previews = self.preview(data, True)
        for preview in previews:
            result.append(preview.replace("\n", ""))

        result.append(
            "_________________________________________________________________________________________________________\n")
        if self.showing_help:
            if self.config['debug']:
                result.append(
                    f"{self.config['separator-1']}\n\nOptions:\n\n{MeetDownConfig.generate_options(self.config)}")
            else:
                result.append(
                    f"Options: {MeetDownConfig.generate_options(self.config)}")
        return result

    def render_root_preview(self):
        os.system('clear')
        # Preview
        previews = self.render_terminal_preview(
            self.config, self.data, True)
        for preview in previews:
            print(preview)

    def meetdown(self, args, config, data):
        self.data = data
        self.config['imported-states'] = args.entities
        self.ensure_default_states_items_exist_in_data()

        while True:

            self.render_root_preview()
            self.ensure_default_states_items_exist_in_data()
            selected_option = input(f"{self.config['prompt-main']}: ")

            # If user hits return with no input, kbai
            if not selected_option:
                self.ensure_default_states_items_exist_in_data()
                self.write(self.config['tmp'], True)
                break

            try:
                selected_option = int(selected_option)
                self.showing_help = False
                self.render_root_preview()
            except ValueError:
                print(f"\n{self.config['error-invalid-option']}\n")
                continue

            states_length = len(self.config['states'])
            if selected_option == 1:
                self.add_prompt()
            elif selected_option == 2:
                self.edit_prompt()
            elif selected_option == 3:
                file_path = input(f"{self.config['prompt-save-location']}: ")
                if not file_path:
                    self.showing_help = True
                    self.render_root_preview()
                    continue
                loaded_data, config = self.load_from_markdown(file_path)
                if loaded_data is not None and config is not None:
                    self.data = loaded_data
                    self.config = config
                    self.showing_help = True
                    self.render_root_preview()
            elif selected_option == 4:
                self.toggle_prompt()
            elif selected_option == 5:
                self.remove_prompt()
            elif selected_option == 6:
                self.save_to_file()
                break

            elif selected_option == 7:
                # Save states & upload to gist
                # gist_desc = input("Enter a description for your `gist`: ")
                # self.write( self.config['tmp'])
                # upload_to_gist(self.config['tmp'], gist_desc)
                print("Not implemented yet")
            else:
                print(f"`${selected_option}` is an invalid option. \nEnter any number 1-{2*states_length+5} and hit return or hit return again to stash & exit")

    def main(self):
        args = self.parse_arguments()

        # Check if the temporary file exists
        if os.path.exists(self.config['tmp']):
            self.utils.clear_screen()
            print(f"{ASCII}")
            # print(f"\n⚪ To create new  <Type a name & press return>\n⚪ To resume <Press return to resume>")
            title = input(
                f"Enter a name to create new meeting; Or press enter to resume previous meeting\n> ")
            empty_title = title == None or title == ""
            print(f"title: {title}")
            if empty_title:
                loaded_data, config = self.load_from_markdown(
                    self.config['tmp'])
                if self.config['debug']:
                    print(f'loaded_data: {loaded_data} config: {config}')
                # Load the data from the specified file
                if loaded_data is not None and config is not None:
                    self.data = loaded_data
                    self.config = config
            elif title:
                empty_title = True
                self.config['title'] = title
            else:
                # Display an error message and continue with default data
                print(
                    "Failed to load data from file. Continuing with default configuration.")
        self.utils.clear_screen()
        self.meetdown(args, self.config, self.data)


if __name__ == "__main__":
    meetdown = MeetDown(MeetDownConfig.default_config())
    meetdown.main()
