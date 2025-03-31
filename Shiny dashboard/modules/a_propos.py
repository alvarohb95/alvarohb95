# modules/a_propos.py

import os
import pandas as pd
from shiny import ui, render

def a_propos_ui(cycle_options):
    """
    Layout/UI for the 'À Propos' page.
    Expects a list of cycle_options loaded in `main.py`.
    """
    return ui.nav_panel(
        ui.tags.span(
            ui.tags.i(class_="fa fa-question-circle icon"),  # Example icon
            " À Propos",
            class_="nav-panel-title"
        ),
        ui.page_fillable(
            #
            # ------------------ TOP HALF ------------------
            #
            ui.layout_columns(
                # Left column: Mise en contexte + Méthodologie
                ui.column(
                    11,
                    # -- Mise en contexte --
                    ui.h2("Mise en contexte"),
                    ui.HTML(
                        """
                        <p class="justified-text">
                        La <strong>situation humanitaire</strong> en Haïti se détériore, affectant directement 
                        les marchés locaux et la <strong>disponibilité</strong> des produits. La recrudescence 
                        de la <strong>violence</strong> et les <strong>fermetures de routes</strong> par des gangs 
                        perturbent sévèrement les <strong>chaînes d’approvisionnement</strong>, limitant l’accès 
                        aux biens essentiels.
                        </p>
                        <p class="justified-text">
                        Ces conditions compliquent la <strong>mise en œuvre des opérations humanitaires</strong>, 
                        entraînant une <strong>pression accrue</strong> sur les ressources disponibles dans les 
                        <strong>marchés locaux</strong>. Ce rapport présente les <strong>résultats</strong> de 
                        l’<strong>Initiative Conjointe de Suivi des Marchés (ICSM)</strong> menée par 
                        <strong>REACH</strong> en septembre 2024, incluant le <strong>prix médian</strong> des 
                        articles du <strong>Minimum Expenditure Basket (MEB) non-alimentaire</strong>, sa valeur 
                        totale estimée, et les <strong>montants nécessaires</strong> pour les 
                        <strong>transferts monétaires</strong>. Il examine aussi la <strong>disponibilité</strong> 
                        des produits et les <strong>ruptures de stock</strong> potentiels sur les marchés, 
                        attribuant des <strong>scores de fonctionnalité</strong>.
                        </p>
                        <p class="justified-text">
                        Ces <strong>données</strong> aideront à optimiser les 
                        <strong>programmes de transferts monétaires</strong> pour une 
                        <strong>intervention efficace</strong> et ciblée auprès des ménages en difficulté.
                        </p>
                        """
                    ),

                    # -- Méthodologie --
                    ui.h2("Méthodologie"),
                    ui.HTML(
                        """
                        <p class="justified-text">
                        Une <strong>approche quantitative</strong> à titre indicatif et au niveau national a été 
                        adoptée pour recueillir des <strong>données</strong> auprès d’<strong>informateurs clés 
                        (ICs)</strong>. Cette démarche impliquait la collecte de <strong>prix</strong> pour chaque 
                        article du <strong>MEB</strong> à travers des <strong>entretiens en face-à-face</strong> 
                        avec les commerçants (ICs) dans deux marchés par département : un 
                        <strong>marché chef-lieu</strong>, considéré comme un <strong>centre commercial clé</strong> 
                        servant de point de convergence pour les produits en provenance des autres marchés du 
                        département, et un <strong>marché régional</strong> de moindre envergure, desservant 
                        spécifiquement sa zone géographique.
                        </p>
                        <p class="justified-text">
                        Pour la <strong>Zone Métropolitaine de Port-au-Prince (ZMPAP)</strong>, une approche 
                        légèrement différente a été adoptée, avec l’évaluation de deux marchés : l’un situé dans 
                        une zone économiquement aisée et l’autre dans un secteur défavorisé, afin de refléter les 
                        <strong>contrastes socioéconomiques</strong> des milieux concernés.
                        </p>
                        <p class="justified-text">
                        Les <strong>données</strong> ont été collectées via <strong>KoboCollect</strong> sur 
                        <strong>smartphones</strong> ou <strong>tablettes</strong>, avec un 
                        <strong>suivi quotidien</strong> et un <strong>nettoyage systématique</strong> (correction 
                        des anomalies, valeurs aberrantes, etc.) à l’aide d’<strong>Excel et R</strong>. Le 
                        processus respectait les <strong>Standards Minimums de Nettoyage REACH</strong> et a été 
                        documenté dans un <strong>registre dédié</strong>. Une <strong>vérification finale</strong> 
                        a été réalisée par l’équipe terrain et au siège. L’<strong>analyse</strong>, conforme au 
                        <strong>Plan d’Analyse de Données</strong>, a utilisé <strong>R et Excel</strong> pour 
                        calculer les <strong>prix médians</strong> par produit et marché, avec une distinction 
                        entre marchés ruraux, urbains et l’ensemble du pays.
                        </p>
                        """
                    ),
                ),
                # Right column: Localisation des marchés évalués (Card)
                ui.column(
                    11,
                    ui.card(
                       ui.h2("Localisation des marchés évalués", style="margin-bottom: -5px;"),
                       ui.HTML(
                           """
                           <p class="justified-text">
                           À travers le pays, <strong>22 marchés</strong> ont été évalués dont 
                           <strong>10 marchés chef-lieu</strong> dans chaque département, 
                           <strong>10 marchés régionaux</strong> dans chaque département, et 
                           <strong>2 marchés</strong> dans la <strong>ZMPAP (Zone Métropolitaine 
                           de Port-au-Prince)</strong> (un en zone pauvre et un en zone plus aisée).
                           </p>
                           <img src="images/ICSM_Suivi de Marchés.jpg"
                                alt="Coverage Map"
                                style="width: 100%; height: auto; display: block; margin-bottom: 10px;">
                           """
                       ),
                    ),
                ),
            ),
            #
            # ------------------ HORIZONTAL LINE  ------------------
            #
            ui.HTML("<hr style='margin-top: 20px; margin-bottom: 20px;'>"),
            #
            # ------------------ BOTTOM HALF ------------------
            #
            ui.layout_columns(
                # Left column: Filter + Période de collecte + dynamic image
                ui.column(
                    11,
                    ui.h5("Choisissez un cycle :"),
                    ui.div(
                        ui.input_select(
                            "selected_cycle",
                            label=None,
                            choices=cycle_options,
                            selected=cycle_options[0] if cycle_options else None
                        ),
                        class_="custom-select"
                    ),
                    ui.h2("Période de collecte"),
                    ui.output_text("periode_collected"),
                    ui.output_ui("dynamic_image"),
                ),
                # Right column: Résultats Clés (in a card, grey style)
                ui.column(
                    11,
                    ui.card(
                        ui.output_ui("resultats_cles"),
                        class_="justified-text"
                    ),
                ),
            )
        )
    )

