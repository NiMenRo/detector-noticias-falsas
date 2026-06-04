# ============================================================
# clases.py  |  Clases 9 y 10 — Introducción al PLN
# Ambigüedad Léxica y Sintáctica + Modelos Probabilísticos
# Universidad del Valle — Luz Carime Lucumí Hernández
# ============================================================

# Tres módulos que necesitamos:
#   re          → tokenizar oraciones con expresiones regulares
#   heapq       → cola de prioridad para el best-first parsing
#   defaultdict → construir conteos desde corpus sin errores de llave
import re
import heapq
from collections import defaultdict


# ============================================================
# PARTE 1: Léxico ambiguo
# Base de la Clase 9. También lo usaremos en la Clase 10
# para construir las reglas léxicas de la gramática probabilística.
# ============================================================

lexico_ambiguo = {

    # Determinantes: una sola categoría posible, sin ambigüedad.
    "la": ["Det"], "el": ["Det"], "las": ["Det"], "los": ["Det"],

    # Sustantivos no ambiguos: siempre son N sin importar el contexto.
    "estudiante": ["N"], "libro":  ["N"], "papas": ["N"],
    "profesor":   ["N"], "medico": ["N"], "banco": ["N"],
    "gato":       ["N"],

    # pelo → N: 'tiene el pelo largo'
    # pelo → V: 'yo pelo la naranja' (primera persona de pelar)
    "pelo": ["N", "V"],

    # nota → N: nota musical / calificación / apunte
    # nota → V: 'ella nota el error' (tercera persona de notar)
    # Única palabra con ambigüedad categorial Y de sentido a la vez.
    "nota": ["N", "V"],

    # sobre → N: 'escribe la dirección en el sobre'
    # sobre → V: 'el agua sobre el punto de ebullición' (superar)
    # sobre → Prep: 'el libro está sobre la mesa'
    # El caso más interesante: tres categorías distintas.
    "sobre": ["N", "V", "Prep"],

    # como → V: 'yo como arroz' (primera persona de comer)
    # como → Conj: 'tan rápido como el viento'
    "como": ["V", "Conj"],

    # bajo → Adj: 'el techo es muy bajo'
    # bajo → V: 'bajo las escaleras corriendo' (primera persona de bajar)
    # bajo → Prep: 'estaba bajo la lluvia'
    "bajo": ["Adj", "V", "Prep"],

    # Verbos que también usaremos en la gramática de la Clase 10.
    "lee": ["V"], "ve": ["V"],
}


# ============================================================
# PARTE 2: Funciones de detección (Clase 9)
# ============================================================

def categorias(token):
    # Retorna la lista de categorías posibles para una palabra.
    # Si la palabra no está en el léxico, retorna lista vacía sin error.
    return lexico_ambiguo.get(token, [])

def es_ambiguo(token):
    # Una palabra es ambigua si puede tener más de una categoría.
    return len(categorias(token)) > 1

def detectar_ambiguedad(oracion):
    # Convierte a minúsculas y usa regex para manejar puntuación:
    # 'banco,' se convierte en 'banco' antes de buscarlo en el léxico.
    tokens = re.findall(r'\b\w+\b', oracion.lower())
    # Solo retornamos los tokens que son ambiguos con sus categorías.
    return [(t, categorias(t)) for t in tokens if es_ambiguo(t)]

# Prueba: tres palabras ambiguas en una sola oración.
print(detectar_ambiguedad("el pelo como el libro sobre la mesa"))
# [('pelo', ['N', 'V']), ('como', ['V', 'Conj']), ('sobre', ['N', 'V', 'Prep'])]
# 'el', 'libro' y 'la' no aparecen porque no son ambiguos.


# ============================================================
# PARTE 3: Frecuencias y probabilidades (Clase 9)
# Las frecuencias se cargan desde corpus_ambiguo.txt.
# Si el archivo no existe, se usan los valores por defecto.
# Para el proyecto: reemplacen corpus_ambiguo.txt con sus
# propias palabras ambiguas y sus frecuencias de dominio.
# ============================================================

