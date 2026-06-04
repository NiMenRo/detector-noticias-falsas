# ============================================================
# Clase 8 — Introducción al PLN
# ============================================================


# ── PARTE 1: Léxico ─────────────────────────────────────────

# El léxico es nuestro diccionario de categorías gramaticales.
# Es exactamente el mismo que usamos en DCG — aquí no cambia nada.
lexico = {
    # Cuatro determinantes: artículos definidos, singular y plural.
    "la": "Det", "el": "Det", "las": "Det", "los": "Det",
    # Sustantivos en singular y plural.
    "estudiante": "N", "estudiantes": "N",
    "libro": "N",      "libros": "N",
    "gato": "N",       "gatos": "N",
    # Verbos también en singular y plural: lee/leen, ve/ven.
    "lee": "V", "leen": "V", "ve": "V", "ven": "V",
}

# cat es nuestra función auxiliar de consulta al léxico.
# Recibe un token y devuelve su categoría — o None si no existe.
def cat(token):
    # .get(token, None) significa: busca token en el diccionario;
    # si no está, devuelve None en lugar de lanzar un error.
    # Eso nos protege cuando aparece una palabra desconocida.
    return lexico.get(token, None)


# ── PARTE 2: red_np  (CAT Det → CAT N → POP) ────────────────

# La subred NP implementa la subred del NP del diagrama ATN.
# Recibe la lista de tokens y la posición actual — pos es el índice.
# Tiene: CAT Det → CAT N → POP.
def red_np(tokens, pos):
    # Antes de intentar cualquier arco verificamos que haya tokens disponibles.
    # Si pos ya llegó al final, no hay nada que analizar — fallamos limpiamente.
    if pos >= len(tokens): return None, pos

    # ── Arco 1: CAT Det → CAT N (caso original) ──────────────
    # Si el token actual es un determinante, intentamos el camino Det+N.
    if cat(tokens[pos]) == "Det":
        det = tokens[pos]   # Guardamos el determinante — esto es SETR DET.
        pos1 = pos + 1      # Avanzamos al siguiente token.

        # Arco CAT N — si el siguiente token es sustantivo, el NP está completo.
        if pos1 < len(tokens) and cat(tokens[pos1]) == "N":
            n = tokens[pos1]
            # POP: devolvemos la estructura [det, n] y la nueva posición.
            # Esto es el retorno de la subred — como regresar de una función.
            return [det, n], pos1 + 1

    # Si ningún arco funcionó, la subred falla.
    # Devolvemos None y la posición original sin consumir nada.
    return None, pos


# ── PARTE 3: red_vp  (CAT V → PUSH NP → POP) ───────────────

# La subred VP reconoce un verbo seguido obligatoriamente de un NP objeto.
# Tiene: CAT V → PUSH NP → POP.
def red_vp(tokens, pos):
    if pos >= len(tokens): return None, pos

    # Arco CAT V — verificamos que el token actual sea un verbo.
    if cat(tokens[pos]) == "V":
        v = tokens[pos]   # Guardamos el verbo — esto es SETR V.

        # ── Arco PUSH NP (caso original) ─────────────────────
        # Intentamos encontrar un NP después del verbo — el objeto directo.
        # Si lo encontramos, retornamos el VP con objeto.
        np, pos2 = red_np(tokens, pos + 1)
        if np is not None:
            # POP: devolvemos la tupla (verbo, objeto) y la nueva posición.
            return [v, np], pos2

    # Si el token no es un verbo, la subred falla.
    return None, pos


# ── PARTE 4: red_s  (PUSH NP → PUSH VP → POP/acepta) ────────

