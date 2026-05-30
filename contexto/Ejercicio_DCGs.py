# ============================================================
# CLASE 7 - DCGs, Unificación y DAGs
# Introducción al PLN - Universidad del Valle
# Profesora: Luz Carime Lucumí Hernández
# ============================================================


# ============================================================
# PARTE 1: DAGs como diccionarios de Python
# ============================================================

# En Python un DAG lo representamos simplemente como un diccionario.
# Cada clave es un rasgo lingüístico y su valor describe a esa palabra.

# "el" es determinante, masculino, singular
dag_el = {
    'cat': 'det',
    'gen': 'masc',
    'num': 'sing'
}

# "las" es determinante, femenino, plural — misma estructura, distintos valores
dag_las = {
    'cat': 'det',
    'gen': 'fem',
    'num': 'plur'
}

# Un DAG puede tener sub-estructuras anidadas, como este NP complejo.
# El valor de 'acuerdo' es otro diccionario — un DAG dentro de un DAG.
dag_np_complejo = {
    'cat': 'np',
    'num': 'sing',
    'acuerdo': {       # aquí adentro viven los rasgos de concordancia
        'gen': 'masc',
        'num': 'sing'
    }
}

print("=" * 55)
print("PARTE 1: DAGs como diccionarios")
print("=" * 55)
print(f"dag_el  = {dag_el}")
print(f"dag_las = {dag_las}")
print(f"dag_np_complejo = {dag_np_complejo}")


# ============================================================
# PARTE 2: Algoritmo de Unificación
# ============================================================

# La idea es simple: combinar dos DAGs en uno.
# Si los dos tienen el mismo rasgo con el mismo valor → sin problema, se fusionan.
# Si tienen el mismo rasgo con valores distintos → conflicto, retornamos None.
# Si un rasgo solo existe en uno de los dos → se agrega al resultado.

def unificar(dag1, dag2):

    # Empezamos con una copia de dag1 — ese es nuestro punto de partida.
    # Ejemplo: dag1 = {'gen': 'masc', 'num': 'sing'}  ← rasgos de 'el'
    resultado = dict(dag1)

    # Ahora recorremos cada rasgo del segundo DAG para irlo incorporando.
    # Ejemplo: dag2 = {'gen': 'masc', 'num': 'sing'}  ← rasgos de 'gato'
    for rasgo, valor in dag2.items():

        if rasgo in resultado:
            # El rasgo ya existe en resultado — hay que verificar compatibilidad.

            if isinstance(resultado[rasgo], dict) and isinstance(valor, dict):
                # Ambos valores son sub-DAGs → unificamos recursivamente hacia adentro.
                sub = unificar(resultado[rasgo], valor)
                if sub is None:
                    return None       # el conflicto está en la sub-estructura
                resultado[rasgo] = sub

            elif resultado[rasgo] != valor:
                # Mismo rasgo, valores distintos → CONFLICTO.
                # Ejemplo: resultado['gen']='masc' pero valor='fem' → return None
                return None

            # Si los valores son iguales, no hay nada que hacer — ya está en resultado.

        else:
            # El rasgo no existía en dag1, simplemente lo agregamos.
            resultado[rasgo] = valor

    # Si llegamos hasta aquí sin conflictos, devolvemos el DAG combinado.
    return resultado


print("\n" + "=" * 55)
print("PARTE 2: Algoritmo de Unificación")
print("=" * 55)

# Caso 1: mismo género y número → se unifican sin problema
a = {'gen': 'masc', 'num': 'sing'}
b = {'gen': 'masc', 'num': 'sing'}
print(f"\nCaso 1 - Exitosa:")
print(f"  dag1 = {a}")
print(f"  dag2 = {b}")
print(f"  resultado = {unificar(a, b)}")

