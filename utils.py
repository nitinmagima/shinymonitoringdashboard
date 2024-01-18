#Loading Packages
import requests
import pandas as pd
import yaml

def load_config(file_path="config.yaml"):
    with open(file_path, "r") as file:
        config = yaml.safe_load(file)
    return config

def get_data(country="djibouti", mode=0, region=[70],
             season="season1", predictor="pnep", predictand="bad-years", year=2023,
             issue_month0=5, freq=15, include_upcoming="false"):

    region_str = ",".join(map(str, region))  # Convert region values to a comma-separated string
    api_url = (f"http://iridl.ldeo.columbia.edu/fbfmaproom2/{country}/"
               f"export?&mode={mode}&region={region_str}&season={season}&"
               f"predictor={predictor}&predictand={predictand}&year={year}&issue_month0={issue_month0}&freq={freq}&"
               f"include_upcoming={include_upcoming}")

    print(api_url)

    # Make a GET request to the API
    response = requests.get(api_url)

    # Check if the request was successful (status code 200)
    if response.status_code == 200:
        # Parse the JSON data
        json_data = response.json()

        # Flatten nested dictionaries using json_normalize
        flattened_data = pd.json_normalize(json_data)

        # Initialize a list to store non-nested columns
        non_nested_columns = []

        # Check for columns with nested data (list of dictionaries) and expand them
        for column in flattened_data.columns:
            if isinstance(flattened_data[column][0], list):
                # Expand nested dictionaries in the list column
                expanded_data = pd.json_normalize(flattened_data[column].explode(), sep='_')

                # Combine the expanded columns with the original DataFrame
                flattened_data = pd.concat([flattened_data, expanded_data], axis=1)

                # Drop the original list column
                flattened_data = flattened_data.drop(column, axis=1)
            else:
                # Save non-nested columns to the list
                non_nested_columns.append(column)

        # Create a separate DataFrame for non-nested columns
        non_nested_df = flattened_data[non_nested_columns]

        # Create a new DataFrame using the data from the first row of non-nested DataFrame
        melted_non_nested_df = pd.DataFrame({
            'Skill Name': non_nested_df.columns,
            'Skill Value': non_nested_df.iloc[0].values
        })

        melted_non_nested_df = melted_non_nested_df.iloc[:2, :]

        # Convert melted_non_nested_df to a dictionary
        melted_non_nested_dict = melted_non_nested_df.set_index('Skill Name')['Skill Value'].to_dict()

        # Convert flattened data to Pandas DataFrame
        df = pd.DataFrame(flattened_data).drop(non_nested_df.columns, axis=1, errors='ignore')
        df['triggered'] = df['pnep'] > melted_non_nested_dict['threshold']
        df['trigger difference'] = df['pnep'] - melted_non_nested_dict['threshold']
        df = df.loc[:, ['triggered','pnep', 'trigger difference']].iloc[1, :].to_frame().T


        # Return the relevant dataframes or results
        return df, melted_non_nested_df

    else:
        # Print an error message if the request was not successful
        print(f"Error: {response.status_code}")
        return None, None  # You might want to handle errors more gracefully