# La red principal S orquesta todo.
# Recibe la oración completa como lista de tokens.
def red_s(tokens):
    # Caso borde: lista vacía — no hay nada que analizar.
    if not tokens: return None

    # PUSH NP — primer PUSH de S: llamamos a red_np desde la posición 0.
    np, pos1 = red_np(tokens, 0)
    # Si red_np falló, no hay sujeto válido — la oración no tiene estructura.
    if np is None: return None

    # PUSH VP — segundo PUSH: llamamos a red_vp desde donde terminó el NP.
    vp, pos2 = red_vp(tokens, pos1)
    if vp is None or pos2 != len(tokens): return None

    # POP final — devolvemos un diccionario con los registros SUBJ y VP.
    # Aquí se ve la 'A' de ATN: aumentamos la salida con información estructurada.
    return {"SUBJ": np, "VP": vp}


# ── PRUEBAS DE LA PARTE SINTÁCTICA ───────────────────────────

# Antes de pasar al diálogo, probamos todos los casos de la ATN sintáctica.
# Fíjense cómo cada caso demuestra algo diferente del formalismo.
print("=" * 55)
print("PRUEBAS ATN SINTÁCTICA")
print("=" * 55)

casos_sintacticos = [
    # ── Casos que PASAN → {"SUBJ": ..., "VP": ...} ──────────
    # Det+N sujeto, V+NP objeto: el camino feliz del diagrama.
    ("la estudiante lee el libro",      "PASA: Det+N sujeto, V+NP objeto"),
    ("los estudiantes leen los libros", "PASA: plural"),
    ("el gato ve el libro",             "PASA: otro sujeto y objeto"),
    ("las estudiantes leen los gatos",  "PASA: Det femenino plural"),

    # ── Casos que FALLAN → None ──────────────────────────────
    # Sin Det: red_np solo tiene el arco Det→N.
    # tokens[0] no es Det → red_np devuelve None → red_s None.
    ("estudiantes leen los libros",     "FALLA: sujeto sin Det → red_np None en pos=0"),
    ("gatos ven libros",                "FALLA: sujeto y objeto sin Det"),

    # VP sin objeto: red_vp exige PUSH NP.
    # np queda None → red_vp devuelve None → vp is None → red_s None.
    ("la estudiante lee",               "FALLA: VP sin objeto → vp None"),

    # Token sobrante: red_s exige pos2 == len(tokens).
    # "corre" no se consume → pos2=5, len=6 → red_s None.
    ("la estudiante lee el libro corre","FALLA: token sobrante → pos2 != len"),

    # Token desconocido en posición de V: cat() devuelve None, no es "V".
    # red_vp no activa ningún arco → vp None → red_s None.
    ("la estudiante xyz el libro",      "FALLA: token desconocido en pos. V"),

    # Un solo token V: red_np falla en pos=0 porque "lee" no es Det.
    ("lee",                             "FALLA: solo el verbo → red_np None"),

    # Det sin N: red_np encuentra Det pero tokens[1] es V, no N.
    ("la lee",                          "FALLA: Det sin sustantivo → red_np None"),
]

for oracion, descripcion in casos_sintacticos:
    tokens    = oracion.split()
    resultado = red_s(tokens)
    print(f"\n  [{descripcion}]")
    print(f"  Entrada : {tokens}")
    print(f"  Resultado: {resultado}")


# ── PARTE 5: ATN de diálogo ──────────────────────────────────

# Ahora pasamos al ATN de diálogo — el mismo formalismo,
# pero el dominio cambia: ya no son oraciones, son turnos de conversación.
# Los estados ya no son NP, VP, S — son momentos de la conversación.

# bd_horarios simula una base de datos.
# En producción esto sería una consulta a una BD real o una API.
bd_horarios = {
    "pln":        "Martes y Jueves 8:00-10:00am — Sala 201",
    "calculo":    "Lunes y Miércoles 10:00-12:00m — Sala 305",
    "algoritmos": "Viernes 2:00-5:00pm — Lab 102",
}