# Caso 2: rasgos distintos pero no contradictorios → se complementan
c = {'cat': 'det', 'gen': 'masc'}
d = {'num': 'sing'}
print(f"\nCaso 2 - Rasgos complementarios:")
print(f"  dag1 = {c}")
print(f"  dag2 = {d}")
print(f"  resultado = {unificar(c, d)}")

# Caso 3: mismo rasgo 'gen' pero valores distintos → conflicto
e = {'gen': 'masc', 'num': 'sing'}
f = {'gen': 'fem',  'num': 'sing'}
print(f"\nCaso 3 - Conflicto de género:")
print(f"  dag1 = {e}")
print(f"  dag2 = {f}")
print(f"  resultado = {unificar(e, f)}  ← None indica incompatibilidad")

# Caso 4: mismo rasgo 'num' pero valores distintos → conflicto
g = {'num': 'sing'}
h = {'num': 'plur'}
print(f"\nCaso 4 - Conflicto de número:")
print(f"  dag1 = {g}")
print(f"  dag2 = {h}")
print(f"  resultado = {unificar(g, h)}  ← None indica incompatibilidad")


# ============================================================
# PARTE 3: Léxico con estructuras de rasgos (DAGs)
# ============================================================

# Cada palabra del vocabulario tiene su propio DAG con sus rasgos.
# Cuando el parser analiza una oración, consulta aquí los rasgos de cada token.

lexico = {
    # Determinantes — cada uno lleva su género y número
    'el':     {'cat': 'det', 'gen': 'masc', 'num': 'sing'},
    'la':     {'cat': 'det', 'gen': 'fem',  'num': 'sing'},
    'los':    {'cat': 'det', 'gen': 'masc', 'num': 'plur'},
    'las':    {'cat': 'det', 'gen': 'fem',  'num': 'plur'},

    # Sustantivos — también llevan género y número
    'gato':   {'cat': 'n',   'gen': 'masc', 'num': 'sing'},
    'gata':   {'cat': 'n',   'gen': 'fem',  'num': 'sing'},
    'gatos':  {'cat': 'n',   'gen': 'masc', 'num': 'plur'},
    'perro':  {'cat': 'n',   'gen': 'masc', 'num': 'sing'},
    'perros': {'cat': 'n',   'gen': 'masc', 'num': 'plur'},
    'niña':   {'cat': 'n',   'gen': 'fem',  'num': 'sing'},
    'niñas':  {'cat': 'n',   'gen': 'fem',  'num': 'plur'},

    # Verbos — llevan número para concordar con el sujeto, y 'accion' para la semántica
    'corre':   {'cat': 'v',  'num': 'sing', 'accion': 'correr'},
    'corren':  {'cat': 'v',  'num': 'plur', 'accion': 'correr'},
    'duerme':  {'cat': 'v',  'num': 'sing', 'accion': 'dormir'},
    'duermen': {'cat': 'v',  'num': 'plur', 'accion': 'dormir'},
    'juega':   {'cat': 'v',  'num': 'sing', 'accion': 'jugar'},
    'juegan':  {'cat': 'v',  'num': 'plur', 'accion': 'jugar'},
}

print("\n" + "=" * 55)
print("PARTE 3: Léxico con DAGs")
print("=" * 55)
for palabra, rasgos in lexico.items():
    print(f"  '{palabra}': {rasgos}")


# ============================================================
# PARTE 4: Parser con unificación de rasgos
# ============================================================

# Este parser implementa la misma lógica de una DCG, pero en Python.
# La gramática que sigue es:
#   S  → NP  VP   (con concordancia de número entre sujeto y verbo)
#   NP → Det  N   (con concordancia de género y número)
#   VP → V        (el verbo aporta número y acción semántica)


