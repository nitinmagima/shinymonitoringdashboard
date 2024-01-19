# Loading Packages
import shinyswatch
from shiny import App, ui, render
from utils import get_admin0data, load_config, style_trigger, get_admin_data
import pandas as pd

# Loading Country Variables
country = "djibouti"
config = load_config()

# Accessing values for the specified country
country_config = config.get("countries", {}).get(country, {})

# Access individual values using the 'country' variable
modes = country_config.get("mode", [])
year = country_config.get("year")
target_season = country_config.get("target_season")
frequencies = country_config['freq']
issue_month = country_config['issue_month']

# Initialize an empty dictionary to store tables
admin0_tables = {}
admin1_tables = {}
admin2_tables = {}

# Creating admin0 table
for freq in frequencies:
    for mode in modes:
        for month in issue_month:
            admin = get_admin_data(country, 0)['key']
            # Iterate over each key value
            for region_key in admin:
                table_name = f"output_freq_{freq}_mode_{mode['key']}_month_{month}_region_{region_key}_table"

                admin_name = f"{mode['key']}"

                admin0_tables = get_admin0data(country=country, mode=mode['key'], region=region_key,
                                                           season="season1", predictor="pnep", predictand="bad-years",
                                                           year=2023,
                                                           issue_month0=month, freq=freq, include_upcoming="false")

combined_admin0 = pd.concat(admin0_tables.values(), ignore_index=True)

# App Layout

app_ui = ui.page_navbar(
    shinyswatch.theme.lux(),
    ui.nav("Trigger Monitor",
           ui.navset_card_pill(
               ui.nav(f"{next((mode for mode in modes if mode['key'] == 0), None).get('name')}",
                      ui.output_table("table_key0_trigger"),
                      ),
               ui.nav(f"{next((mode for mode in modes if mode['key'] == 1), None).get('name')}", "Page AX2"),
               ui.nav(f"{next((mode for mode in modes if mode['key'] == 2), None).get('name')}", "Page AX3")
           ),
           ),
    ui.nav("FEWSNET", "Page B content"),
    ui.nav("Resources", "Page C content"),
    title=f"{country.capitalize()} Trigger Monitoring -  {target_season} {year}",
    id="navbar"
)


def server(input, output, session):
    @output
    @render.table
    def table_key0_trigger():
        return (combined_df.style.set_table_attributes(
            'class="dataframe shiny-table table w-auto"'
        )
                .map(style_trigger, props='color:white;background-color:red'))


app = App(app_ui, server)
