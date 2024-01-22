# Loading Packages
import shinyswatch
from shiny import App, ui, render
from utils import load_config, style_trigger, get_trigger_tables
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

# Combine admin tables for a specific mode

admin_tables = get_trigger_tables()

combined_admin0 = pd.concat(admin_tables["admin0_tables"].values(), ignore_index=True)
combined_admin1 = pd.concat(admin_tables["admin1_tables"].values(), ignore_index=True)


# App Layout

app_ui = ui.page_navbar(
    shinyswatch.theme.lux(),
    ui.nav("Trigger Monitor",
           ui.navset_card_pill(
               ui.nav(f"{next((mode for mode in modes if mode['key'] == 0), None).get('name')}",
                      ui.output_table("table_key0_trigger"),
                      ),
               ui.nav(f"{next((mode for mode in modes if mode['key'] == 1), None).get('name')}",
                      ui.output_table("table_key1_trigger")
                      ),
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
        return (combined_admin0.style.set_table_attributes(
            'class="dataframe shiny-table table w-auto"'
        )
                .map(style_trigger, props='color:white;background-color:red'))

    @output
    @render.table
    def table_key1_trigger():
        return (combined_admin1.style.set_table_attributes(
            'class="dataframe shiny-table table w-auto"'
        )
                .map(style_trigger, props='color:white;background-color:red'))


app = App(app_ui, server)
