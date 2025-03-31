# modules/indicateurs_non_tarifaires.py

import os
import pandas as pd
import plotly.express as px
import plotly.graph_objs as go
import textwrap
import logging

from shiny import ui, reactive, render
from shinywidgets import render_widget, output_widget

###################################
# 1. LOADING AND PREPROCESSING DATA
###################################

def load_indicateurs_data(DATA_DIR):
    """
    Load and merge all Excel files ending with '_ICSM_analyse.xlsx' from DATA_DIR,
    adding a 'Cycle' column to each dataset. The merged DataFrame is then cleaned
    and transformed for use in the Indicateurs Non-Tarifaires app.
    """
    excel_files = [f for f in os.listdir(DATA_DIR) if f.endswith('_ICSM_analyse.xlsx')]
    if not excel_files:
        raise FileNotFoundError("No Excel files ending with '_ICSM_analyse.xlsx' found in the specified directory.")

    # Merge all Excel files, each annotated with a 'Cycle' column.
    list_dfs = []
    for file in excel_files:
        file_path = os.path.join(DATA_DIR, file)
        try:
            df_temp = pd.read_excel(file_path)
        except Exception as e:
            raise ValueError(f"Error reading the Excel file {file}: {e}")

        # Extract the cycle name from the file name, e.g. "cycle_1_ICSM_analyse.xlsx" => "cycle_1"
        cycle_name = file.split('_ICSM_analyse.xlsx')[0]
        df_temp['Cycle'] = cycle_name
        list_dfs.append(df_temp)

    df = pd.concat(list_dfs, ignore_index=True)

    # Basic cleanup (columns that you rely on must exist in each file)
    required_cols = ['question_type', 'question_variable_name', 'answer_variable_label',
                     'Indicator description', 'Filtre', 'Disag', 'Sector', 'Sujet', 'Value']
    for col in required_cols:
        if col not in df.columns:
            raise KeyError(f"Required column '{col}' is missing from the data.")

    # Recode certain question types
    df['question_type'] = df['question_type'].replace({
        'recoded_variable_categorical': 'select_one',
        'recoded_variable_numeric': 'integer'
    })

    # Example label truncation
    long_phrase = 'De nombreux clients ne peuvent pas payer leurs articles d’une manière que vous pouvez accepter'
    df['answer_variable_label'] = df['answer_variable_label'].apply(
        lambda x: long_phrase if str(x).startswith(long_phrase) else x
    )

    # Replace "Toute l'evaluation" with "Tout le pays" in 'Filtre' and 'Disag'
    df['Filtre'] = df['Filtre'].replace({"Toute l'evaluation": 'Tout le pays'})
    df['Disag'] = df['Disag'].replace({"Toute l'evaluation": 'Tout le pays'})

    # Replace 'Indicateurs transversaux' with 'TOUS LES ARTICLES'
    df['Sector'].replace({'Indicateurs transversaux': 'TOUS LES ARTICLES'}, inplace=True)

    # Extract product name from variable
    def extract_product_name(var_name):
        indicator_suffixes = [
            '_availability_market_item',
            '_supplier_unique_item',
            '_imported_item',
            '_supplier_origin_country_item',
        ]
        for suffix in indicator_suffixes:
            if isinstance(var_name, str) and var_name.endswith(suffix):
                return var_name.replace(suffix, '')
        return None

    df['Produit'] = df['question_variable_name'].apply(extract_product_name)

    # Map codes to product names
    product_mapping = {
        'kitchen_knife': 'Couteau de cuisine',
        'cooking_pot_with_lid': 'Casserole avec couvercle',
        'fork': 'Fourchette',
        'cooking_pot': 'Casserole',
        'nails_50mm': 'Clous 50mm',
        'spoon': 'Cuillère',
        'knife': 'Couteau',
        'bowl': 'Bol',
        'nails_75mm': 'Clous 75mm',
        'pan': 'Poêle',
        'toothpaste': 'Dentifrice',
        'sanitary_pad': 'Serviette hygiénique',
        'nails_63mm': 'Clous 63mm',
        'torch': 'Torche',
        'hammer': 'Marteau',
        'mug': 'Mug',
        'plate': 'Assiette',
        'baby_oil': 'Huile pour bébé',
        'roll_tie_wire': 'Fil de fer',
        'baby_soap': 'Savon pour bébé',
        'toothbrush_adult': 'Brosse à dents adulte',
        'cooking_fuel': 'Combustible de cuisson',
        'shampoo': 'Shampooing',
        'scouring_pad': 'Tampon à récurer',
        'shovel': 'Pelle',
        'soap': 'Savon',
        'sim_card': 'Carte SIM',
        'blanket': 'Couverture',
        'towel_children': 'Serviette pour enfants',
        'diaper': 'Couche',
        'deodorant': 'Déodorant',
        'hoe': 'Houe',
        'laundry_soap_bar': 'Savon lessive',
        'pickaxe': 'Pioche',
        'toilet_paper': 'Papier toilette',
        'serving_spoon': 'Cuillère de service',
        'water_container_small': "Petit récipient d'eau",
        'mosquito_net': 'Moustiquaire',
        'water_container': "Récipient d'eau",
        'tub': 'Baignoire',
        'sleeping_mat': 'Tapis de couchage',
        'mobile_phone': 'Téléphone mobile',
        'pair_of_shears': 'Paire de cisailles',
        'stove': 'Cuisinière',
        'water_bottle': "Bouteille d'eau",
        'carpet': 'Tapis',
        'charcoal': 'Charbon de bois',
        'rope': 'Corde',
        'draw_hoe': 'Houe à tirer',
        'bucket_with_tap': 'Seau avec robinet',
    }
    df['Produit'] = df['Produit'].map(product_mapping).fillna(df['Produit'])

    return df