def construir_frecuencias(ruta_corpus):
    # Lee corpus_ambiguo.txt y cuenta cuántas veces aparece
    # cada palabra con cada categoría gramatical.
    #
    # defaultdict anidado: evita verificar si la llave existe.
    # conteos['pelo']['N'] += 1 funciona aunque 'pelo' no haya
    # sido visto antes — el contador empieza en 0 automáticamente.
    conteos = defaultdict(lambda: defaultdict(int))

    with open(ruta_corpus, encoding="utf-8") as f:
        for linea in f:
            linea = linea.strip()
            if not linea or linea.startswith("#"):
                continue
            partes = linea.split()
            if len(partes) == 2:
                palabra, categoria = partes
                conteos[palabra.lower()][categoria] += 1

    return {palabra: dict(cats) for palabra, cats in conteos.items()}


# Valores por defecto equivalentes al corpus pero hardcodeados.
# Se usan si corpus_ambiguo.txt no está disponible.
frecuencias_default = {
    "pelo":  {"N": 300, "V": 50},           # 86% N
    "nota":  {"N": 380, "V": 70},           # 84% N
    "sobre": {"Prep": 400, "N": 50, "V": 10},  # 87% Prep
    "como":  {"V": 150, "Conj": 100},          # 60% V
}

try:
    frecuencias = construir_frecuencias("corpus_ambiguo.txt")
    print("Frecuencias cargadas desde corpus_ambiguo.txt")
except FileNotFoundError:
    frecuencias = frecuencias_default
    print("corpus_ambiguo.txt no encontrado — usando frecuencias por defecto.")


def prob_categoria(palabra, categoria):
    # Si la palabra no tiene frecuencias registradas, no tenemos
    # datos para calcular — retornamos 0.0.
    if palabra not in frecuencias:
        return 0.0
    conteos = frecuencias[palabra]
    # Frecuencia de esta categoría dividida entre el total de apariciones.
    return conteos.get(categoria, 0) / sum(conteos.values())

def categoria_mas_probable(palabra):
    # Sin frecuencias, usamos el primer elemento del léxico como fallback.
    if palabra not in frecuencias:
        cats = categorias(palabra)
        return cats[0] if cats else None
    # max() con key=dict.get retorna la categoría con el conteo más alto.
    return max(frecuencias[palabra], key=frecuencias[palabra].get)


print(prob_categoria("pelo",  "N"))    # ≈ 0.86
print(prob_categoria("pelo",  "V"))    # ≈ 0.14
print(categoria_mas_probable("nota"))  # 'N'
print(categoria_mas_probable("sobre")) # 'Prep'


# ============================================================
# PARTE 4: Desambiguador completo (Clase 9)
# ============================================================

def desambiguar(oracion):
    print(f"\nOración: '{oracion}'")
    for token in re.findall(r'\b\w+\b', oracion.lower()):
        if es_ambiguo(token):
            cat = categoria_mas_probable(token)
            p   = prob_categoria(token, cat)
            print(f"  {token:10s} -> {cat:6s}  (P={p:.2f})  *ambiguo*")
        elif categorias(token):
            print(f"  {token:10s} -> {categorias(token)[0]}")
        else:
            print(f"  {token:10s} -> DESCONOCIDO")


# Caso fácil: 'sobre' es preposición → el sistema acierta.
desambiguar("deje el libro sobre la mesa")

# Caso difícil: 'pelo' ES verbo aquí (primera persona de pelar),
# pero el sistema elige N porque N es más frecuente en el corpus.
# Falla porque ignora que 'yo' antes de 'pelo' señala un verbo.
# Eso es exactamente lo que resuelven modelos como BERT:
# leen el contexto completo, no solo la palabra aislada.
desambiguar("yo pelo la naranja para el jugo")


# ============================================================
# PARTE 5: Estadísticas de ambigüedad (Clase 9)
# ============================================================

def estadisticas(oracion):
    tokens       = re.findall(r'\b\w+\b', oracion.lower())
    ambiguos     = [t for t in tokens if es_ambiguo(t)]
    desconocidos = [t for t in tokens if not categorias(t)]
    conocidos    = [t for t in tokens if categorias(t) and not es_ambiguo(t)]

    print(f"\nEstadísticas para: '{oracion}'")
    print(f"  Total tokens:   {len(tokens)}")
    print(f"  No ambiguos:    {len(conocidos):3d}  ({100*len(conocidos)/len(tokens):.0f}%)")
    print(f"  Ambiguos:       {len(ambiguos):3d}  ({100*len(ambiguos)/len(tokens):.0f}%)")
    print(f"  Desconocidos:   {len(desconocidos):3d}  ({100*len(desconocidos)/len(tokens):.0f}%)")


