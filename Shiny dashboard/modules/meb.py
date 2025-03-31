import pandas as pd
import os
import pandas as pd
#from shiny import render, reactive, ui
from shiny import App, ui, render, reactive
from shiny.ui import tags, modal, modal_show

def load_meb_data(DATA_DIR):
    """
    Load and prepare data for the "MEB" tab panel.
    """
    # Loop through all Excel files ending with '_MEB_analyse.xlsx'
    excel_files = [f for f in os.listdir(DATA_DIR) if f.endswith('_MEB_analyse.xlsx')]
    if not excel_files:
        raise FileNotFoundError("No Excel files ending with '_MEB_analyse.xlsx' found in the specified directory.")
    
    list_dfs = []
    for file in excel_files:
        file_path = os.path.join(DATA_DIR, file)
        try:
            df_temp = pd.read_excel(file_path)
        except Exception as e:
            raise ValueError(f"Error reading the Excel file {file}: {e}")
        # Extract the cycle name from the file name (e.g. 'cycle_1' from 'cycle_1_MEB_analyse.xlsx')
        cycle_name = file.split('_MEB_analyse.xlsx')[0]
        df_temp['Cycle'] = cycle_name
        list_dfs.append(df_temp)
    df_meb = pd.concat(list_dfs, ignore_index=True)

    # Drop rows where 'meb_par' is NaN
    df_meb.dropna(subset=['meb_par'], inplace=True)

    # Identify MEB columns that are numerical
    meb_columns = [col for col in df_meb.columns if col.startswith('MEB_') and pd.api.types.is_numeric_dtype(df_meb[col])]

    # Filter rows where 'Type_meb' is 'Urgence' and 'meb_par' is 'Marché'
    mask = (df_meb['Type_meb'] == 'Urgence') & (df_meb['meb_par'] == 'Marché')
    df_urgent_marche = df_meb[mask].copy()

    # Check if there are any rows to process
    if not df_urgent_marche.empty:
        # Convert MEB columns from HTG to USD by dividing by 'USD_official'
        df_urgent_usd = df_urgent_marche.copy()
        df_urgent_usd['currency'] = 'USD'
        df_urgent_usd[meb_columns] = df_urgent_usd[meb_columns].div(df_urgent_usd['USD_official'], axis=0)

        # Append the new USD rows to the original DataFrame
        df_meb = pd.concat([df_meb, df_urgent_usd], ignore_index=True)

    df_meb.reset_index(drop=True, inplace=True)

    # Strip whitespace from text columns
    df_meb['Type_meb'] = df_meb['Type_meb'].str.strip()
    df_meb['meb_par'] = df_meb['meb_par'].str.strip()
    df_meb['currency'] = df_meb['currency'].str.strip()
    df_meb['zone'] = df_meb['zone'].str.strip()

    # Change 'pays' to 'Tout le pays' in 'zone' column
    df_meb['zone'] = df_meb['zone'].replace({'pays': 'Tout le pays'})
    df_meb['Type_meb'] = df_meb['Type_meb'].replace({
        "Crise prolongée": "MEB crise prolongée",
        "Urgence": "MEB crise d'urgence"
    })

    # Identify MEB_ columns
    meb_columns = [col for col in df_meb.columns if col.startswith('MEB_')]

    # Create mapping of 'MEB_' columns to sectors
    sector_mapping = {
        # ABNA
        'MEB_cooking_pot': 'ABNA',
        'MEB_bowl': 'ABNA',
        'MEB_mug': 'ABNA',
        'MEB_spoon': 'ABNA',
        'MEB_serving_spoon': 'ABNA',
        'MEB_knife': 'ABNA',
        'MEB_scouring_pad': 'ABNA',
        'MEB_blanket': 'ABNA',
        'MEB_carpet_price_item': 'ABNA',
        'MEB_charcoal': 'ABNA',
        'MEB_stove': 'ABNA',
        'MEB_pan': 'ABNA',
        'MEB_cooking_pot_with_lid': 'ABNA',
        'MEB_plate': 'ABNA',
        'MEB_fork': 'ABNA',
        'MEB_kitchen_knife': 'ABNA',
        'MEB_sleeping_mat': 'ABNA',
        'MEB_cooking_fuel': 'ABNA',
        'MEB_abna_basket': 'ABNA',
        # WASH
        'MEB_tub': 'WASH',
        'MEB_water_bottle': 'WASH',
        'MEB_laundry_soap_bar': 'WASH',
        'MEB_toothbrush_adult': 'WASH',
        'MEB_toothpaste': 'WASH',
        'MEB_toilet_paper': 'WASH',
        'MEB_sanitary_pad': 'WASH',
        'MEB_soap': 'WASH',
        'MEB_water_container_small': 'WASH',
        'MEB_water_container': 'WASH',
        'MEB_deodorant': 'WASH',
        'MEB_WASH_basket': 'WASH',
        # ABNA Shelter
        'MEB_rope': 'ABNA Shelter',
        'MEB_nails_50mm': 'ABNA Shelter',
        'MEB_nails_75mm': 'ABNA Shelter',
        'MEB_nails_63mm': 'ABNA Shelter',
        'MEB_roll_tie_wire': 'ABNA Shelter',
        'MEB_hammer': 'ABNA Shelter',
        'MEB_shovel': 'ABNA Shelter',
        'MEB_pair_of_shears': 'ABNA Shelter',
        'MEB_hoe': 'ABNA Shelter',
        'MEB_pickaxe': 'ABNA Shelter',
        'MEB_ABNA_shelter_basket': 'ABNA Shelter',
        # Protection
        'MEB_torch': 'Protection',
        'MEB_sim_card': 'Protection',
        'MEB_mobile_phone': 'Protection',
        'MEB_carte_telephone': 'Protection',
        'MEB_Protection_basket': 'Protection',
        # Santé
        'MEB_mosquito_net': 'Santé',
        'MEB_depanse_median_sante': 'Santé',
        'MEB_sante_basket': 'Santé',
        # Education
        'MEB_depanse_median_education': 'Education',
        'MEB_Education_basket': 'Education',
        # TOTAL
        'MEB_total': 'Total',
    }

    # Melt the DataFrame to long format
    df_meb_long = df_meb.melt(
        id_vars=['currency', 'zone', 'Type_meb', 'meb_par', 'Cycle'],
        value_vars=meb_columns,
        var_name='Product',
        value_name='Value'
    )

    # Map 'Product' to 'sector'
    df_meb_long['sector'] = df_meb_long['Product'].map(sector_mapping)

    # Convert 'Value' to numeric
    df_meb_long['Value'] = pd.to_numeric(df_meb_long['Value'], errors='coerce')

    # Normalize 'sector' column
    df_meb_long['sector'] = df_meb_long['sector'].str.strip()

    # Identify basket products
    basket_products = [product for product in sector_mapping if 'basket' in product.lower()]
    # Include 'MEB_total' as a basket product
    basket_products.append('MEB_total')

    df_meb_long['is_basket'] = df_meb_long['Product'].isin(basket_products)
    df_meb_long['is_total'] = df_meb_long['Product'] == 'MEB_total'

    return df_meb_long