def get_cycle_choices(df):
    """
    Return a sorted list of the unique cycles found in df['Cycle'].
    """
    cycles = sorted(df['Cycle'].dropna().unique().tolist())
    return cycles

###################################
# 2. UI DEFINITION
###################################

def indicateurs_ui(cycle_choices):
    # Derive numeric cycles from e.g. "cycle_1" -> [1]
    numeric_cycles = []
    for cyc in cycle_choices:
        try:
            numeric = int(cyc.replace("cycle_", ""))
            numeric_cycles.append(numeric)
        except:
            pass
    if not numeric_cycles:
        numeric_cycles = [1]  # fallback

    # Create three separate sliders, each with a unique ID
    cycle_slider_stock = ui.input_slider(
        "cycle_select_ind_stock",
        "Choisir le Cycle",
        min=min(numeric_cycles),
        max=max(numeric_cycles),
        value=min(numeric_cycles),
        step=1
    )
    cycle_slider_disp = ui.input_slider(
        "cycle_select_ind_disp",
        "Choisir le Cycle",
        min=min(numeric_cycles),
        max=max(numeric_cycles),
        value=min(numeric_cycles),
        step=1
    )
    cycle_slider_fonc = ui.input_slider(
        "cycle_select_ind_func",
        "Choisir le Cycle",
        min=min(numeric_cycles),
        max=max(numeric_cycles),
        value=min(numeric_cycles),
        step=1
    )

    return ui.nav_menu(
        ui.tags.span(
            ui.tags.i(class_="fa fa-bar-chart icon"),  
            " Indicateurs non tarifaires",
            class_="nav-panel-title"
        ),

        #=== 1) STOCK ET RÉAPPROVISIONNEMENT ===
        ui.nav_panel("Stock et réapprovisionnement",
            ui.layout_sidebar(
                ui.sidebar(
                    # 1) Slider for STOCK
                    ui.div(
                        cycle_slider_stock,
                        class_="custom-select"
                    ),
                    ui.div(
                        ui.tags.label("Choisir le Secteur", class_="custom-select-label"),
                        ui.input_select("sector_stock", None, choices=[], selected=None),
                        class_="custom-select"
                    ),
                    ui.div(
                        ui.tags.label("Choisir l'indicateur", class_="custom-select-label"),
                        ui.input_select("indicator_stock", None, choices=[], selected=None),
                        class_="custom-select"
                    ),
                    ui.div(
                        ui.tags.label("Choisir le niveau géographique", class_="custom-select-label"),
                        ui.input_select("niveau_stock", None, choices=[], selected=None),
                        class_="custom-select"
                    ),
                    ui.panel_conditional(
                        "output.qtype_stock_out == 'select_multiple'",
                        ui.div(
                            ui.tags.label("Choisir l'unité géographique", class_="custom-select-label"),
                            ui.input_select("niveau_stock_II", None, choices=[], selected=None),
                            class_="custom-select"
                        )
                    ),
                ),
                ui.div(
                    ui.HTML("<p>Cette page vous permet d’afficher et analyser les données sur la "
                            "disponibilité des stocks, les difficultés de réapprovisionnement et "
                            "les raisons potentielles des ruptures.</p>"),
                    output_widget("plot_stock"),
                    ui.HTML("<hr><p><strong>Type de question :</strong></p>"),
                    ui.output_text("qtype_stock_out"),
                    style="width:100%; height:auto; overflow:auto; padding:20px;"
                )
            )
        ),

        #=== 2) DISPONIBILITÉ ET ORIGINE DE PRODUITS ===
        ui.nav_panel("Disponibilité et origine de produits",
            ui.layout_sidebar(
                ui.sidebar(
                    # 2) Slider for DISPONIBILITÉ
                    ui.div(
                        cycle_slider_disp,
                        class_="custom-select"
                    ),
                    ui.div(
                        ui.tags.label("Choisir le Secteur", class_="custom-select-label"),
                        ui.input_select("sector_dispo", None, choices=[], selected=None),
                        class_="custom-select"
                    ),
                    ui.div(
                        ui.tags.label("Choisir le Produit", class_="custom-select-label"),
                        ui.input_select("produit_dispo", None, choices=[], selected=None),
                        class_="custom-select"
                    ),
                    ui.div(
                        ui.tags.label("Choisir l'indicateur", class_="custom-select-label"),
                        ui.input_select("indicator_dispo", None, choices=[], selected=None),
                        class_="custom-select"
                    ),
                    ui.div(
                        ui.tags.label("Choisir le niveau géographique", class_="custom-select-label"),
                        ui.input_select("niveau_dispo", None, choices=[], selected=None),
                        class_="custom-select"
                    ),
                    ui.panel_conditional(
                        "output.qtype_dispo_out == 'select_multiple'",
                        ui.div(
                            ui.tags.label("Choisir l'unité géographique", class_="custom-select-label"),
                            ui.input_select("niveau_dispo_II", None, choices=[], selected=None),
                            class_="custom-select"
                        )
                    ),
                ),
                ui.div(
                    ui.HTML("<p>Cette page vous permet d’observer l’origine des produits (importés ou locaux) "
                            "et leur disponibilité sur les marchés. Cela permet d’évaluer la résilience "
                            "des chaînes d’approvisionnement.</p>"),
                    output_widget("plot_dispo"),
                    ui.HTML("<hr><p><strong>Type de question :</strong></p>"),
                    ui.output_text("qtype_dispo_out"),
                    style="width:100%; height:auto; overflow:auto; padding:20px;"
                )
            )
        ),

        #=== 3) FONCTIONNALITÉ DES MARCHÉS ===
        ui.nav_panel("Fonctionnalité des marchés",
            ui.layout_sidebar(
                ui.sidebar(
                    # 3) Slider for FONCTIONNALITÉ
                    ui.div(
                        cycle_slider_fonc,
                        class_="custom-select"
                    ),
                    ui.div(
                        ui.tags.label("Choisir l'indicateur", class_="custom-select-label"),
                        ui.input_select("indicator_fonc", None, choices=[], selected=None),
                        class_="custom-select"
                    ),
                    ui.div(
                        ui.tags.label("Choisir le niveau géographique", class_="custom-select-label"),
                        ui.input_select("niveau_fonc", None, choices=[], selected=None),
                        class_="custom-select"
                    ),
                    ui.panel_conditional(
                        "output.qtype_fonc_out == 'select_multiple'",
                        ui.div(
                            ui.tags.label("Choisir l'unité géographique", class_="custom-select-label"),
                            ui.input_select("niveau_fonc_II", None, choices=[], selected=None),
                            class_="custom-select"
                        )
                    ),
                ),
                ui.div(
                    ui.HTML("<p>Cette page vous permet d’explorer des indicateurs illustrant la facilité ou la "
                            "difficulté d’accès aux marchés, leur fonctionnement global, et tout autre "
                            "facteur influençant leur performance.</p>"),
                    output_widget("plot_fonc"),
                    ui.HTML("<hr><p><strong>Type de question :</strong></p>"),
                    ui.output_text("qtype_fonc_out"),
                    style="width:100%; height:auto; overflow:auto; padding:20px;"
                )
            )
        )
    )

