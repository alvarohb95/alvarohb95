# modules/map.py

from shiny import ui, render
from shiny.ui import tags, modal, modal_show
import pandas as pd
import geopandas as gpd
import os
import folium
from folium.plugins import MarkerCluster

# Define the data paths
DATA_DIR = os.path.join(os.path.dirname(__file__), 'data')

# --- Load and prepare data for "Score de Fonctionnalité des marchés" ---

# Load shapefiles
shapefile_dir = os.path.join(DATA_DIR, 'Shapefiles', 'hti_adm_cnigs_20181129')
country_shp = gpd.read_file(os.path.join(shapefile_dir, 'hti_admbnda_adm0_cnigs_20181129.shp'))
departments_shp = gpd.read_file(os.path.join(shapefile_dir, 'hti_admbnda_adm1_cnigs_20181129.shp'))
communes_shp = gpd.read_file(os.path.join(shapefile_dir, 'hti_admbnda_adm2_cnigs_20181129.shp'))

def convert_datetime_columns_to_str(gdf):
    for col in gdf.columns:
        if pd.api.types.is_datetime64_any_dtype(gdf[col]):
            gdf[col] = gdf[col].astype(str)
    return gdf

country_shp = convert_datetime_columns_to_str(country_shp)
departments_shp = convert_datetime_columns_to_str(departments_shp)
communes_shp = convert_datetime_columns_to_str(communes_shp)

# Load market data
icsm_marketplaces = pd.read_excel(os.path.join(DATA_DIR, 'ICSM_Marketplaces.xlsx'))

# Loop through all Excel files ending with '_mfs.xlsx'
excel_files = [f for f in os.listdir(DATA_DIR) if f.endswith('_mfs.xlsx')]
if not excel_files:
    raise FileNotFoundError("No Excel files ending with '_mfs.xlsx' found in the specified directory.")

list_dfs = []
for file in excel_files:
    file_path = os.path.join(DATA_DIR, file)
    try:
        df_temp = pd.read_excel(file_path)
    except Exception as e:
        raise ValueError(f"Error reading the Excel file {file}: {e}")

    # Extract the cycle name from the file name (e.g. 'cycle_1' from 'cycle_1_mfs.xlsx')
    cycle_name = file.split('_mfs.xlsx')[0]
    df_temp['Cycle'] = cycle_name

    list_dfs.append(df_temp)

mfs_analysis = pd.concat(list_dfs, ignore_index=True)

# Merge marketplace info with the MFS analysis
markets_df = pd.merge(icsm_marketplaces, mfs_analysis, on='marketplace')
markets_df.columns = markets_df.columns.str.strip()
markets_df['marketplace'] = markets_df['marketplace'].str.strip()

# Indicators
numerical_indicators = {
    'mfs_accessibility_score': {'max': 25, 'type': 'numerical'},
    'mfs_availability_score': {'max': 30, 'type': 'numerical'},
    'mfs_affordability_score': {'max': 15, 'type': 'numerical'},
    'mfs_resilience_score': {'max': 20, 'type': 'numerical'},
    'mfs_infrastructure_score': {'max': 10, 'type': 'numerical'},
    'mfs_total_score': {'max': 100, 'type': 'numerical'}
}
categorical_indicators = {
    'sum_low_dimensions': {'rename': 'Dimensions Totales Faibles', 'type': 'categorical'},
    'mfs_functionality_classification': {'rename': 'Classification Fonctionnalité', 'type': 'categorical'}
}
indicator_choices = {**numerical_indicators, **categorical_indicators}

# Labels for displaying indicators
indicator_labels = {
    'mfs_accessibility_score': 'Accessibilité',
    'mfs_availability_score': 'Disponibilité',
    'mfs_affordability_score': 'Abordabilité',
    'mfs_resilience_score': 'Résilience',
    'mfs_infrastructure_score': 'Infrastructure',
    'mfs_total_score': 'Score Total',
    'sum_low_dimensions': 'Dimensions Totales Faibles',
    'mfs_functionality_classification': 'Classification Fonctionnalité'
}

# Font Awesome icons
indicator_icons = {
    'mfs_accessibility_score': 'road',
    'mfs_availability_score': 'shopping-cart',
    'mfs_affordability_score': 'usd',
    'mfs_resilience_score': 'shopping-basket',
    'mfs_infrastructure_score': 'credit-card',
    'mfs_total_score': 'shopping-basket',
    'sum_low_dimensions': 'check-square',
    'mfs_functionality_classification': 'shopping-basket',
}