def get_meb_choices(df_meb_long):
    """
    Get unique choices for the select inputs based on the MEB DataFrame
    """
    type_meb_choices = sorted(df_meb_long['Type_meb'].dropna().unique().tolist())
    meb_par_choices = sorted(df_meb_long['meb_par'].dropna().unique().tolist())
    sector_choices_meb = sorted(df_meb_long['sector'].dropna().unique().tolist())
    currency_choices_meb = sorted(df_meb_long['currency'].dropna().unique().tolist())
    cycle_choices = sorted(df_meb_long['Cycle'].dropna().unique().tolist())
    return type_meb_choices, meb_par_choices, sector_choices_meb, currency_choices_meb, cycle_choices


def create_meb_secteurs_table(df_meb_long, input):
    """
    Create the pivot table for the "Secteurs" tab (normal table), including the 'Total' row.
    IMPORTANT: now we filter on the selected cycle to show the correct data.
    """
    # Normalize inputs
    type_meb_selected = input.type_meb_select_sectors().strip()
    meb_par_selected = input.meb_par_select().strip()
    currency_selected = input.currency_select_meb().strip()

    # Read cycle from the slider and build the cycle string (e.g. "cycle_1", "cycle_2")
    try:
        cycle_num = int(input.cycle_select_meb())
    except ValueError:
        cycle_num = 1
    cycle_selected = f"cycle_{cycle_num}"

    # Filter data to include basket indicators AND the currently selected cycle
    filtered_df = df_meb_long[
        (df_meb_long['Cycle'] == cycle_selected) &
        (df_meb_long['Type_meb'] == type_meb_selected) &
        (df_meb_long['meb_par'] == meb_par_selected) &
        (df_meb_long['currency'] == currency_selected) &
        (df_meb_long['is_basket'])
    ]

    # Pivot table
    pivot_df = filtered_df.pivot_table(
        index='sector',
        columns='zone',
        values='Value',
        aggfunc='mean'
    ).reset_index()

    # Remove decimals from the values
    pivot_df.iloc[:, 1:] = pivot_df.iloc[:, 1:].round(0).astype(int)

    # Rename 'sector' to 'Secteur'
    pivot_df = pivot_df.rename(columns={'sector': 'Secteur'})

    # Sort sectors, move 'Total' to the last row
    pivot_df['Secteur'] = pivot_df['Secteur'].astype(str)
    pivot_df = pivot_df.sort_values(by='Secteur')
    if 'Total' in pivot_df['Secteur'].values:
        total_row = pivot_df[pivot_df['Secteur'] == 'Total']
        pivot_df = pivot_df[pivot_df['Secteur'] != 'Total']
        pivot_df = pd.concat([pivot_df, total_row], ignore_index=True)

    # Rearrange columns to have 'Pays' as the last column, if it exists
    columns_order = ['Secteur'] + [col for col in pivot_df.columns if col != 'Secteur' and col != 'Tout le pays']
    if 'Tout le pays' in pivot_df.columns:
        columns_order.append('Tout le pays')
    pivot_df = pivot_df[columns_order]

    return pivot_df


