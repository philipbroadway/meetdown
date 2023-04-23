desc = """
┌┬┐┌─┐┌─┐┌┬┐┌┬┐┌─┐┬ ┬┌┐┌
│││├┤ ├┤  │  │││ │││││││
┴ ┴└─┘└─┘ ┴ ─┴┘└─┘└┴┘┘└┘
"""
import os
import argparse
import datetime

# Global
users_data = {}

now = datetime.datetime.now()
now.strftime("%m-%d-%y")

default_folder = ""
default_location = f"standup-{now}.md"  # set here or use --out flag
default_users = []  # Default list of users or use  --users flag separated by commas

def parse_arguments():
    
    parser = argparse.ArgumentParser(description='Process command-line arguments.')

    parser.add_argument('--title', type=str, default=f"standup-{now}", help='Title (default: meetdown-date.md)')

    parser.add_argument('--users', type=str, default='philipbroadway', help='List of usernames separated by commas (default: empty list)')

    parser.add_argument('--out', type=str, default="", help='Save directory path (default: empty string)')

    args = parser.parse_args()

    if args.users:
        args.users = args.users.split(',')

    return args

def clear_screen():
    if os.name == 'posix':
        os.system('clear')
    elif os.name == 'nt':
        os.system('cls')

def get_jira_url(ticket):
    return f"https://frontdeskhq.atlassian.net/jira/software/c/projects/FD/boards/7/backlog?view=detail&selectedIssue={ticket}"

def add_user():
    new_user = input("Enter name of new user: ")
    users_data[new_user] = {"[ ]": [], "✅": [], "❌": []}
    default_users.append(new_user)
    print(f"User '{new_user}' added.")

def remove_user():
    user_index = select_user()
    if user_index is None:
        return
    selected_user = default_users[user_index]
    default_users.pop(user_index)
    users_data.pop(selected_user)
    print(f"User '{selected_user}' removed.")

def remove_item(category):
    user_index = select_user()
    if user_index is None:
        return
    selected_user = default_users[user_index]
    items = users_data[selected_user][category]
    if not items:
        print(f"No {category} items to remove.")
        return
    print(f"{selected_user}'s {category} items:")
    for i, item in enumerate(items, start=1):
        print(f"{i}. {item['description']}")
    item_index = int(input(f"Enter the number of the {category} item to remove: ")) - 1
    items.pop(item_index)
    print(f"{category.capitalize()} item removed.")

def add_item(category):
    user_index = select_user()
    if user_index is None:
      user_index = 1
    selected_user = default_users[user_index]
    
    is_jira = input("Is this a Jira ticket? (y/n, default: n): ").lower() == "y"
    jira_ticket = ""
    if is_jira:
        jira_ticket = input("Enter Jira ticket name: ")
    description = input(f"Enter {category} description: ")
    users_data[selected_user][category].append({
        "jira_ticket": jira_ticket,
        "description": description
    })

def select_user():
    for i, user in enumerate(default_users, start=1):
        print(f"{i}. {user}")
    user_index = int(input("Select a user by entering the number: ")) - 1
    if user_index < 0 or user_index >= len(default_users):
        print("Invalid selection.")
        return None
    return user_index

def save_to_file():
    save_location = input(f"Enter save location (default: meetdown-{now}.md): ") or f"meetdown-{now}.md"
    with open(f"{default_folder}{save_location}", "w") as file:
        for user, data in users_data.items():
            file.write(f"## {user}\n\n")
            file.write("| Category | Jira Ticket | Description |\n")
            file.write("|----------|-------------|-------------|\n")
            for category, items in data.items():
                for item in items:
                    jira_ticket = get_jira_url(item["jira_ticket"]) if item["jira_ticket"] else ""
                    file.write(f"| {category.capitalize()} | {jira_ticket} | {item['description']} |\n")
    print(f"Standup meeting notes saved to:\n{default_folder}{save_location}\n")

def standup_meeting(args):
    while True:
        os.system('clear')
        print(f"{desc}\n@{default_location}\n")
        # Preview
        print(f"# {now}\n")
        for user, data in users_data.items():
            print(f"\n## {user}\n")
            print("| Status | Jira Ticket | Description |")
            print("|----------|-------------|-------------|")
            for category, items in data.items():
                for item in items:
                    jira_ticket = get_jira_url(item["jira_ticket"]) if item["jira_ticket"] else ""
                    print(f"| {category.capitalize()} | {jira_ticket} | {item['description']} |")
        # Get user input for the selected option
        print("\nOptions:")
        print("1. Add User 👤\t\t8. Remove User 👤")
        print("2. Add in-progress\t5. Remove in-progress")
        print("3. Complete ✅\t\t6. Remove Completed ✅")
        print("4. Add Blocker ❌\t7. Remove Blocker ❌")
        print("\t\t\t9. Exit and save\n")
        selected_option = int(input("Select an option by entering the number: "))
        if selected_option == 1:
            add_user()
        elif selected_option == 2:
            add_item("[ ]")
        elif selected_option == 3:
            add_item("✅")
        elif selected_option == 4:
            add_item("❌")
        elif selected_option == 5:
            remove_item("[ ]")
        elif selected_option == 6:
            remove_item("✅")
        elif selected_option == 7:
            remove_item("❌")
        elif selected_option == 8:
            remove_user()
        elif selected_option == 9:
            save_to_file()
            break
        else:
            print("Invalid option. Please try again.")
            
args = parse_arguments()
users_data = {user: {"[ ]": [], "✅": [], "❌": []} for user in args.users}
default_users = args.users
default_location = args.title 
default_folder = args.out
clear_screen()

standup_meeting(args)