def a_propos_server(input, output, session, data_dir):
    """
    Server logic for the 'À Propos' page. Expects `data_dir` so it can read 'cycle_data.xlsx'.
    We do NOT call set_choices here; the cycles are already set in the UI from main.py.
    """
    # 1) Load the cycle data to get the "Période de collecte" column and so on
    df_cycle = pd.read_excel(os.path.join(data_dir, "cycle_data.xlsx"))

    # 2) Helper: retrieve row for the currently selected cycle
    def get_selected_cycle_info():
        selected = input.selected_cycle()
        row = df_cycle[df_cycle["Cycle"] == selected]
        return row.iloc[0] if not row.empty else None

    # 3) Output "Période de collecte"
    @output
    @render.text
    def periode_collected():
        info = get_selected_cycle_info()
        if info is not None:
            return f"{info['Période de collecte']}"
        return "Période de collecte : N/A"

    # 4) Dynamic image based on cycle
    @output
    @render.ui
    def dynamic_image():
        info = get_selected_cycle_info()
        if info is not None:
            cycle_value = info["Cycle"]
            return ui.HTML(
                f"""
                <img src="images/{cycle_value}.PNG"
                     alt="Dynamic Cycle Image"
                     style="width: 135%; height: auto; display: block; margin-left: -100px; margin-top: 20px;">
                """
            )
        return ui.HTML("<p>Aucune image disponible pour ce cycle.</p>")

    # 5-A) Dynamic main title for Résultats Clés (used in some places if needed)
    @output
    @render.text
    def res_cl_title():
        info = get_selected_cycle_info()
        if info is not None:
            cyc = info["Cycle"]  # e.g. "Cycle 1"
            return f"Résultats Clés - {cyc}"
        return "Résultats Clés"

    # 5-B) Résultats Clés content
    @output
    @render.ui
    def resultats_cles():
        """
        Renders the 'Résultats Clés' section, with bolded important words
        in the paragraphs.
        """
        sel = input.selected_cycle()
        
        # If no cycle is selected yet
        if not sel:
            return ui.HTML("<p>Veuillez sélectionner un cycle pour afficher les résultats clés.</p>")

        # --- CYCLE 1 ---
        if sel == "Cycle 1":
            return ui.HTML(f"""
                <!-- Main Title -->
                <div style="color: #ee5859;
                            font-size: 30px;
                            margin-bottom: -5px;
                            font-weight: 700;
                            font-family: 'Arial Narrow';">
                Résultats Clés - {sel}
                </div>

                <!-- Subheading #1 -->
                <p style="font-weight: 700; 
                        font-size: 20px;
                        margin-bottom: -5px;  
                        font-family: 'Arial Narrow';">
                1. Coût du MEB
                </p>
                <p style="margin-left: 30px;
                        margin-bottom: -5px; 
                        line-height: 1.2;">
                - Le <strong>coût</strong> du <strong>MEB multisectoriel non-alimentaire</strong> le plus élevé du 
                panier de <strong>crise prolongée</strong> est observé dans le département de la 
                <strong>Grand’Anse</strong> alors que le plus faible <strong>coût</strong> du panier de 
                <strong>crise prolongée</strong> se fait remarquer dans le département du 
                <strong>Centre</strong>.
                </p>
                <p style="margin-left: 30px; 
                        line-height: 1.2;">
                - Pour ce qui est du <strong>panier d’urgence</strong>, son <strong>coût</strong> est le plus élevé 
                dans le département de l’<strong>Ouest</strong> tandis qu’il est le plus faible au niveau de la 
                <strong>ZMPAP</strong> (<strong>Zone Métropolitaine de Port-au-Prince</strong>). 
                Ces <strong>disparités régionales</strong> peuvent être partiellement expliquées par des 
                <strong>défis logistiques</strong> et <strong>sécuritaires</strong> significatifs impactant 
                le <strong>transport</strong> et l’<strong>accès</strong> aux marchandises.
                </p>

                <!-- Subheading #2 -->
                <p style="font-weight: 700;
                        margin-bottom: -5px;  
                        font-size: 20px; 
                        font-family: 'Arial Narrow';">
                2. Fonctionnalité des marchés
                </p>
                <p style="margin-left: 30px;
                        margin-bottom: -5px;  
                        line-height: 1.4;">
                - Notre étude sur la <strong>fonctionnalité des marchés</strong> révèle qu’aucun 
                <strong>marché évalué</strong> ne répond entièrement aux attentes en termes de 
                <strong>services</strong> et d’<strong>accès</strong> aux produits, indiquant 
                qu’aucun ne peut être considéré comme pleinement <strong>fonctionnel</strong>.
                </p>
                <p style="margin-left: 30px; 
                        line-height: 1.4;">
                - Dans les <strong>Nippes</strong>, les marchés de <strong>Fonds des Nègres</strong> et de 
                <strong>Miragôane</strong> se démarquent par leur meilleure performance, bien qu’ils 
                rencontrent encore des <strong>difficultés</strong>.
                </p>

                <!-- Subheading #3 -->
                <p style="font-weight: 700; 
                        font-size: 20px; 
                        margin-bottom: -5px;
                        font-family: 'Arial Narrow';">
                3. Chaînes d’approvisionnement
                </p>
                <p style="margin-left: 30px; 
                        margin-bottom: -5px; 
                        line-height: 1.4;">
                - Les marchés de <strong>Jean Rabel</strong>, <strong>Anse d’Hainault</strong>, et 
                <strong>Les Perches</strong> sont confrontés à des <strong>défis majeurs</strong> en termes 
                de <strong>résilience des chaînes d’approvisionnement</strong>, de 
                <strong>l’état des infrastructures</strong>, et de <strong>l’accessibilité</strong>. 
                Ces difficultés sont exacerbées par des <strong>délais de réapprovisionnement</strong> 
                prolongés et des <strong>coûts de transport</strong> accrus, principalement dus à des 
                <strong>routes bloquées</strong> et à un <strong>climat d’insécurité</strong> résultant 
                de la présence de <strong>groupes armés</strong>.
                </p>
                <p style="margin-left: 30px; 
                        line-height: 1.4;">
                - Ces <strong>obstacles</strong> empêchent les <strong>livraisons régulières</strong> et 
                <strong>suffisantes</strong> de marchandises, réduisant la <strong>capacité</strong> de ces 
                marchés à répondre efficacement aux <strong>besoins</strong> des consommateurs locaux.
                </p>

                <!-- Subheading #4 -->
                <p style="font-weight: 700; 
                        font-size: 20px; 
                        margin-bottom: -5px;
                        font-family: 'Arial Narrow';">
                4. Importations
                </p>
                <p style="margin-left: 30px; 
                        margin-bottom: -5px; 
                        line-height: 1.4;">
                - La majorité des <strong>produits</strong> disponibles sur les <strong>marchés haïtiens</strong> 
                sont <strong>importés</strong> (71% en moyenne), principalement de la 
                <strong>République dominicaine</strong> (25% des <strong>IC</strong>), bien que 57% des 
                <strong>IC</strong> ne connaissent pas l’origine exacte.
                </p>
            """)

        # --- CYCLE 2 ---
        elif sel == "Cycle 2":
            return ui.HTML(f"""
                <!-- Main Title -->
                <div style="color: #ee5859;
                            font-size: 30px;
                            margin-bottom: -5px;
                            font-weight: 700;
                            font-family: 'Arial Narrow';">
                Résultats Clés - {sel}
                </div>

                <!-- Subheading #1 -->
                <p style="font-weight: 700; 
                        font-size: 20px;
                        margin-bottom: -5px;  
                        font-family: 'Arial Narrow';">
                1. Coût du MEB
                </p>
                <p style="margin-left: 30px;
                        margin-bottom: -5px; 
                        line-height: 1.2;">
                - Lors du <strong>cycle</strong> de <strong>décembre 2024</strong>, le 
                <strong>coût</strong> du <strong>MEB multisectoriel non-alimentaire</strong> pour la 
                <strong>crise prolongée</strong> était le plus élevé dans le département du <strong>Nord</strong>, 
                tandis que le département du <strong>Centre</strong> enregistrait le <strong>coût</strong> le 
                plus faible.
                </p>
                <p style="margin-left: 30px; 
                        line-height: 1.2;">
                - Pour le <strong>panier d’urgence</strong>, le <strong>coût</strong> le plus élevé a été relevé 
                dans le département du <strong>Sud</strong>, avec à l’inverse, le plus faible dans le 
                <strong>Centre</strong>. Ces <strong>variations régionales</strong> pourraient être influencées 
                par des <strong>défis logistiques</strong>, <strong>climatiques</strong> et 
                <strong>sécuritaires</strong>, qui impactent le <strong>transport</strong> et 
                l’<strong>accès</strong> aux marchandises.
                </p>

                <!-- Subheading #2 -->
                <p style="font-weight: 700;
                        margin-bottom: -5px;  
                        font-size: 20px; 
                        font-family: 'Arial Narrow';">
                2. Fonctionnalité des marchés
                </p>
                <p style="margin-left: 30px;
                        margin-bottom: -5px;  
                        line-height: 1.4;">
                - Notre étude sur la <strong>fonctionnalité des marchés</strong> indique, comme lors du 
                <strong>premier cycle</strong>, qu’aucun des <strong>marchés évalués</strong> ne remplit 
                complètement les critères de <strong>services</strong> et d’<strong>accès</strong> aux articles 
                nécessaires pour être considéré comme pleinement <strong>fonctionnel</strong>.
                </p>
                <p style="margin-left: 30px; 
                        line-height: 1.4;">
                - Néanmoins, certains <strong>marchés</strong> dans les <strong>Nippes</strong> et 
                l’<strong>Ouest</strong>, notamment à <strong>Fonds des Nègres</strong>, 
                <strong>Miragôane</strong> (déjà remarqué lors du <strong>premier cycle</strong>) et 
                <strong>Vialet</strong>, montrent des <strong>performances relativement meilleures</strong>, 
                même s’ils rencontrent toujours certaines <strong>difficultés</strong>.
                </p>

                <!-- Subheading #3 -->
                <p style="font-weight: 700; 
                        font-size: 20px; 
                        margin-bottom: -5px;
                        font-family: 'Arial Narrow';">
                3. Chaînes d’approvisionnement
                </p>
                <p style="margin-left: 30px; 
                        margin-bottom: -5px; 
                        line-height: 1.4;">
                - Les <strong>marchés</strong> d’<strong>Anse d’Hainault</strong>, 
                <strong>Saint Raphaël</strong>, <strong>Cap-Haïtien</strong> et <strong>Les Perches</strong> 
                rencontrent, une fois de plus, des <strong>défis importants</strong> en matière de 
                <strong>résilience des chaînes d’approvisionnement</strong>, de 
                <strong>qualité des infrastructures</strong> et d’<strong>accessibilité</strong>.
                </p>
                <p style="margin-left: 30px; 
                        line-height: 1.4;">
                - Comme lors du <strong>cycle 1</strong> en <strong>septembre 2024</strong>, 
                ces <strong>difficultés</strong> sont amplifiées par des 
                <strong>délais de réapprovisionnement prolongés</strong>, des 
                <strong>coûts de transport</strong> élevés et des <strong>options restreintes</strong>, 
                principalement en raison de <strong>routes bloquées</strong> ou endommagées et d’un 
                <strong>climat d’insécurité</strong> lié à la présence de <strong>groupes armés</strong>.
                </p>

                <!-- Subheading #4 -->
                <p style="font-weight: 700; 
                        font-size: 20px; 
                        margin-bottom: -5px;
                        font-family: 'Arial Narrow';">
                4. Importations
                </p>
                <p style="margin-left: 30px; 
                        margin-bottom: -5px; 
                        line-height: 1.4;">
                - La majorité des <strong>produits</strong> disponibles sur les 
                <strong>marchés haïtiens</strong> sont <strong>importés</strong> (63% en moyenne), 
                principalement de la <strong>République dominicaine</strong> (20% des <strong>IC</strong>), 
                bien que 59% des <strong>IC</strong> ne connaissent pas l’origine exacte.
                </p>
            """)

        # --- ANY OTHER CYCLE / DEFAULT ---
        else:
            return ui.HTML(f"""
                <div style="color: #ee5859;
                            font-size: 30px;
                            margin-bottom: 5px;
                            font-weight: 700;
                            font-family: 'Arial Narrow';">
                Résultats Clés - {sel}
                </div>
                <p>Veuillez sélectionner un cycle pris en charge pour afficher les résultats clés.</p>
            """)
