# --------------------------------------------------------------------------------------------------
# Functions for Trigger Monitoring Dashboard
#
# Author - Nitin Magima
# Date - 2024
# Version - 1.0
# --------------------------------------------------------------------------------------------------

# ==================================================================================================
#
# IMPORTANT - DISCLAIMER AND RIGHTS STATEMENT
# This is a set of scripts written by the Financial Instruments Team at the International Research
# Institute for Climate and Society (IRI) part of The Columbia Climate School, Columbia University
# They are shared for educational purposes only.  Anyone who uses this code or its
# functionality or structure, assumes full liability and should inform and credit IRI.
#
# ==================================================================================================

# Loading Packages
import requests
import pandas as pd
import yaml

maproom = "madagascar"


def load_config(file_path="config.yaml"):
    with open(file_path, "r") as file:
        config = yaml.safe_load(file)
    return config


# Loading Country Variables
config = load_config()

# Accessing values for the specified country
country_config = config.get("maprooms", {}).get(maproom, {})

# Access individual values using the 'country' variable
modes = country_config.get("mode", [])
year = country_config.get("year")
target_season = country_config.get("target_season")
frequencies = country_config['freq']
issue_month = country_config['issue_month']
predictor = country_config['predictor']
predictand = country_config['predictand']
username = country_config['username']
password = country_config['password']
threshold_protocol = country_config['threshold_protocol']


def get_data(maproom=maproom, mode=0, region=[70],
             season="season1", predictor="pnep", predictand="bad-years", year=2023,
             issue_month0=5, freq=15, include_upcoming="false", username=username, password=password):
    # Make a GET request to the API
    region_str = ",".join(map(str, region))  # Convert region values to a comma-separated string
    api_url = (f"https://iridl.ldeo.columbia.edu/fbfmaproom2/{maproom}/"
               f"export?season={season}&issue_month0={issue_month0}&freq={freq}&predictor"
               f"={predictor}&predictand={predictand}&include_upcoming={include_upcoming}&mode={mode}"
               f"&region={region_str}")

    print(api_url)

    auth = (username, password)
    response = requests.get(api_url, auth=auth)

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
            'Metric': non_nested_df.columns,
            'Value': non_nested_df.iloc[0].values
        })

        melted_non_nested_df = melted_non_nested_df.iloc[:2, :]

        replace_values = {'threshold': 'Forecast Threshold', 'skill.accuracy': 'Forecast Accuracy'}
        melted_non_nested_df['Metric'].replace(replace_values, inplace=True)

        # Convert melted_non_nested_df to a dictionary
        melted_non_nested_dict = melted_non_nested_df.set_index('Metric')['Value'].to_dict()

        # Convert flattened data to Pandas DataFrame
        df = pd.DataFrame(flattened_data).drop(non_nested_df.columns, axis=1, errors='ignore')
        df['triggered'] = df[predictor] > melted_non_nested_dict['Forecast Threshold']
        df['trigger difference'] = df[predictor] - melted_non_nested_dict['Forecast Threshold']
        df['Adjusted Forecast Threshold'] = melted_non_nested_dict['Forecast Threshold'] + threshold_protocol
        df['Triggered Adjusted'] = df[predictor] > melted_non_nested_dict['Forecast Threshold']
        df.rename(columns={predictor: 'forecast'}, inplace=True)
        df['forecast'] = df['forecast']
        df['trigger difference'] = df['trigger difference']
        df = df.loc[:, ['forecast', 'trigger difference', 'triggered',
                        'Triggered Adjusted', 'Adjusted Forecast Threshold']].iloc[1, :].to_frame().T

        melted_non_nested_df['Value'] = melted_non_nested_df['Value']

        # Combine df and melted_non_nested_df
        melted_non_nested_df = melted_non_nested_df.T  # Transpose the DataFrame
        melted_non_nested_df.columns = melted_non_nested_df.iloc[0]  # Set the first row as column names
        melted_non_nested_df = melted_non_nested_df.iloc[1:, :].reset_index(drop=True).rename_axis(None,
                                                                                                   axis=1)  # Reset index
        combined_df = pd.concat([df.reset_index(drop=True), melted_non_nested_df], axis=1).reset_index(drop=True)
        combined_df['Frequency (%)'] = f"{freq}%"
        combined_df['Forecast Accuracy (%)'] = combined_df['Forecast Accuracy'] * 100
        combined_df['Threshold Protocol'] = f"{threshold_protocol}"

        month_mapping = {
            0: 'Jan',
            1: 'Feb',
            2: 'Mar',
            3: 'Apr',
            4: 'May',
            5: 'Jun',
            6: 'Jul',
            7: 'Aug',
            8: 'Sep',
            9: 'Oct',
            10: 'Nov',
            11: 'Dec'
        }

        combined_df['Issue Month'] = issue_month0
        combined_df['Issue Month'] = combined_df['Issue Month'].map(month_mapping)

        # Rearrange the columns in a specific sequence
        desired_columns = ['Frequency (%)', 'Issue Month', 'forecast', 'Forecast Threshold', 'trigger difference',
                           'Forecast Accuracy (%)', 'triggered', 'Adjusted Forecast Threshold',
                           'Threshold Protocol', 'Triggered Adjusted',]
        combined_df = combined_df[desired_columns]

        # Return the combined DataFrame
        return combined_df
    else:
        # Return an empty DataFrame or handle the error as needed
        print(f"Error: {response.status_code}")
        return pd.DataFrame()


# Function to apply conditional formatting to tables
# def style_trigger(v, props=''):
#     return props if v == True else None


def get_admin_data(maproom, level):
    # Construct the API URL with the provided parameters
    api_url = f"https://iridl.ldeo.columbia.edu/fbfmaproom2/regions?country={maproom}&level={level}"

    print(api_url)

    # Make a GET request to the API
    if username and password:
        auth = (username, password)
        response = requests.get(api_url, auth=auth)
    else:
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


def get_trigger_tables(mode=0):
    # Initialize a dictionary to store admin tables
    admin_tables = {}

    # Creating trigger tables

    admin_name = f"admin{mode}_tables"
    admin_tables[admin_name] = {}
    for freq in frequencies:
        for month in issue_month:
            admin_data = get_admin_data(maproom, mode)
            # Iterate over each key value
            if isinstance(admin_data, pd.Series):
                for region_key, label in admin_data.items():
                    print(region_key, label)
                    table_name = f"output_freq_{freq}_mode_{mode}_month_{month}_region_{region_key}_table"

                    df = get_data(maproom=maproom, mode=mode, region=[region_key],
                                  season="season1", predictor=predictor, predictand=predictand,
                                  year=year,
                                  issue_month0=month, freq=freq, include_upcoming="false", username=username,
                                  password=password)

                    df.insert(0, 'Admin Name', label)
                    admin_tables[admin_name][table_name] = df

            elif isinstance(admin_data, pd.DataFrame):
                for index, row in admin_data.iterrows():
                    region_key, label = row['key'], row['label']

                    table_name = f"output_freq_{freq}_mode_{mode}_month_{month}_region_{region_key}_table"

                    df = get_data(maproom=maproom, mode=mode, region=[region_key],
                                  season="season1", predictor=predictor, predictand=predictand,
                                  year=year,
                                  issue_month0=month, freq=freq, include_upcoming="false", username=username,
                                  password=password)

                    df.insert(0, 'Admin Name', label)
                    admin_tables[admin_name][table_name] = df

            else:
                # Handle other cases or raise an error
                raise ValueError("Unexpected output type from get_admin_data.")

    return admin_tables
