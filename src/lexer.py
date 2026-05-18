import re

def tokenize(text):
    """
    Recibe un string y devuelve una lista de tokens.
    Separa:
    - Palabras
    - Números
    - Signos de puntuación: ¡ ! ¿ ? . ,
    """

    # La expresión regular separa:
    # \d+              -> números
    # [A-Za-zÁÉÍÓÚáéíóúÑñ]+ -> palabras
    # [¡!¿?.,]         -> signos de puntuación
    pattern = r"\d+|[A-Za-zÁÉÍÓÚáéíóúÑñ]+|[¡!¿?.,]"

    # findall devuelve cada elemento encontrado como un token independiente
    tokens = re.findall(pattern, text)

    return tokens


# Prueba

# Texto 1: saludo simple
texto1 = "¡Hola! ¿Cómo estás?"
resultado1 = tokenize(texto1)
print(resultado1)
# Texto 2: números y puntuación
texto2 = "Tengo 2 perros, 1 gato y 3 peces."
resultado2 = tokenize(texto2)
print(resultado2)

# Texto 3: preguntas y exclamaciones
texto3 = "¿Qué hora es? ¡Son las 8!"
resultado3 = tokenize(texto3)
print(resultado3)

# Texto 4: varias comas y puntos
texto4 = "Python, Java, C++ y JavaScript son lenguajes populares."
resultado4 = tokenize(texto4)
print(resultado4)

# Texto 5: mezcla completa
texto5 = "¡Atención! El examen será el 25 de mayo, a las 7."
resultado5 = tokenize(texto5)
print(resultado5)

# Texto 6: texto más largo
texto6 = "Hola, hoy trabajaremos en el proyecto. ¿Ya terminaste tu parte? ¡Espero que sí!"
resultado6 = tokenize(texto6)
print(resultado6)

# Texto 7: múltiples signos seguidos
texto7 = "¿En serio?! ¡No lo puedo creer!"
resultado7 = tokenize(texto7)
print(resultado7)

# Texto 8: solo números
texto8 = "10 20 300 4500"
resultado8 = tokenize(texto8)
print(resultado8)

# Texto 9: texto corto
texto9 = "Hola."
resultado9 = tokenize(texto9)
print(resultado9)

# Texto 10: conversación simple
texto10 = "—Hola, Juan. ¿Cómo te fue en el parcial? —Bien, saqué 4."
resultado10 = tokenize(texto10)
print(resultado10)