def create_meb_difference_table(df_meb_long, input):
    """
    Create a pivot table of percent differences between consecutive cycles for MEB.
    For the selected cycle (e.g. cycle_2) compare with cycle_1,
    computing ((current - previous) / previous)*100 for each sector & zone.
    
    Returns None if user selects the first cycle or if there's no data to compare.
    Returns an empty DataFrame if the filtering yields no valid pivot for comparison.
    """
    import logging
    try:
        cycle_num = int(input.cycle_select_meb())
    except Exception as e:
        logging.error(f"Error converting cycle selection to integer: {e}")
        return pd.DataFrame()
    
    # If the user chooses cycle 1, there's no previous cycle to compare.
    if cycle_num <= 1:
        return None

    current_cycle = f"cycle_{cycle_num}"
    previous_cycle = f"cycle_{cycle_num - 1}"

    type_meb_selected = input.type_meb_select_sectors().strip()
    meb_par_selected = input.meb_par_select().strip()
    currency_selected = input.currency_select_meb().strip()

    # Filter for the current cycle
    df_current = df_meb_long[
        (df_meb_long['Cycle'] == current_cycle) &
        (df_meb_long['Type_meb'] == type_meb_selected) &
        (df_meb_long['meb_par'] == meb_par_selected) &
        (df_meb_long['currency'] == currency_selected) &
        (df_meb_long['is_basket'])
    ]
    # Filter for the previous cycle
    df_previous = df_meb_long[
        (df_meb_long['Cycle'] == previous_cycle) &
        (df_meb_long['Type_meb'] == type_meb_selected) &
        (df_meb_long['meb_par'] == meb_par_selected) &
        (df_meb_long['currency'] == currency_selected) &
        (df_meb_long['is_basket'])
    ]

    if df_current.empty or df_previous.empty:
        return pd.DataFrame()

    # Pivot each
    pivot_current = df_current.pivot_table(
        index='sector',
        columns='zone',
        values='Value',
        aggfunc='mean'
    ).reset_index()

    pivot_previous = df_previous.pivot_table(
        index='sector',
        columns='zone',
        values='Value',
        aggfunc='mean'
    ).reset_index()

    # Merge on 'sector'
    merged = pd.merge(
        pivot_current, pivot_previous,
        on='sector', how='outer',
        suffixes=('_curr', '_prev')
    )

    # Compute difference for each 'zone' column
    for col in pivot_current.columns:
        if col == 'sector':
            continue
        curr_col = f"{col}_curr"
        prev_col = f"{col}_prev"
        if curr_col in merged.columns and prev_col in merged.columns:
            merged[f"{col}_diff"] = merged.apply(
                lambda row: (
                    ((row[curr_col] - row[prev_col]) / row[prev_col]) * 100
                    if pd.notna(row[curr_col]) and pd.notna(row[prev_col]) and row[prev_col] != 0
                    else None
                ),
                axis=1
            )

    # Build final difference table
    diff_cols = ['sector']
    for col in pivot_current.columns:
        if col != 'sector' and f"{col}_diff" in merged.columns:
            diff_cols.append(f"{col}_diff")

    diff_table = merged[diff_cols].copy()

    # Rename columns to remove "_diff"
    new_columns = {}
    for c in diff_table.columns:
        if c.endswith("_diff"):
            new_columns[c] = c.replace("_diff", "")
        else:
            new_columns[c] = c
    diff_table.rename(columns=new_columns, inplace=True)

    return diff_table


