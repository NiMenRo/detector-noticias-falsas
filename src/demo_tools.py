"""
Demostraciones del Sistema de PLN
Basado en la lógica de la Universidad del Valle
"""

from unification import unificar, extraer_rasgos, combinar_dags, mostrar_dag
from dcg import Parser, crear_lexico_fake_news
from dag import FeatureStructure, estadisticas_dag


def demo_1_unificacion():
    """Demostración 1: Unificación básica de DAGs"""
    print("\n" + "="*70)
    print("DEMOSTRACIÓN 1: UNIFICACIÓN DE DAGs")
    print("="*70 + "\n")
    
    print("1. Unificación exitosa:")
    dag1 = {'gen': 'masc', 'num': 'sing'}
    dag2 = {'gen': 'masc', 'num': 'sing'}
    resultado = unificar(dag1, dag2)
    print(f"  DAG1: {dag1}")
    print(f"  DAG2: {dag2}")
    print(f"  Resultado: {resultado}\n")
    
    print("2. Unificación complementaria:")
    dag1 = {'cat': 'det', 'gen': 'masc'}
    dag2 = {'num': 'sing'}
    resultado = unificar(dag1, dag2)
    print(f"  DAG1: {dag1}")
    print(f"  DAG2: {dag2}")
    print(f"  Resultado: {resultado}\n")
    
    print("3. Conflicto de género:")
    dag1 = {'gen': 'masc', 'num': 'sing'}
    dag2 = {'gen': 'fem', 'num': 'sing'}
    resultado = unificar(dag1, dag2)
    print(f"  DAG1: {dag1}")
    print(f"  DAG2: {dag2}")
    print(f"  Resultado: {resultado} (None = conflicto)\n")
    
    print("4. Unificación anidada:")
    dag1 = {
        'cat': 'np',
        'concordancia': {'gen': 'masc', 'num': 'sing'}
    }
    dag2 = {
        'concordancia': {'gen': 'masc', 'num': 'sing'},
        'componentes': {'det': 'el', 'n': 'gato'}
    }
    resultado = unificar(dag1, dag2)
    print(f"  DAG1: {dag1}")
    print(f"  DAG2: {dag2}")
    print(f"  Resultado unificado:")
    mostrar_dag(resultado, indent=2)


def demo_2_parser():
    """Demostración 2: Parser con unificación"""
    print("\n" + "="*70)
    print("DEMOSTRACIÓN 2: PARSER DCG CON UNIFICACIÓN")
    print("="*70 + "\n")
    
    lexico = {
        'el': {'cat': 'det', 'gen': 'masc', 'num': 'sing'},
        'la': {'cat': 'det', 'gen': 'fem', 'num': 'sing'},
        'los': {'cat': 'det', 'gen': 'masc', 'num': 'plur'},
        'las': {'cat': 'det', 'gen': 'fem', 'num': 'plur'},
        
        'gato': {'cat': 'n', 'gen': 'masc', 'num': 'sing'},
        'gata': {'cat': 'n', 'gen': 'fem', 'num': 'sing'},
        'gatos': {'cat': 'n', 'gen': 'masc', 'num': 'plur'},
        'niñas': {'cat': 'n', 'gen': 'fem', 'num': 'plur'},
        
        'corre': {'cat': 'v', 'num': 'sing', 'accion': 'correr'},
        'corren': {'cat': 'v', 'num': 'plur', 'accion': 'correr'},
        'juega': {'cat': 'v', 'num': 'sing', 'accion': 'jugar'},
        'juegan': {'cat': 'v', 'num': 'plur', 'accion': 'jugar'},
    }
    
    parser = Parser(lexico, debug=True)
    
    oraciones_prueba = [
        (["el", "gato", "corre"], "✓ Correcto - masc sing"),
        (["la", "gata", "corre"], "✓ Correcto - fem sing"),
        (["los", "gatos", "corren"], "✓ Correcto - masc plur"),
        (["las", "niñas", "juegan"], "✓ Correcto - fem plur"),
        (["el", "gata", "corre"], "✗ ERROR género: det masc, n fem"),
        (["los", "gatos", "corre"], "✗ ERROR número: NP plur, VP sing"),
    ]
    
    print("Pruebas de parsing:")
    print("-" * 70)
    
    for tokens, descripcion in oraciones_prueba:
        print(f"\n[{descripcion}]")
        oracion = parser.analizar_s(tokens)
        print(f"{parser.extraer_intencion(oracion)}\n")