# ── CAPA 1: Clasificador de intención ────────────────────────
# Esta es la capa que faltaba: convierte texto libre en una intención
# y extrae datos relevantes (como la materia).
# En producción sería un modelo de ML o un LLM; aquí usamos palabras clave.
# Devuelve (intencion, datos) — datos es un dict que se fusiona al contexto.
def clasificar_intencion(texto):
    texto = texto.lower()

    if any(p in texto for p in ["hola", "buenos", "buenas", "hey"]):
        return "saludo", {}

    # Buscamos el nombre de la materia ANTES de decidir la intención.
    # Así "horario de pln" ya llega con materia=pln al contexto.
    for materia in bd_horarios:
        if materia in texto:
            return "pedir_horario", {"materia": materia}
    if any(p in texto for p in ["horario", "cuándo", "cuando", "clases"]):
        return "pedir_horario", {}

    if any(p in texto for p in ["repite", "repetir", "de nuevo", "otra vez"]):
        return "repetir", {}

    if any(p in texto for p in ["sí", "si", "ok", "perfecto", "gracias", "listo"]):
        return "confirmar", {}

    if any(p in texto for p in ["adiós", "adios", "chao", "hasta", "bye"]):
        return "despedida", {}

    return None, {}


# ── CAPA 2: Tabla de transiciones (el diagrama en código) ────
# Esta tabla ES el diagrama de la diapositiva — cada fila es un estado,
# cada clave interna es un arco, cada valor es el estado siguiente.
dialogo_atn = {
    # inicio: solo acepta saludo — guarda de entrada.
    "inicio":      {"saludo":        "esperando"},

    # esperando: el usuario hace su consulta.
    "esperando":   {"pedir_horario": "consultando"},

    # consultando: confirmar avanza, repetir hace bucle (mismo estado).
    "consultando": {"confirmar":     "fin",
                    "repetir":       "consultando"},

    # fin: despedida limpia contexto y vuelve a inicio — la ATN cicla.
    "fin":         {"despedida":     "inicio"},
}


# ── CAPA 3: Motor ATN ────────────────────────────────────────
# procesar_dialogo recibe estado + intención + contexto.
# Consulta la tabla, ejecuta las acciones del arco y devuelve el nuevo estado.
def procesar_dialogo(estado, intencion, contexto):
    transiciones = dialogo_atn.get(estado, {})
    nuevo_estado  = transiciones.get(intencion, None)

    # Sin transición válida: el estado actúa como guarda, no avanza.
    if nuevo_estado is None:
        print(f"  [{estado}] '{intencion}' no tiene arco — sin transición")
        return estado, contexto

    print(f"  {estado:12s} --[{intencion}]--> {nuevo_estado}")

    if intencion == "saludo":
        print(f"  → Sistema: ¡Hola! ¿En qué puedo ayudarte?")

    elif intencion == "pedir_horario":
        # GETR MATERIA del contexto (lo puso el clasificador).
        materia   = contexto.get("materia", "desconocida")
        respuesta = bd_horarios.get(materia, None)
        if respuesta:
            # SETR RESPUESTA: persiste para poder repetirla en el turno siguiente.
            contexto["respuesta"] = respuesta
            print(f"  → GETR MATERIA   = {materia}")
            print(f"  → SETR RESPUESTA = '{respuesta}'")
            print(f"  → Sistema: El horario de {materia} es: {respuesta}")
        else:
            print(f"  → Sistema: No encontré '{materia}'. ¿Cuál materia buscás?")
            nuevo_estado = "esperando"

    elif intencion == "repetir":
        # GETR RESPUESTA: el registro persiste desde el turno anterior.
        respuesta = contexto.get("respuesta", None)
        if respuesta:
            print(f"  → Sistema (repite): {respuesta}")
        else:
            print(f"  → Sistema: No tengo información que repetir.")

    elif intencion == "confirmar":
        print(f"  → Sistema: Perfecto. ¿Necesitas algo más?")

    elif intencion == "despedida":
        print(f"  → Sistema: ¡Hasta luego!")
        # Reset completo — la próxima conversación empieza con memoria en blanco.
        contexto = {}

    return nuevo_estado, contexto