def create_meb_produits_data():
    """
    Create the DataFrame for the 'Produits du MEB' tab.
    """
    data = []

    # MEB CRISE PROLONGEÉ
    crisis_type = 'MEB Crise prolongée'

    # ABNA
    sector = 'ABNA'
    data.extend([
        {'Crisis Type': crisis_type, 'Sector': sector, 'Articles': 'Marmite - acier inoxydable', 'Unités': 'Pièce 7L', 'Quantité pour menage 5 personnes': 1, 'Quantités/ménage/mois': 0.1, 'Fréquence': 'Ponctuelle'},
        {'Crisis Type': crisis_type, 'Sector': sector, 'Articles': 'Poêle à frire', 'Unités': 'Pièce 2.5L', 'Quantité pour menage 5 personnes': 1, 'Quantités/ménage/mois': 0.1, 'Fréquence': 'Ponctuelle'},
        {'Crisis Type': crisis_type, 'Sector': sector, 'Articles': 'Marmite avec couvercle', 'Unités': 'Pièce 5L', 'Quantité pour menage 5 personnes': 1, 'Quantités/ménage/mois': 0.1, 'Fréquence': 'Ponctuelle'},
        {'Crisis Type': crisis_type, 'Sector': sector, 'Articles': 'Bol métallique', 'Unités': 'Pièce 1L', 'Quantité pour menage 5 personnes': 5, 'Quantités/ménage/mois': 0.4, 'Fréquence': 'Ponctuelle'},
        {'Crisis Type': crisis_type, 'Sector': sector, 'Articles': 'Assiette métallique', 'Unités': 'Pièce 0.75L', 'Quantité pour menage 5 personnes': 5, 'Quantités/ménage/mois': 0.4, 'Fréquence': 'Ponctuelle'},
        {'Crisis Type': crisis_type, 'Sector': sector, 'Articles': 'Gobelet métallique', 'Unités': 'Pièce 0.3L', 'Quantité pour menage 5 personnes': 5, 'Quantités/ménage/mois': 0.4, 'Fréquence': 'Ponctuelle'},
        {'Crisis Type': crisis_type, 'Sector': sector, 'Articles': 'Cuillère à soupe en acier inoxydable', 'Unités': 'Pièce 10 mL', 'Quantité pour menage 5 personnes': 5, 'Quantités/ménage/mois': 0.4, 'Fréquence': 'Ponctuelle'},
        {'Crisis Type': crisis_type, 'Sector': sector, 'Articles': 'Cuillère en bois à mélanger 30 cm', 'Unités': 'Pièce 30 cm', 'Quantité pour menage 5 personnes': 1, 'Quantités/ménage/mois': 0.1, 'Fréquence': 'Ponctuelle'},
        {'Crisis Type': crisis_type, 'Sector': sector, 'Articles': 'Fourchette de table acier inoxydable', 'Unités': 'Pièce 17 cm', 'Quantité pour menage 5 personnes': 5, 'Quantités/ménage/mois': 0.4, 'Fréquence': 'Ponctuelle'},
        {'Crisis Type': crisis_type, 'Sector': sector, 'Articles': 'Couteau de table acier inoxydable', 'Unités': 'Pièce 17 cm', 'Quantité pour menage 5 personnes': 5, 'Quantités/ménage/mois': 0.4, 'Fréquence': 'Ponctuelle'},
        {'Crisis Type': crisis_type, 'Sector': sector, 'Articles': 'Couteau de cuisine, lame en acier inoxydable', 'Unités': 'Pièce 15 cm', 'Quantité pour menage 5 personnes': 1, 'Quantités/ménage/mois': 0.1, 'Fréquence': 'Ponctuelle'},
        {'Crisis Type': crisis_type, 'Sector': sector, 'Articles': 'Tampon à récurer/paille de fer', 'Unités': 'Pièce', 'Quantité pour menage 5 personnes': 1, 'Quantités/ménage/mois': 1, 'Fréquence': 'Mensuelle'},
        {'Crisis Type': crisis_type, 'Sector': sector, 'Articles': 'Couverture 50% laine', 'Unités': 'Pièce 1.5x2m', 'Quantité pour menage 5 personnes': 3, 'Quantités/ménage/mois': 0.3, 'Fréquence': 'Ponctuelle'},
        {'Crisis Type': crisis_type, 'Sector': sector, 'Articles': 'Matelas', 'Unités': 'Pièce', 'Quantité pour menage 5 personnes': 2, 'Quantités/ménage/mois': 0.2, 'Fréquence': 'Ponctuelle'},
        {'Crisis Type': crisis_type, 'Sector': sector, 'Articles': 'Combustible - charbon de bois', 'Unités': 'Gros sac 18Lb', 'Quantité pour menage 5 personnes': 1, 'Quantités/ménage/mois': 1, 'Fréquence': 'Mensuelle'},
        {'Crisis Type': crisis_type, 'Sector': sector, 'Articles': 'Combustible - gaz propane', 'Unités': 'Litre', 'Quantité pour menage 5 personnes': 9, 'Quantités/ménage/mois': 9, 'Fréquence': 'Mensuelle'},
        {'Crisis Type': crisis_type, 'Sector': sector, 'Articles': 'Rechaud de 3 pièces (à charbon)', 'Unités': 'Pièce', 'Quantité pour menage 5 personnes': 1, 'Quantités/ménage/mois': 0.1, 'Fréquence': 'Ponctuelle'},
    ])

    # WASH
    sector = 'WASH'
    data.extend([
        {'Crisis Type': crisis_type, 'Sector': sector, 'Articles': 'Grande bassine', 'Unités': 'Pièce', 'Quantité pour menage 5 personnes': 3, 'Quantités/ménage/mois': 0.3, 'Fréquence': 'Ponctuelle'},
        {'Crisis Type': crisis_type, 'Sector': sector, 'Articles': 'Cuvette', 'Unités': 'Pièce', 'Quantité pour menage 5 personnes': 1, 'Quantités/ménage/mois': 0.1, 'Fréquence': 'Ponctuelle'},
        {'Crisis Type': crisis_type, 'Sector': sector, 'Articles': 'Eau potable (l)', 'Unités': 'litres', 'Quantité pour menage 5 personnes': 750, 'Quantités/ménage/mois': 750, 'Fréquence': 'Mensuelle'},
        {'Crisis Type': crisis_type, 'Sector': sector, 'Articles': 'Savon lessive', 'Unités': 'Kg', 'Quantité pour menage 5 personnes': 1, 'Quantités/ménage/mois': 1, 'Fréquence': 'Mensuelle'},
        {'Crisis Type': crisis_type, 'Sector': sector, 'Articles': 'Brosse à dents', 'Unités': 'Pièce', 'Quantité pour menage 5 personnes': 5, 'Quantités/ménage/mois': 5, 'Fréquence': 'Mensuelle'},
        {'Crisis Type': crisis_type, 'Sector': sector, 'Articles': 'Dentifrice', 'Unités': 'Pièce (85 gr)', 'Quantité pour menage 5 personnes': 4, 'Quantités/ménage/mois': 4, 'Fréquence': 'Mensuelle'},
        {'Crisis Type': crisis_type, 'Sector': sector, 'Articles': 'Papier toilette', 'Unités': 'Pièce', 'Quantité pour menage 5 personnes': 5, 'Quantités/ménage/mois': 5, 'Fréquence': 'Mensuelle'},
        {'Crisis Type': crisis_type, 'Sector': sector, 'Articles': 'Serviettes hygiéniques', 'Unités': 'Paquet (8)', 'Quantité pour menage 5 personnes': 3, 'Quantités/ménage/mois': 3, 'Fréquence': 'Mensuelle'},
        {'Crisis Type': crisis_type, 'Sector': sector, 'Articles': 'Savon bain (75 Gr)', 'Unités': 'Pièce', 'Quantité pour menage 5 personnes': 13, 'Quantités/ménage/mois': 13, 'Fréquence': 'Mensuelle'},
        {'Crisis Type': crisis_type, 'Sector': sector, 'Articles': 'Bassine pour faire la lessive', 'Unités': 'Piece', 'Quantité pour menage 5 personnes': 1, 'Quantités/ménage/mois': 0.1, 'Fréquence': 'Ponctuelle'},
        {'Crisis Type': crisis_type, 'Sector': sector, 'Articles': 'Deodorant', 'Unités': 'Flacon', 'Quantité pour menage 5 personnes': 3, 'Quantités/ménage/mois': 3, 'Fréquence': 'Mensuelle'},
    ])

    # PROTECTION
    sector = 'Protection'
    data.extend([
        {'Crisis Type': crisis_type, 'Sector': sector, 'Articles': 'Torche (y compris piles ou batteries)', 'Unités': 'Pièce', 'Quantité pour menage 5 personnes': 1, 'Quantités/ménage/mois': 0.1, 'Fréquence': 'Ponctuelle'},
        {'Crisis Type': crisis_type, 'Sector': sector, 'Articles': 'Carte sim', 'Unités': 'Pièce', 'Quantité pour menage 5 personnes': 1, 'Quantités/ménage/mois': 0.1, 'Fréquence': 'Ponctuelle'},
        {'Crisis Type': crisis_type, 'Sector': sector, 'Articles': 'Téléphone', 'Unités': 'Pièce', 'Quantité pour menage 5 personnes': 1, 'Quantités/ménage/mois': 0.1, 'Fréquence': 'Ponctuelle'},
        {'Crisis Type': crisis_type, 'Sector': sector, 'Articles': 'Recharge de telephone de 100 HTG', 'Unités': 'Personne', 'Quantité pour menage 5 personnes': 3, 'Quantités/ménage/mois': 3, 'Fréquence': 'Mensuelle'},
    ])

    # EDUCATION
    sector = 'Education'
    data.extend([
        {'Crisis Type': crisis_type, 'Sector': sector, 'Articles': 'Dépenses moyennes (basé sur les dépenses moyennes des ménages)', 'Unités': 'Forfait en HTG', 'Quantité pour menage 5 personnes': None, 'Quantités/ménage/mois': None, 'Fréquence': 'Mensuelle'},
    ])

    # SANTE
    sector = 'Santé'
    data.extend([
        {'Crisis Type': crisis_type, 'Sector': sector, 'Articles': 'Moustiquaire double', 'Unités': 'Pièce', 'Quantité pour menage 5 personnes': 2, 'Quantités/ménage/mois': 0.2, 'Fréquence': 'Ponctuelle'},
        {'Crisis Type': crisis_type, 'Sector': sector, 'Articles': 'Dépenses moyennes (basé sur les dépenses moyennes des ménages)', 'Unités': 'Forfait en HTG', 'Quantité pour menage 5 personnes': None, 'Quantités/ménage/mois': None, 'Fréquence': 'Mensuelle'},
    ])

    # MEB CRISE D'URGENCE
    crisis_type = "MEB Crise d'urgence"

    # ABNA
    sector = 'ABNA'
    data.extend([
        {'Crisis Type': crisis_type, 'Sector': sector, 'Articles': 'Marmite - acier inoxydable', 'Unités': 'Pièce 7L', 'Quantité pour menage 5 personnes': 1, 'Quantités/ménage/mois': 0.1, 'Fréquence': 'Ponctuelle'},
        {'Crisis Type': crisis_type, 'Sector': sector, 'Articles': 'Bol métallique', 'Unités': 'Pièce 1L', 'Quantité pour menage 5 personnes': 5, 'Quantités/ménage/mois': 0.4, 'Fréquence': 'Ponctuelle'},
        {'Crisis Type': crisis_type, 'Sector': sector, 'Articles': 'Gobelet métallique', 'Unités': 'Pièce 0.3L', 'Quantité pour menage 5 personnes': 5, 'Quantités/ménage/mois': 0.4, 'Fréquence': 'Ponctuelle'},
        {'Crisis Type': crisis_type, 'Sector': sector, 'Articles': 'Cuillère à soupe en acier inoxydable', 'Unités': 'Pièce 10 mL', 'Quantité pour menage 5 personnes': 5, 'Quantités/ménage/mois': 0.4, 'Fréquence': 'Ponctuelle'},
        {'Crisis Type': crisis_type, 'Sector': sector, 'Articles': 'Cuillère en bois à mélanger 30 cm', 'Unités': 'Pièce 30 cm', 'Quantité pour menage 5 personnes': 1, 'Quantités/ménage/mois': 0.1, 'Fréquence': 'Ponctuelle'},
        {'Crisis Type': crisis_type, 'Sector': sector, 'Articles': 'Couteau de cuisine, lame en acier inoxydable', 'Unités': 'Pièce 15 cm', 'Quantité pour menage 5 personnes': 1, 'Quantités/ménage/mois': 0.1, 'Fréquence': 'Ponctuelle'},
        {'Crisis Type': crisis_type, 'Sector': sector, 'Articles': 'Tampon à récurer/paille de fer', 'Unités': 'Pièce', 'Quantité pour menage 5 personnes': 1, 'Quantités/ménage/mois': 1, 'Fréquence': 'Mensuelle'},
        {'Crisis Type': crisis_type, 'Sector': sector, 'Articles': 'Couverture 50% laine', 'Unités': 'Pièce 1.5x2m', 'Quantité pour menage 5 personnes': 3, 'Quantités/ménage/mois': 0.3, 'Fréquence': 'Ponctuelle'},
        {'Crisis Type': crisis_type, 'Sector': sector, 'Articles': 'Natte', 'Unités': 'Pièce', 'Quantité pour menage 5 personnes': 2, 'Quantités/ménage/mois': 0.2, 'Fréquence': 'Ponctuelle'},
        {'Crisis Type': crisis_type, 'Sector': sector, 'Articles': 'Combustible - charbon de bois', 'Unités': 'Gros sac 18Lb', 'Quantité pour menage 5 personnes': 1, 'Quantités/ménage/mois': 1, 'Fréquence': 'Mensuelle'},
        {'Crisis Type': crisis_type, 'Sector': sector, 'Articles': 'Rechaud de 3 pièces (à charbon)', 'Unités': 'Pièce', 'Quantité pour menage 5 personnes': 1, 'Quantités/ménage/mois': 0.1, 'Fréquence': 'Ponctuelle'},
    ])

    # ABNA Shelter
    sector = 'ABNA Shelter'
    data.extend([
        {'Crisis Type': crisis_type, 'Sector': sector, 'Articles': 'Corde Polypropylène, 6 mm diamètre rouleaux torsadés', 'Unités': 'm', 'Quantité pour menage 5 personnes': 60, 'Quantités/ménage/mois': 5, 'Fréquence': 'Ponctuelle'},
        {'Crisis Type': crisis_type, 'Sector': sector, 'Articles': '2” clou (50mm)', 'Unités': 'kg', 'Quantité pour menage 5 personnes': 2, 'Quantités/ménage/mois': 0.2, 'Fréquence': 'Ponctuelle'},
        {'Crisis Type': crisis_type, 'Sector': sector, 'Articles': '3” clou (75mm)', 'Unités': 'kg', 'Quantité pour menage 5 personnes': 1, 'Quantités/ménage/mois': 0.1, 'Fréquence': 'Ponctuelle'},
        {'Crisis Type': crisis_type, 'Sector': sector, 'Articles': '2.5” clou pour toiture (63mm)', 'Unités': 'kg', 'Quantité pour menage 5 personnes': 1, 'Quantités/ménage/mois': 0.1, 'Fréquence': 'Ponctuelle'},
        {'Crisis Type': crisis_type, 'Sector': sector, 'Articles': 'Fil de ligature', 'Unités': 'm', 'Quantité pour menage 5 personnes': 100, 'Quantités/ménage/mois': 8.3, 'Fréquence': 'Ponctuelle'},
        {'Crisis Type': crisis_type, 'Sector': sector, 'Articles': 'Marteau', 'Unités': 'Pièce', 'Quantité pour menage 5 personnes': 2, 'Quantités/ménage/mois': 0.2, 'Fréquence': 'Ponctuelle'},
        {'Crisis Type': crisis_type, 'Sector': sector, 'Articles': 'Pelle', 'Unités': 'Pièce', 'Quantité pour menage 5 personnes': 1, 'Quantités/ménage/mois': 0.1, 'Fréquence': 'Ponctuelle'},
        {'Crisis Type': crisis_type, 'Sector': sector, 'Articles': 'Sécateur', 'Unités': 'Pièce', 'Quantité pour menage 5 personnes': 1, 'Quantités/ménage/mois': 0.1, 'Fréquence': 'Ponctuelle'},
        {'Crisis Type': crisis_type, 'Sector': sector, 'Articles': 'Houe', 'Unités': 'Pièce', 'Quantité pour menage 5 personnes': 1, 'Quantités/ménage/mois': 0.1, 'Fréquence': 'Ponctuelle'},
        {'Crisis Type': crisis_type, 'Sector': sector, 'Articles': 'Pioche', 'Unités': 'Pièce', 'Quantité pour menage 5 personnes': 1, 'Quantités/ménage/mois': 0.1, 'Fréquence': 'Ponctuelle'},
    ])

    # WASH
    sector = 'WASH'
    data.extend([
        {'Crisis Type': crisis_type, 'Sector': sector, 'Articles': 'Grande bassine', 'Unités': 'Pièce', 'Quantité pour menage 5 personnes': 3, 'Quantités/ménage/mois': 0.3, 'Fréquence': 'Ponctuelle'},
        {'Crisis Type': crisis_type, 'Sector': sector, 'Articles': 'Eau potable (l)', 'Unités': '(litres)', 'Quantité pour menage 5 personnes': 750, 'Quantités/ménage/mois': 750, 'Fréquence': 'Mensuelle'},
        {'Crisis Type': crisis_type, 'Sector': sector, 'Articles': 'Savon lessive', 'Unités': 'Kg', 'Quantité pour menage 5 personnes': 1, 'Quantités/ménage/mois': 1, 'Fréquence': 'Mensuelle'},
        {'Crisis Type': crisis_type, 'Sector': sector, 'Articles': 'Brosse à dents', 'Unités': 'Pièce', 'Quantité pour menage 5 personnes': 5, 'Quantités/ménage/mois': 5, 'Fréquence': 'Mensuelle'},
        {'Crisis Type': crisis_type, 'Sector': sector, 'Articles': 'Dentifrice', 'Unités': 'Pièce (85 gr)', 'Quantité pour menage 5 personnes': 4, 'Quantités/ménage/mois': 4, 'Fréquence': 'Mensuelle'},
        {'Crisis Type': crisis_type, 'Sector': sector, 'Articles': 'Papier toilette', 'Unités': 'Pièce', 'Quantité pour menage 5 personnes': 5, 'Quantités/ménage/mois': 5, 'Fréquence': 'Mensuelle'},
        {'Crisis Type': crisis_type, 'Sector': sector, 'Articles': 'Serviettes hygiéniques', 'Unités': 'Paquet (8)', 'Quantité pour menage 5 personnes': 3, 'Quantités/ménage/mois': 3, 'Fréquence': 'Mensuelle'},
        {'Crisis Type': crisis_type, 'Sector': sector, 'Articles': 'Savon bain (75 Gr)', 'Unités': 'Pièce', 'Quantité pour menage 5 personnes': 13, 'Quantités/ménage/mois': 13, 'Fréquence': 'Mensuelle'},
    ])

    # PROTECTION
    sector = 'Protection'
    data.extend([
        {'Crisis Type': crisis_type, 'Sector': sector, 'Articles': 'Torche (y compris piles ou batteries)', 'Unités': 'Pièce', 'Quantité pour menage 5 personnes': 1, 'Quantités/ménage/mois': 0.1, 'Fréquence': 'Ponctuelle'},
        {'Crisis Type': crisis_type, 'Sector': sector, 'Articles': 'Carte sim', 'Unités': 'Pièce', 'Quantité pour menage 5 personnes': 1, 'Quantités/ménage/mois': 0.1, 'Fréquence': 'Ponctuelle'},
        {'Crisis Type': crisis_type, 'Sector': sector, 'Articles': 'Téléphone', 'Unités': 'Pièce', 'Quantité pour menage 5 personnes': 1, 'Quantités/ménage/mois': 0.1, 'Fréquence': 'Ponctuelle'},
        {'Crisis Type': crisis_type, 'Sector': sector, 'Articles': 'Recharge de telephone de 100 HTG', 'Unités': 'Personne', 'Quantité pour menage 5 personnes': 3, 'Quantités/ménage/mois': 3, 'Fréquence': 'Mensuelle'},
    ])

    # EDUCATION
    sector = 'Education'
    data.extend([
        {'Crisis Type': crisis_type, 'Sector': sector, 'Articles': 'Dépenses moyennes (basé sur les dépenses moyennes des ménages)', 'Unités': 'Forfait en HTG', 'Quantité pour menage 5 personnes': None, 'Quantités/ménage/mois': None, 'Fréquence': 'Mensuelle'},
    ])

    # SANTE
    sector = 'Santé'
    data.extend([
        {'Crisis Type': crisis_type, 'Sector': sector, 'Articles': 'Moustiquaire double', 'Unités': 'Pièce', 'Quantité pour menage 5 personnes': 2, 'Quantités/ménage/mois': 0.2, 'Fréquence': 'Ponctuelle'},
        {'Crisis Type': crisis_type, 'Sector': sector, 'Articles': 'Dépenses moyennes (basé sur les dépenses moyennes des ménages)', 'Unités': 'Forfait en HTG', 'Quantité pour menage 5 personnes': None, 'Quantités/ménage/mois': None, 'Fréquence': 'Mensuelle'},
    ])

    # Convert data to DataFrame
    df_produits = pd.DataFrame(data)

    return df_produits

