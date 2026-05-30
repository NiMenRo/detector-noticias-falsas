"""
Main extendido: Demuestra Chart Parser + Unificación + DCG + DAG
Flujo completo de análisis sintáctico con PLN.
"""

from lexer import tokenize
from grammar import gramatica
from chart_parser import chart_parser
from nodes import Nodo

# Importar nuevas herramientas
from unification import (
    Variable, Atom, Compound, Substitution,
    unify, get_variables
)
from dcg import DCGGrammar, expand_dcg_rule
from dag import DAG, dag_to_string, tree_to_dag_stats


def mostrar_menu():
    """Muestra menú de opciones"""
    print("\n" + "="*70)
    print("ANALIZADOR SINTÁCTICO - DETECTOR DE NOTICIAS FALSAS")
    print("="*70)
    print("\nOpciones:")
    print("  1. Análisis completo (Chart Parser + DAG + Unificación)")
    print("  2. Solo Chart Parser (análisis tradicional)")
    print("  3. Convertir a DAG (árbol → grafo acíclico)")
    print("  4. Extraer componentes (unificación)")
    print("  5. Ver gramática DCG")
    print("  6. Salir")
    print()


def opcion_1_analisis_completo():
    """Opción 1: Análisis completo"""
    print("\n" + "-"*70)
    print("OPCIÓN 1: ANÁLISIS COMPLETO")
    print("-"*70 + "\n")
    
    # Entrada
    texto = input("Ingrese el texto a analizar (o presione Enter para ejemplo): ").strip()
    if not texto:
        texto = "¡el virus amenaza!"
    
    print(f"\nTexto: '{texto}'")
    
    # PASO 1: Tokenización
    print("\n" + "="*70)
    print("PASO 1: TOKENIZACIÓN")
    print("="*70)
    tokens = tokenize(texto)
    print(f"Tokens: {tokens}")
    print(f"Total de tokens: {len(tokens)}")
    
    # PASO 2: Parsing
    print("\n" + "="*70)
    print("PASO 2: PARSING CON CHART PARSER")
    print("="*70)
    arboles, chart = chart_parser(tokens, gramatica)
    
    if not arboles:
        print("❌ No se encontraron derivaciones válidas.")
        return
    
    print(f"✓ Se encontraron {len(arboles)} árbol(es)")
    
    # PASO 3: Procesar cada árbol
    for i, arbol in enumerate(arboles):
        print(f"\n" + "="*70)
        print(f"ÁRBOL {i+1}")
        print("="*70)
        
        # 3a. Mostrar árbol
        print("\n--- Árbol de Derivación ---")
        print(arbol)
        
        # 3b. Convertir a DAG
        print("\n--- DAG Comprimido ---")
        dag = DAG()
        root = dag.build_from_tree(arbol)
        print(dag_to_string(root))
        
        # 3c. Estadísticas
        print("\n--- Estadísticas de Compresión ---")
        stats = tree_to_dag_stats(arbol, dag)
        for clave, valor in stats.items():
            print(f"  {clave}: {valor}")
        
        # 3d. Extracción de componentes
        print("\n--- Extracción de Componentes (Unificación) ---")
        extraer_componentes(arbol)


def opcion_2_chart_parser():
    """Opción 2: Chart Parser solo"""
    print("\n" + "-"*70)
    print("OPCIÓN 2: CHART PARSER TRADICIONAL")
    print("-"*70 + "\n")
    
    texto = input("Ingrese el texto a analizar: ").strip()
    if not texto:
        texto = "¡el virus amenaza!"
    
    print(f"\nTexto: '{texto}'")
    
    # Tokenización
    tokens = tokenize(texto)
    print(f"Tokens: {tokens}\n")
    
    # Parsing
    arboles, chart = chart_parser(tokens, gramatica)
    
    if arboles:
        print(f"✓ Se encontraron {len(arboles)} árbol(es)\n")
        for i, arbol in enumerate(arboles):
            print(f"Árbol {i+1}:")
            print(arbol)
    else:
        print("❌ No se encontraron derivaciones válidas.")


