#!/usr/bin/env python3

import datetime
import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

MEETDOWN_FOLDER = os.getenv("MEETDOWN_FOLDER") if os.getenv("MEETDOWN_FOLDER") else os.path.dirname(os.path.realpath(__file__))
MEETDOWN_TICKET_BASE = os.getenv("MEETDOWN_TICKET_BASE") if os.getenv("MEETDOWN_TICKET_BASE") else ""
usernames = os.getenv("MEETDOWN_USERS").split('/') if os.getenv("MEETDOWN_USERS") else [os.environ.get('USER', os.environ.get('USERNAME'))]
tags = os.getenv("MEETDOWN_TAGS").split('/') if os.getenv("MEETDOWN_TAGS") else ["r&d", "standup"]
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
    
    Path(f"{location}").mkdir(parents=True, exist_ok=True)
    markdown_content = generate_markdown()

    with open(f"{filename}", "w") as file:
        file.write(markdown_content)
    return f"Markdown file '{filename}' has been written to the location '{location}'."

def generate_markdown():
    date_str = datetime.datetime.now().strftime("%m-%d-%y")
    Path("{location}").mkdir(parents=True, exist_ok=True)

    markdown_content = f"# {date_str}"
    markdown_content += f"\n{' #'.join(tags)} #{date_str}\n___\n"
    for username, tasks in user_data.items():
        markdown_content += f"\n## {username}\n\n"
        markdown_content += "| `Task ID` | `Description` | `Completed` |\n"
        markdown_content += "|---------|-------------|-----------|\n"
        for task in tasks:
            completed_checkbox = "[x]" if task["completed"] else "[ ]"
            blocker_note = " (Blocker)" if task.get("blocker", False) else ""
            if not task['id']:
              markdown_content += f"| `-` | {task['description']}{blocker_note} | {completed_checkbox} |\n"
            else:
                markdown_content += f"| [{task['id']}]({MEETDOWN_TICKET_BASE}{task['id']}) | {task['description']}{blocker_note} | {completed_checkbox} |\n"
            
        markdown_content += "\n\n"

    return markdown_content

def main_loop(usernames):
    global MEETDOWN_FOLDER
    while True:
        os.system('clear')
        banner = f"""
███    ███ ███████ ███████ ████████ ██████   ██████  ██     ██ ███    ██ 
████  ████ ██      ██         ██    ██   ██ ██    ██ ██     ██ ████   ██ 
██ ████ ██ █████   █████      ██    ██   ██ ██    ██ ██  █  ██ ██ ██  ██ 
██  ██  ██ ██      ██         ██    ██   ██ ██    ██ ██ ███ ██ ██  ██ ██ 
██      ██ ███████ ███████    ██    ██████   ██████   ███ ███  ██   ████ 
$MEETDOWN_FOLDER: {MEETDOWN_FOLDER}
$MEETDOWN_TAGS: {os.getenv("MEETDOWN_TAGS").split('/')}
$MEETDOWN_USERS: {",".join(usernames)}
Preview:
{generate_markdown()}
Choose an action:
1 - Add Todo
2 - Add Completed
3 - Add Blocker
4 - Add User
5 - Add Tag
6 - Change save location
7 - Save to file
8 - Exit
"""
        print(banner)
        print(os.getenv("MEETDOWN_TAGS"))
        action = input("Enter the action number: ")
        
        if action == "1" or action == "2" or action == "3":
            
            selected_user_index = 0
            username = usernames[0]

            if len(usernames) > 1:
              print("Usernames:")
              for i, username in enumerate(usernames, 1):
                print(f"{i}. {username}")
              selected_user_index = int(input("Select a user by entering the corresponding number: "))
              username = usernames[selected_user_index - 1]

            
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
            if username not in usernames:
              usernames.append(username)
            else:
                usernames.append(f"{username}-{len(usernames)})")
        
        elif action == "5":
            tag = input("Enter the tag: ")
            if tag not in tags:
              tags.append(tag)
            else:
                tags.append(f"{tag}-{len(tags)})")
        
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
            break
        else:
            print("Invalid action. Please choose a valid action number.")

main_loop(usernames)