def get_produits_meb_choices(df_produits):
    type_meb_choices = sorted(df_produits['Crisis Type'].unique().tolist())
    secteur_choices = sorted(df_produits['Sector'].unique().tolist())
    return type_meb_choices, secteur_choices

def create_produits_meb_table(df_produits, input):
    """
    Create the table for the 'Produits du MEB' tab.
    """
    # Get selected crisis type and sector
    crisis_type_selected = input.type_meb_select_products().strip()
    sector_selected = input.secteur_select().strip()

    # Filter data
    filtered_df = df_produits[
        (df_produits['Crisis Type'] == crisis_type_selected) &
        (df_produits['Sector'] == sector_selected)
    ]

    # Select columns to display
    columns_to_display = ['Articles', 'Unités', 'Quantité pour menage 5 personnes', 'Quantités/ménage/mois', 'Fréquence']

    # Return the filtered DataFrame
    return filtered_df[columns_to_display]


def meb_ui(cycle_choices, type_meb_choices, meb_par_choices, currency_choices, type_meb_choices_produits, secteur_choices):
    """
    Define the UI for the "MEB" tab panel, with the cycle slider placed
    in the "Cout du MEB par secteurs" sidebar.
    """

    # Prepare the slider input for cycle selection
    cycle_slider = ui.input_slider(
        "cycle_select_meb",
        "Choisir le Cycle",
        min=1,
        #max=len(cycle_choices),
        max=2,
        value=1,
        step=1
    )

    return ui.nav_panel(
        ui.tags.span(
            ui.tags.i(class_="fa fa-shopping-cart icon"),
            " MEB",
            class_="nav-panel-title"
        ),
        ui.p("Cette page vous permet de consulter les composantes du MEB (Minimum Expenditure Basket) selon le type de crise."),
        ui.p("Le coût du MEB est calculé en multipliant le prix médian de chaque article dans la zone concernée par la quantité indiquée dans le tableau de référence. Enfin, lorsque qu’un article inclus dans le MEB n’est pas disponible dans une zone donnée, le calcul de l’indice utilise le prix médian global en remplacement."), 
        ui.p("Deux types de paniers ont été retenus. Le MEB d’urgence correspond aux besoins essentiels des ménages après une catastrophe naturelle ou un incident de protection. Il ne s’agit pas d’un panier minimum de survie, mais d’un ensemble de dépenses nécessaires et ponctuelles, pouvant être couvert par un transfert monétaire unique. Le MEB de crise prolongée, pour sa part, inclut des articles essentiels dans les domaines ABNA, WASH, Protection, Santé et Éducation, et s’applique en dehors du contexte d’urgence."),

        ui.navset_pill(
            # 1) "Produits du MEB" sub-panel
            ui.nav_panel(
                "Produits du MEB",
                ui.layout_sidebar(
                    ui.sidebar(
                        ui.div(
                            ui.tags.label("Choisir le type de crise", class_="custom-select-label"),
                            ui.input_radio_buttons(
                                "type_meb_select_products",
                                None,
                                choices=type_meb_choices_produits,
                                selected=type_meb_choices_produits[0],
                                inline=True,
                            ),
                            class_="custom-select"
                        ),
                        ui.div(
                            ui.tags.label("Choisir le Secteur", class_="custom-select-label"),
                            ui.input_select(
                                "secteur_select",
                                None,
                                choices=secteur_choices,
                            ),
                            class_="custom-select"
                        ),
                    ),
                    ui.h2("Inventaire des articles utilisés"),
                    ui.div(
                        ui.output_data_frame("produits_meb_table"),
                        class_="produits_meb_table"
                    ),
                ),
            ),

            # 2) "Cout du MEB par secteurs" sub-panel
            ui.nav_panel(
                "Cout du MEB par secteurs",
                ui.layout_sidebar(
                    ui.sidebar(
                        ui.div(
                            ui.tags.label(class_="custom-select-label"),
                            cycle_slider,  # <- cycle slider here
                            class_="custom-select"
                        ),
                        ui.div(
                            ui.tags.label("Choisir le type de crise", class_="custom-select-label"),
                            ui.input_radio_buttons(
                                "type_meb_select_sectors",
                                None,
                                choices=type_meb_choices,
                                selected=type_meb_choices[0],
                                inline=True,
                            ),
                            class_="custom-select"
                        ),
                        ui.div(
                            ui.tags.label("Choisir le Niveau géographique", class_="custom-select-label"),
                            ui.input_select(
                                "meb_par_select",
                                None,
                                choices=meb_par_choices,
                            ),
                            class_="custom-select"
                        ),
                        ui.div(
                            ui.tags.label("Choisir la monnaie", class_="custom-select-label"),
                            ui.input_select(
                                "currency_select_meb",
                                None,
                                choices=currency_choices,
                            ),
                            class_="custom-select"
                        ),
                    ),
                    ui.div(
                        # Switch to toggle between normal table and difference table
                        ui.div(
                            ui.input_switch(
                                id="toggle_diff_meb",
                                label="Afficher les différences (%)",
                                value=False
                            ),
                            class_="switch-container"
                        ),
                        ui.h2("MEB par Secteurs"),
                        ui.output_ui("meb_secteurs_table"),
                    ),
                ),
            ),
            id="meb_tab_selected",
            selected="Produits du MEB"
        )
    )