def demo_3_lexico_fake_news():
    """Demostración 3: Léxico especializado para fake news"""
    print("\n" + "="*70)
    print("DEMOSTRACIÓN 3: LÉXICO ESPECIALIZADO PARA FAKE NEWS")
    print("="*70 + "\n")
    
    lexico = crear_lexico_fake_news()
    parser = Parser(lexico, debug=True)
    
    print("Analizando textos sensacionalistas...")
    print("-" * 70)
    
    textos = [
        (["el", "virus", "amenaza"], "Tema: salud, Verbo alarmista"),
        (["la", "celula", "revela"], "Tema: salud, Verbo revelador"),
        (["el", "gobierno", "oculta"], "Tema: política, Verbo conspiración"),
        (["la", "crisis", "causa"], "Tema: economía, Verbo de amenaza"),
    ]
    
    for tokens, descripcion in textos:
        print(f"\n[{descripcion}]")
        print(f"  Tokens: {tokens}")
        oracion = parser.analizar_s(tokens)
        if oracion:
            print(f"  {parser.extraer_intencion(oracion)}")
            if oracion['vp'].get('sensacionalismo'):
                print(f"  ⚠️  ALERTA: Lenguaje sensacionalista detectado")
        else:
            print(f"  No se pudo analizar")


def demo_4_feature_structures():
    """Demostración 4: Estructuras de rasgos (Feature Structures)"""
    print("\n" + "="*70)
    print("DEMOSTRACIÓN 4: ESTRUCTURAS DE RASGOS")
    print("="*70 + "\n")
    
    print("1. Feature Structure simple:")
    fs = FeatureStructure({
        'cat': 'np',
        'gen': 'masc',
        'num': 'sing'
    })
    print(f"  {fs}")
    
    print("\n2. Feature Structure anidada:")
    fs_compleja = FeatureStructure({
        'cat': 'S',
        'sujeto': {
            'cat': 'np',
            'det': 'el',
            'n': 'gato',
            'concordancia': {'gen': 'masc', 'num': 'sing'}
        },
        'predicado': {
            'cat': 'vp',
            'v': 'corre',
            'accion': 'correr'
        }
    })
    print("  Estructura:")
    fs_compleja.mostrar(indent=2)


def demo_5_estadisticas():
    """Demostración 5: Estadísticas de DAGs"""
    print("\n" + "="*70)
    print("DEMOSTRACIÓN 5: ESTADÍSTICAS DE DAGs")
    print("="*70 + "\n")
    
    dag_simple = {'cat': 'n', 'gen': 'masc'}
    dag_complejo = {
        'cat': 'S',
        'np': {
            'cat': 'np',
            'det': 'el',
            'n': 'gato',
            'concordancia': {'gen': 'masc', 'num': 'sing'}
        },
        'vp': {
            'cat': 'vp',
            'v': 'corre',
            'accion': 'correr',
            'modificadores': {
                'adverbio': 'rápidamente'
            }
        }
    }
    
    print("1. DAG Simple:")
    print(f"  Estructura: {dag_simple}")
    stats = estadisticas_dag(dag_simple)
    print(f"  Nodos: {stats['nodos']}")
    print(f"  Profundidad: {stats['profundidad']}")
    print(f"  Rasgos top-level: {stats['rasgos_top']}\n")
    
    print("2. DAG Complejo:")
    print(f"  Estructura:")
    mostrar_dag(dag_complejo, indent=2)
    stats = estadisticas_dag(dag_complejo)
    print(f"\n  Nodos: {stats['nodos']}")
    print(f"  Profundidad: {stats['profundidad']}")
    print(f"  Rasgos top-level: {stats['rasgos_top']}")


def main():
    """Ejecuta todas las demostraciones"""
    print("\n" + "#"*70)
    print("# DEMOSTRACIONES: SISTEMA DE PLN")
    print("# Basado en Lógica de Universidad del Valle")
    print("#"*70)
    
    demo_1_unificacion()
    demo_2_parser()
    demo_3_lexico_fake_news()
    demo_4_feature_structures()
    demo_5_estadisticas()
    
    print("\n" + "="*70)
    print("FIN DE DEMOSTRACIONES")
    print("="*70 + "\n")


if __name__ == "__main__":
    main()

