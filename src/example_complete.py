"""
Ejemplo Completo: Usando Unificación, DCG y DAG juntos
Demuestra el flujo completo de análisis sintáctico con PLN.
"""

from unification import (
    Variable, Atom, Compound, Substitution,
    unify, get_variables
)
from dcg import DCGGrammar, expand_dcg_rule
from dag import DAG, dag_to_string, tree_to_dag_stats
from nodes import Nodo
from lexer import tokenize
from grammar import gramatica
from chart_parser import chart_parser


def ejemplo_1_unificacion_simple():
    """Ejemplo 1: Unificación simple para extracción de patrones"""
    print("\n" + "="*70)
    print("EJEMPLO 1: UNIFICACIÓN PARA EXTRACCIÓN DE PATRONES")
    print("="*70 + "\n")
    
    # Patrón de regla sintáctica: S -> NP VP
    patrón = Compound("s", [Variable("NP"), Variable("VP")])
    
    # Instancia parseada del Chart Parser
    instancia = Compound("s", [
        Compound("np", [Atom("el"), Atom("virus")]),
        Compound("vp", [Atom("amenaza")])
    ])
    
    print(f"Patrón:   {patrón}")
    print(f"Instancia: {instancia}\n")
    
    # Unificar
    subst = unify(patrón, instancia)
    
    if subst:
        print(f"✓ Unificación exitosa: {subst}\n")
        
        # Extraer componentes
        np = subst.apply(Variable("NP"))
        vp = subst.apply(Variable("VP"))
        
        print(f"Componente NP: {np}")
        print(f"Componente VP: {vp}\n")
        
        # Unificar NP con sub-patrón
        patrón_np = Compound("np", [Variable("Det"), Variable("N")])
        subst_np = unify(patrón_np, np)
        
        if subst_np:
            print("Análisis de NP:")
            print(f"  Determinante: {subst_np.apply(Variable('Det'))}")
            print(f"  Nombre: {subst_np.apply(Variable('N'))}\n")


def ejemplo_2_dcg_expansion():
    """Ejemplo 2: Expansión de reglas DCG a Prolog"""
    print("\n" + "="*70)
    print("EJEMPLO 2: EXPANSIÓN DCG A CLÁUSULAS PROLOG")
    print("="*70 + "\n")
    
    # Crear gramática DCG
    dcg = DCGGrammar()
    
    reglas = [
        ("s", [], ["np", "vp"]),
        ("np", [], ["det", "n"]),
        ("vp", [], ["v", "np"]),
        ("det", [], ["el"]),
        ("n", [], ["virus"]),
        ("v", [], ["amenaza"]),
    ]
    
    for lhs, args, body in reglas:
        dcg.add_rule(lhs, args, body)
    
    print("Gramática DCG:")
    for lhs, args, body in reglas:
        print(f"  {lhs} --> {' '.join(body)}\n")
    
    # Expandir cada regla
    print("Expansión a cláusulas Prolog (con threading):\n")
    
    for functor in ["s", "np", "vp"]:
        rule = dcg.get_rules(functor)[0]
        head, body_goals = expand_dcg_rule(rule)
        
        print(f"{functor}:")
        print(f"  Cabeza:  {head}")
        print(f"  Cuerpo: {[str(g) for g in body_goals]}\n")


def ejemplo_3_dag_compresion():
    """Ejemplo 3: Compresión de árbol a DAG"""
    print("\n" + "="*70)
    print("EJEMPLO 3: COMPRESIÓN ÁRBOL → DAG")
    print("="*70 + "\n")
    
    # Construir árbol con duplicados
    det_el = Nodo("Det", ["el"])
    n_virus = Nodo("N", ["virus"])
    
    # Crear dos NPs idénticos
    np1 = Nodo("NP", [det_el, n_virus])
    np2 = Nodo("NP", [Nodo("Det", ["el"]), Nodo("N", ["virus"])])
    
    arbol = Nodo("S", [
        np1,
        Nodo("VP", [Nodo("V", ["amenaza"]), np2])
    ])
    
    print("Árbol Original:")
    print(arbol)
    
    # Convertir a DAG
    dag = DAG()
    root = dag.build_from_tree(arbol)
    
    print("\n" + "="*70)
    print("DAG Comprimido:")
    print("="*70 + "\n")
    print(dag_to_string(root))
    
    # Estadísticas
    stats = tree_to_dag_stats(arbol, dag)
    print("\nEstadísticas de Compresión:")
    for clave, valor in stats.items():
        print(f"  {clave}: {valor}")


