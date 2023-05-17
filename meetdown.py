# """
# ┌┬┐┌─┐┌─┐┌┬┐┌┬┐┌─┐┬ ┬┌┐┌
# │││├┤ ├┤  │  │││ │││││││
# ┴ ┴└─┘└─┘ ┴ ─┴┘└─┘└┴┘┘└┘
# ________________________
# """
NAME="""
# meetdown
"""
import os, time
import argparse
import datetime
import panflute as pf
from bs4 import BeautifulSoup
import redis
from meetdown_parser import MeetDownParser
from meetdown_config import MeetDownConfig
from meetdown_utils import MeetDownUtils

class MeetDown:
    @staticmethod
    def default_config():
        return MeetDownConfig.default_config()

    def __init__(self, config):
        self.config = config
        self.utils = MeetDownUtils(config)
        self.md_data = {}
        redis_host = os.environ.get('REDIS_HOST')
        redis_port = os.environ.get('REDIS_PORT')
        redis_password = os.environ.get('REDIS_PASSWORD')
        self.redis_client = redis.Redis(host=redis_host, port=redis_port, password=redis_password)

    def status_types(self):
        types = []
        for obj in self.config['states']:
            for key in obj:
                types.append(key)
        return types

    def editables(self):
        
        result = []

        for entity in self.md_data.keys():
            
            for category in self.md_data[entity].keys():
                category_index = 0
                for item in self.md_data[entity][category]:
                    result.append({"entity": entity, "category": category, "item": item, "category_index": category_index, "external_ticket": item['external_ticket'], "description": item['description']})
                category_index += 1

        return result

    def generate_options(self):
        opts = []
        opts.append(f"1. {self.config['prompt-add']}")
        opts.append(f"2. {self.config['prompt-remove']}")
        opts.append(f"3. {self.config['prompt-toggle']}")
        opts.append(f"4. {self.config['prompt-edit']}")
        opts.append(f"5. {self.config['prompt-load']}")
        opts.append(f"6. {self.config['prompt-save']}")
        
        if self.config['debug']:
          opts.append(f"7. Upload")
        
        return "\n".join(["\n".join(opts)])

    def parse_arguments(self):
      now = self.utils.now()
      whoiam = self.utils.whoami()
      parser = argparse.ArgumentParser(description='Process command-line arguments.')
      parser.add_argument('--title', type=str, default=f"meetdown-{now}", help='Title (default: aws-p13.md)')
      parser.add_argument('--entities', type=str, default=whoiam, help='Comma separated people or entities (example: pike13,aws-sales)')
      parser.add_argument('--out', type=str, default=MeetDownUtils.cwd(), help='Save directory path (default: empty string)')
      args = parser.parse_args()

      if args.entities:
          args.entities = args.entities.split(',')
      return args

    def external(self):
        return self.config['external']['id']

    def toMarkdownExternalURL(self,id):
        return f"[{id}]({self.config['external']['url']}{id})"

    def toggle_prompt(self):
        # First, create a flat list of all items
        all_items = []
        for entity, data in self.md_data.items():
            for category, items in data.items():
                for item in items:
                    all_items.append((entity, category, item))

        if not all_items:
            print("No items to toggle.")
            return

        # Now, print all items and let the user select one
        for i, (entity, category, item) in enumerate(all_items, start=1):
            print(f"{i}. {entity} - {category} - {item['description']}")
        
        item_index = input(f"Toggle which item?: ")
        if item_index == '':  # if input is empty, return to main menu
            return
        item_index = int(item_index) - 1

        # Get the selected item and its details
        entity, from_category, item = all_items[item_index]

        # Now, let the user select the new category
        for i, states in enumerate(self.config['states'], start=1):
            print(f"{i}. {list(states.keys())[0]}")
        to_category_index = input("Select the new category of the item by entering the number: ")
        if to_category_index == '':  # if input is empty, return to main menu
            return
        to_category_index = int(to_category_index) - 1
        to_category = list(self.config['states'][to_category_index].keys())[0]

        self.toggle_status(entity, from_category, to_category, item)

    def toggle_status(self, entity, from_category, to_category, item):
        if to_category not in self.md_data[entity]:
          self.md_data[entity][to_category] = []
        if self.md_data[entity][from_category]:
          self.md_data[entity][from_category].remove(item)
        self.md_data[entity][to_category].append(item)

    def add_entity(self, entity):
        self.md_data[entity] = {list(states.keys())[0]: [] for states in self.config['states']}
        self.config['status-types'].append(entity)
        if entity not in self.md_data:
            self.md_data[entity] = {}
            for category in self.config['states']:
                self.md_data[entity][list(category.keys())[0]] = []

    def remove_entity(self, entity):
        if entity in self.md_data:
          del self.md_data[entity]

    def add_prompt(self):
        # Get the list of all types of items
        item_types = self.status_types()
        item_count = 0
        # Print all item types and let the user select one
        items = []
        print(f"{self.config['separator-2']}\n\n{self.config['prompt-add']}\n")
        
        for i, item_type in enumerate(item_types, start=1):
            for n, entity in enumerate(self.md_data, start=1):
              item_count += 1
              print(f"{item_count}. {entity}-{item_type}")
              items.append({"index": item_count, "entity": entity, "item_type": item_type})
        item_count += 1
        print(f"{item_count}. {self.config['id']}")
        items.append({"index": item_count+1, "entity": self.config['id'], "item_type": self.config['id']})
        
        item_type_index = input(f"\n{self.config['prompt-main']}: ")
        if item_type_index == '' or  item_type_index.isdigit() == False:
            return
        
        if int(item_type_index) -1 > len(items):
          print(f"Please select a number between 1 and {len(items)}")
          return

        item = items[int(item_type_index) -1]
        
        selected_entity = item['entity']
        selected_item_type = item['item_type']

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
        
    def edit_ticket_or_description(self, editable):
        ticket_or_description = input("\nOptions:\n\n1. Edit Ticket\n2. Edit Description\n\nSelect an option by entering the number: ")
        if not ticket_or_description.isdigit():
            print("Invalid input. Please enter a number.")
            return None, None, None
        ticket_or_description = 1 if int(ticket_or_description) == 1 else 2
        ticket_key = 'external_ticket' if ticket_or_description == 1 else 'description'
        print(f"\nCurrent value: {editable[ticket_key]}")
        input_text = input(f"\nNew value: ")
        if input_text == '':
            return None, None, None

        return editable, ticket_or_description, input_text

        
    def edit_prompt(self):
      print("\nEditables:\n")
      for i, editable in enumerate(self.editables(), start=1):
          ticket = f"{editable['external_ticket']}" if editable['external_ticket'] else "N/A"
          print(f"{i}. {editable['category']} | {editable['entity']} | {ticket} | {editable['description']}")

      selected_index = input("\nSelect an editable item by entering the number: ")
      if not selected_index.isdigit():
          print(f"{self.config['invalid']}")
          return None

      selected_index = int(selected_index)
      if selected_index < 1 or selected_index > len(self.editables()):
          print(f"{self.config['invalid']}")
          return None

      selected_editable = self.editables()[selected_index - 1]

      editable, ticket_or_description, input_text = self.edit_ticket_or_description(selected_editable)
      return self.edit(selected_editable, ticket_or_description, input_text)

    def edit(self, editable, option, new_value):
      data = self.md_data
      option_key = 'external_ticket' if option == 1 else 'description'
      print(f"Edit {option_key}: {editable[option_key]} -> {new_value}")
      for type in data[editable['entity']]:
          for i, item in enumerate(data[editable['entity']][type]):
              if item['external_ticket'] == editable['external_ticket'] and item['description'] == editable['description']:
                  print(f"✅  {editable['entity']} - {type} - {new_value} -> {data[editable['entity']][type][i][option_key]}")
                  self.md_data[editable['entity']][type][i][option_key] = new_value
                  print(f"✅ {data[editable['entity']][type][i][option_key]}")
                  continue
      return data, self.config

    def remove_prompt(self):
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
      if self.config['debug']:
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
        now = self.utils.now()
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
        data, config = parser.load_from_markdown(file_path)
        self.config = config
        self.md_data = data
        return data, config
    
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


    def ensure_default_states_items_exist_in_md_data(self):
        for record in self.config['status-types']:
            for entity in self.md_data.keys():
                if record not in self.md_data[entity]:
                    self.md_data[entity][record] = []

    def preview(self, md_data, compact=False):
        now = self.utils.now()
        spacer = " " if compact else ""
        result =[]
        if compact:
          result = [f"{NAME} > {now}", ""]
        else:
          result = [f"", f"\n> {now}", "\n\n"]
        interval = 0
        refs = []
        for entity, data in md_data.items():
            new_line = "" if interval > 0 else ""
            result.append(f"{new_line}## {entity}")
            if not compact:
                result.append("\n")
                result.append("\n")
            result.append(f"{spacer}| Category | {self.external().capitalize()} Ticket | Description |\n")
            result.append(f"{spacer}{self.config['table-separator']}\n")

            for category, items in data.items():
                  for item in items:
                      if item.get("external_ticket"):
                        refs.append(self.createInternalReferenceLink(item))
                        external_ticket = self.toInternalLink(item)
                        ticket = f"[{item['external_ticket']}]" if compact else external_ticket
                        if self.config['debug']:
                            print(f"external_ticket: {external_ticket} item: {item}")
                        result.append(f"{spacer}| {category} | {ticket} | {item['description']} |\n")
                      else:
                        result.append(f"{spacer}| {category} |  | {item['description']} |\n")
            result.append("\n")
            interval += 1
        if len(refs) > 0:
            if not compact:
                result.append("### References\n\n")
                uniq_refs = list(set(refs))
                for ref in uniq_refs:
                  result.append(f"{ref}\n")
        return result
    
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
    
    def render_terminal_preview(self, config, md_data, compact=False):
        result = []
        previews = self.preview(md_data, True)
        for preview in previews:
                result.append(preview.replace("\n",""))

        if self.config['debug']:
            result.append(f"{self.config['separator-1']}\n\nOptions:\n\n{self.generate_options()}\n") 
        else:
            result.append(f"Options:\n\n{self.generate_options()}\n")
        return result

    def meetdown(self, args, config, md_data):
        self.md_data = md_data
        self.config['status-types'] = args.entities
        self.ensure_default_states_items_exist_in_md_data()

        while True:
            os.system('clear')
            # Preview
            
            previews = self.render_terminal_preview(self.config, self.md_data, True)
            for preview in previews:
                print(preview)
            self.ensure_default_states_items_exist_in_md_data()
            selected_option = input(f"{self.config['prompt-main']}: ")
            
            # If user hits return with no input, kbai
            if not selected_option:
                self.ensure_default_states_items_exist_in_md_data()
                self.write(self.config['tmp'], True)
                break
            
            try:
                selected_option = int(selected_option)
            except ValueError:
                print(f"\n{self.config['error-invalid-option']}\n")
                continue
            
            states_length = len(self.config['states'])
            if selected_option == 1:
                self.add_prompt()
            elif selected_option == 2:
                self.remove_prompt()
            elif selected_option == 3:
                self.toggle_prompt()
            elif selected_option == 4:
               self.edit_prompt()
            elif selected_option == 5:
              file_path = input(f"{self.config['prompt-save-location']}: ")
              if not file_path:
                  return
              loaded_data, config = self.load_from_markdown(file_path)
              if loaded_data is not None and config is not None:
                  self.md_data = loaded_data
                  self.config = config
            elif selected_option == 6:
                self.save_to_file()
                break
            elif selected_option == 7:
                # Save states & upload to gist
                gist_desc = input("Enter a description for your `gist`: ")
                self.write( self.config['tmp'])
                # upload_to_gist(self.config['tmp'], gist_desc)
            else:
                print(f"`${selected_option}` is an invalid option. \nEnter any number 1-{2*states_length+5} and hit return or hit return again to stash & exit")
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
        self.utils.clear_screen()
        self.meetdown(args, self.config, self.md_data)

if __name__ == "__main__":
    meetdown = MeetDown(MeetDownConfig.default_config())
    meetdown.main()
