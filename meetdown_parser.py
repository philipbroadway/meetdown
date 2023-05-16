import os
import re

class MeetDownParser:
    """
      A parser to load and process markdown content from a given file path, expecting a specific format:
      
      Input Format:
      -------------
      ## Entity Header
      | Category | External Ticket | Description |
      |----------|-----------------|-------------|
      | Category | [ticket_id][ticket_id-ref] | Item description |
      | Category |  | Item no ticket description |
      
      [ticket_id-ref]: https://ticketing_system.com/ticket/ticket_id

      The input format should consist of entity headers preceded by '##', followed by a table with three columns:
      - Category: The category of the item (e.g. '✅', '⬜', etc.).
      - External Ticket: The ticket ID from an external ticketing system (e.g. Jira, Trello, etc.) enclosed in square brackets.
      - Description: The description of the item.
      
      If there items with external tickets, at the end of the markdown file, there should be a list of markdown reference links to the external ticketing system URLs.

      Generated Data Structure:
      -------------------------
      {
          "Entity Header": {
              "Category": [
                  {
                      "description": "Item description",
                      "external_ticket": "ticket_id"
                  },
                  ...
              ],
              ...
          },
          ...
      }
    """
    def __init__(self, config):
        self.config = config

    def load_from_markdown(self, file_path):
        path = str(file_path).strip()
        if not os.path.isfile(path):
            print(f"Error: No such file or directory: '{path}'")
            return {}, self.config  # Return an empty dictionary and the existing configuration

        content = self.read_file_content(file_path)
        entity_headers = self.extract_entity_headers(content)
        data, page_refs = self.parse_entity_headers(entity_headers, content)
        self.update_config_with_external_url(page_refs, content)

        return data, self.config


    def read_file_content(self, file_path):
        with open(file_path, 'r') as file:
            content = file.read()
        return content

    def extract_entity_headers(self, content):
        return re.findall(r'##\s+(.+)\s+', content)

    def parse_entity_headers(self, entity_headers, content):
        data = {}
        page_refs = []
        for entity_header in entity_headers:
            entity_content = self.extract_entity_content(entity_header, content)
            if entity_content:
                category_matches = self.extract_category_matches(entity_content)
                data[entity_header] = {}
                for category_match in category_matches:
                    category, description, item, is_header = self.process_category_match(category_match)
                    if is_header:
                        continue
                    page_refs = self.process_item(item, description, category_match, page_refs)
                    self.update_data_item_categories(data, entity_header, category)
                    data[entity_header][category].append(item)
        return data, page_refs

    def extract_entity_content(self, entity_header, content):
        entity_regex = r'##\s+' + re.escape(entity_header) + r'\s+.*\|.*\|.*\|.*\n((?:.*\|.*\|.*\|.*\n)*)'
        entity_match = re.search(entity_regex, content)
        return entity_match.group(1) if entity_match else None

    def extract_category_matches(self, entity_content):
        category_regex = r'\|(.+)\|(.+)\|(.+)\|'
        return re.findall(category_regex, entity_content)

    def process_category_match(self, category_match):
        category = category_match[0].strip()
        description = category_match[2].strip()
        is_header = bool(re.findall(r'^-+$', category))
        item = {"description": category_match[2].strip(), "external_ticket": ""}
        return category, description, item, is_header

    def process_item(self, item, description, category_match, page_refs):
        link_regex = r'\[(.*?)\]\[(.*?)\]'
        for match in category_match:
            if re.search(link_regex, match):
                link_match = re.search(link_regex, match)
                if link_match:
                    description = link_match.group(1).strip()
                    external_ticket = link_match.group(2).strip()

                    # Remove "-ref" from the external_ticket if it's already there
                    if external_ticket.endswith("-ref"):
                        external_ticket = external_ticket[:-4]

                    page_refs.append(f"{external_ticket}-ref")
                    item["external_ticket"] = external_ticket

        return page_refs



    def update_data_item_categories(self, data, category):
        if category not in data:
            data[category] = []

    def update_config_with_external_url(self, page_refs, content):
        for ref in page_refs:
            pattern = re.escape(f"[{ref}]:") + r'\s*(.*?)\s*$'
            url_match = re.search(pattern, content, re.MULTILINE)
            if url_match:
                url = url_match.group(1)
                key = f"{ref.replace('-ref', '')}"
                replaced = url.replace(f"{key}", "")
                self.config['external']['url'] = replaced

    def update_data_item_categories(self, data, entity_header, category):
        if entity_header not in data:
            data[entity_header] = {}

        if category not in data[entity_header]:
            data[entity_header][category] = []
