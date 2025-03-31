# modules/prix_median.py

import os
import pandas as pd
import logging
from shiny import App, ui, render, reactive
from shiny.ui import tags, modal, modal_show

def load_prix_median_data(DATA_DIR):
    """
    Load and prepare data for the "Prix des Produits" tab panel.
    
    This function now loads all Excel files ending with '_ICSM_analyse.xlsx'
    from DATA_DIR. For each file, it adds a column 'Cycle' (e.g. 'cycle_1') based
    on the file name, then merges them into a single DataFrame.

    Parameters:
    - DATA_DIR (str): The directory where the Excel data files are located.
    
    Returns:
    - df (pd.DataFrame): The original DataFrame with additional columns.
    - df_filtered (pd.DataFrame): The filtered DataFrame for 'Prix median' and 'HTG' currency.
    """
    # Loop through all Excel files ending with '_ICSM_analyse.xlsx'
    excel_files = [f for f in os.listdir(DATA_DIR) if f.endswith('_ICSM_analyse.xlsx')]
    if not excel_files:
        raise FileNotFoundError("No Excel files ending with '_ICSM_analyse.xlsx' found in the specified directory.")
    
    list_dfs = []
    for file in excel_files:
        file_path = os.path.join(DATA_DIR, file)
        try:
            df_temp = pd.read_excel(file_path)
        except Exception as e:
            raise ValueError(f"Error reading the Excel file {file}: {e}")
        # Extract the cycle name from the file name (e.g. 'cycle_1' from 'cycle_1_ICSM_analyse.xlsx')
        cycle_name = file.split('_ICSM_analyse.xlsx')[0]
        df_temp['Cycle'] = cycle_name
        list_dfs.append(df_temp)
    df = pd.concat(list_dfs, ignore_index=True)
    
    # Ensure required columns exist
    required_columns = ['question_variable_label', 'Filtre', 'Sujet', 'Sector']
    for col in required_columns:
        if col not in df.columns:
            raise KeyError(f"Required column '{col}' is missing from the data.")
    
    # Create 'Produit' column
    df['Produit'] = df['question_variable_label']
    
    # Create 'currency' column
    df['currency'] = df['question_variable_label'].apply(
        lambda x: 'USD' if 'usd' in str(x).lower() else 'HTG'
    )
    
    # Define the mapping for 'Filtre' column and adjust 'Disag'
    df['Filtre'] = df['Filtre'].replace({"Toute l'evaluation": 'Tout le pays'}) 
    df['Disag'] = df['Disag'].replace({"Toute l'evaluation": 'Tout le pays'})    
    
    # Filter the DataFrame for 'Prix median'
    df_filtered = df[df['Sujet'] == 'Prix median']
    
    # Further filter for 'HTG' currency
    df_filtered = df_filtered[df_filtered['currency'] == 'HTG']
    
    return df, df_filtered


def get_prix_median_choices(df_filtered):
    """
    Get unique choices for dropdowns in the "Prix des Produits" tab panel.
    
    Now also returns the unique cycles.
    """
    secteur_choices_prix = sorted(df_filtered['Sector'].dropna().unique().tolist())
    region_choices = sorted(df_filtered['Filtre'].dropna().unique().tolist())
    cycle_choices = sorted(df_filtered['Cycle'].dropna().unique().tolist())
    # Assuming cycles are in the format "cycle_X", we extract the numeric parts:
    # (They will be used to define the slider range.)
    return secteur_choices_prix, region_choices, cycle_choices