# Classification labels
classification_labels = {
    'Limited functionality': 'Fonctionnalité limitée',
    'Poor functionality': 'Fonctionnalité pauvre',
    'Severe issues': 'Problèmes sévères',
    'Unknown': 'Pas connu'
}

# Classification colors recognized by Folium (or CSS hex codes)
classification_colors = {
    'Limited functionality': 'orange',
    'Poor functionality': 'lightred',
    'Severe issues': 'red',
    'Unknown': 'gray'
}

# Helper to fix "lightred" in the legend
def fix_color_for_legend(color_name: str) -> str:
    if color_name.lower() == "lightred":
        return "#ff8080"
    return color_name

def create_legend_html(thresholds, colors, indicator_label):
    """
    Create a legend for numerical indicators with thresholds.
    """
    legend_html = f'''
    <div style="
        position: fixed; 
        bottom: 40px; right: 20px; width: 270px; height: auto;
        border:2px solid grey; z-index:9999; font-size:14px;
        background-color:white; opacity: 0.9;
        padding: 10px;
        border-radius: 5px;
        box-shadow: 2px 2px 5px rgba(0,0,0,0.3);
        ">
     &nbsp;<b>{indicator_label}</b><br><br>
    '''
    for i in range(len(colors)):
        from_val = round(thresholds[i], 2)
        to_val = round(thresholds[i+1], 2)
        display_color = fix_color_for_legend(colors[i])
        legend_html += f'''
        &nbsp;<i style="background:{display_color}; width:14px; height:14px; 
        display:inline-block; vertical-align:middle; margin-right:5px;"></i>
        {from_val} - {to_val}<br>
        '''
    legend_html += '</div>'
    return legend_html

def create_categorical_legend_html(categories, colors, indicator_label):
    """
    Create a legend for categorical indicators, converting "lightred"
    to a visible hex code for the squares.
    """
    legend_html = f'''
    <div style="
        position: fixed; 
        bottom: 40px; right: 20px; width: 270px; height: auto;
        border:2px solid grey; z-index:9999; font-size:14px;
        background-color:white; opacity: 0.9;
        padding: 10px;
        border-radius: 5px;
        box-shadow: 2px 2px 5px rgba(0,0,0,0.3);
        ">
     &nbsp;<b>{indicator_label}</b><br><br>
    '''
    for category, color in zip(categories, colors):
        display_color = fix_color_for_legend(color)
        legend_html += f'''
        &nbsp;<i style="background:{display_color}; width:14px; height:14px; 
        display:inline-block; vertical-align:middle; margin-right:5px;"></i>
        {category}<br>
        '''
    legend_html += '</div>'
    return legend_html

