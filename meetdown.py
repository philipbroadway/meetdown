NAME="""
┌┬┐┌─┐┌─┐┌┬┐┌┬┐┌─┐┬ ┬┌┐┌
│││├┤ ├┤  │  │││ │││││││
┴ ┴└─┘└─┘ ┴ ─┴┘└─┘└┴┘┘└┘
________________________
"""
import os
import getpass
import argparse
import datetime
import re
import panflute as pf
from bs4 import BeautifulSoup
import re
import redis
from meetdown_parser import MeetDownParser

class MeetDown:
    @staticmethod
    def default_config():
        
        res = {
            "users": getpass.getuser(),
            "title": f".meetdown.md",
            "folder": f"{os.getcwd()}",
            "tmp": ".meetdown.md",
            "id": "👤",
            "desc": "👤 person",
            "prompt-type": "Option",
            "prompt-main": "Enter number",
            "prompt-add": "Add",
            "prompt-remove": "Remove",
            "prompt-toggle": "Toggle",
            "prompt-load": "Load",
            "prompt-save": "Save & Quit",
            "prompt-save-location": "Enter the path of the Markdown file to load",
            "external": {
                "id": "jira",
                "url": "https://frontdeskhq.atlassian.net/jira/software/c/projects/FD/boards/7/backlog?view=detail&selectedIssue="
            },
            "ctx": [
                {"⬜":  "⬜ todo"},
                {"✅":  "✅ done"},
                # mojii: https://emojidb.org
            ],
            "debug": 1,
            "tmpl": [
                {id: "⛔", "desc": "Invalid"}
            ],
            "status-types-selections-invalid": "⛔ Invalid selection.",
            "separator-1": "________________________",
            "separator-2": "______________",
            "table-header": "| ID  | $external_id | Description |",
            "table-header-divider": "----------",
            
        }
        res["table-separator"] = f"| {res['table-header-divider']} | {res['table-header-divider']} |"
        return res

    def __init__(self, config):
        self.config = config
        self.md_data = {}
        redis_host = os.environ.get('REDIS_HOST')
        redis_port = os.environ.get('REDIS_PORT')
        redis_password = os.environ.get('REDIS_PASSWORD')
        self.redis_client = redis.Redis(host=redis_host, port=redis_port, password=redis_password)

    def status_types(self):
        types = []
        for obj in self.config['ctx']:
            for key in obj:
                types.append(key)
        return types

    def generate_options(self):
        opts = []
        opts.append(f"1. {self.config['prompt-add']}")
        opts.append(f"2. {self.config['prompt-remove']}")
        opts.append(f"3. {self.config['prompt-toggle']}")
        opts.append(f"4. {self.config['prompt-load']}")
        opts.append(f"5. {self.config['prompt-save']}")
    
        if self.config['debug']:
          opts.append(f"6. Upload")
        
        return "\n".join(["\n".join(opts)])

    def parse_arguments(self):
      now = datetime.datetime.now()
      now.strftime("%m-%d-%Y-")
      parser = argparse.ArgumentParser(description='Process command-line arguments.')
      parser.add_argument('--title', type=str, default=f"standup-{now}", help='Title (default: aws-p13.md)')
      parser.add_argument('--entities', type=str, default='philipbroadway', help='List of entities separated by commas (example: pike13,aws-sales)')
      parser.add_argument('--out', type=str, default="", help='Save directory path (default: empty string)')

      args = parser.parse_args()

      if args.entities:
          args.entities = args.entities.split(',')

      return args

    def clear_screen(self):
      if os.name == 'posix':
          os.system('clear')
      elif os.name == 'nt':
          os.system('cls')

    def external(self):
        return self.config['external']['id']

    def toMarkdownExternalURL(self,id):
        return f"[{id}]({self.config['external']['url']}{id})"

    def toggle(self):
        # First, create a flat list of all items
        all_items = []
        for entity, data in self.md_data.items():
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
        for i, ctx in enumerate(self.config['ctx'], start=1):
            print(f"{i}. {list(ctx.keys())[0]}")
        to_category_index = input("Select the new category of the item by entering the number: ")
        if to_category_index == '':  # if input is empty, return to main menu
            return
        to_category_index = int(to_category_index) - 1
        to_category = list(self.config['ctx'][to_category_index].keys())[0]

        self.toggle_status(entity, from_category, to_category, item)

    def toggle_status(self, entity, from_category, to_category, item):
        if to_category not in self.md_data[entity]:
          self.md_data[entity][to_category] = []
        if self.md_data[entity][from_category]:
          self.md_data[entity][from_category].remove(item)
        self.md_data[entity][to_category].append(item)

    def add_entity(self, entity):
        self.md_data[entity] = {list(ctx.keys())[0]: [] for ctx in self.config['ctx']}
        self.config['status-types'].append(entity)
        if entity not in self.md_data:
            self.md_data[entity] = {}
            for category in self.config['ctx']:
                self.md_data[entity][list(category.keys())[0]] = []

    def remove_entity(self, entity):
        if entity in self.md_data:
          del self.md_data[entity]
          #self.config['status-types'].remove(entity)

    def add(self):
        # Get the list of all types of items
        item_types = self.status_types()
        item_count = 0
        # Print all item types and let the user select one
        items = []
        print(f"{self.config['separator-2']}\n\n{self.config['prompt-add']}\n")
        
        for i, item_type in enumerate(item_types, start=1):
            for n, entity in enumerate(self.md_data, start=1):
              # print(f"{n}. {entity}-{item_type}")
              if item_count <= 1:
                items = [{"index": 1, "entity": entity, "item_type": item_type}]
              item_count += 1
              print(f"{item_count}. {entity}-{item_type}")
              items.append({"index": i, "entity": entity, "item_type": item_type})
        item_count += 1
        print(f"{item_count}. {self.config['id']}")
        items.append({"index": i+1, "entity": self.config['id'], "item_type": self.config['id']})
        
        item_type_index = input(f"\n{self.config['prompt-main']}: ")
        if item_type_index == '' or  item_type_index.isdigit() == False:
            return
        
        if int(item_type_index) > len(items):
          print(f"Please select a number between 1 and {len(items)}")
          return

        item = items[int(item_type_index) - 1]
        
        selected_entity = item['entity']
        selected_item_type = item['item_type']
        # selected_item_index = item['index']

        if selected_entity == self.config['id']:
          new_root = input(f"Enter name for {self.config['desc']}: ")
          # Initialize an empty list for each category in config's context
          self.add_entity(new_root)
          print(f"➕  '{new_root}'")

        else:
          # Ask for the details of the new item
          is_external = input(f"Is this a {self.external().capitalize()} ticket? (y/n): ").lower() 
          if is_external == 'y':
              external_ticket = input(f"Enter {self.external().capitalize()} ID (ex: FD-12234): ")
          else:
              external_ticket = ''
          description = input(f"Enter {selected_item_type} description: ")
          if description == '':  # if input is empty, return to main menu
              return

          # Add the new item to the selected category for the selected entity
          self.add_item(selected_entity, selected_item_type, external_ticket, description)

          print(f"New {selected_item_type} item added for {selected_entity}.")
    
    def add_item(self, entity, item_type, external_ticket, description):
        self.md_data[entity][item_type].append({
            "external_ticket": external_ticket,
            "description": description
    })

    def remove(self):
      # Prepare a list of all items, each entity and each entity's category items
      items = []
      item_count = 0
      for entity, data in self.md_data.items():
          # Append each entity to the list
          item_count += 1
          print(f"{item_count}. {self.config['id']} {entity}")
          items.append({
              "index": item_count,
              "entity": entity,
              "type": "entity"
          })

          # Append each entity's category items to the list
          for category, category_items in data.items():
              for category_index, item in enumerate(category_items):
                  item_count += 1
                  print(f"{item_count}. {category} for {entity} - {item['description']}")
                  items.append({
                      "index": item_count,
                      "entity": entity,
                      "category": category,
                      "item": item,
                      "type": "item",
                      "category_index": category_index
                  })

      # Ask the user to select an item or entity to remove
      item_index = input("Enter the number of the item to remove: ")
      if item_index == '' or  item_index.isdigit() == False:
          return
      print(f"data: {self.md_data}")
      item_index = int(item_index) - 1
      selected_item = items[item_index]

      if selected_item['type'] == 'entity':
          self.remove_entity(selected_item['entity'])
      else:
          self.remove_item(selected_item['entity'], selected_item['category'], selected_item['category_index'])

    def remove_item(self, entity, item_type, item_index):
        if self.md_data[entity][item_type][item_index] == None:
            return
        self.md_data[entity][item_type].pop(item_index)

    def select_entity(self):
        for i, entity in enumerate(self.config['status-types'], start=1):
            print(f"{i}. {entity}")
        entity_index = input(f"Select a {self.config['desc']} by entering the number, or press Enter to return to main menu: ")
        if entity_index == '':  # if entity input is empty, return to main menu
            return None
        entity_index = int(entity_index) - 1
        if entity_index < 0 or entity_index >= len(self.config['status-types']):
            print(self.config['error-invalid-entity'])
            return None
        return entity_index

    def save_to_file(self):
        now = datetime.datetime.now()
        now.strftime("%m-%d-%Y-")
        save_location = input(f"Enter filename (default: meetdown-{now}.md): ") or f"meetdown-{now}.md"

        if not save_location.endswith(".md"):
            save_location += ".md"

        self.write( save_location)
        with open(f"{save_location}", "w") as file:
            interval = 0
            for entity, data in self.md_data.items():
                new_line = "\n" if interval > 0 else ""
                file.write(f"{new_line}## {entity}\n\n")
                file.write(f"| Category | {self.external().capitalize()} Ticket | Description |\n")
                file.write(f"{self.config['table-separator']}\n")
                
                for category, items in data.items():
                      for item in items:
                          external_ticket = self.toMarkdownExternalURL(item.get("external_ticket")) if item.get("external_ticket") else ""
                          file.write(f"| {category} | {external_ticket} | {item['description']} |\n")
                file.write("\n\n")
                interval += 1
        print(f"\n💾:\n{save_location}\n")

    def save_to_redis(self):
        # Prompt user for Redis folder and filename
        folder_name = input("Enter Redis folder name: ")
        filename = input("Enter filename: ")

        # Save the Markdown data to Redis
        key = f"{folder_name}:{filename}"
        self.redis_client.set(key, self.md_data)

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
            self.md_data = markdown_data.decode("utf-8")
            print(f"\nMarkdown data for key '{selected_key}':\n")
            print(self.md_data)
        else:
            print("Markdown data not found.")

    def load_from_markdown(self, file_path):
        parser = MeetDownParser(self.config)
        d = {}
        c = {}
        d, c = parser.load_from_markdown(file_path)
        self.config = c
        self.md_data = d

        return d, c
    def update_data_item_categories(self, data, category):
        # print(f"\n-------before: {data}------")
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
        # print(f"\n-------after: {data}------")

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
            
            for line in self.preview(self.md_data):
                file.write(line)

        if buhbye:
            print(f"\nkthx👋")
        print(f"\n💾: {os.getcwd()}/{self.config['tmp']}\n")


    def ensure_default_ctx_items_exist_in_md_data(self):
        for record in self.config['status-types']:
            if record not in self.md_data:
                self.md_data[record] = {list(ctx.keys())[0]: [] for ctx in self.config['ctx']}

    def preview(self, md_data):
        result = []
        interval = 0
        refs = []
        for entity, data in md_data.items():
            new_line = "" if interval > 0 else ""
            result.append(f"{new_line}## {entity}\n")
            result.append(f"| Category | {self.external().capitalize()} Ticket | Description |\n")
            result.append("|----------|-------------|-------------|\n")
            no_items = True
            for category, items in data.items():
                  for item in items:
                      no_items = False
                      if item.get("external_ticket"):
                        refs.append(self.createInternalReferenceLink(item))
                        external_ticket = self.toInternalLink(item)
                        result.append(f"| {category} | {external_ticket} | {item['description']} |\n")
                      else:
                        result.append(f"| {category} |  | {item['description']} |\n")
            result.append("")
            interval += 1
        if len(refs) > 0:
            result.append("\n\n")
            # remove duplicates
            uniq_refs = list(set(refs))
            for ref in uniq_refs:
                result.append(f"{ref}\n")
        result.append("\n")

        return result

    def meetdown(self, args, config, md_data):
        self.md_data = md_data#{entity: {list(ctx.keys())[0]: [] for ctx in self.config['ctx']} for entity in args.entities}
        self.config['status-types'] = args.entities
        #ensure each entitiy has each ctx with an empty array
        self.ensure_default_ctx_items_exist_in_md_data()
        while True:
            # Ensure each entity has each ctx and same keys with an empty array and optionally items in each array
            
            os.system('clear')

            print(f"{NAME}")
            # Preview
            previews = self.preview(self.md_data)
            for preview in previews:
                print(preview.replace("\n",""))## We dont want to show \n only used for written file

            # Options
            print(f"{self.config['separator-1']}\n\nOptions:\n\n{self.generate_options()}\n") 
            self.ensure_default_ctx_items_exist_in_md_data()
            selected_option = input(f"{self.config['prompt-main']}: ")
            
            # If user hits return with no input, kbai
            if not selected_option:
                self.ensure_default_ctx_items_exist_in_md_data()
                self.write(self.config['tmp'], True)
                break
            
            try:
                selected_option = int(selected_option)
            except ValueError:
                print(f"\n{self.config['error-invalid-option']}\n")
                continue
            
            ctx_length = len(self.config['ctx'])
            if selected_option == 1:
                # Add ctx item
                self.add()
            elif selected_option == 2:
                # Remove ctx item
                self.remove()
            elif selected_option == 3:
                # Toggle item
                self.toggle()
            elif selected_option == 4:
              file_path = input(f"{self.config['prompt-save-location']}: ")
              loaded_data, config = self.load_from_markdown(file_path)
              if loaded_data is not None and config is not None:
                  self.md_data = loaded_data
                  self.config = config
            elif selected_option == 5:
                # Save ctx to markdown
                self.save_to_file()
                break
            elif selected_option == 6:
                # Save ctx & upload to gist
                gist_desc = input("Enter a description for your `gist`: ")
                self.write( self.config['tmp'])
                # upload_to_gist(self.config['tmp'], gist_desc)
            else:
                print(f"`${selected_option}` is an invalid option. \nEnter any number 1-{2*ctx_length+5} and hit return or hit return again to stash & exit")
    def main(self):
        args = self.parse_arguments()

        # Check if the temporary file exists
        if os.path.exists(self.config['tmp']):
            # If it exists, ask the user if they want to load it
            load_previous = input(f"Previous session detected. {self.config['tmp']}\nLoad it? (y/n): ").lower() == 'y'
            if load_previous:
                loaded_data, config = self.load_from_markdown(self.config['tmp'])  
                if self.config['debug']:
                  print(f'loaded_data: {loaded_data} config: {config}')
                # Load the data from the specified file
                if loaded_data is not None and config is not None:
                    self.md_data = loaded_data
                    self.config = config

                else:
                    # Display an error message and continue with default data
                    print("Failed to load data from file. Continuing with default configuration.")

        self.meetdown(args, self.config, self.md_data)


if __name__ == "__main__":
    meetdown = MeetDown(MeetDown.default_config())
    meetdown.main()