def create_prix_median_table(df, input):
    """
    Create a pivot table for the "Prix des Produits" tab panel based on user inputs.
    Formats numbers with commas and rearranges columns.

    Parameters:
    - df (pd.DataFrame): The filtered DataFrame (already filtered for 'Sujet' and 'currency').
    - input: Shiny input object.

    Returns:
    - pivot_df (pd.DataFrame): The formatted pivot table.
    """
    # Convert the slider value to the corresponding cycle string.
    current_cycle = f"cycle_{input.cycle_select()}"
    
    # Filter data based on user inputs, including the new Cycle filter
    filtered_df = df[
        (df['Sector'] == input.secteur_select_prix()) &
        (df['Filtre'] == input.region_select()) &
        (df['Cycle'] == current_cycle)
    ]

    # Create pivot table
    pivot_df = filtered_df.pivot_table(
        index='Produit',
        columns='Disag',
        values='Value',
        aggfunc='median'
    ).reset_index()

    # Format numerical values with commas
    numeric_cols = pivot_df.select_dtypes(include=['float', 'int']).columns
    pivot_df[numeric_cols] = pivot_df[numeric_cols].applymap(lambda x: f"{x:,.0f}" if pd.notnull(x) else x)

    # Rearrange columns to move 'Tout le pays' to the last
    if "Tout le pays" in pivot_df.columns:
        cols = list(pivot_df.columns)
        cols.remove("Tout le pays")
        cols.append("Tout le pays")
        pivot_df = pivot_df[cols]

    return pivot_df


def create_prix_difference_table(df, input):
    """
    Create a pivot table of percent differences between consecutive cycles.
    
    For the selected cycle (e.g. cycle_2) the function finds the corresponding previous cycle (cycle_1)
    and computes, for each product and for each 'Disag' level, the percentage difference as:
        ((value_current - value_previous) / value_previous) * 100.
    
    If the selected cycle is the first cycle (i.e. cycle_1) or if data for either cycle is missing,
    an empty DataFrame (or None) is returned.

    Parameters:
    - df (pd.DataFrame): The full DataFrame with data for all cycles.
    - input: Shiny input object.

    Returns:
    - diff_table (pd.DataFrame): Pivot table with percentage differences.
      The column names (other than 'Produit') correspond to the 'Disag' levels.
    """
    secteur = input.secteur_select_prix()
    region = input.region_select()
    # Here input.cycle_select() is now an integer value from the slider.
    try:
        cycle_num = int(input.cycle_select())
    except Exception as e:
        logging.error(f"Error converting cycle selection to integer: {e}")
        return pd.DataFrame()
    
    if cycle_num <= 1:
        # No previous cycle to compare with.
        return None

    current_cycle = f"cycle_{cycle_num}"
    previous_cycle = f"cycle_{cycle_num - 1}"
    
    # Filter for the selected sector, region, and both cycles
    df_current = df[(df['Sector'] == secteur) &
                    (df['Filtre'] == region) &
                    (df['Cycle'] == current_cycle)]
    df_previous = df[(df['Sector'] == secteur) &
                     (df['Filtre'] == region) &
                     (df['Cycle'] == previous_cycle)]
    
    if df_current.empty or df_previous.empty:
        return pd.DataFrame()
    
    # Create pivot tables for current and previous cycles
    pivot_current = df_current.pivot_table(
        index='Produit',
        columns='Disag',
        values='Value',
        aggfunc='median'
    ).reset_index()
    pivot_previous = df_previous.pivot_table(
        index='Produit',
        columns='Disag',
        values='Value',
        aggfunc='median'
    ).reset_index()
    
    # Merge the two pivot tables on 'Produit'
    merged = pd.merge(pivot_current, pivot_previous, on='Produit', how='outer', suffixes=('_curr', '_prev'))
    
    # For each 'Disag' column present in both, compute the percent difference.
    for col in pivot_current.columns:
        if col == 'Produit':
            continue
        curr_col = f"{col}_curr"
        prev_col = f"{col}_prev"
        if curr_col in merged.columns and prev_col in merged.columns:
            merged[f"{col}_diff"] = merged.apply(
                lambda row: ((row[curr_col] - row[prev_col]) / row[prev_col] * 100)
                            if pd.notna(row[curr_col]) and pd.notna(row[prev_col]) and row[prev_col] != 0
                            else None,
                axis=1
            )
    
    # Build the difference table: keep 'Produit' and for each 'Disag' that we could compute, take its _diff column.
    diff_cols = ['Produit']
    for col in pivot_current.columns:
        if col != 'Produit' and f"{col}_diff" in merged.columns:
            diff_cols.append(f"{col}_diff")
    
    diff_table = merged[diff_cols].copy()
    # Rename the difference columns to remove the suffix
    new_columns = {}
    for col in diff_table.columns:
        if col.endswith("_diff"):
            new_columns[col] = col.replace("_diff", "")
        else:
            new_columns[col] = col
    diff_table.rename(columns=new_columns, inplace=True)
    
    return diff_table


