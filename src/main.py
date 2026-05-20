from lexer import tokenize
from grammar import gramatica
from chart_parser import chart_parser


# Texto de prueba
texto = "¡el virus amenaza!"


# Tokenización
tokens = tokenize(texto)

print("========== TOKENS ==========\n")
print(tokens)
print()


# Parsing
arboles, chart = chart_parser(tokens, gramatica)


# Mostrar chart
print("========== CHART ==========\n")

for i, columna in enumerate(chart):

    print(f"Posición {i}:")

    for edge in columna:

        print(edge)

    print()


# Mostrar árboles encontrados
print("========== ÁRBOLES ==========\n")

if arboles:

    for i, arbol in enumerate(arboles):

        print(f"Árbol {i + 1}:\n")

        print(arbol)

else:

    print("No se encontraron derivaciones válidas.")