estadisticas("el pelo como el libro sobre la mesa")


# ============================================================
# ── CLASE 10 ─────────────────────────────────────────────────
# ============================================================

# Hasta aquí la Clase 9: desambiguamos palabras individuales.
# La Clase 10 extiende esa idea a oraciones completas.
# Ya no preguntamos '¿qué categoría tiene esta palabra?'
# sino '¿cuál de los árboles posibles para esta oración es el correcto?'
# Respuesta: el árbol con mayor probabilidad.


# ============================================================
# PARTE 6: Estimación de gramática desde corpus (Clase 10)
# Hacemos con las reglas sintácticas lo mismo que hicimos
# en la Clase 9 con las palabras: contamos y calculamos probabilidades.
# ============================================================

def estimar_gramatica_desde_corpus(ruta_corpus):
    # Lee corpus_PCFG.txt y cuenta cuántas veces se usó
    # cada regla al analizar las oraciones del dominio.
    conteos = defaultdict(lambda: defaultdict(int))

    with open(ruta_corpus, encoding="utf-8") as f:
        for linea in f:
            linea = linea.strip()
            if not linea or linea.startswith("#"):
                continue
            partes = linea.split()
            if len(partes) < 2:
                continue
            lhs = partes[0]
            rhs = tuple(partes[1:])
            conteos[lhs][rhs] += 1

    # Divide cada conteo entre el total de su símbolo para obtener
    # probabilidades. Ordena de mayor a menor: el best-first intentará
    # primero las reglas más frecuentes, lo que mejora su eficiencia.
    gramatica_estimada = {}
    for lhs, rhs_counts in conteos.items():
        total = sum(rhs_counts.values())
        gramatica_estimada[lhs] = sorted(
            [(rhs, round(count / total, 4)) for rhs, count in rhs_counts.items()],
            key=lambda x: -x[1]
        )
    return gramatica_estimada


def mostrar_gramatica(gram, titulo="Gramática"):
    # Imprime cada regla con su probabilidad y verifica que sumen 1.
    print(f"\n=== {titulo} ===")
    for lhs, producciones in gram.items():
        suma = sum(p for _, p in producciones)
        print(f"  {lhs}  (suma={suma:.2f}):")
        for rhs, prob in producciones:
            print(f"    → {' '.join(rhs):20s}  [{prob:.4f}]")


def comparar_gramaticas(gram_default, gram_corpus):
    # Muestra lado a lado las probabilidades por defecto y las del corpus.
    # Útil para ver cuánto difieren los supuestos iniciales de los datos reales.
    print("\n=== Comparación: gramática por defecto vs corpus ===")
    simbolos = set(gram_default) | set(gram_corpus)
    for lhs in sorted(simbolos):
        prods_default = {rhs: p for rhs, p in gram_default.get(lhs, [])}
        prods_corpus  = {rhs: p for rhs, p in gram_corpus.get(lhs, [])}
        rhs_todas     = set(prods_default) | set(prods_corpus)
        print(f"\n  {lhs}:")
        for rhs in sorted(rhs_todas):
            rhs_str    = " ".join(rhs)
            p_default  = prods_default.get(rhs, 0.0)
            p_corpus   = prods_corpus.get(rhs, 0.0)
            diferencia = p_corpus - p_default
            signo = "↑" if diferencia > 0.01 else "↓" if diferencia < -0.01 else "="
            print(f"    → {rhs_str:20s}  default={p_default:.2f}  corpus={p_corpus:.2f}  {signo}")


# ============================================================
# PARTE 6b: La gramática probabilística (PCFG)
# Se carga desde corpus_PCFG.txt. Si no existe, se usa
# la gramática por defecto con probabilidades ilustrativas.
# Para el proyecto: reemplacen corpus_PCFG.txt con las reglas
# de las oraciones de su propio dominio.
# ============================================================

