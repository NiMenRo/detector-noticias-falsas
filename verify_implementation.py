"""
Script de verificación de la implementación de DAG, DCG y Unificación
Compara con la referencia de ejercicioDCGs.py
"""

import sys
sys.path.insert(0, 'src')

from unification import unificar, extraer_rasgos
from dcg import Parser, crear_lexico_fake_news

print("=" * 70)
print("VERIFICACIÓN DE IMPLEMENTACIÓN: DAG, DCG Y UNIFICACIÓN")
print("=" * 70)

# ============================================================
# TEST 1: ALGORITMO DE UNIFICACIÓN
# ============================================================
print("\n" + "=" * 70)
print("TEST 1: ALGORITMO DE UNIFICACIÓN")
print("=" * 70)

test_cases_unificacion = [
    ({}, {}, {}, "Caso: ambos DAGs vacíos"),
    ({'gen': 'masc', 'num': 'sing'}, {'gen': 'masc', 'num': 'sing'}, 
     {'gen': 'masc', 'num': 'sing'}, "Caso 1: mismos rasgos, mismos valores"),
    
    ({'cat': 'det', 'gen': 'masc'}, {'num': 'sing'}, 
     {'cat': 'det', 'gen': 'masc', 'num': 'sing'}, "Caso 2: rasgos complementarios"),
    
    ({'gen': 'masc', 'num': 'sing'}, {'gen': 'fem', 'num': 'sing'}, 
     None, "Caso 3: conflicto de género"),
    
    ({'num': 'sing'}, {'num': 'plur'}, 
     None, "Caso 4: conflicto de número"),
    
    ({'acuerdo': {'gen': 'masc', 'num': 'sing'}}, 
     {'acuerdo': {'gen': 'masc', 'num': 'sing'}}, 
     {'acuerdo': {'gen': 'masc', 'num': 'sing'}}, "Caso 5: DAGs anidados compatibles"),
    
    ({'acuerdo': {'gen': 'masc'}}, 
     {'acuerdo': {'gen': 'fem'}}, 
     None, "Caso 6: DAGs anidados incompatibles"),
]

passed = 0
failed = 0

for dag1, dag2, expected, descripcion in test_cases_unificacion:
    resultado = unificar(dag1, dag2)
    status = "✓ PASS" if resultado == expected else "✗ FAIL"
    if resultado == expected:
        passed += 1
    else:
        failed += 1
    print(f"\n{status}: {descripcion}")
    print(f"  dag1: {dag1}")
    print(f"  dag2: {dag2}")
    print(f"  esperado: {expected}")
    print(f"  obtenido: {resultado}")

print(f"\n[Unificación] Pasados: {passed}/{len(test_cases_unificacion)}")

# ============================================================
# TEST 2: EXTRACCIÓN DE RASGOS
# ============================================================
print("\n" + "=" * 70)
print("TEST 2: EXTRACCIÓN DE RASGOS")
print("=" * 70)

test_cases_rasgos = [
    ({'cat': 'n', 'gen': 'masc', 'num': 'sing', 'sem': 'animal'}, 
     ['gen', 'num'], 
     {'gen': 'masc', 'num': 'sing'}, 
     "Extrae gen y num de un sustantivo"),
    
    ({'cat': 'det', 'gen': 'fem', 'num': 'plur'}, 
     ['gen'], 
     {'gen': 'fem'}, 
     "Extrae solo género"),
    
    ({'cat': 'v', 'num': 'sing', 'accion': 'correr'}, 
     ['num', 'accion'], 
     {'num': 'sing', 'accion': 'correr'}, 
     "Extrae número y acción del verbo"),
]

passed_rasgos = 0
for dag, rasgos_lista, expected, descripcion in test_cases_rasgos:
    resultado = extraer_rasgos(dag, rasgos_lista)
    status = "✓ PASS" if resultado == expected else "✗ FAIL"
    if resultado == expected:
        passed_rasgos += 1
    print(f"\n{status}: {descripcion}")
    print(f"  DAG: {dag}")
    print(f"  Rasgos a extraer: {rasgos_lista}")
    print(f"  Esperado: {expected}")
    print(f"  Obtenido: {resultado}")

print(f"\n[Extracción de rasgos] Pasados: {passed_rasgos}/{len(test_cases_rasgos)}")

# ============================================================
# TEST 3: PARSER DCG CON LÉXICO ESTÁNDAR
# ============================================================
print("\n" + "=" * 70)
print("TEST 3: PARSER DCG CON LÉXICO ESTÁNDAR")
print("=" * 70)