def map_output(input):
    """
    Build the Folium map using:
      - cycle_select_map (an integer slider)
      - indicator_select
    Then compare the selected cycle vs. previous cycle if available.
    We keep the previous marker format (colored icons). 
    Popup shows "Cycle actuel" / "Cycle précédent" instead of cycle_xx labels.
    """

    # Determine selected cycle, e.g. 2 => "cycle_2"
    selected_cycle_int = input.cycle_select_map()
    selected_cycle_str = f"cycle_{selected_cycle_int}"

    # Previous cycle (if any)
    if selected_cycle_int > 1:
        prev_cycle_str = f"cycle_{selected_cycle_int - 1}"
    else:
        prev_cycle_str = None

    # Filter for the current cycle
    current_df = markets_df[markets_df["Cycle"] == selected_cycle_str].copy()
    # Merge with previous if it exists
    if prev_cycle_str is not None:
        prev_df = markets_df[markets_df["Cycle"] == prev_cycle_str].copy()
        merged_df = pd.merge(
            current_df,
            prev_df,
            on="marketplace",
            how="left",
            suffixes=("_current", "_prev")
        )
    else:
        merged_df = current_df.copy()
        # rename columns => *_current (except for marketplace)
        for col in merged_df.columns:
            if col != "marketplace":
                merged_df.rename(columns={col: col + "_current"}, inplace=True)
        # Add dummy prev columns
        for ind in indicator_choices.keys():
            merged_df[ind + "_prev"] = None

    # Identify which indicator is selected
    label_to_key = {v: k for k, v in indicator_labels.items()}
    selected_label = input.indicator_select()
    selected_key = label_to_key.get(selected_label, "mfs_total_score")

    indicator_info = indicator_choices[selected_key]
    indicator_type = indicator_info['type']
    selected_icon = indicator_icons.get(selected_key, 'info-circle')

    # Build Folium map
    m = folium.Map(
        location=[19.0, -72.0],
        zoom_start=8,
        tiles='cartodbpositron',
    )
    folium.GeoJson(
        data=communes_shp,
        name='Communes',
        style_function=lambda x: {'color': '#737373', 'weight': 1, 'fillOpacity': 0}
    ).add_to(m)
    folium.GeoJson(
        data=departments_shp,
        name='Départements',
        style_function=lambda x: {'color': '#737373', 'weight': 2, 'fillOpacity': 0}
    ).add_to(m)
    folium.GeoJson(
        data=country_shp,
        name='Pays',
        style_function=lambda x: {'color': '#737373', 'weight': 4, 'fillOpacity': 0}
    ).add_to(m)

    marker_cluster = MarkerCluster(name='Indicateurs de marché').add_to(m)

    # ------------------------------------------------------
    # 1) Numerical Indicators
    # ------------------------------------------------------
    if indicator_type == 'numerical':
        curr_col = selected_key + "_current"
        valid_rows = merged_df[~merged_df[curr_col].isna()]

        # compute threshold color bins from current values
        if not valid_rows.empty:
            values = valid_rows[curr_col]
            q25, q50, q75 = values.quantile([0.25, 0.5, 0.75]).tolist()
            min_val = values.min()
            max_val = values.max()
            thresholds = [min_val, q25, q50, q75, max_val]
        else:
            thresholds = [0, 0, 0, 0, 0]

        colors = ['red', 'lightred', 'orange', 'green']

        def get_color(v):
            for i in range(len(thresholds) - 1):
                if thresholds[i] <= v <= thresholds[i+1]:
                    return colors[i]
            return 'gray'

        for idx, row in merged_df.iterrows():
            lat = row.get("latitude_current", None)
            lon = row.get("longitude_current", None)
            curr_val = row.get(curr_col, None)

            if pd.isna(lat) or pd.isna(lon) or pd.isna(curr_val):
                continue

            marketplace_name = row.get("marketplace", "Unknown")
            color_bg = get_color(curr_val)  # background color from thresholds

            prev_val = row.get(selected_key + "_prev", None)
            # Build popup: "Cycle actuel" / "Cycle précédent"
            current_str = f"Cycle actuel: {round(curr_val,1)}"
            if prev_cycle_str and pd.notna(prev_val):
                prev_str = f"Cycle précédent: {round(prev_val,1)}"
            else:
                prev_str = "(Pas de cycle précédent)"

            popup_html = f"""
            <table style='width:220px;'>
              <tr><td colspan='2'><b>{marketplace_name}</b></td></tr>
              <tr><td>{current_str}</td><td></td></tr>
              <tr><td>{prev_str}</td><td></td></tr>
            </table>
            """

            folium.Marker(
                location=[lat, lon],
                popup=folium.Popup(popup_html, max_width=250),
                icon=folium.Icon(
                    color=color_bg,
                    prefix='fa',
                    icon=selected_icon
                )
            ).add_to(marker_cluster)

        # numerical legend
        legend_html = create_legend_html(thresholds, colors, selected_label)
        m.get_root().html.add_child(folium.Element(legend_html))

    # ------------------------------------------------------
    # 2) sum_low_dimensions (categorical approach)
    # ------------------------------------------------------
    elif selected_key == 'sum_low_dimensions':
        # 1 -> orange, 2 -> lightred, >=3 -> red
        def get_sld_color(v):
            if v >= 3:
                return 'red'
            elif v == 2:
                return 'lightred'
            elif v == 1:
                return 'orange'
            else:
                return 'gray'

        curr_col = "sum_low_dimensions_current"
        prev_col = "sum_low_dimensions_prev"

        for idx, row in merged_df.iterrows():
            lat = row.get("latitude_current", None)
            lon = row.get("longitude_current", None)
            curr_val = row.get(curr_col, None)

            if pd.isna(lat) or pd.isna(lon) or pd.isna(curr_val):
                continue

            marketplace_name = row.get("marketplace", "Unknown")
            color_bg = get_sld_color(curr_val)

            prev_val = row.get(prev_col, None)
            current_str = f"Cycle actuel: {int(curr_val)}"
            if prev_cycle_str and pd.notna(prev_val):
                prev_str = f"Cycle précédent: {int(prev_val)}"
            else:
                prev_str = "(Pas de cycle précédent)"

            popup_html = f"""
            <table style='width:220px;'>
              <tr><td colspan='2'><b>{marketplace_name}</b></td></tr>
              <tr><td>{current_str}</td><td></td></tr>
              <tr><td>{prev_str}</td><td></td></tr>
            </table>
            """

            folium.Marker(
                location=[lat, lon],
                popup=folium.Popup(popup_html, max_width=250),
                icon=folium.Icon(
                    color=color_bg,
                    prefix='fa',
                    icon=indicator_icons['sum_low_dimensions']
                )
            ).add_to(marker_cluster)

        categories = ['1', '2', '≥ 3']
        legend_colors = ['orange', 'lightred', 'red']
        legend_title = f"{indicator_info['rename']} (dimensions < 50% de leur score max)"
        legend_html = create_categorical_legend_html(categories, legend_colors, legend_title)
        m.get_root().html.add_child(folium.Element(legend_html))

    # ------------------------------------------------------
    # 3) mfs_functionality_classification (categorical)
    # ------------------------------------------------------
    else:
        curr_col = "mfs_functionality_classification_current"
        prev_col = "mfs_functionality_classification_prev"

        for idx, row in merged_df.iterrows():
            lat = row.get("latitude_current", None)
            lon = row.get("longitude_current", None)
            curr_val = row.get(curr_col, "Unknown")

            if pd.isna(lat) or pd.isna(lon):
                continue

            marketplace_name = row.get("marketplace", "Unknown")
            curr_label = classification_labels.get(curr_val, 'Pas connu')
            color_bg = classification_colors.get(curr_val, 'gray')

            prev_val = row.get(prev_col, None)
            current_str = f"Cycle actuel: {curr_label}"
            if prev_cycle_str and pd.notna(prev_val):
                prev_label = classification_labels.get(prev_val, 'Pas connu')
                prev_str = f"Cycle précédent: {prev_label}"
            else:
                prev_str = "(Pas de cycle précédent)"

            popup_html = f"""
            <table style='width:220px;'>
              <tr><td colspan='2'><b>{marketplace_name}</b></td></tr>
              <tr><td>{current_str}</td><td></td></tr>
              <tr><td>{prev_str}</td><td></td></tr>
            </table>
            """

            folium.Marker(
                location=[lat, lon],
                popup=folium.Popup(popup_html, max_width=250),
                icon=folium.Icon(
                    color=color_bg,
                    prefix='fa',
                    icon=indicator_icons['mfs_functionality_classification']
                )
            ).add_to(marker_cluster)

        # Build a legend from whatever classifications we have in the current cycle
        all_current_vals = merged_df[curr_col].dropna().unique()
        classifications = [v for v in all_current_vals if v in classification_labels]
        if classifications:
            cat_labels = [classification_labels[c] for c in classifications]
            cat_colors = [classification_colors[c] for c in classifications]
            legend_label = indicator_labels[selected_key]
            legend_html = create_categorical_legend_html(cat_labels, cat_colors, legend_label)
            m.get_root().html.add_child(folium.Element(legend_html))

    folium.LayerControl().add_to(m)
    return ui.HTML(m._repr_html_())

