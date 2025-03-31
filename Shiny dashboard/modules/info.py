from shiny import ui, reactive
from shiny.ui import tags, modal, modal_show

def info_modal():
    return modal_show(
        modal(
            tags.strong(tags.h1("Initiative Conjointe de Suivi des Marchés (ICSM) 2024")),
            tags.h2("Présentation du tableau de bord"),
            tags.hr(),
            tags.p("Ce tableau de bord est composé des pages et sous-pages suivantes :"),

            tags.ul(
                tags.li(
                    tags.strong("1. À Propos : ", class_="info-tab-title"),
                    tags.br(),  # Line break after the title
                    "Cette section contextualise l'évaluation et présente la méthodologie, la période de collecte, ",
                    "ainsi que les résultats clés et la localisation des marchés évalués."
                ),
                tags.li(
                    tags.strong("2. Prix des Produits : ", class_="info-tab-title"),
                    tags.br(),
                    "Ici, vous pouvez consulter en détail les prix médians des différents produits. ",
                    "Vous pourrez choisir le secteur et le niveau géographique afin de visualiser un tableau récapitulant les prix par produit."
                ),
                tags.li(
                    tags.strong("3. MEB : ", class_="info-tab-title"),
                    tags.br(),
                    "Cette section est dédiée au Minimum Expenditure Basket (MEB) non-alimentaire. Elle se décline en deux sous-pages :",
                    tags.ul(
                        tags.li(
                            tags.strong("3.1. Produits du MEB : ", class_="info-tab-title"),
                            tags.br(),
                            "Visualisez les produits composants le MEB en fonction du type de crise ",
                            "et du secteur sélectionnés. Vous accéderez à un tableau listant les produits et leurs valeurs."
                        ),
                        tags.li(
                            tags.strong("3.2. Coût du MEB par Secteurs : ", class_="info-tab-title"),
                            tags.br(),
                            "Consultez le coût global du MEB par secteur et par niveau géographique, ",
                            "ainsi que dans la monnaie de votre choix. Vous trouverez un tableau permettant de comparer les coûts entre différentes zones et types de crises."
                        ),
                        class_="info-list"
                    )
                ),
                tags.li(
                    tags.strong("4. Indicateurs non tarifaire : ", class_="info-tab-title"),
                    tags.br(),
                    "Cette section regroupe plusieurs indicateurs qualitatifs relatifs au fonctionnement des marchés. ",
                    "Elle est subdivisée en trois sous-pages :",
                    tags.ul(
                        tags.li(
                            tags.strong("4.1. Stock et réapprovisionnement : ", class_="info-tab-title"),
                            tags.br(),
                            "Affichez et analysez les données sur la disponibilité des stocks, ",
                            "les difficultés de réapprovisionnement et les raisons potentielles des ruptures."
                        ),
                        tags.li(
                            tags.strong("4.2. Disponibilité et origine de produits : ", class_="info-tab-title"),
                            tags.br(),
                            "Observez l’origine des produits (importés ou locaux) et leur disponibilité sur les marchés. ",
                            "Cela permet d’évaluer la résilience des chaînes d’approvisionnement."
                        ),
                        tags.li(
                            tags.strong("4.3. Fonctionnalité des marchés : ", class_="info-tab-title"),
                            tags.br(),
                            "Explorez des indicateurs illustrant la facilité ou la difficulté d’accès aux marchés, ",
                            "leur fonctionnement global, et tout autre facteur influençant leur performance."
                        ),
                        class_="info-list"
                    )
                ),
                tags.li(
                    tags.strong("5. Score de Fonctionnalité des marchés : ", class_="info-tab-title"),
                    tags.br(),
                    "Cette page propose une visualisation cartographique vous permettant de consulter ",
                    "et de comparer les indicateurs de fonctionnalité à travers différentes régions. ",
                    "Choisissez un indicateur pour afficher une carte interactive reflétant la classification de la fonctionnalité des marchés."
                ),
                tags.li(
                    tags.strong("6. Infos Pratiques : ", class_="info-tab-title"),
                    tags.br(),
                    "Cette dernière page fournit des informations complémentaires, notamment sur la méthodologie, ",
                    "les limites de l’étude, les contacts, les ressources publiées, et les remerciements envers les partenaires et bailleurs de fonds."
                ),
                class_="info-list"
            ),
            ui.HTML(
                """
                <img src="images/market.jpg" 
                     alt="market" 
                     style="width: 50%; height: auto; display: block; margin: 0 auto; margin-bottom: 10px;">
                """
            ),       
            size="l",
            easy_close=True,
            footer=ui.modal_button("Fermer"),
        )
    )
