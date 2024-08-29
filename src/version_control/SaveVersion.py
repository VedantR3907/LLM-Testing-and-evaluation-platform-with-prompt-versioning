from CheckVersion import query_huggingface_api, determine_version_increment
from datetime import datetime, timedelta
import sys
from pathlib import Path
from dateutil import parser
parent_dir = str(Path(__file__).resolve().parent.parent)
if parent_dir not in sys.path:
    sys.path.append(parent_dir)
from  database.prompts import get_latest_version_from_view

def Saving_Version(prompt_id, prompt):

    try:
        version_data = get_latest_version_from_view(prompt_id)
        
        if version_data:
            version_info = version_data.data
            try:
                last_updated = datetime.fromisoformat(version_info[0]['created_at'])  # Parses ISO datetime string
                print("Successfully parsed Last Updated:", last_updated)
            except ValueError as e:
                print(f"Unable to parse created_at {version_info['created_at']} due to error: {e}")
                return

            similarity_score = query_huggingface_api(prompt, version_info[0]['last_prompt'])
            version_increment = determine_version_increment(last_updated, similarity_score)
            print("Version increment determined:", version_increment)

            new_version_number = calculate_new_version(version_info[0]['last_version'], version_increment)

            return new_version_number

    except Exception as e:
        return f"An error occurred: {e}"


def calculate_new_version(current_version, increment):
    major, minor = map(int, current_version.split('.'))
    if increment == '+1':
        major += 1
        new_version = f"{major}.0"
    else:  # Assume increment is '+.1'
        minor += 1
        new_version = f"{major}.{minor}"
    return new_version