def ejemplo_4_flujo_completo():
    """Ejemplo 4: Flujo completo de análisis"""
    print("\n" + "="*70)
    print("EJEMPLO 4: FLUJO COMPLETO DE ANÁLISIS")
    print("="*70 + "\n")
    
    # Texto de entrada
    texto = "¡el virus amenaza!"
    print(f"Texto de entrada: '{texto}'\n")
    
    # PASO 1: Tokenización
    print("PASO 1: Tokenización")
    print("-" * 70)
    tokens = tokenize(texto)
    print(f"Tokens: {tokens}\n")
    
    # PASO 2: Parsing con Chart Parser
    print("PASO 2: Parsing con Chart Parser")
    print("-" * 70)
    arboles, chart = chart_parser(tokens, gramatica)
    print(f"Árboles encontrados: {len(arboles)}\n")
    
    # PASO 3: Para cada árbol
    for i, arbol in enumerate(arboles):
        print(f"PASO 3: Análisis del Árbol {i+1}")
        print("-" * 70)
        
        print("Árbol de Derivación:")
        print(arbol)
        
        # PASO 4: Convertir a DAG
        print("\nPASO 4: Convertir a DAG")
        print("-" * 70)
        
        dag = DAG()
        root = dag.build_from_tree(arbol)
        
        print(dag_to_string(root))
        
        # PASO 5: Estadísticas
        print("\nPASO 5: Estadísticas")
        print("-" * 70)
        
        stats = tree_to_dag_stats(arbol, dag)
        for clave, valor in stats.items():
            print(f"  {clave}: {valor}")
        
        # PASO 6: Extracción con Unificación
        print("\nPASO 6: Extracción de Componentes (Unificación)")
        print("-" * 70)
        
        # Convertir árbol Nodo a Compound para unificar
        def nodo_to_compound(nodo):
            if not isinstance(nodo, Nodo):
                return Atom(str(nodo))
            
            hijos_comp = []
            for hijo in nodo.hijos:
                hijos_comp.append(nodo_to_compound(hijo))
            
            return Compound(nodo.etiqueta, hijos_comp)
        
        tree_comp = nodo_to_compound(arbol)
        
        # Buscar estructura principal
        patrón_s = Compound("S", [Variable("X"), Variable("Y")])
        subst = unify(patrón_s, tree_comp)
        
        if subst:
            print(f"✓ Estructura S encontrada")
            x = subst.apply(Variable("X"))
            y = subst.apply(Variable("Y"))
            print(f"  Componente 1: {x.functor if hasattr(x, 'functor') else x}")
            print(f"  Componente 2: {y.functor if hasattr(y, 'functor') else y}")


def ejemplo_5_unificacion_multiples():
    """Ejemplo 5: Unificación con múltiples instancias"""
    print("\n" + "="*70)
    print("EJEMPLO 5: UNIFICACIÓN CON MÚLTIPLES INSTANCIAS")
    print("="*70 + "\n")
    
    # Patrón general
    patrón = Compound("vp", [Variable("V"), Variable("OBJ")])
    
    # Instancias diferentes
    instancias = [
        Compound("vp", [Atom("amenaza"), Atom("virus")]),
        Compound("vp", [Atom("come"), Compound("np", [Atom("ratón")])]),
        Compound("vp", [Atom("causa"), Compound("np", [Atom("pánico")])]),
    ]
    
    print(f"Patrón: {patrón}\n")
    print("Instancias:")
    for i, inst in enumerate(instancias, 1):
        print(f"  {i}. {inst}")
    
    print("\nResultados de Unificación:")
    print("-" * 70)
    
    for i, inst in enumerate(instancias, 1):
        subst = unify(patrón, inst)
        if subst:
            v = subst.apply(Variable("V"))
            obj = subst.apply(Variable("OBJ"))
            print(f"  {i}. V={v}, OBJ={obj}")


def main():
    """Ejecuta todos los ejemplos"""
    print("\n")
    print("#" * 70)
    print("# EJEMPLO COMPLETO: UNIFICACIÓN, DCG Y DAG EN PLN")
    print("#" * 70)
    
    ejemplo_1_unificacion_simple()
    ejemplo_2_dcg_expansion()
    ejemplo_3_dag_compresion()
    ejemplo_4_flujo_completo()
    ejemplo_5_unificacion_multiples()
    
    print("\n" + "="*70)
    print("FIN DE EJEMPLOS")
    print("="*70 + "\n")


if __name__ == "__main__":
    main()