# Gramática por defecto — probabilidades ilustrativas.
gramatica_default = {

    # S siempre es NP VP en esta gramática → probabilidad 1.0.
    "S":   [(("NP", "VP"),    1.0)],

    # NP con artículo ocurre el 70%, sin artículo el 30%. Suma: 1.0 ✓
    "NP":  [(("Det", "N"),   0.7),
            (("N",),          0.3)],

    # VP transitivo (con objeto) 60%, intransitivo 40%. Suma: 1.0 ✓
    "VP":  [(("V",  "NP"),   0.6),
            (("V",),          0.4)],

    # 'el' y 'la' son equiprobables en este corpus. Suma: 1.0 ✓
    "Det": [(("el",),         0.5),
            (("la",),         0.5)],

    # 'estudiante' es el sustantivo más frecuente. Suma: 1.0 ✓
    "N":   [(("estudiante",), 0.4),
            (("libro",),      0.3),
            (("gato",),       0.3)],

    # 'lee' más frecuente que 've'. Suma: 1.0 ✓
    "V":   [(("lee",),        0.6),
            (("ve",),         0.4)],
}

try:
    gramatica = estimar_gramatica_desde_corpus("corpus_PCFG.txt")
    print("\nGramática estimada desde corpus_PCFG.txt")
    mostrar_gramatica(gramatica, "Gramática desde corpus")
    comparar_gramaticas(gramatica_default, gramatica)
except FileNotFoundError:
    gramatica = gramatica_default
    print("\ncorpus_PCFG.txt no encontrado — usando gramática por defecto.")
    mostrar_gramatica(gramatica, "Gramática por defecto")


# ============================================================
# PARTE 7: Probabilidad de una regla
# ============================================================

def prob_regla(lhs, rhs):
    # Busca la regla lhs → rhs en la gramática y retorna su probabilidad.
    # Si lhs no existe (es un terminal como 'el' o 'lee'), retorna 0.0.
    for produccion, prob in gramatica.get(lhs, []):
        if produccion == tuple(rhs):
            return prob
    return 0.0


print("\n=== Verificación de reglas ===")
print(prob_regla("NP",  ("Det", "N")))  # según corpus o default
print(prob_regla("VP",  ("V",)))
print(prob_regla("Det", ("el",)))
print(prob_regla("N",   ("libro",)))
print(prob_regla("S",   ("VP",)))       # 0.0 — regla que no existe


# ============================================================
# PARTE 8: Probabilidad de un árbol completo
# P(árbol) = producto de P(r) para cada regla r usada en el árbol.
# Se calcula recursivamente: P(nodo) = P(su regla) × P(cada hijo).
#
# Los árboles se representan como tuplas anidadas:
#   nodo no-terminal → (símbolo, hijo1, hijo2, ...)
#   nodo terminal    → string dentro de su padre
#
# Ejemplo: ('NP', ('Det', 'el'), ('N', 'libro'))
#               NP
#              /  \
#            Det    N
#             |     |
#            el   libro
# ============================================================

def prob_arbol(arbol):
    simbolo = arbol[0]
    hijos   = arbol[1:]

    # Construimos la tupla RHS con los símbolos de los hijos
    # para poder buscar la regla en la gramática.
    rhs = []
    for h in hijos:
        if isinstance(h, str):
            rhs.append(h)
        else:
            rhs.append(h[0])  # primer elemento de la tupla = símbolo raíz del hijo
    rhs = tuple(rhs)

    p = prob_regla(simbolo, rhs)

    # Multiplicamos recursivamente por la probabilidad de cada subárbol.
    for hijo in hijos:
        if isinstance(hijo, tuple):
            p *= prob_arbol(hijo)
    return p


print("\n=== Cálculo de P(árbol) ===")

# P(el estudiante lee):
# S→NP VP: 1.0 | NP→Det N: 0.7 | Det→el: 0.5 | N→estudiante: 0.4
# VP→V: 0.4 | V→lee: 0.6
# Total = 1.0 × 0.7 × 0.5 × 0.4 × 0.4 × 0.6 = 0.033600
arbol_intrans = ("S",
    ("NP", ("Det", "el"), ("N", "estudiante")),
    ("VP", ("V", "lee")))
print(f"P(el estudiante lee)         = {prob_arbol(arbol_intrans):.6f}")

