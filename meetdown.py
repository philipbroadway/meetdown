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

class MeetDown:
    @staticmethod
    def default_config():
        return {
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
          "debug": 0,
          "tmpl": [
              {id: "⛔", "desc": "Invalid"}
          ],
          "status-types-selections-invalid": "⛔ Invalid selection.",
          "separator-1": "________________________",
          "separator-2": "______________",
    }

    def __init__(self, config):
        self.config = config
        self.md_data = {}

    def itemTypes(self):
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

        # Now, remove the item from the old category and add it to the new one
        self.md_data[entity][from_category].remove(item)
        self.md_data[entity][to_category].append(item)
        print(f"Item toggled from {from_category} to {to_category}.")

    def add(self):
        # Get the list of all types of items
        item_types = self.itemTypes()
        item_count = 0
        # Print all item types and let the user select one
        items = []
        print(f"{self.config['separator-2']}\n\n{self.config['prompt-add']}\n")
        for i, item_type in enumerate(item_types, start=1):
            for n, entity in enumerate(self.config['status-types'], start=1):
              if item_count <= 1:
                items = [{"index": 1, "entity": entity, "item_type": item_type}]
              item_count += 1
              print(f"{item_count}. {entity}-{item_type}")
              items.append({"index": i, "entity": entity, "item_type": item_type})
        item_count += 1
        print(f"{item_count}. {self.config['id']}")
        items.append({"index": i+1, "entity": self.config['id'], "item_type": self.config['id']})
        
        item_type_index = input(f"\n{self.config['prompt-main']}: ")
        if item_type_index == '':
            return

        item = items[int(item_type_index) - 1]
        
        selected_entity = item['entity']
        selected_item_type = item['item_type']
        selected_item_index = item['index']

        if selected_entity == self.config['id']:
          new_root = input(f"Enter name for {self.config['desc']}: ")
          # Initialize an empty list for each category in config's context
          self.md_data[new_root] = {list(ctx.keys())[0]: [] for ctx in self.config['ctx']}
          self.config['status-types'].append(new_root)
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
          self.md_data[selected_entity][selected_item_type].append({
              "external_ticket": external_ticket,
              "description": description
          })

          print(f"New {selected_item_type} item added for {selected_entity}.")

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
              for item in category_items:
                  item_count += 1
                  print(f"{item_count}. {category} for {entity} - {item['description']}")
                  items.append({
                      "index": item_count,
                      "entity": entity,
                      "category": category,
                      "item": item,
                      "type": "item"
                  })

      # Ask the user to select an item or entity to remove
      item_index = input("Enter the number of the item to remove: ")
      if item_index == '':  # if input is empty, return to main menu
          return

      item_index = int(item_index) - 1
      selected_item = items[item_index]

      if selected_item['type'] == 'entity':
          # If an entity was selected, remove the entity
          self.md_data.pop(selected_item['entity'])
          print(f"Removed: {self.config['id']} {selected_item['entity']}")
      else:
          # If an item was selected, remove the item from its entity's category
          self.md_data[selected_item['entity']][selected_item['category']].remove(selected_item['item'])
          print(f"Removed: {selected_item['category']} for {selected_item['entity']} - {selected_item['item']['description']}")


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
                file.write("|----------|-------------|-------------|\n")
                no_items = True
                for category, items in data.items():
                      for item in items:
                          no_items = False
                          external_ticket = self.toMarkdownExternalURL(item.get("external_ticket")) if item.get("external_ticket") else ""
                          file.write(f"| {category} | {external_ticket} | {item['description']} |\n")
                file.write("\n\n")
                interval += 1
        print(f"\n💾:\n{save_location}\n")
      
    def load_from_markdown(self, file_path):
        if not os.path.isfile(file_path.strip()):
            print(f"Error: No such file or directory: '{file_path.strip()}'")
            return

        with open(file_path, 'r') as file:
            content = file.read()

        entity_headers = re.findall(r'##\s+(.+)\s+', content)
        print(entity_headers)
        data = {}

        for entity_header in entity_headers:
            entity_regex = r'##\s+' + re.escape(entity_header) + r'\s+.*\|.*\|.*\|.*\n((?:.*\|.*\|.*\|.*\n)*)'
            entity_match = re.search(entity_regex, content)
            print(entity_match)
            if entity_match:
                entity_content = entity_match.group(1)
                category_regex = r'\|(.+)\|(.+)\|(.+)\|'
                category_matches = re.findall(category_regex, entity_content)
                if category_matches:
                    data[entity_header] = {}
                    index=0
                    for category_match in category_matches:
                        category = category_match[0].strip()
                        jira_ticket = category_match[1].strip()
                        description = category_match[2].strip()
                        if index == 0:
                            index += 1
                            continue

                        if category not in data[entity_header]:
                            data[entity_header][category] = []
                            print(f"Created: {category} for {entity_header}")

                        item = {"status": category, "external_ticket": jira_ticket, "description": description}
                        data[entity_header][category].append(item)
        
        print(data)
        return data, self.config

    def write(self,filename, buhbye=False):
        with open(filename, "w") as file:
            interval = 0
            for entity, data in self.md_data.items():
                new_line = "\n\n" if 1 > 0 else ""
                file.write(f"{new_line}## {entity}\n")
                file.write(f"| Category | {self.external().capitalize()} Ticket | Description |\n")
                file.write("|----------|-------------|-------------|\n")
                no_items = True
                for category, items in data.items():
                    for item in items:
                        print(f"item: {item}")
                        no_items = False
                        external_ticket = self.toMarkdownExternalURL( item["external_ticket"]) if item["external_ticket"] else ""
                        file.write(f"| {category.capitalize()} | {external_ticket} | {item['description']} |\n")
        if buhbye:
          print(f"\n💾:\nmd_data:{self.md_data}\nself.config:{self.config}\n")        
          print(f"\nkthx👋\n")

    def ensure_default_ctx_items_exist_in_md_data(self):
      for record in self.md_data:
        for ctx in self.config['ctx']:
            category = list(ctx.keys())[0]
            if category not in self.md_data[record]:
                self.md_data[record][category] = []

    def meetdown(self, args, config, md_data):
        self.md_data = md_data#{entity: {list(ctx.keys())[0]: [] for ctx in self.config['ctx']} for entity in args.entities}
        self.config['status-types'] = args.entities
        #ensure each entitiy has each ctx with an empty array
        self.ensure_default_ctx_items_exist_in_md_data()
        while True:
            self.ensure_default_ctx_items_exist_in_md_data()
            os.system('clear')
            print(f"{NAME}")
            # Preview
            for entity, data in self.md_data.items():
                print(f"\n## {entity}\n")
                print(f"| Status | {self.external().capitalize()} | Description |")
                print("|----------|-------------|-------------|")
                no_items = True
                for category, items in data.items():
                    for item in items:
                        no_items = False
                        external_ticket = self.toMarkdownExternalURL( item["external_ticket"]) if item["external_ticket"] else ""
                        print(f"| {category.capitalize()} | {external_ticket} | {item['description']} |")
                if no_items:
                    print("| - | - | - |")

            print(f"{self.config['separator-1']}\n\nOptions:\n\n{self.generate_options()}\n") 
            selected_option = input(f"{self.config['prompt-main']}: ")
            
            # If user hits return with no input, kbai
            if not selected_option:
                self.ensure_default_ctx_items_exist_in_md_data()
                self.write(self.config['tmp'], True)
                break
            
            try:
                selected_option = int(selected_option)
            except ValueError:
                print("Invalid option. Please try again.")
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