def prix_median_ui(cycle_choices, secteur_choices_prix, region_choices):
    """
    Define the UI for the "Prix des Produits" tab.

    Parameters:
    - cycle_choices (list): Choices for the Cycle dropdown.
    - secteur_choices_prix (list): Choices for the sector dropdown.
    - region_choices (list): Choices for the geographic level dropdown.

    Returns:
    - Shiny UI component for the tab.
    """
    # We assume that cycle_choices is a list like ["cycle_1", "cycle_2", ...].
    # The slider will run from 1 to the number of cycles.
    cycle_slider = ui.input_slider(
        "cycle_select",
        "Choisir le Cycle",
        min=1,
        max=len(cycle_choices),
        value=1,
        step=1
    )

    return ui.nav_panel(
        ui.tags.span(
            ui.tags.i(class_="fa fa-money icon"),
            " Prix des Produits",
            class_="nav-panel-title"
        ),
        ui.layout_sidebar(
            ui.sidebar(
                # Use the slider for cycle selection
                ui.div(
                    tags.label(class_="custom-select-label"),
                    cycle_slider,
                    class_="custom-select"
                ),
                ui.div(
                    tags.label("Choisir le Secteur", class_="custom-select-label"),
                    ui.input_select(
                        "secteur_select_prix",
                        None,
                        choices=secteur_choices_prix,
                    ),
                    class_="custom-select"
                ),
                ui.div(
                    tags.label("Choisir le Niveau géographique", class_="custom-select-label"),
                    ui.input_select(
                        "region_select",
                        None,
                        choices=region_choices,
                    ),
                    class_="custom-select"
                ),
            ),
            # Main panel content:
            ui.div(
                # Container to position the switch at the top right
                ui.div(
                    ui.input_switch(
                        id="toggle_diff",
                        label="Évolution des prix (en %)",
                        value=False
                    ),
                    class_="switch-container"
                ),
                ui.HTML(
                    """
                    <p style="font-size: 18px; text-align: justify; font-family: 'Arial Narrow'; 
                            line-height: 1.1; font-weight: 500; color: #58595a;">
                        Cette page vous permet de consulter plus en détail les prix médians des produits.
                    </p>
                    """
                ),
                ui.h2("Prix médian des produits en gourdes haïtiennes (HTG)"),
                ui.output_ui("prix_table")
            )
        ),
    )