# P(el estudiante lee el libro):
# Mismas reglas anteriores + VP→V NP: 0.6 | NP→Det N: 0.7 | Det→el: 0.5 | N→libro: 0.3
# Total = 1.0 × 0.7 × 0.5 × 0.4 × 0.6 × 0.6 × 0.7 × 0.5 × 0.3 = 0.005292
arbol_trans = ("S",
    ("NP", ("Det", "el"), ("N", "estudiante")),
    ("VP", ("V",   "lee"),
           ("NP",  ("Det", "el"), ("N", "libro"))))
print(f"P(el estudiante lee el libro)= {prob_arbol(arbol_trans):.6f}")


# ============================================================
# PARTE 9: Elegir el mejor árbol
# ============================================================

def mejor_arbol(arboles):
    # max() con key=prob_arbol calcula la probabilidad de cada árbol
    # y retorna el que tenga el valor más alto.
    return max(arboles, key=prob_arbol)


def reglas_del_arbol(arbol):
    # Recorre el árbol recursivamente y retorna una lista de
    # (lhs, rhs_str, prob) para cada regla usada.
    reglas = []
    simbolo = arbol[0]
    hijos   = arbol[1:]
    rhs     = tuple(h if isinstance(h, str) else h[0] for h in hijos)
    p       = prob_regla(simbolo, rhs)
    reglas.append((simbolo, " ".join(rhs), p))
    for hijo in hijos:
        if isinstance(hijo, tuple):
            reglas.extend(reglas_del_arbol(hijo))
    return reglas


def mostrar_comparacion(nombre_A, arbol_a, nombre_B, arbol_b):
    reglas_a = reglas_del_arbol(arbol_a)
    reglas_b = reglas_del_arbol(arbol_b)
    pa = prob_arbol(arbol_a)
    pb = prob_arbol(arbol_b)

    # Encuentra las reglas que difieren entre A y B para resaltarlas.
    set_a = set((l, r) for l, r, _ in reglas_a)
    set_b = set((l, r) for l, r, _ in reglas_b)
    solo_en_a = set_a - set_b
    solo_en_b = set_b - set_a

    print(f"\n  {nombre_A}:")
    for lhs, rhs, p in reglas_a:
        marca = "  <-- regla distinta" if (lhs, rhs) in solo_en_a else ""
        print(f"    {lhs:4s} → {rhs:20s}  [{p:.2f}]{marca}")
    print(f"    {'':4s}   {'P(árbol)':20s}= {pa:.6f}")

    print(f"\n  {nombre_B}:")
    for lhs, rhs, p in reglas_b:
        marca = "  <-- regla distinta" if (lhs, rhs) in solo_en_b else ""
        print(f"    {lhs:4s} → {rhs:20s}  [{p:.2f}]{marca}")
    print(f"    {'':4s}   {'P(árbol)':20s}= {pb:.6f}")

    ganador = mejor_arbol([arbol_a, arbol_b])
    nombre_ganador = nombre_A if ganador is arbol_a else nombre_B
    print(f"\n  Ganador: {nombre_ganador}  (P={max(pa, pb):.6f})")


print("\n=== Eligiendo entre dos árboles ambiguos ===")
print("Oración: 'el estudiante lee el libro'")
print("¿El sujeto lleva artículo o no?\n")

arbol_A = ("S",
    ("NP", ("Det", "el"), ("N", "estudiante")),
    ("VP", ("V", "lee"),
           ("NP", ("Det", "el"), ("N", "libro"))))

# Árbol B: sujeto sin artículo → usa NP→N (prob 0.3) en lugar de NP→Det N (prob 0.7).
arbol_B = ("S",
    ("NP", ("N", "estudiante")),
    ("VP", ("V", "lee"),
           ("NP", ("Det", "el"), ("N", "libro"))))

mostrar_comparacion(
    "Árbol A — sujeto CON artículo  (el estudiante)", arbol_A,
    "Árbol B — sujeto SIN artículo  (estudiante)",    arbol_B
)


# ============================================================
# PARTE 10: Best-first parsing
# Hasta ahora construimos árboles a mano y los comparamos.
# En la práctica hay que BUSCAR el mejor árbol automáticamente.
# Best-first siempre expande el estado más prometedor primero
# y se detiene en cuanto encuentra un parse completo,
# garantizando que ese parse es el más probable.
# ============================================================

