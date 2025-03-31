# modules/infos_pratiques.py

from shiny import ui

def infos_pratiques_ui():
    return ui.nav_panel(
        ui.tags.span(
            ui.tags.i(class_="fa fa-exclamation-circle icon"),  # Example icon
            " Infos Pratiques",
            class_="nav-panel-title"  # Added class
        ),
        ui.page_fillable(
            ui.layout_columns(
                # Column 1: Main Content
                ui.column(
                    11,
                    ui.p(
                        "Cette évaluation se définit comme étant quantitative, indicative et nationale avec pour but de garantir aux acteurs humanitaires l'accès aux informations sur le coût total du MEB et sur la disponibilité des articles de base sur les marchés de chaque zone évaluée. La collecte de données s'est réalisée en face-à-face auprès d'informateurs clés (IC) à travers neuf (9) départements du pays, sélectionnés selon la méthode d'échantillonnage « échantillon choisi ». Les IC sont des commerçants qui vendent les produits clés dans les marchés ciblés par cette évaluation afin de permettre de collecter des informations sur les prix et la disponibilité qui les concernent directement. Pour chaque département, deux (2) marchés ont été ciblés : un marché en milieu rural et un autre en milieu urbain.",
                        class_="justified-text"
                    ),
                    ui.p(
                        "La collecte a été assurée par des partenaires qui font des interventions dans les zones d'études.",
                        class_="justified-text"
                    ),
                    # Section 2: Limites méthodologiques
                    ui.h2("Limites méthodologiques"),
                    ui.p(
                        "Les données sur les prix sont indicatives et représentatives uniquement pour la période de collecte, sans permettre de suivre les variations continues.",
                        class_="justified-text"
                    ),
                    ui.p(
                        "Certains partenaires n’ont pas pu recueillir les quatre prix par article recommandés, limitant l’analyse des tendances des prix sur les marchés évalués.",
                        class_="justified-text"
                    ),
                    ui.p(
                        "Les articles relevés dans l’ICSM sont les moins chers disponibles, mais leur disponibilité varie selon les régions, ce qui peut entraîner des comparaisons entre produits légèrement différents.",
                        class_="justified-text"
                    ),
                    ui.p(
                        "Le coût médian national est basé sur les marchés couverts par l’évaluation, sans inclure l’ensemble des marchés existants dans le pays.",
                        class_="justified-text"
                    ),                              
                    ui.p(
                        "Les prix sont exprimés pour des quantités et unités prédéfinies, qui ne correspondent pas toujours aux pratiques des marchés locaux. Ainsi, la standardisation des unités est complexe pour certains articles (par exemple, le fil de ligature vendu au poids plutôt qu’à la longueur), introduisant des marges d’erreur.",
                        class_="justified-text"
                    ),          
                    # Section 3: cadre
                    ui.h2("Étude réalisée dans le cadre du :"),
                    ui.p(
                        "Groupe de Travail sur les Transferts Monétaires (GTTM), une plateforme d'échanges techniques qui associe de nombreuses institutions, parmi lesquelles des institutions gouvernementales, des prestataires de services financiers, des agences des Nations Unies, et des organisations non gouvernementales nationales et internationales. Ce groupe vise notamment à améliorer la qualité́ des transferts monétaires pour les populations les plus vulnérables en Haïti.",
                        class_="justified-text"
                    ),
                    class_="panel-margin-left",
                ),
                # Column 2: Contact, Publications, and Acknowledgements
                ui.column(
                    11,
                    ui.card(
                        # Contacts Section
                        ui.div(
                            ui.h4("Contacts"),
                            ui.p("Pour toute question concernant le projet, veuillez contacter l'un des collègues suivants :"),
                            ui.tags.ul(
                                ui.tags.li(
                                    ui.tags.a(
                                        "Amine Bahri - Research Manager",
                                        href="mailto:amine.bahri@impact-initiatives.org",
                                        target="_blank",
                                        class_="publication-link"
                                    )
                                ),
                                ui.p("amine.bahri@impact-initiatives.org"),
                                ui.tags.li(
                                    ui.tags.a(
                                        "Juliette GRAF - Senior Assessment Officer",
                                        href="mailto:juliette.graf@impact-initiatives.org",
                                        target="_blank",
                                        class_="publication-link"
                                    )
                                ),
                                ui.p("juliette.graf@impact-initiatives.org"),

                            ),                            
                            class_="contacts-section",  # Only one class per ui.div
                        ),
                        # Publications Section
                        ui.div(
                            ui.h4("Publications"),
                            ui.p("Vous trouverez toutes les ressources du projet MSNA en Haiti sur ",
                                    ui.tags.a(
                                    "cette page ci",
                                    href = "https://www.impact-initiatives.org/resource-centre/?category[]=data_methods&location[]=111&programme[]=756&order=latest&limit=10",
                                    target = "_blank",
                                    class_ = "publication-link"    # Add the class here
                                    ),
                                    ". Parmi les résultats, on trouve des fiches d'information et des présentations sectorielles et par département."
                                ),
                                ui.p(
                                    "En particulier, ce tableau de bord utilise les informations et les données provenant des ressources suivantes :"
                                ),
                            ui.tags.ul(
                                ui.tags.li(
                                    ui.tags.a(
                                        "1. Termes de référence",
                                        href="https://repository.impact-initiatives.org/document/impact/63f043de/HTI_ICSM_TDR_2024.pdf",
                                        target="_blank",
                                        class_="publication-link"
                                    )
                                ),
                                ui.tags.li(
                                    ui.tags.a(
                                        "2. Note méthodologique",
                                        href="https://repository.impact-initiatives.org/document/reach/40ba2413/REACH_HTI2301_Note-Methodologique_2023.pdf",
                                        target="_blank",
                                        class_="publication-link"
                                    )
                                ),
                                ui.tags.li(
                                    ui.tags.a(
                                        "3. Rapport MEB non-alimentaire et calcul de valeur de transfert",
                                        href="https://repository.impact-initiatives.org/document/impact/55b93b59/HTI2404_ICSM_Novembre2024-1.pdf",
                                        target="_blank",
                                        class_="publication-link"
                                    )
                                ),
                                ui.tags.li(
                                    ui.tags.a(
                                        "4. Note d’orientation des valeurs de transfert monétaire en Haïti, basée sur l’ICSM de novembre 2023",
                                        href="https://repository.impact-initiatives.org/document/impact/dafea594/REACH_Haiti_Note-dorientation_Valeur-de-Transfert_Avril-2024.pdf",
                                        target="_blank",
                                        class_="publication-link"
                                    )
                                ),                                
                                ui.tags.li(
                                    ui.tags.a(
                                        "5. Tableau des résultats en Excel",
                                        href="https://repository.impact-initiatives.org/document/impact/37e847a4/2024-10-30-HTI2404-Clean-Data-analyse-MEB-ICSM-final-update.xlsx",
                                        target="_blank",
                                        class_="publication-link"
                                    )
                                ),
                            ),
                            class_="publication-section",  # Only one class per ui.div
                        ),
                        # Remerciements Section
                        ui.div(
                            ui.h4("Remerciements"),
                            ui.tags.b("En collaboration avec :"),
                            ui.HTML(
                                """
                                <div style="margin-bottom: 20px; margin-top: 5px;">
                                    <img src="Logos/OCHA.png" 
                                        alt="OCHA" 
                                        style="width: 22%; height: auto; display: inline-block; margin-right: 20px;">
                                    <img src="Logos/WFP.png" 
                                        alt="WFP" 
                                        style="width: 22%; height: auto; display: inline-block; margin-right: 10px;">
                                </div>
                                """
                            ),
                            ui.tags.b("Financée par :"),
                            ui.HTML(
                                """
                                <div style="margin-bottom: 20px; margin-top: 15px;">
                                    <img src="Logos/ECHO.png" 
                                        alt="ECHO" 
                                        style="width: 22%; height: auto; display: inline-block; margin-right: 10px;">
                                </div>
                                """
                            ),
                            ui.tags.b("Avec le soutien opérationnel de :"),
                            ui.HTML(
                                """
                                <div style="margin-bottom: 20px; margin-top: 10px;">
                                    <img src="Logos/ACTED.png" 
                                        alt="ACTED" 
                                        style="width: 20%; height: auto; display: inline-block; margin-right: 10px;">
                                    <img src="Logos/AVSI.png" 
                                        alt="AVSI" 
                                        style="width: 15%; height: auto; display: inline-block; margin-right: 10px;">
                                    <img src="Logos/CONCERN.png" 
                                        alt="CONCERN" 
                                        style="width: 20%; height: auto; display: inline-block; margin-right: 10px;">
                                    <img src="Logos/whh.png" 
                                        alt="WHH" 
                                        style="width: 18%; height: auto; display: inline-block; margin-right: 10px;">                                        
                                </div>
                                """
                            ),                          
                            class_="acknowledgements-section" 
                        ),
                        class_="contacts-card"
                    ),
                ),
            )
        )
    )
def infos_pratiques_server(input, output, session):
    # Static rendering of the coverage map image
    pass  # Since ui.HTML is handling the image, no server-side processing is needed here
