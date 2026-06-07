# CFG Auténtica - Estructura sintáctica real del español
# Las reglas modelan estructura sintáctica, no categorías de sospecha

gramatica = {
    # Oración completa: NP (sujeto) + VP (predicado)
    "S": [
        ["NP", "VP"],
        ["NP", "VP", "PUNC"]
    ],

    # Frases nominales (sujeto/objeto)
    "NP": [
        ["Det", "N"],
        ["Det", "ADJ", "N"],
        ["N"],
        ["ADJ", "N"],
        ["N", "ADJ"],
        ["NP", "PREP", "NP"],
        ["Det", "N", "PP"],
        ["N", "PP"]
    ],

    # Frases verbales (predicado)
    "VP": [
        ["V", "NP"],
        ["V"],
        ["V", "NP", "PP"],
        ["VP", "PP"],
        ["V", "PP"],
        ["MODAL", "VP"],
        ["ADV_ABS", "VP"],
        ["VP", "FUENTE_INDEFINIDA"],
        ["V", "ADJ"]
    ],

    # Frases preposicionales (para ambigüedad de adjunción)
    "PP": [
        ["PREP", "NP"]
    ],

    # Preposiciones
    "PREP": [
        ["de"], ["en"], ["con"], ["sin"], ["para"], ["por"], ["sobre"], ["a"], ["al"]
    ],

    # Signos de puntuación
    "PUNC": [
        ["."], ["!"], ["?"]
    ],

    # Determinantes
    "Det": [
        ["el"], ["la"], ["los"], ["las"],
        ["un"], ["una"], ["unos"], ["unas"],
        ["al"], ["lo"]
    ],

    # Adjetivos
    "ADJ": [
        ["secreto"], ["peligroso"], ["mortal"], ["oculto"], ["ilegal"],
        ["viral"], ["alarmante"], ["falso"], ["cierto"], ["grave"],
        ["nuevas"], ["nuevo"], ["publico"], ["completo"],
        ["planos"], ["plana"], ["cercanas"]
    ],

    # Sustantivos / entidades del dominio
    "N": [
        ["gobierno"], ["oms"], ["onu"], ["policia"], ["ejercito"],
        ["presidente"], ["celebridad"], ["cientificos"], ["expertos"],
        ["pueblo"], ["ninos"], ["mujeres"], ["minorias"], ["migrantes"],
        ["vacuna"], ["virus"], ["crisis"], ["economia"], ["democracia"],
        ["china"], ["europa"], ["latinoamerica"], ["documento"], ["fuente"],
        ["noticia"], ["reportaje"], ["investigacion"],
        ["medicos"], ["medico"], ["personas"], ["mente"], ["hecho"],
        ["tierra"], ["nasa"], ["pruebas"], ["ano"], ["informacion"],
        ["ministerio"], ["salud"], ["informe"], ["martes"], ["ministra"],
        ["rueda"], ["prensa"], ["datos"], ["sitio"], ["web"], ["portal"],
        ["institucional"], ["periodista"], ["politico"], ["telescopio"],
        ["medidas"], ["detalles"], ["cientifico"], ["fuentes"],
        ["cientificos"], ["hombre"], ["mujer"], ["binoculares"],
        ["parque"],         ["camara"], ["cámara"]
    ],

    # Verbos típicos del dominio
    "V": [
        ["alerta"], ["amenaza"], ["colapsa"], ["muere"], ["infecta"],
        ["descubren"], ["revelan"], ["filtran"], ["confirman"],
        ["prohiben"], ["ocultan"], ["censuran"], ["atacan"], ["provoca"],
        ["causa"], ["origina"], ["afirma"], ["dice"], ["declara"],
        ["anuncio"], ["publico"], ["presento"], ["pueden"],
        ["vio"], ["admitieron"], ["compartelo"], ["borren"],
        ["oculto"], ["revelado"], ["esperaba"], ["existen"],
        ["es"], ["son"], ["fue"], ["esta"], ["habia"],
        ["ha"], ["puede"], ["pueden"], ["podria"], ["podrian"],
        ["tiene"], ["estan"], ["estaba"], ["vi"],
        ["anuncio"], ["anunció"], ["confirmó"], ["declaro"], ["declaró"],
        ["reportó"], ["oculta"], ["miente"], ["controlar"]
    ],

    # Modales - indican incertidumbre o hipótesis (Problema 5)
    "MODAL": [
        ["podria"], ["aparentemente"], ["posiblemente"], ["quizas"],
        ["supuestamente"], ["segun"], ["dicen"], ["parece"],
        ["tal", "vez"], ["podrian"], ["puede"]
    ],

    # Adverbios de afirmación absoluta (Problema 5)
    "ADV_ABS": [
        ["siempre"], ["nunca"], ["definitivamente"], ["absolutamente"],
        ["claramente"], ["obviamente"], ["evidentemente"],
        ["todos"], ["jamas"], ["nadie"]
    ],

    # Fuente indefinida (Problema 5)
    "FUENTE_INDEFINIDA": [
        ["segun", "fuentes"], ["se", "rumorea"], ["fuentes", "anonimas"],
        ["se", "dice"], ["informalmente"]
    ],

    # Conectores / complementantes
    "CONJ": [
        ["que"], ["y"], ["pero"], ["aunque"], ["porque"]
    ],

    # Palabras funcionales adicionales
    "FUNC": [
        ["se"], ["no"], ["lo"], ["le"], ["me"],
        ["te"], ["su"], ["sus"], ["tu"], ["mi"],
        ["mas"], ["ya"], ["esto"], ["eso"], ["esta"],
        ["este"], ["muy"], ["tan"], ["asi"], ["aqui"]
    ]
}