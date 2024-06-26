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
from utils import load_config, get_trigger_tables
import pandas as pd

# Loading Country Variables
maproom = "lesotho-ond"

config = load_config()

# Accessing values for the specified maproom
country_config = config.get("maprooms", {}).get(maproom, {})

# Access individual values using the 'maproom' variable
country = country_config.get("country")
modes = country_config.get("mode", [])
year = country_config.get("year")
season = country_config.get("season")
target_season = country_config.get("target_season")
frequencies = country_config['freq']
issue_month = country_config['issue_month']
predictor = country_config['predictor']
predictand = country_config['predictand']
include_upcoming = country_config['include_upcoming']
design_tool = country_config['design_tool']
report = country_config['report']
username = country_config['username']
password = country_config['password']
threshold_protocol = country_config['threshold_protocol']
need_valid_keys = country_config['need_valid_keys']
valid_keys = country_config['admin1_list']

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
    async def table_key0_trigger():
        with ui.Progress(min=1, max=15) as p:
            p.set(message="Calculation in progress", detail="This may take a few mins...")

            admin_tables = get_trigger_tables(maproom=maproom, mode=0, season=season, predictor=predictor,
                                              predictand=predictand, issue_month=issue_month, frequencies=frequencies,
                                              include_upcoming=include_upcoming, threshold_protocol=threshold_protocol,
                                              username=username, password=password,need_valid_keys=need_valid_keys,
                                              valid_keys=valid_keys)

            combined_admin0 = pd.concat(admin_tables["admin0_tables"].values(), ignore_index=True)

            data = combined_admin0

            p.set(15, message="Finished!")

        return render.DataTable(data, filters=True)

    @render.data_frame
    def table_key1_trigger():
        with ui.Progress(min=1, max=15) as p:
            p.set(message="Calculation in progress", detail="This may take a few mins...")

            admin_tables = get_trigger_tables(maproom=maproom, mode=1, season=season, predictor=predictor,
                                              predictand=predictand, issue_month=issue_month, frequencies=frequencies,
                                              include_upcoming=include_upcoming, threshold_protocol=threshold_protocol,
                                              username=username, password=password,need_valid_keys=need_valid_keys,
                                              valid_keys=valid_keys)

            combined_admin1 = pd.concat(admin_tables["admin1_tables"].values(), ignore_index=True)

            data = combined_admin1

            p.set(15, message="Finished!")

        return render.DataTable(data, filters=True)


app = App(app_ui, server)