def best_first_parse(tokens, gram):

    # Los estados en la cola deben ser inmutables → convertimos a tupla.
    tokens = tuple(tokens)

    # Cada estado tiene tres componentes:
    #   neg_prob   → probabilidad negada (heapq es min-heap; negamos para simular max-heap)
    #   pendientes → símbolos que todavía hay que expandir o hacer match
    #   restantes  → tokens de la oración que aún no se han consumido
    estado_inicial = (-1.0, ("S",), tokens)
    cola  = [estado_inicial]
    pasos = 0

    while cola:
        pasos += 1

        # heapq.heappop extrae el elemento de menor valor.
        # Como usamos probabilidad negada, menor valor = mayor probabilidad real.
        neg_prob, pendientes, restantes = heapq.heappop(cola)
        prob = -neg_prob

        # Condición de éxito: no quedan símbolos ni tokens → parse completo.
        if not pendientes and not restantes:
            print(f"  Parse encontrado en {pasos} pasos. P = {prob:.6f}")
            return prob

        if not pendientes:
            continue

        actual = pendientes[0]
        resto  = pendientes[1:]

        # Si el símbolo actual no está en la gramática, es un terminal.
        # Solo avanzamos si coincide exactamente con el siguiente token.
        if actual not in gram:
            if restantes and restantes[0] == actual:
                heapq.heappush(cola, (-prob, resto, restantes[1:]))
            continue

        # Si es un no-terminal, lo expandimos con cada producción posible.
        # Cada expansión genera un nuevo estado con probabilidad acumulada.
        for produccion, p_regla in gram[actual]:
            nueva_prob  = prob * p_regla
            nuevos_pend = produccion + resto
            heapq.heappush(cola, (-nueva_prob, nuevos_pend, restantes))

    print("  No se encontró parse válido.")
    return 0.0


# ============================================================
# PARTE 11: Demostración del best-first
# ============================================================

print("\n=== Best-first parsing ===")

print("Oración 1: 'el estudiante lee el libro'")
p1 = best_first_parse(["el", "estudiante", "lee", "el", "libro"], gramatica)

print("\nOración 2: 'la estudiante ve el gato'")
p2 = best_first_parse(["la", "estudiante", "ve", "el", "gato"], gramatica)

print("\nOración 3: 'el gato ve el libro'")
p3 = best_first_parse(["el", "gato", "ve", "el", "libro"], gramatica)

# 'corre' no está en la gramática → el parser no encontrará parse válido.
print("\nOración 4: 'el estudiante corre' (token inválido)")
p4 = best_first_parse(["el", "estudiante", "corre"], gramatica)

print("\n=== Comparación de probabilidades ===")
oraciones = [
    ("el estudiante lee el libro", p1),
    ("la estudiante ve el gato",   p2),
    ("el gato ve el libro",        p3),
]
oraciones.sort(key=lambda x: x[1], reverse=True)
for texto, p in oraciones:
    print(f"  P = {p:.6f}  ← {texto}")


# ============================================================
# PARTE 12: Conexión Clase 9 → Clase 10
# En Clase 9: P(categoría | palabra) — desambiguación léxica.
# En Clase 10: P(árbol) = ∏ P(regla) — desambiguación sintáctica.
# Aquí mostramos que son el mismo mecanismo a distinta escala.
# ============================================================

print("\n=== Conexión Clase 9 → Clase 10 ===")

def frecuencias_a_pcfg(palabra, conteos):
    # Convierte el diccionario de conteos de una palabra
    # al formato (producción, probabilidad) que usa la gramática.
    total = sum(conteos.values())
    return [((cat,), count / total) for cat, count in conteos.items()]


for palabra in ["pelo", "nota"]:
    reglas = frecuencias_a_pcfg(palabra, frecuencias[palabra])
    print(f"\nReglas PCFG para '{palabra}':")
    for produccion, prob in reglas:
        print(f"  {palabra} → {produccion[0]}  [{prob:.2f}]")

# Conclusión:
# Clase 9: P(N | 'pelo') = conteo_N / total = 0.86
# Clase 10: P(N → 'pelo') = conteo_N / total = 0.86
# Es el mismo número, ahora viene de corpus_ambiguo.txt.
# La diferencia: en Clase 10 estas probabilidades léxicas
# se combinan con las sintácticas de corpus_PCFG.txt
# para calcular P(árbol) = reglas estructurales × reglas léxicas.