###################################
# 3. SERVER LOGIC
###################################

def indicateurs_server(input, output, session, df):

    @reactive.Calc
    def selected_cycle():
        """
        Convert the numeric slider value into a string like "cycle_1".
        """
        cycle_num = input.cycle_select_indic()
        return f"cycle_{cycle_num}"

    # Filtered subsets by topic + cycle
    @reactive.Calc
    def data_stock():
        return df[(df['Sujet'] == 'Stock et réapprovisionnement') &
                  (df['Cycle'] == selected_cycle())]

    @reactive.Calc
    def data_dispo():
        return df[(df['Sujet'] == 'Disponibilité et origine de produits') &
                  (df['Cycle'] == selected_cycle())]

    @reactive.Calc
    def data_fonc():
        return df[(df['Sujet'] == 'Fonctionalité des Marchés') &
                  (df['Cycle'] == selected_cycle())]

    # Determine question types
    @reactive.Calc
    def question_type_stock():
        indicator = input.indicator_stock()
        data_ = data_stock()
        if indicator:
            data_ = data_[data_['Indicator description'] == indicator]
            if not data_.empty:
                qtype = data_['question_type'].iloc[0]
                if qtype in ['select_one', 'select_multiple', 'integer']:
                    return qtype
        return None

    @reactive.Calc
    def question_type_dispo():
        indicator = input.indicator_dispo()
        data_ = data_dispo()
        if indicator:
            data_ = data_[data_['Indicator description'] == indicator]
            if not data_.empty:
                qtype = data_['question_type'].iloc[0]
                if qtype in ['select_one', 'select_multiple', 'integer']:
                    return qtype
        return None

    @reactive.Calc
    def question_type_fonc():
        indicator = input.indicator_fonc()
        data_ = data_fonc()
        if indicator:
            data_ = data_[data_['Indicator description'] == indicator]
            if not data_.empty:
                qtype = data_['question_type'].iloc[0]
                if qtype in ['select_one', 'select_multiple', 'integer']:
                    return qtype
        return None

    ###################################
    # 3a. UPDATE FILTERS DYNAMICALLY
    ###################################

    #=== REACTIVE CALCS FOR EACH SLIDER ===
    @reactive.Calc
    def selected_cycle_stock():
        """Convert the numeric slider value from the stock panel into 'cycle_X'."""
        cycle_num = input.cycle_select_ind_stock()  # from the STOCK slider
        return f"cycle_{cycle_num}"

    @reactive.Calc
    def selected_cycle_disp():
        """Convert the numeric slider value from the disponibilité panel into 'cycle_X'."""
        cycle_num = input.cycle_select_ind_disp()   # from the DISP slider
        return f"cycle_{cycle_num}"

    @reactive.Calc
    def selected_cycle_fonc():
        """Convert the numeric slider value from the fonctionnalité panel into 'cycle_X'."""
        cycle_num = input.cycle_select_ind_func()   # from the FUNC slider
        return f"cycle_{cycle_num}"

    #=== FILTER DATA FOR EACH TOPIC & CYCLE ===
    @reactive.Calc
    def data_stock():
        return df[
            (df['Sujet'] == 'Stock et réapprovisionnement') &
            (df['Cycle'] == selected_cycle_stock())
        ]

    @reactive.Calc
    def data_dispo():
        return df[
            (df['Sujet'] == 'Disponibilité et origine de produits') &
            (df['Cycle'] == selected_cycle_disp())
        ]

    @reactive.Calc
    def data_fonc():
        return df[
            (df['Sujet'] == 'Fonctionalité des Marchés') &
            (df['Cycle'] == selected_cycle_fonc())
        ]

    # ----------- STOCK -----------
    @reactive.Effect
    def update_stock_filters():
        data_ = data_stock()
        sectors = data_['Sector'].dropna().unique().tolist()
        sectors.sort()
        ui.update_select("sector_stock", choices=sectors)

        niveau = data_['Filtre'].dropna().unique().tolist()
        niveau.sort()
        ui.update_select("niveau_stock", choices=niveau)

    @reactive.Effect
    def update_indicator_stock():
        sector = input.sector_stock()
        data_ = data_stock()
        if sector:
            data_ = data_[data_['Sector'] == sector]
            indicators = data_['Indicator description'].dropna().unique().tolist()
            indicators.sort()
            ui.update_select("indicator_stock", choices=indicators)
        else:
            ui.update_select("indicator_stock", choices=[])

    @reactive.Effect
    def update_niveau_stock_II():
        qtype = question_type_stock()
        data_ = data_stock()
        sector = input.sector_stock()
        indicator = input.indicator_stock()
        niveau = input.niveau_stock()

        if sector:
            data_ = data_[data_['Sector'] == sector]
        if indicator:
            data_ = data_[data_['Indicator description'] == indicator]
        if niveau:
            data_ = data_[data_['Filtre'] == niveau]

        if qtype == 'select_multiple':
            niveau_II = data_['Disag'].dropna().unique().tolist()
            niveau_II.sort()
            ui.update_select("niveau_stock_II", choices=niveau_II)
        else:
            ui.update_select("niveau_stock_II", choices=[])

    # ----------- DISPO -----------
    @reactive.Effect
    def update_dispo_filters():
        data_ = data_dispo()
        sectors = data_['Sector'].dropna().unique().tolist()
        sectors.sort()
        ui.update_select("sector_dispo", choices=sectors)

        niveau = data_['Filtre'].dropna().unique().tolist()
        niveau.sort()
        ui.update_select("niveau_dispo", choices=niveau)

    @reactive.Effect
    def update_produit_dispo():
        data_ = data_dispo()
        sector = input.sector_dispo()
        if sector and sector != 'TOUS LES ARTICLES':
            data_ = data_[data_['Sector'] == sector]
            produits = data_['Produit'].dropna().unique().tolist()
            produits.sort()
            ui.update_select("produit_dispo", choices=produits)
        else:
            ui.update_select("produit_dispo", choices=[])

    @reactive.Effect
    def update_indicator_dispo():
        sector = input.sector_dispo()
        produit = input.produit_dispo()
        data_ = data_dispo()
        if sector:
            data_ = data_[data_['Sector'] == sector]
        if produit and sector != 'TOUS LES ARTICLES':
            data_ = data_[data_['Produit'] == produit]
        indicators = data_['Indicator description'].dropna().unique().tolist()
        indicators.sort()
        ui.update_select("indicator_dispo", choices=indicators)
        if not indicators:
            ui.update_select("indicator_dispo", choices=[])

    @reactive.Effect
    def update_niveau_dispo_II():
        qtype = question_type_dispo()
        data_ = data_dispo()
        sector = input.sector_dispo()
        produit = input.produit_dispo()
        indicator = input.indicator_dispo()
        niveau = input.niveau_dispo()
        if sector:
            data_ = data_[data_['Sector'] == sector]
        if produit and sector != 'TOUS LES ARTICLES':
            data_ = data_[data_['Produit'] == produit]
        if indicator:
            data_ = data_[data_['Indicator description'] == indicator]
        if niveau:
            data_ = data_[data_['Filtre'] == niveau]

        if qtype == 'select_multiple':
            niveau_II = data_['Disag'].dropna().unique().tolist()
            niveau_II.sort()
            ui.update_select("niveau_dispo_II", choices=niveau_II)
        else:
            ui.update_select("niveau_dispo_II", choices=[])

    # ----------- FONC -----------
    @reactive.Effect
    def update_fonc_filters():
        data_ = data_fonc()
        indicators = data_['Indicator description'].dropna().unique().tolist()
        indicators.sort()
        ui.update_select("indicator_fonc", choices=indicators)

        niveau = data_['Filtre'].dropna().unique().tolist()
        niveau.sort()
        ui.update_select("niveau_fonc", choices=niveau)

    @reactive.Effect
    def update_niveau_fonc_II():
        qtype = question_type_fonc()
        data_ = data_fonc()
        indicator = input.indicator_fonc()
        niveau = input.niveau_fonc()

        if indicator:
            data_ = data_[data_['Indicator description'] == indicator]
        if niveau:
            data_ = data_[data_['Filtre'] == niveau]

        if qtype == 'select_multiple':
            niveau_II = data_['Disag'].dropna().unique().tolist()
            niveau_II.sort()
            ui.update_select("niveau_fonc_II", choices=niveau_II)
        else:
            ui.update_select("niveau_fonc_II", choices=[])

    ###################################
    # 3b. OUTPUTS
    ###################################

    # Display question type
    @output
    @render.text
    def qtype_stock_out():
        qtype = question_type_stock()
        return qtype if qtype else ""

    @output
    @render.text
    def qtype_dispo_out():
        qtype = question_type_dispo()
        return qtype if qtype else ""

    @output
    @render.text
    def qtype_fonc_out():
        qtype = question_type_fonc()
        return qtype if qtype else ""

    # PLOTS
    @output
    @render_widget
    def plot_stock():
        sector = input.sector_stock()
        indicator = input.indicator_stock()
        niveau = input.niveau_stock()
        niveau_II = input.niveau_stock_II()
        data_ = data_stock()

        if sector:
            data_ = data_[data_['Sector'] == sector]
        if indicator:
            data_ = data_[data_['Indicator description'] == indicator]
        if niveau:
            data_ = data_[data_['Filtre'] == niveau]

        question_type = question_type_stock()
        if question_type == 'select_multiple' and niveau_II:
            data_ = data_[data_['Disag'] == niveau_II]

        if data_.empty:
            return go.Figure()

        return create_plot(data_, question_type)

    @output
    @render_widget
    def plot_dispo():
        sector = input.sector_dispo()
        produit = input.produit_dispo()
        indicator = input.indicator_dispo()
        niveau = input.niveau_dispo()
        niveau_II = input.niveau_dispo_II()
        data_ = data_dispo()

        if sector:
            data_ = data_[data_['Sector'] == sector]
        if produit and sector != 'TOUS LES ARTICLES':
            data_ = data_[data_['Produit'] == produit]
        if indicator:
            data_ = data_[data_['Indicator description'] == indicator]
        if niveau:
            data_ = data_[data_['Filtre'] == niveau]

        question_type = question_type_dispo()
        if question_type == 'select_multiple' and niveau_II:
            data_ = data_[data_['Disag'] == niveau_II]

        if data_.empty:
            return go.Figure()

        return create_plot(data_, question_type)

    @output
    @render_widget
    def plot_fonc():
        indicator = input.indicator_fonc()
        niveau = input.niveau_fonc()
        niveau_II = input.niveau_fonc_II()
        data_ = data_fonc()

        if indicator:
            data_ = data_[data_['Indicator description'] == indicator]
        if niveau:
            data_ = data_[data_['Filtre'] == niveau]

        question_type = question_type_fonc()
        if question_type == 'select_multiple' and niveau_II:
            data_ = data_[data_['Disag'] == niveau_II]

        if data_.empty:
            return go.Figure()

        return create_plot(data_, question_type)

    ###################################
    # 3c. HELPER: CREATE PLOT
    ###################################
    def create_plot(data_, question_type):
        # Color palettes
        grey = '#BDBDBD'
        color_1 = '#F3BEBD'
        color_2 = '#F27D7C'
        color_3 = '#EE5859'
        color_4 = '#C0474A'
        color_5 = '#792a2e'

        title_text = data_['question_variable_label'].iloc[0]
        if len(title_text) > 100:
            title_text = '<br>'.join(textwrap.wrap(title_text, width=100))

        # Plotly layout config
        layout_config = dict(
            autosize=True,
            margin=dict(l=50, r=200, t=100, b=50),
            title=dict(x=0.4, xanchor='center'),
            font=dict(family="Arial Narrow", color="#58585A")
        )

        title_color = "#EE5859"
        font_family_title = "Arial Narrow"

        if question_type == 'select_one':
            # Group by Filtre or Disag
            if 'Disag' in data_.columns and not data_['Disag'].isnull().all():
                y_axis = 'Disag'
                y_label = 'Unité Géographique'
            else:
                y_axis = 'Filtre'
                y_label = 'Niveau Géographique'

            plot_data = data_.groupby([y_axis, 'answer_variable_label'])['Value'].sum().reset_index()
            categories = plot_data[y_axis].unique().tolist()
            # Move "Tout le pays" last, if it exists
            if "Tout le pays" in categories:
                categories.remove("Tout le pays")
                categories.append("Tout le pays")

            distinct_answers = plot_data['answer_variable_label'].unique().tolist()
            # Identify "ne sait pas" answers
            ne_sait_pas_answers = [
                ans for ans in distinct_answers
                if 'ne sait pas' in ans.lower()
                   or 'ne pas répondre' in ans.lower()
                   or 'ne sais pas' in ans.lower()
            ]
            n_answers = len(distinct_answers)

            # Basic cycle of 5 colors
            colors_cycle = [color_1, color_2, color_3, color_4, color_5]
            answer_to_color = {}

            # Assign grey to "ne sait pas" first
            for ans in ne_sait_pas_answers:
                answer_to_color[ans] = grey

            # Filter out "ne sait pas" from main list
            remaining_answers = [ans for ans in distinct_answers if ans not in ne_sait_pas_answers]

            # Assign colors for the rest
            if n_answers <= 5:
                for i, ans in enumerate(remaining_answers):
                    answer_to_color[ans] = colors_cycle[i]
            else:
                for i, ans in enumerate(remaining_answers):
                    answer_to_color[ans] = colors_cycle[i % len(colors_cycle)]

            fig = px.bar(
                plot_data,
                x='Value',
                y=y_axis,
                color='answer_variable_label',
                orientation='h',
                text='Value',
                labels={'Value': 'Pourcentage', y_axis: y_label, 'answer_variable_label': 'Réponses'},
                title=title_text,
                category_orders={y_axis: categories},
                color_discrete_map=answer_to_color
            )
            fig.update_layout(**layout_config)
            fig.update_layout(title_font_color=title_color, title_font_family=font_family_title)
            fig.update_layout(legend=dict(orientation='v', yanchor='top', y=1, xanchor='left', x=1.02))
            fig.update_xaxes(range=[0, 100])
            fig.update_traces(texttemplate='%{text:.1f}%')

            # If only one category, make the bar narrower
            if len(categories) == 1:
                for trace in fig.data:
                    trace.width = 0.2

            return fig

        elif question_type == 'select_multiple':
            plot_data = data_.groupby('answer_variable_label')['Value'].sum().reset_index()
            plot_data = plot_data.sort_values(by='Value', ascending=False)

            fig = px.bar(
                plot_data,
                x='Value',
                y='answer_variable_label',
                orientation='h',
                labels={'Value': 'Pourcentage', 'answer_variable_label': 'Réponses'},
                title=title_text,
                color_discrete_sequence=[color_2]
            )
            fig.update_layout(**layout_config)
            fig.update_layout(title_font_color=title_color, title_font_family=font_family_title)
            fig.update_layout(legend=dict(orientation='v', yanchor='top', y=1, xanchor='left', x=1.02))
            fig.update_yaxes(autorange='reversed')
            fig.update_traces(texttemplate='%{x:.1f}%')
            return fig

        elif question_type == 'integer':
            if 'Disag' in data_.columns and not data_['Disag'].isnull().all():
                y_axis = 'Disag'
                y_label = 'Unité Géographique'
            else:
                y_axis = 'Filtre'
                y_label = 'Niveau Géographique'

            plot_data = data_.groupby(y_axis)['Value'].mean().reset_index()
            categories = plot_data[y_axis].unique().tolist()
            if "Tout le pays" in categories:
                categories.remove("Tout le pays")
                categories.append("Tout le pays")

            fig = px.bar(
                plot_data,
                x='Value',
                y=y_axis,
                orientation='h',
                labels={'Value': 'Jours', y_axis: y_label},
                title=title_text,
                category_orders={y_axis: categories},
                color_discrete_sequence=[color_2]
            )
            fig.update_layout(**layout_config)
            fig.update_layout(title_font_color=title_color, title_font_family=font_family_title)
            fig.update_layout(legend=dict(orientation='v', yanchor='top', y=1, xanchor='left', x=1.02))
            fig.update_traces(texttemplate='%{x:.0f}')
            return fig

        else:
            return go.Figure()
