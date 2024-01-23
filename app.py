# --------------------------------------------------------------------------------------------------
# Base Code for Trigger Monitoring Dashboard
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
import shinyswatch
from shiny import App, Inputs, Outputs, Session, reactive, render, ui
from utils import load_config, style_trigger, get_trigger_tables
import pandas as pd

# Loading Country Variables
country = "madagascar"
config = load_config()

# Accessing values for the specified country
country_config = config.get("countries", {}).get(country, {})

# Access individual values using the 'country' variable
modes = country_config.get("mode", [])
year = country_config.get("year")
target_season = country_config.get("target_season")
frequencies = country_config['freq']
issue_month = country_config['issue_month']
design_tool = country_config['design_tool']
report = country_config['report']

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
                      ui.output_data_frame("table_key0_trigger"),
                      ),
               ui.nav(f"{next((mode for mode in modes if mode['key'] == 1), None).get('name')}",
                      ui.output_data_frame("table_key1_trigger")
                      ),
           ),
           ),
    ui.nav_spacer(),
    ui.nav_menu(
        "Additional Resources",
        ui.nav_control(
            ui.a(
                "Design Tool",
                href=design_tool,
                target="_blank",
            )
        ),
        ui.nav_control(
            ui.a(
                "R Markdown Reports",
                href=report,
                target="_blank",
            )
        ),
        align="right",
    ),
    ui.nav_control(
        ui.img(
            src="https://iri.columbia.edu/wp-content/uploads/2015/10/IRI_icon_Blue-300x295.png",
            href="https://iri.columbia.edu",
            width="50px",
            height="50px",
        )
    ),
    title=f"{country.capitalize()} Trigger Monitoring -  {target_season} {year}",
    window_title=f"{country.capitalize()} Trigger Monitoring -  {target_season} {year}",
    collapsible=True,
    fluid=True,
    id="navbar"
)


def server(input, output, session):
    @render.data_frame
    def table_key0_trigger():
        with ui.Progress(min=1, max=15) as p:
            p.set(message="Calculation in progress", detail="This may take a few secs...")

            data = combined_admin0

        return render.DataTable(data, filters=True)

    @render.data_frame
    def table_key1_trigger():
        with ui.Progress(min=1, max=15) as p:
            p.set(message="Calculation in progress", detail="This may take a few secs...")

            data = combined_admin1

        return render.DataTable(data, filters=True)


app = App(app_ui, server)
