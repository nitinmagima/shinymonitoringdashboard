#Loading Packages
import shinyswatch
from shiny import App, ui, render
from utils import get_data, load_config, style_trigger

# Loading Country Variables
country = "djibouti"
config = load_config()

# Accessing values for the specified country
country_config = config.get("countries", {}).get(country, {})

# Now you can access individual values using the 'country' variable
modes = country_config.get("mode", [])
year = country_config.get("year")
target_season = country_config.get("target_season")
frequencies = country_config['freq']
issue_month = country_config['issue_month']

for freq in frequencies:
    for mode in modes:
        for month in issue_month:
            skill = f"output_freq_{freq}_mode_{mode['key']}_month_{month}_skill"
            table = f"output_freq_{freq}_mode_{mode['key']}_month_{month}_table"

            locals()[table], locals()[skill] = get_data(country="djibouti", mode=0, region=[70],
             season="season1", predictor="pnep", predictand="bad-years", year=2023,
             issue_month0=5, freq=freq, include_upcoming="false")

            print(skill)
            print(table)

#App Layout

app_ui = ui.page_navbar(
    shinyswatch.theme.lux(),
    ui.nav(
        "Trigger Monitor",
        ui.layout_sidebar(
            ui.panel_sidebar(
            ),
            ui.panel_main(
                ui.navset_tab(
                    ui.nav(
                        f"{next((mode for mode in modes if mode['key'] == 0), None).get('name')}",
                                ui.navset_tab(ui.nav(f"Frequency - {frequencies[0]}")),
                        ui.tags.h2("  "),
                        ui.tags.h3("Skill Analysis"),
                        ui.output_table("table_key0_skill"),
                        ui.tags.h3("Trigger Analysis"),
                        ui.output_table("table_key0_trigger"),
                    ),
#                    ui.nav(f"{next((mode for mode in modes if mode['key'] == 1), None).get('name')}"),
#                    ui.nav(f"{next((mode for mode in modes if mode['key'] == 2), None).get('name')}"),
                )
            ),
        ),
    ),
    ui.nav("FEWSNET"),
    ui.nav("Resources"),
    title=f"Trigger Monitoring Dashboard - {country.capitalize()} {target_season} {year}",
)

def server(input, output, session):
    @output
    @render.table
    def table_key0_trigger():
        return (output_freq_15_mode_0_month_3_table.style.set_table_attributes(
                    'class="dataframe shiny-table table w-auto"'
                )
                .map(style_trigger, props='color:white;background-color:red'))

    @output
    @render.table
    def table_key0_skill():
        return output_freq_15_mode_0_month_3_skill


app = App(app_ui, server)