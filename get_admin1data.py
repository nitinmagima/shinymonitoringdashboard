import requests
import pandas as pd
import yaml
import os

def get_admin_data(maproom, level):
    # Construct the API URL with the provided parameters
    api_url = f"https://iridl.ldeo.columbia.edu/fbfmaproom2/regions?country={maproom}&level={level}"

    print(api_url)

    response = requests.get(api_url)

    # Check if the request was successful (status code 200)
    if response.status_code == 200:
        # Parse the JSON data
        json_data = response.json()

        # Create a DataFrame from the JSON data
        df = pd.DataFrame(json_data)

        # Extract "key" and "label" from the "regions" column
        df[['key', 'label']] = df['regions'].apply(pd.Series)

        # Drop the original "regions" column if needed
        df = df.drop('regions', axis=1)

        return df
    else:
        # Print an error message if the request was not successful
        print(f"Error: {response.status_code}")
        return None

def save_admin_data_to_csv(maproom_names):
    for maproom in maproom_names:
        # Get admin data for the current maproom value
        admin_data = get_admin_data(maproom, level)  # Assuming 'level' is defined somewhere

        # Check if admin data is retrieved successfully
        if admin_data is not None:
            # Define the filename for the CSV file
            csv_filename = f"data/{maproom}_admin_data.csv"

            # Save the admin data to CSV file
            admin_data.to_csv(csv_filename, index=False)
            print(f"Saved admin data for {maproom} to {csv_filename}")
        else:
            print(f"Failed to retrieve admin data for {maproom}")

if __name__ == "__main__":
    # Load maproom values from the YAML file
    with open("config.yaml", "r") as yaml_file:
        yaml_data = yaml.safe_load(yaml_file)
        maproom_data = yaml_data.get("maprooms", {})

    # Define the level variable
    level = 1  # Define your level value here

    # Ensure the data directory exists
    if not os.path.exists("data"):
        os.makedirs("data")

    # Extract only the maproom names
    maproom_names = [data['maproom'] for data in maproom_data.values()]

    print(maproom_names)

    # Save admin data to CSV files
    save_admin_data_to_csv(maproom_names)