def parse_np(tokens, pos):
    # Necesitamos al menos dos tokens desde pos: uno para Det y otro para N.
    # Ejemplo: tokens = ['el', 'gato', 'corre'],  pos = 0
    if pos + 1 >= len(tokens):
        return None, pos

    # Tomamos los dos candidatos en la posición actual.
    # palabra_det = tokens[0] = 'el'
    # palabra_n   = tokens[1] = 'gato'
    palabra_det = tokens[pos]
    palabra_n   = tokens[pos + 1]

    # Ambas palabras tienen que estar en el léxico — si no, no podemos analizarlas.
    if palabra_det not in lexico or palabra_n not in lexico:
        print(f"    ✗ '{palabra_det}' o '{palabra_n}' no están en el léxico")
        return None, pos

    # Consultamos los rasgos de cada palabra en el léxico.
    # rasgos_det = {'cat': 'det', 'gen': 'masc', 'num': 'sing'}
    # rasgos_n   = {'cat': 'n',   'gen': 'masc', 'num': 'sing'}
    rasgos_det = lexico[palabra_det]
    rasgos_n   = lexico[palabra_n]

    # Verificamos que la primera palabra sea realmente un determinante
    # y la segunda un sustantivo — no vale cualquier combinación.
    if rasgos_det.get('cat') != 'det':
        print(f"    ✗ '{palabra_det}' no es un determinante")
        return None, pos
    if rasgos_n.get('cat') != 'n':
        print(f"    ✗ '{palabra_n}' no es un sustantivo")
        return None, pos

    # Extraemos solo los rasgos de concordancia: género y número.
    # concord_det = {'gen': 'masc', 'num': 'sing'}
    # concord_n   = {'gen': 'masc', 'num': 'sing'}
    concord_det = {'gen': rasgos_det['gen'], 'num': rasgos_det['num']}
    concord_n   = {'gen': rasgos_n['gen'],   'num': rasgos_n['num']}

    # Aquí es donde entra la unificación: si género y número coinciden, ok.
    # Si no coinciden — por ejemplo 'el gata' — unificar devuelve None y el NP falla.
    unificado = unificar(concord_det, concord_n)

    if unificado is None:
        print(f"    ✗ Conflicto: '{palabra_det}' {concord_det} ≠ '{palabra_n}' {concord_n}")
        return None, pos

    # Todo concordó — armamos la estructura del NP con los rasgos combinados.
    # np = {'cat': 'np', 'gen': 'masc', 'num': 'sing', 'det': 'el', 'n': 'gato'}
    np = {
        'cat': 'np',
        'gen': unificado['gen'],
        'num': unificado['num'],
        'det': palabra_det,
        'n':   palabra_n
    }
    print(f"    ✓ NP: [{palabra_det} + {palabra_n}]  rasgos={unificado}")

    # Retornamos la estructura y avanzamos pos en 2 porque consumimos dos tokens.
    return np, pos + 2


def parse_vp(tokens, pos):
    # Verificamos que todavía queden tokens por analizar.
    # En nuestro ejemplo: pos = 2, len(tokens) = 3 → hay exactamente uno más.
    if pos >= len(tokens):
        return None, pos

    # Tomamos el token en la posición actual como candidato a verbo.
    # palabra_v = tokens[2] = 'corre'
    palabra_v = tokens[pos]

    if palabra_v not in lexico:
        print(f"    ✗ '{palabra_v}' no está en el léxico")
        return None, pos

    # Consultamos sus rasgos.
    # rasgos_v = {'cat': 'v', 'num': 'sing', 'accion': 'correr'}
    rasgos_v = lexico[palabra_v]

    # Confirmamos que sea un verbo.
    if rasgos_v.get('cat') != 'v':
        print(f"    ✗ '{palabra_v}' no es un verbo")
        return None, pos

    # Armamos la estructura VP con el número — para concordar con el NP —
    # y con la acción semántica, que usaremos después para extraer el significado.
    # vp = {'cat': 'vp', 'num': 'sing', 'accion': 'correr', 'v': 'corre'}
    vp = {
        'cat':    'vp',
        'num':    rasgos_v['num'],
        'accion': rasgos_v['accion'],
        'v':      palabra_v
    }
    print(f"    ✓ VP: [{palabra_v}]  accion='{rasgos_v['accion']}', num={rasgos_v['num']}")

    # Retornamos la estructura y avanzamos pos en 1 porque consumimos un token.
    return vp, pos + 1


