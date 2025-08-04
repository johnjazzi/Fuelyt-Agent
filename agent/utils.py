import json
import csv
import sys
import os

def export_chat_history_to_csv(json_file_path, csv_file_path):
    """
    Reads user conversation history from a JSON file and exports it to a CSV file.

    Args:
        json_file_path (str): The path to the input JSON file.
        csv_file_path (str): The path to the output CSV file.
    """
    with open(json_file_path, 'r') as f:
        data = json.load(f)

    with open(csv_file_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        # Write the header row
        writer.writerow(['user_id', 'user_message', 'agent_response'])

        # The data is nested under a 'users' key, which in turn contains a dictionary of users
        users = data.get('users', {})
        for user_key, user_data in users.items():
            user_id = user_data.get('user_id', user_key) # Use user_id field, fallback to key
            conversation_history = user_data.get('ai_context', {}).get('conversation_history', [])
            for entry in conversation_history:
                user_message = entry.get('user_message') or entry.get('user')
                agent_response = entry.get('agent_response') or entry.get('ai')
                
                if user_message is not None and agent_response is not None:
                    writer.writerow([user_id, user_message, agent_response])

def main():
    """
    Main function to handle command-line arguments.
    """
    if len(sys.argv) < 2:
        print("Usage: python agent/utils.py <command>")
        print("Available commands: export_chat_hist")
        sys.exit(1)

    command = sys.argv[1]

    if command == 'export_chat_hist':
        # Assumes the script is run from the project root.
        json_file_path = 'fuelyt_data.json'
        csv_file_path = 'chat_history.csv'
        export_chat_history_to_csv(json_file_path, csv_file_path)
        print(f"Chat history has been exported to {csv_file_path}")
    else:
        print(f"Unknown command: {command}")
        sys.exit(1)

if __name__ == '__main__':
    main()