# ── Función auxiliar para las simulaciones ───────────────────
# Une las dos capas: texto → clasificar → procesar.
# Así las simulaciones muestran el pipeline completo.
def turno(texto, estado, contexto):
    print(f"\n  Usuario: \"{texto}\"")
    intencion, datos = clasificar_intencion(texto)
    if intencion is None:
        print(f"  → Clasificador: no reconoció la intención")
        return estado, contexto
    print(f"  → Clasificador: intención='{intencion}'" +
          (f" | datos={datos}" if datos else ""))
    contexto.update(datos)
    return procesar_dialogo(estado, intencion, contexto)


# ── SIMULACIONES ─────────────────────────────────────────────
print("\n\n" + "=" * 55)
print("SIMULACIONES ATN DE DIÁLOGO")
print("=" * 55)


# ── Simulación 1: flujo normal ───────────────────────────────
# El camino feliz: inicio → esperando → consultando → fin → inicio.
print("\n=== Simulación 1: flujo normal ===")
estado, contexto = "inicio", {}
estado, contexto = turno("hola buenas",                  estado, contexto)
estado, contexto = turno("¿cuál es el horario de pln?",  estado, contexto)
estado, contexto = turno("sí gracias",                   estado, contexto)
estado, contexto = turno("adiós",                        estado, contexto)
print(f"  Estado final: {estado} | Contexto: {contexto}")


# ── Simulación 2: usuario pide repetir ───────────────────────
# El arco 'repetir' es un bucle — el estado no cambia.
# GETR RESPUESTA sigue disponible porque el contexto no se limpió.
print("\n=== Simulación 2: usuario pide repetir ===")
estado, contexto = "inicio", {}
estado, contexto = turno("hola",                              estado, contexto)
estado, contexto = turno("horario de calculo por favor",      estado, contexto)
estado, contexto = turno("no entendí, repite",                estado, contexto)
estado, contexto = turno("ok perfecto",                       estado, contexto)
estado, contexto = turno("chao",                              estado, contexto)
print(f"  Estado final: {estado} | Contexto: {contexto}")


# ── Simulación 3: el estado actúa como guarda ────────────────
# El usuario va directo al grano sin saludar.
# Desde 'inicio', 'pedir_horario' no tiene arco — el sistema no avanza.
print("\n=== Simulación 3: el estado como guarda ===")
estado, contexto = "inicio", {}
estado, contexto = turno("¿cuándo es algoritmos?",  estado, contexto)
print(f"  Estado sigue en: {estado}")
estado, contexto = turno("hey hola",                estado, contexto)
estado, contexto = turno("horario de algoritmos",   estado, contexto)
estado, contexto = turno("listo gracias",           estado, contexto)
estado, contexto = turno("hasta luego",             estado, contexto)
print(f"  Estado final: {estado} | Contexto: {contexto}")


# ── Simulación 4: ciclo completo — la ATN no termina ─────────
# Un parser analiza una oración y termina.
# Una ATN de diálogo cicla: después de 'despedida' vuelve a 'inicio'
# lista para el próximo usuario — con contexto en blanco.
print("\n=== Simulación 4: ciclo — dos conversaciones seguidas ===")
estado, contexto = "inicio", {}

print("  -- Conversación 1 --")
estado, contexto = turno("buenas",                      estado, contexto)
estado, contexto = turno("horario de calculo",          estado, contexto)
estado, contexto = turno("gracias",                     estado, contexto)
estado, contexto = turno("adios",                       estado, contexto)
print(f"  Sesión 1 cerrada: estado={estado} | contexto={contexto}")

print("  -- Conversación 2 --")
estado, contexto = turno("hola",                        estado, contexto)
estado, contexto = turno("¿cuándo es pln?",             estado, contexto)
estado, contexto = turno("ok",                          estado, contexto)
estado, contexto = turno("chao",                        estado, contexto)
print(f"  Sesión 2 cerrada: estado={estado} | contexto={contexto}")