def parse_s(tokens):
    print(f"\n  Analizando: '{' '.join(tokens)}'")

    # Primero buscamos el sujeto: intentamos reconocer un NP desde el inicio.
    # Si falla, la oración no es válida — terminamos aquí.
    np, pos = parse_np(tokens, 0)
    if np is None:
        print(f"    ✗ No se reconoció el NP")
        return None

    # Con pos ya actualizado al token siguiente, buscamos el predicado: el VP.
    # En nuestro ejemplo: pos = 2, entonces buscamos el verbo en tokens[2].
    vp, pos = parse_vp(tokens, pos)
    if vp is None:
        print(f"    ✗ No se reconoció el VP")
        return None

    # Verificamos que no haya tokens sobrantes — la oración debe terminar aquí.
    # pos = 3 == len(tokens) = 3 → perfecto, consumimos todo.
    if pos != len(tokens):
        print(f"    ✗ Tokens sobrantes: {tokens[pos:]}")
        return None

    # Último chequeo: concordancia de número entre sujeto y verbo.
    # np['num'] = 'sing',  vp['num'] = 'sing' → unificar devuelve {'num': 'sing'} → ok.
    # Si fuera 'los gatos corre': np['num']='plur' vs vp['num']='sing' → None → falla.
    concordancia = unificar({'num': np['num']}, {'num': vp['num']})
    if concordancia is None:
        print(f"    ✗ Conflicto sujeto-verbo: NP={np['num']} vs VP={vp['num']}")
        return None

    # Todo pasó — construimos la estructura final de la oración.
    oracion = {
        'cat':    'S',
        'np':     np,
        'vp':     vp,
        'accion': vp['accion']   # la acción viene del verbo
    }
    print(f"    ✓ Oración válida")
    return oracion


# ============================================================
# PARTE 5: Extracción de intención semántica
# ============================================================

# Una vez que la oración fue reconocida, podemos extraer su significado:
# quién es el sujeto y qué acción realiza.

def extraer_intencion(oracion):
    # Si el parser no reconoció la oración, no hay nada que extraer.
    if oracion is None:
        return "→ Oración no válida"

    # El sujeto lo armamos con el determinante y el sustantivo del NP.
    # oracion['np']['det'] = 'el',  oracion['np']['n'] = 'gato'  → "el gato"
    sujeto = f"{oracion['np']['det']} {oracion['np']['n']}"

    # La acción viene directamente del verbo, guardada en el VP.
    # oracion['accion'] = 'correr'
    accion = oracion['accion']

    return f"→ Sujeto: '{sujeto}'  |  Acción: '{accion}'"


# ============================================================
# PARTE 6: Casos de prueba
# ============================================================

print("\n\n" + "=" * 55)
print("PARTE 4-5: Parser con unificación + semántica")
print("=" * 55)

oraciones = [
    (["el",  "gato",   "corre"],   "correcto - masc sing"),
    (["la",  "gata",   "corre"],   "correcto - fem sing"),
    (["los", "gatos",  "corren"],  "correcto - masc plur"),
    (["las", "niñas",  "juegan"],  "correcto - fem plur"),
    (["el",  "gata",   "corre"],   "ERROR género: det masc, n fem"),
    (["los", "gatos",  "corre"],   "ERROR número: NP plur, VP sing"),
    (["la",  "perro",  "duerme"],  "ERROR género: det fem, n masc"),
    (["los", "perros", "duermen"], "correcto - masc plur"),
]

for tokens, descripcion in oraciones:
    print(f"\n  [{descripcion}]")
    resultado = parse_s(tokens)
    print(f"  {extraer_intencion(resultado)}")