def prix_median_server(input, output, session, df):
    """
    Define the server logic for the "Prix des Produits" tab.

    Parameters:
    - input: Shiny input object.
    - output: Shiny output object.
    - session: Shiny session object.
    - df (pd.DataFrame): The filtered DataFrame loaded from data.
    """

    @output
    @render.ui
    def prix_table():
        # Check the switch: if toggled, show the differences table; otherwise, show the price values.
        if input.toggle_diff():
            diff_df = create_prix_difference_table(df, input)
            if diff_df is None:
                # This happens when the selected cycle is the first one
                return ui.HTML("<p>Aucune donnée disponible pour calculer la différence pour le cycle sélectionné.</p>")
            if diff_df.empty:
                logging.warning("Differences table is empty. Check the input selections.")
                return ui.HTML("<p>Aucune donnée disponible pour les sélections actuelles.</p>")
            
            # Build HTML table for differences
            def apply_diff_format(row):
                # Format each row: first column is Produit; other columns are differences.
                styled_row = []
                for col in diff_df.columns:
                    if col == 'Produit':
                        styled_row.append(f"<td><strong>{row[col]}</strong></td>")
                    else:
                        cell_value = row[col]
                        if cell_value is None or pd.isna(cell_value):
                            styled_row.append("<td></td>")
                        else:
                            if cell_value > 0:
                                # Positive difference: show ▲ +x.x% with red color (#CD2030)
                                formatted = f"▲ +{cell_value:.1f}%"
                                styled_row.append(f"<td style='color: #CD2030;'><strong>{formatted}</strong></td>")
                            elif cell_value < 0:
                                # Negative difference: show ▼-x.x% with green color (#086D38)
                                formatted = f"▼{cell_value:.1f}%"
                                styled_row.append(f"<td style='color: #086D38;'><strong>{formatted}</strong></td>")
                            else:
                                # Exactly zero difference => show "="
                                formatted = f"= {cell_value:.1f}%"
                                styled_row.append(f"<td><strong>{formatted}</strong></td>")
                return "<tr>" + "".join(styled_row) + "</tr>"
            
            table_html = "<table class='difference-table'><thead><tr>"
            for col in diff_df.columns:
                table_html += f"<th>{col}</th>"
            table_html += "</tr></thead><tbody>"
            for _, row in diff_df.iterrows():
                table_html += apply_diff_format(row)
            table_html += "</tbody></table>"
            
            return ui.HTML(table_html)
        else:
            try:
                # Create the pivot table for price values
                pivot_df = create_prix_median_table(df, input)
                if pivot_df.empty:
                    logging.warning("Pivot table is empty. Check the input selections.")
                    return ui.HTML("<p>Aucune donnée disponible pour les sélections actuelles.</p>")
            except Exception as e:
                logging.error(f"Error creating pivot table: {e}")
                return ui.HTML("<p>Une erreur s'est produite lors de la création du tableau.</p>")
            
            evaluation_col = "Tout le pays"
            def apply_conditional_colors(row):
                # Exclude the 'Produit' and evaluation column from quantile calculations
                numeric_cols = [col for col in row.index if col not in ['Produit', evaluation_col]]
                try:
                    values = pd.to_numeric(row[numeric_cols].replace(',', '', regex=True), errors='coerce')
                except AttributeError:
                    values = pd.to_numeric(row[numeric_cols], errors='coerce')
                quantiles = values.quantile([0.25, 0.5, 0.75]).to_dict()
                
                styled_row = []
                for col in pivot_df.columns:
                    if col == 'Produit':
                        styled_row.append(f"<td><strong>{row[col]}</strong></td>")
                    elif col == evaluation_col:
                        styled_row.append(f"<td class='highlighted'><strong>{row[col]}</strong></td>")
                    elif col in numeric_cols:
                        cell_value = row[col]
                        if isinstance(cell_value, str):
                            try:
                                val = pd.to_numeric(cell_value.replace(',', ''), errors='coerce')
                            except Exception as e:
                                logging.error(f"Error converting cell value '{cell_value}' in column '{col}': {e}")
                                val = None
                        else:
                            try:
                                val = pd.to_numeric(cell_value, errors='coerce')
                            except Exception as e:
                                logging.error(f"Error converting cell value '{cell_value}' in column '{col}': {e}")
                                val = None
                        if pd.isna(val):
                            styled_row.append(f"<td></td>")
                        else:
                            color = "#FEEEED"
                            if val > quantiles.get(0.75, 0):
                                color = "#EE5859"
                            elif val > quantiles.get(0.5, 0):
                                color = "#F27D7C"
                            elif val > quantiles.get(0.25, 0):
                                color = "#F3BEBD"
                            styled_row.append(f"<td style='background-color: {color};'>{row[col]}</td>")
                    else:
                        styled_row.append(f"<td>{row[col]}</td>")
                return "<tr>" + "".join(styled_row) + "</tr>"
            
            table_html = "<table class='prix-table'><thead><tr>"
            for col in pivot_df.columns:
                if col == evaluation_col:
                    table_html += f"<th class='highlighted-header'>{col}</th>"
                else:
                    table_html += f"<th>{col}</th>"
            table_html += "</tr></thead><tbody>"
            
            for _, row in pivot_df.iterrows():
                table_html += apply_conditional_colors(row)
            
            table_html += "</tbody></table>"
            return ui.HTML(table_html)