# Creamos el léxico idéntico al del ejercicio de referencia
lexico_standar = {
    # Determinantes
    'el':     {'cat': 'det', 'gen': 'masc', 'num': 'sing'},
    'la':     {'cat': 'det', 'gen': 'fem',  'num': 'sing'},
    'los':    {'cat': 'det', 'gen': 'masc', 'num': 'plur'},
    'las':    {'cat': 'det', 'gen': 'fem',  'num': 'plur'},
    
    # Sustantivos
    'gato':   {'cat': 'n',   'gen': 'masc', 'num': 'sing'},
    'gata':   {'cat': 'n',   'gen': 'fem',  'num': 'sing'},
    'gatos':  {'cat': 'n',   'gen': 'masc', 'num': 'plur'},
    'perro':  {'cat': 'n',   'gen': 'masc', 'num': 'sing'},
    'perros': {'cat': 'n',   'gen': 'masc', 'num': 'plur'},
    'niña':   {'cat': 'n',   'gen': 'fem',  'num': 'sing'},
    'niñas':  {'cat': 'n',   'gen': 'fem',  'num': 'plur'},
    
    # Verbos
    'corre':   {'cat': 'v',  'num': 'sing', 'accion': 'correr'},
    'corren':  {'cat': 'v',  'num': 'plur', 'accion': 'correr'},
    'duerme':  {'cat': 'v',  'num': 'sing', 'accion': 'dormir'},
    'duermen': {'cat': 'v',  'num': 'plur', 'accion': 'dormir'},
    'juega':   {'cat': 'v',  'num': 'sing', 'accion': 'jugar'},
    'juegan':  {'cat': 'v',  'num': 'plur', 'accion': 'jugar'},
}

parser = Parser(lexico_standar, debug=False)

test_cases_parser = [
    (["el",  "gato",   "corre"],   True,  "Correcto: masc sing"),
    (["la",  "gata",   "corre"],   True,  "Correcto: fem sing"),
    (["los", "gatos",  "corren"],  True,  "Correcto: masc plur"),
    (["las", "niñas",  "juegan"],  True,  "Correcto: fem plur"),
    (["el",  "gata",   "corre"],   False, "ERROR: género (det masc, n fem)"),
    (["los", "gatos",  "corre"],   False, "ERROR: número (NP plur, VP sing)"),
    (["la",  "perro",  "duerme"],  False, "ERROR: género (det fem, n masc)"),
    (["los", "perros", "duermen"], True,  "Correcto: masc plur"),
]

passed_parser = 0
for tokens, should_parse, descripcion in test_cases_parser:
    resultado = parser.analizar_s(tokens)
    parsed_successfully = resultado is not None
    status = "✓ PASS" if parsed_successfully == should_parse else "✗ FAIL"
    if parsed_successfully == should_parse:
        passed_parser += 1
    
    print(f"\n{status}: {descripcion}")
    print(f"  Oración: {' '.join(tokens)}")
    print(f"  Esperado: {'parseable' if should_parse else 'NO parseable'}")
    print(f"  Obtenido: {'parseable' if parsed_successfully else 'NO parseable'}")
    
    if parsed_successfully and should_parse:
        intencion = parser.extraer_intencion(resultado)
        print(f"  {intencion}")

print(f"\n[Parser DCG] Pasados: {passed_parser}/{len(test_cases_parser)}")

# ============================================================
# TEST 4: ANÁLISIS DE COMPONENTES (NP, VP)
# ============================================================
print("\n" + "=" * 70)
print("TEST 4: ANÁLISIS DE SINTAGMAS (NP, VP)")
print("=" * 70)

parser_debug = Parser(lexico_standar, debug=True)

print("\nPrueba NP - Caso exitoso:")
np, pos = parser_debug.analizar_np(["el", "gato", "corre"], 0)
print(f"Resultado: {np}, Nueva posición: {pos}\n")

print("Prueba NP - Caso fallido (género):")
np, pos = parser_debug.analizar_np(["el", "gata", "corre"], 0)
print(f"Resultado: {np}, Nueva posición: {pos}\n")

print("Prueba VP - Caso exitoso:")
vp, pos = parser_debug.analizar_vp(["corre"], 0)
print(f"Resultado: {vp}, Nueva posición: {pos}\n")

# ============================================================
# RESUMEN FINAL
# ============================================================
print("\n" + "=" * 70)
print("RESUMEN FINAL DE PRUEBAS")
print("=" * 70)

total_tests = len(test_cases_unificacion) + len(test_cases_rasgos) + len(test_cases_parser)
total_passed = passed + passed_rasgos + passed_parser

print(f"\nTotal de pruebas: {total_tests}")
print(f"Pasadas: {total_passed}")
print(f"Fallidas: {total_tests - total_passed}")
print(f"Porcentaje de éxito: {(total_passed / total_tests * 100):.1f}%")

if total_passed == total_tests:
    print("\n✓ ¡TODAS LAS PRUEBAS PASARON!")
    print("La implementación funciona correctamente.")
else:
    print(f"\n✗ Hay {total_tests - total_passed} pruebas fallidas.")
    print("Revisa los errores arriba.")

print("\n" + "=" * 70)