def opcion_3_convertir_dag():
    """Opción 3: Convertir árbol a DAG"""
    print("\n" + "-"*70)
    print("OPCIÓN 3: CONVERTIR A DAG")
    print("-"*70 + "\n")
    
    texto = input("Ingrese el texto a analizar: ").strip()
    if not texto:
        texto = "¡el virus amenaza!"
    
    print(f"\nTexto: '{texto}'")
    
    # Tokenización y parsing
    tokens = tokenize(texto)
    arboles, _ = chart_parser(tokens, gramatica)
    
    if not arboles:
        print("❌ No se encontraron derivaciones.")
        return
    
    for i, arbol in enumerate(arboles):
        print(f"\n--- Árbol Original {i+1} ---")
        print(arbol)
        
        print(f"\n--- DAG Comprimido {i+1} ---")
        dag = DAG()
        root = dag.build_from_tree(arbol)
        print(dag_to_string(root))
        
        print("\n--- Estadísticas ---")
        stats = tree_to_dag_stats(arbol, dag)
        for clave, valor in stats.items():
            print(f"  {clave}: {valor}")


def opcion_4_extraer_componentes():
    """Opción 4: Extraer componentes"""
    print("\n" + "-"*70)
    print("OPCIÓN 4: EXTRAER COMPONENTES")
    print("-"*70 + "\n")
    
    texto = input("Ingrese el texto a analizar: ").strip()
    if not texto:
        texto = "¡el virus amenaza!"
    
    print(f"\nTexto: '{texto}'")
    
    # Tokenización y parsing
    tokens = tokenize(texto)
    arboles, _ = chart_parser(tokens, gramatica)
    
    if not arboles:
        print("❌ No se encontraron derivaciones.")
        return
    
    extraer_componentes(arboles[0])


def extraer_componentes(arbol):
    """Extrae componentes de un árbol usando unificación"""
    
    def nodo_to_compound(nodo):
        """Convierte Nodo a Compound para unificar"""
        if not isinstance(nodo, Nodo):
            return Atom(str(nodo))
        
        hijos = []
        for hijo in nodo.hijos:
            hijos.append(nodo_to_compound(hijo))
        
        return Compound(nodo.etiqueta, hijos)
    
    tree_comp = nodo_to_compound(arbol)
    
    # Extraer estructura principal
    patrón = Compound("S", [Variable("X"), Variable("Y")])
    subst = unify(patrón, tree_comp)
    
    if subst:
        print("✓ Estructura S encontrada")
        x = subst.apply(Variable("X"))
        y = subst.apply(Variable("Y"))
        
        if hasattr(x, 'functor'):
            print(f"  Componente 1 ({x.functor})")
        if hasattr(y, 'functor'):
            print(f"  Componente 2 ({y.functor})")


def opcion_5_ver_dcg():
    """Opción 5: Ver gramática DCG"""
    print("\n" + "-"*70)
    print("OPCIÓN 5: GRAMÁTICA DCG")
    print("-"*70 + "\n")
    
    # Crear gramática DCG simplificada
    dcg = DCGGrammar()
    
    reglas = [
        ("S", [], ["NP", "VP"]),
        ("NP", [], ["Det", "N"]),
        ("NP", [], ["Det", "ADJ", "N"]),
        ("VP", [], ["V"]),
        ("VP", [], ["V", "NP"]),
        ("Det", [], ["el"]),
        ("Det", [], ["la"]),
        ("N", [], ["virus"]),
        ("N", [], ["amenaza"]),
        ("V", [], ["amenaza"]),
        ("V", [], ["causa"]),
        ("ADJ", [], ["peligroso"]),
    ]
    
    for lhs, args, body in reglas:
        dcg.add_rule(lhs, args, body)
    
    print("Gramática DCG:")
    print(dcg)
    
    # Mostrar expansión de una regla
    print("\n" + "-"*70)
    print("Ejemplo de Expansión a Prolog:")
    print("-"*70 + "\n")
    
    rule = dcg.get_rules("S")[0]
    head, body_goals = expand_dcg_rule(rule)
    
    print(f"Regla DCG:  S --> NP, VP")
    print(f"Cabeza:     {head}")
    print(f"Cuerpo:     {[str(g) for g in body_goals]}\n")


def main():
    """Función principal"""
    while True:
        mostrar_menu()
        opcion = input("Seleccione una opción (1-6): ").strip()
        
        if opcion == "1":
            opcion_1_analisis_completo()
        elif opcion == "2":
            opcion_2_chart_parser()
        elif opcion == "3":
            opcion_3_convertir_dag()
        elif opcion == "4":
            opcion_4_extraer_componentes()
        elif opcion == "5":
            opcion_5_ver_dcg()
        elif opcion == "6":
            print("\n¡Hasta luego!")
            break
        else:
            print("❌ Opción no válida.")
        
        input("\nPresione Enter para continuar...")


if __name__ == "__main__":
    main()