# ---------------------
# UI Definition
# ---------------------
def map_ui():
    """
    Return a nav panel containing:
      - A left column with the cycle slider and indicator select
      - A right column with the map
    """
    # Gather unique cycle names (e.g. "cycle_1", "cycle_2", ...)
    unique_cycles = sorted(
        markets_df["Cycle"].unique(),
        key=lambda x: int(x.replace("cycle_", ""))
    )
    # Convert them to int for the slider
    cycle_nums = [int(x.replace("cycle_", "")) for x in unique_cycles]

    cycle_slider = ui.input_slider(
        "cycle_select_map",
        "Choisir le Cycle",
        min=min(cycle_nums),
        max=max(cycle_nums),
        value=min(cycle_nums),
        step=1
    )

    return ui.nav_panel(
        ui.tags.span(
            ui.tags.i(class_="fa fa-map icon"),
            "Carte du Score de MFS",
            class_="nav-panel-title"
        ),
        ui.row(
            ui.column(3,
                ui.div(
                    tags.label(class_="custom-select-label"),
                    cycle_slider,
                    class_="custom-select"
                ),
                ui.div(
                    tags.label("Choisir l'indicateur", class_="custom-select-label"),
                    ui.input_select(
                        "indicator_select",
                        None,
                        choices=[indicator_labels[key] for key in indicator_choices.keys()],
                        selected=indicator_labels.get(
                            'mfs_functionality_classification',
                            'Classification Fonctionnalité'
                        ),
                    ),
                    class_="custom-select"
                ),
                ui.output_ui("map_info"),
                class_="map-sidebar"
            ),
            ui.column(9,
                ui.output_ui("map"),
                class_="map-container"
            )
        )
    )

