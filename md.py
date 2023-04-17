#!/usr/bin/env python3

ASCII="""
███    ███ ███████ ███████ ████████ ██████   ██████  ██     ██ ███    ██ 
████  ████ ██      ██         ██    ██   ██ ██    ██ ██     ██ ████   ██ 
██ ████ ██ █████   █████      ██    ██   ██ ██    ██ ██  █  ██ ██ ██  ██ 
██  ██  ██ ██      ██         ██    ██   ██ ██    ██ ██ ███ ██ ██  ██ ██ 
██      ██ ███████ ███████    ██    ██████   ██████   ███ ███  ██   ████ 
"""
PROMPT = """
Options:

1 - Add Todo
2 - Add Completed
3 - Add Blocker
4 - Add User
5 - Add Tag
6 - Change save location
7 - Save to file
8 - Exit
"""

TABLE_HEADER = """
| `Task ID` | `Description` | `Completed` |
|---|---|---|"""

TODO="☑️"
COMPLETED="✅"

import datetime
import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

MEETDOWN_FOLDER = os.getenv("MEETDOWN_FOLDER") if os.getenv("MEETDOWN_FOLDER") else ""# Add a default here if not using .env
MEETDOWN_TICKET_BASE = os.getenv("MEETDOWN_TICKET_BASE") if os.getenv("MEETDOWN_TICKET_BASE") else ""# Add a default here if not using .env
MEETDOWN_USERS = os.getenv("MEETDOWN_USERS").split('/') if os.getenv("MEETDOWN_USERS") else [os.environ.get('USER', os.environ.get('USERNAME'))]
MEETDOWN_TAGS = os.getenv("MEETDOWN_TAGS").split('/') if os.getenv("MEETDOWN_TAGS") else ["r&d", "standup"]

user_data = {}

def add_todo(username, task_id, description):
    if username not in user_data:
        user_data[username] = []
    user_data[username].append({"id": task_id, "description": description, "completed": False})

def add_completed(username, task_id, description):
    if username not in user_data:
        user_data[username] = []
    user_data[username].append({"id": task_id, "description": description, "completed": True})

def add_blocker(username, task_id, description):
    if username not in user_data:
        user_data[username] = []
    user_data[username].append({"id": task_id, "description": description, "completed": False, "blocker": True})

def write_markdown(filename, location):
    
    Path(location).mkdir(parents=True, exist_ok=True)
    markdown_content = generate_markdown()

    with open(f"{filename}", "w") as file:
        file.write(markdown_content)
    return f"Markdown file '{filename}' has been written to the location '{location}'."

def generate_markdown():
    date_str = datetime.datetime.now().strftime("%m-%d-%y")
    Path(MEETDOWN_FOLDER).mkdir(parents=True, exist_ok=True)

    markdown_content = f"# {date_str}"
    markdown_content += f"\n#{' #'.join(MEETDOWN_TAGS)} #{date_str}\n___\n"
    for username, tasks in user_data.items():
        markdown_content += f"\n## {username}\n\n"
        markdown_content += f"{TABLE_HEADER}\n"
        for task in tasks:
            completed_checkbox = "✅" if task["completed"] else "☑️"
            blocker_note = " (Blocker)" if task.get("blocker", False) else ""
            if not task['id']:
              markdown_content += f"| `-` | {task['description']}{blocker_note} | {completed_checkbox} |\n"
            else:
                markdown_content += f"| [{task['id']}]({MEETDOWN_TICKET_BASE}{task['id']}) | {task['description']}{blocker_note} | {completed_checkbox} |\n"
            
        markdown_content += "\n\n"

    return markdown_content

def main(usernames):
    global MEETDOWN_FOLDER
    while True:
        os.system('clear')
        banner = f"{ASCII}\n"
        if os.getenv("MEETDOWN_DEBUG"):
          banner += f"$MEETDOWN_FOLDER: {MEETDOWN_FOLDER}\n"
          banner += f"$MEETDOWN_TAGS: {os.getenv('MEETDOWN_TAGS').split('/')}\n"
          banner += f"$MEETDOWN_USERS: {','.join(MEETDOWN_USERS)}\n"
        banner += f"\nMarkdown:\n"
        banner += f"{generate_markdown()}\n"
        banner += f"{PROMPT}\n"
        print(banner)

        action = input(">")
        
        if action == "1" or action == "2" or action == "3":
            
            selected_user_index = 0
            username = MEETDOWN_USERS[0]

            if len(MEETDOWN_USERS) > 1:
              print("MEETDOWN_USERS:")
              for i, username in enumerate(MEETDOWN_USERS, 1):
                print(f"{i}. {username}")
              selected_user_index = int(input(">"))
              username = MEETDOWN_USERS[selected_user_index - 1]

            
            task_id = input("Enter the task ID (blank if not jira): ")
            description = input("Enter the task description: ")
            
            if action == "1":
                add_todo(username, task_id, description)
            elif action == "2":
                add_completed(username, task_id, description)
            elif action == "3":
                add_blocker(username, task_id, description)
        elif action == "4":
            username = input("Enter the username: ")
            if username not in MEETDOWN_USERS:
              MEETDOWN_USERS.append(username)
            else:
                MEETDOWN_USERS.append(f"{username}-{len(MEETDOWN_USERS)})")
        
        elif action == "5":
            tag = input("Enter the tag: ")
            if tag not in MEETDOWN_TAGS:
              MEETDOWN_TAGS.append(tag)
            else:
                MEETDOWN_TAGS.append(f"{tag}-{len(MEETDOWN_TAGS)})")
        
        elif action == "6":
            new_location = input("Enter the folder path: ")
            MEETDOWN_FOLDER = new_location
            
        elif action == "7":
            date_str = datetime.datetime.now().strftime("%m-%d-%y-%H%M%s")
            filename = input(f"Enter the filename (default is '{date_str}.md'): ")
            if filename == "":
                filename = f"{date_str}.md"
            else:
                filename = f"{filename}.md"

            write_markdown(filename, MEETDOWN_FOLDER)

        elif action == "8":
            os.system('clear')
            break
        else:
            print("Invalid action. Please choose a valid action number.")

main(MEETDOWN_USERS)
