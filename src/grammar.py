#Definicion de la gramatica CFG

gramatica = {

    # Una oración completa
    "S": [
        ["S_NEUTRAL"],
        ["S_SENSACIONALISTA"]
    ],

    # Oraciones normales
    "S_NEUTRAL": [
        ["NP", "VP"],
        ["NP", "VP", "PUNC"]
    ],

    # Oraciones sensacionalistas
    "S_SENSACIONALISTA": [
        ["Signo_Ex_Abre", "NP", "VP", "Signo_Ex_Cierra"],
        ["Signo_Ex_Abre", "EXPRESION_ALARMISTA", "Signo_Ex_Cierra"],
        ["Signo_Ex_Abre", "NP", "VP", "PUNC", "Signo_Ex_Cierra"]
    ],

    # Frases nominales
    "NP": [
        ["Det", "N"],
        ["Det", "ADJ", "N"],
        ["N"]
    ],

    # Frases verbales
    "VP": [
        ["V", "NP"],
        ["V"],
        ["V", "ADJ"]
    ],

    # Expresiones alarmistas cortas
    "EXPRESION_ALARMISTA": [
        ["ADJ"],
        ["Det", "N", "V", "ADJ"]
    ],

    # Signos de puntuación
    "PUNC": [
        ["."],
        ["!"],
        ["?"]
    ],


    # Signos de exclamación
    "Signo_Ex_Abre": [ ["¡"] ],

    "Signo_Ex_Cierra": [ ["!"] ],

    # Signos de pregunta
    "Signo_Preg_Abre": [ ["¿"] ],

    "Signo_Preg_Cierra": [ ["?"] ],

    # Determinantes
    "Det": [
        ["el"], ["la"], ["los"], ["las"],
        ["un"], ["una"], ["unos"], ["unas"]
    ],

    # Adjetivos frecuentes en fake news
    "ADJ": [
        ["secreto"],
        ["peligroso"],
        ["mortal"],
        ["oculto"],
        ["ilegal"],
        ["viral"],
        ["alarmante"]
    ],

    # Sustantivos / entidades del dominio
    "N": [
        ["gobierno"], ["oms"], ["onu"],
        ["policía"], ["ejército"], ["presidente"],
        ["celebridad"], ["científicos"], ["expertos"],
        ["pueblo"], ["niños"], ["mujeres"],
        ["minorías"], ["migrantes"], ["vacuna"],
        ["virus"], ["crisis"], ["economía"],
        ["democracia"], ["china"], ["ee.uu."],
        ["europa"], ["latinoamérica"]
    ],

    # Verbos típicos del dominio
    "V": [
        ["alerta"], ["amenaza"], ["colapsa"],
        ["muere"], ["infecta"], ["descubren"],
        ["revelan"], ["filtran"], ["confirman"],
        ["prohíben"], ["ocultan"], ["censuran"],
        ["atacan"], ["provoca"], ["causa"],
        ["origina"]
    ]
}