# ---------------------
# Server Definition
# ---------------------
def map_server(input, output, session):
    @output
    @render.ui
    def map():
        return map_output(input)

    @output
    @render.ui
    def map_info():
        selected_label = input.indicator_select()

        # MFS explanation
        mfs_text = ui.TagList(
            ui.h5("Méthodologie de Calcul du Score de Fonctionnalité des Marchés (MFS)"),
            tags.p(
                "Le Score de Fonctionnalité des Marchés (MFS) : est une méthode développée par REACH "
                "pour classifier les marchés en fonction de leur niveau de fonctionnalité. Il permet de "
                "comparer les marchés au sein d’un pays et entre différents pays, afin d’aider les "
                "acteurs humanitaires à identifier les marchés suffisamment fonctionnels pour être des "
                "cibles appropriées pour les programmes d’assistance en espèces et bons (CVA), et ceux "
                "qui nécessitent des interventions supplémentaires pour améliorer leur autonomie. "
                "Le MFS repose sur un ensemble d’indicateurs couvrant divers aspects de la fonctionnalité "
                "et se regroupent des clients/acheteurs à s’appropier d’un produit par rapport à son prix "
                "et la stabilité de ce dernier.",
                class_="p1"
            ),
            tags.p(
                tags.strong("L’accessibilité (25%) "),
                "des acteurs d'une manière générale à se rendre physiquement aux marchés. "
                "Elle permet également de vérifier l’accès social et le niveau de sûreté "
                "et de sécurité des routes menant aux marchés.",
                class_="p1"
            ),
            tags.p(
                tags.strong("La disponibilité (30%) "),
                "des produits, elle permet de comprendre si les marchés/vendeurs sont en mesure de "
                "fournir de manière fiable et régulière les articles de base qu’un ménage local moyen "
                "souhaite acheter.",
                class_="p1"
            ),
            tags.p(
                tags.strong("L’abordabilité (15%) "),
                "qui renseigne sur l’accès financier des clients/acheteurs à s’approprier un produit "
                "par rapport à son prix et la stabilité de ce dernier.",
                class_="p1"
            ),
            tags.p(
                tags.strong("La résilience (20%) "),
                "des chaînes d’approvisionnement qui montre la capacité des vendeurs à renouveler "
                "leur stock au niveau des marchés.",
                class_="p1"
            ),
            tags.p(
                tags.strong("L’infrastructure (10%) "),
                "indique l’état physique des bâtiments, routes, etc. au niveau ou dans les environs "
                "des marchés. Elle permet de comprendre le niveau de sécurité des entrepôts dans les "
                "marchés et aussi les différentes modalités de paiement des articles.",
                class_="p1"
            ),
            ui.h5("Méthodologie de classification sur la carte"),
            tags.p(
                "Afin de représenter visuellement les différentes valeurs des dimensions et le score total, "
                "nous avons utilisé les quantiles comme points de coupure pour les diviser en 4 groupes "
                "(vert, orange, rouge clair et rouge).",
                class_="p1"
            ),
        )

        # Classification explanation
        classification_text = ui.TagList(
            ui.h5("Catégorisation du score de fonctionnalité des Marchés (MFS)"),
            tags.p(
                "Sur un score maximum de 100, les marchés sont classés en quatre catégories dépendamment "
                "du cumul de score obtenu pour chaque dimension qui décrit chacun un aspect de leur niveau "
                "de fonctionnalité.",
                class_="p1"
            ),
            tags.p(
                tags.strong("Fonctionnalité complète: "),
                "(1) le score total du MFS est > 80% du score total maximum et (2) aucune dimension "
                "ne tombe en dessous de 50% de son score maximum.",
                class_="p1"
            ),
            tags.p(
                tags.strong("Fonctionnalité limitée: "),
                "(1) le score total du MFS est > 50% du score total maximum ou (2) pas plus d'une dimension "
                "ne tombe en dessous de 50% de son score maximum.",
                class_="p1"
            ),
            tags.p(
                tags.strong("Fonctionnalité pauvre: "),
                "(1) le score total du MFS est < 50% du score total maximum ou (2) au moins deux dimensions "
                "tombent en dessous de 50% de leurs scores maximums.",
                class_="p1"
            ),
            tags.p(
                tags.strong("Problèmes sévères: "),
                "(1) le score total du MFS est < 25% du score total maximum ou (2) au moins trois dimensions "
                "tombent en dessous de 50% de leurs scores maximums.",
                class_="p1"
            )
        )

        # Which text to show depends on the selected indicator
        mfs_indicators = [
            'Accessibilité',
            'Disponibilité',
            'Abordabilité',
            'Résilience',
            'Infrastructure',
            'Score Total'
        ]
        if selected_label in mfs_indicators:
            return mfs_text
        else:
            return classification_text
