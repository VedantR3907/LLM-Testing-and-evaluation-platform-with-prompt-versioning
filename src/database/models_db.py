from supabase_config import supabase


def fetch_model_details():
    # Fetch data from the 'models' table in Supabase
    response = supabase.table("models").select("model_id, model_name").execute()
    # Create a dictionary to map model names to their IDs
    model_details = {model['model_name']: model['model_id'] for model in response.data}
    return model_details

def update_model_uservotes(model_name):
    """Update the total_votes of a model in the database."""
    try:
        # Fetch the current total_votes for the model
        response = supabase.table("models").select("total_votes").eq("model_name", model_name).execute()
        if response.data:
            current_votes = response.data[0]['total_votes']
            # Increment total_votes by 1
            new_votes = current_votes + 1
            # Update the total_votes field in the database
            response = supabase.table("models").update({"total_votes": new_votes}, returning="minimal").eq("model_name", model_name).execute()
            return response
        else:
            print(f"No model found with name: {model_name}")
    except Exception as e:
        print(f"An error occurred: {e}")

def fetch_model_votes():
    # Execute the SQL query
    response = supabase.table("models").select("model_name, total_votes").execute()

    # Check if the query was successful
    if response:
        return response.data
    print(f"An error occurred: {response.error}")
    return []