def meb_server(input, output, session, df_meb_long, df_produits):
    """
    Server logic for the MEB panel.
    Handles the rendering of produits_meb_table and meb_secteurs_table,
    including the 'Afficher les différences (%)' feature for the MEB table.
    """

    @output
    @render.data_frame
    def produits_meb_table():
        """
        Renders the 'Produits du MEB' data frame based on user inputs.
        """
        df_table = create_produits_meb_table(df_produits, input)
        return df_table

    @output
    @render.ui
    def meb_secteurs_table():
        """
        Renders the 'Cout du MEB par secteurs' table as either:
         - The normal pivot (avg values) table, or
         - The difference (%) table compared to the previous cycle,
           depending on the toggle_diff_meb switch.
        """
        # Check the switch: if toggled, show the differences table; otherwise, show the normal table.
        if input.toggle_diff_meb():
            diff_df = create_meb_difference_table(df_meb_long, input)
            if diff_df is None:
                # This happens when the selected cycle is the first one
                return ui.HTML("<p>Aucune donnée disponible pour calculer la différence pour le cycle sélectionné.</p>")
            if diff_df.empty:
                return ui.HTML("<p>Aucune donnée disponible pour les sélections actuelles ou pas de comparaison possible.</p>")

            # Build HTML table for the difference data
            def apply_diff_format(row):
                styled_row = []
                for col in diff_df.columns:
                    if col == 'sector':
                        # Bold sector name
                        styled_row.append(f"<td><strong>{row[col]}</strong></td>")
                    else:
                        cell_value = row[col]
                        if cell_value is None or pd.isna(cell_value):
                            styled_row.append("<td></td>")
                        else:
                            if cell_value > 0:
                                # Positive difference => red color (#CD2030), up arrow
                                formatted = f"▲ +{cell_value:.1f}%"
                                styled_row.append(f"<td style='color: #CD2030;'><strong>{formatted}</strong></td>")
                            elif cell_value < 0:
                                # Negative difference => green color (#086D38), down arrow
                                formatted = f"▼ {cell_value:.1f}%"
                                styled_row.append(f"<td style='color: #086D38;'><strong>{formatted}</strong></td>")
                            else:
                                # Exactly zero difference => show "="
                                formatted = f"= {cell_value:.1f}%"
                                styled_row.append(f"<td><strong>{formatted}</strong></td>")
                return "<tr>" + "".join(styled_row) + "</tr>"

            table_html = "<table class='difference-table'><thead><tr>"
            for col in diff_df.columns:
                if col == 'sector':
                    table_html += "<th>Secteur</th>"
                else:
                    table_html += f"<th>{col}</th>"
            table_html += "</tr></thead><tbody>"
            for _, row in diff_df.iterrows():
                table_html += apply_diff_format(row)
            table_html += "</tbody></table>"

            return ui.HTML(table_html)

        else:
            # Render the normal (avg value) MEB table
            pivot_df = create_meb_secteurs_table(df_meb_long, input)
            if pivot_df.empty:
                return ui.HTML("<p>Aucune donnée disponible pour les sélections actuelles.</p>")

            def apply_conditional_colors(row):
                numeric_cols = [col for col in pivot_df.columns if col != 'Secteur']
                try:
                    values = pd.to_numeric(row[numeric_cols].replace(',', '', regex=True), errors='coerce')
                except AttributeError:
                    values = pd.to_numeric(row[numeric_cols], errors='coerce')

                quantiles = values.quantile([0.25, 0.5, 0.75]).to_dict()

                # Check if this row is 'Total'
                row_class = "class='total-row'" if row['Secteur'] == 'Total' else ""
                styled_row = [f"<tr {row_class}>"]

                for col in pivot_df.columns:
                    cell_value = row[col]
                    if col == 'Secteur':
                        # First column in bold
                        styled_row.append(f"<td class='first-column'>{cell_value}</td>")
                    else:
                        if pd.isna(cell_value):
                            styled_row.append("<td></td>")
                        else:
                            val = pd.to_numeric(str(cell_value).replace(',', ''), errors='coerce')
                            color = "#FEEEED"  # default color for lower quantiles
                            if val is not None:
                                if val > quantiles.get(0.75, 0):
                                    color = "#EE5859"
                                elif val > quantiles.get(0.5, 0):
                                    color = "#F27D7C"
                                elif val > quantiles.get(0.25, 0):
                                    color = "#F3BEBD"

                            # Thousands separator formatting
                            cell_display = "{:,}".format(int(val)) if val is not None else ""
                            styled_row.append(f"<td style='background-color: {color};'>{cell_display}</td>")

                styled_row.append("</tr>")
                return "".join(styled_row)

            # Build the HTML table
            table_html = """
            <table class="meb-secteurs-table">
                <thead>
                    <tr>
            """
            # Add table headers
            for col in pivot_df.columns:
                table_html += f"<th>{col}</th>"
            table_html += "</tr></thead><tbody>"

            # Add rows with conditional styling
            for _, row in pivot_df.iterrows():
                table_html += apply_conditional_colors(row)

            table_html += "</tbody></table>"

            return ui.HTML(table_html)
