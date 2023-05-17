import os
import getpass

class MeetDownConfig:
    def __init__(self, config_obj=None):
        if config_obj is None:
            config_obj = self.default_config()
        self.config = config_obj

    @staticmethod
    def default_config():
        res = {
            "users": getpass.getuser(),
            "title": ".meetdown.md",
            "folder": os.getcwd(),
            "tmp": ".meetdown.md",
            "id": "👤",
            "desc": "👤 person",
            "prompt-type": "Option",
            "prompt-main": " Enter number",
            "prompt-add": "Add",
            "prompt-remove": "Remove",
            "prompt-toggle": "Toggle",
            "prompt-edit": "Edit",
            "prompt-load": "Load",
            "prompt-save": "Save & Quit",
            "prompt-save-location": "Enter the path of the Markdown file to load",
            "external": {
                "id": "jira",
                "url": "https://frontdeskhq.atlassian.net/jira/software/c/projects/FD/boards/7/backlog?view=detail&selectedIssue="
            },
            "states": [
                {"⬜": "⬜ todo"},
                {"✅": "✅ done"},
                # {"🔥":  "🔥 ready-qa"},
                # {"🚫":  "🚫 blocked"},
                # {"💩:  "💩 trash"},
                # {"🔴":  "🔴 blocked"},
                # {"🟡":  "🟡 in-progress"},
                # {"🟢":  "🟢 ready-review"},
                # {"🟣":  "🟣 review"},
                # {"🟤":  "🟤 ready-test"},
                # {"🔵":  "🔵 test"},
                # {"⚫":  "⚫ ready-deploy"},
                # {"⚪":  "⚪ deploy"},
                # {"🟠":  "🟠 ready-release"},
                # {"🟣":  "🟣 release"},
                # {"🟤":  "🟤 ready-archive"},
                # {"🟦":  "🟦 archive"},
                # {"🟩":  "🟩 ready-merge"},
                # {"🟨":  "🟨 merge"},

               
                # mojii: https://emojidb.org
            ],
            'imported-states': [],
            "debug": 0,
            "tmpl": [
                {"id": "⛔", "desc": "Invalid"}
            ],
            "invalid": "⛔ Invalid ",
            "separator-1": "________________________",
            "separator-2": "______________",
            "table-header": "| ID  | $external_id | Description |",
            "table-header-divider": "----------",
        }
        res["table-separator"] = f"| {res['table-header-divider']} | {res['table-header-divider']} | {res['table-header-divider']} |"
        return res
    
    @staticmethod
    def generate_options(config):
        opts = []
        opts.append(f" 1. {config['prompt-add']}")
        opts.append(f" 2. {config['prompt-edit']}")
        opts.append(f" 3. {config['prompt-load']}")
        opts.append(f" 4. {config['prompt-save']}")
        opts.append(f" 5. {config['prompt-remove']}")
        opts.append(f" 6. {config['prompt-toggle']}")
        
        if config['debug']:
          opts.append(f"7. Upload")
        
        return "\n".join(["\n".join(opts)])