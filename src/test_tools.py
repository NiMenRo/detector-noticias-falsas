"""
Tests Unitarios - Unificación de DAGs, Parser DCG y Estructuras de Rasgos
Basado en la lógica de la Universidad del Valle
"""

from unification import unificar, extraer_rasgos, combinar_dags
from dcg import Parser, crear_lexico_fake_news
from dag import FeatureStructure, crear_dag_palabra, crear_dag_sintagma, estadisticas_dag


class TestUnificacion:
    """Tests para el algoritmo de unificación de DAGs"""
    
    @staticmethod
    def test_unificacion_basica():
        """Unificación simple de rasgos idénticos"""
        dag1 = {'gen': 'masc', 'num': 'sing'}
        dag2 = {'gen': 'masc', 'num': 'sing'}
        resultado = unificar(dag1, dag2)
        assert resultado == dag1, "Rasgos idénticos deben unificarse"
        print("✓ test_unificacion_basica")
    
    @staticmethod
    def test_unificacion_complementaria():
        """Rasgos distintos pero no contradictorios se complementan"""
        dag1 = {'cat': 'det', 'gen': 'masc'}
        dag2 = {'num': 'sing'}
        resultado = unificar(dag1, dag2)
        assert resultado == {'cat': 'det', 'gen': 'masc', 'num': 'sing'}
        print("✓ test_unificacion_complementaria")
    
    @staticmethod
    def test_unificacion_conflicto_genero():
        """Conflicto de género → None"""
        dag1 = {'gen': 'masc', 'num': 'sing'}
        dag2 = {'gen': 'fem', 'num': 'sing'}
        resultado = unificar(dag1, dag2)
        assert resultado is None, "Géneros diferentes deben fallar"
        print("✓ test_unificacion_conflicto_genero")
    
    @staticmethod
    def test_unificacion_conflicto_numero():
        """Conflicto de número → None"""
        dag1 = {'num': 'sing'}
        dag2 = {'num': 'plur'}
        resultado = unificar(dag1, dag2)
        assert resultado is None, "Números diferentes deben fallar"
        print("✓ test_unificacion_conflicto_numero")
    
    @staticmethod
    def test_unificacion_anidada():
        """Unificación de DAGs anidados"""
        dag1 = {
            'cat': 'np',
            'concordancia': {'gen': 'masc', 'num': 'sing'}
        }
        dag2 = {
            'concordancia': {'gen': 'masc', 'num': 'sing'}
        }
        resultado = unificar(dag1, dag2)
        assert resultado is not None, "DAGs anidados deben unificarse"
        print("✓ test_unificacion_anidada")
    
    @staticmethod
    def test_extraer_rasgos():
        """Extracción de rasgos específicos"""
        dag = {'cat': 'n', 'gen': 'masc', 'num': 'sing', 'sem': 'animal'}
        extraidos = extraer_rasgos(dag, ['gen', 'num'])
        assert extraidos == {'gen': 'masc', 'num': 'sing'}
        print("✓ test_extraer_rasgos")
    
    @staticmethod
    def test_combinar_multiples_dags():
        """Combinar múltiples DAGs"""
        dags = [
            {'cat': 'n'},
            {'gen': 'masc'},
            {'num': 'sing'}
        ]
        resultado = combinar_dags(dags)
        assert resultado == {'cat': 'n', 'gen': 'masc', 'num': 'sing'}
        print("✓ test_combinar_multiples_dags")


class TestParser:
    """Tests para el Parser DCG con unificación"""
    
    @staticmethod
    def test_parser_np_valido():
        """Parsear NP válido"""
        lexico = {
            'el': {'cat': 'det', 'gen': 'masc', 'num': 'sing'},
            'gato': {'cat': 'n', 'gen': 'masc', 'num': 'sing'},
            'corre': {'cat': 'v', 'num': 'sing', 'accion': 'correr'}
        }
        parser = Parser(lexico, debug=False)
        np, pos = parser.analizar_np(['el', 'gato', 'corre'], 0)
        
        assert np is not None, "NP válido debe parsearse"
        assert np['det'] == 'el'
        assert np['n'] == 'gato'
        print("✓ test_parser_np_valido")
    
    @staticmethod
    def test_parser_np_conflicto_genero():
        """NP con conflicto de género → falla"""
        lexico = {
            'el': {'cat': 'det', 'gen': 'masc', 'num': 'sing'},
            'gata': {'cat': 'n', 'gen': 'fem', 'num': 'sing'},
            'corre': {'cat': 'v', 'num': 'sing', 'accion': 'correr'}
        }
        parser = Parser(lexico, debug=False)
        np, pos = parser.analizar_np(['el', 'gata', 'corre'], 0)
        
        assert np is None, "NP con conflicto debe fallar"
        print("✓ test_parser_np_conflicto_genero")
    
    @staticmethod
    def test_parser_vp_valido():
        """Parsear VP válido"""
        lexico = {
            'corre': {'cat': 'v', 'num': 'sing', 'accion': 'correr'}
        }
        parser = Parser(lexico, debug=False)
        vp, pos = parser.analizar_vp(['corre'], 0)
        
        assert vp is not None, "VP válido debe parsearse"
        assert vp['accion'] == 'correr'
        print("✓ test_parser_vp_valido")
    
    @staticmethod
    def test_parser_oracion_valida():
        """Parsear oración válida"""
        lexico = {
            'el': {'cat': 'det', 'gen': 'masc', 'num': 'sing'},
            'gato': {'cat': 'n', 'gen': 'masc', 'num': 'sing'},
            'corre': {'cat': 'v', 'num': 'sing', 'accion': 'correr'}
        }
        parser = Parser(lexico, debug=False)
        oracion = parser.analizar_s(['el', 'gato', 'corre'])
        
        assert oracion is not None, "Oración válida debe parsearse"
        assert oracion['accion'] == 'correr'
        print("✓ test_parser_oracion_valida")
    
    @staticmethod
    def test_parser_oracion_conflicto_numero():
        """Oración con conflicto NP-VP → falla"""
        lexico = {
            'los': {'cat': 'det', 'gen': 'masc', 'num': 'plur'},
            'gatos': {'cat': 'n', 'gen': 'masc', 'num': 'plur'},
            'corre': {'cat': 'v', 'num': 'sing', 'accion': 'correr'}
        }
        parser = Parser(lexico, debug=False)
        oracion = parser.analizar_s(['los', 'gatos', 'corre'])
        
        assert oracion is None, "Conflicto número debe fallar"
        print("✓ test_parser_oracion_conflicto_numero")
    
    @staticmethod
    def test_extraer_intencion():
        """Extracción de intención semántica"""
        lexico = {
            'la': {'cat': 'det', 'gen': 'fem', 'num': 'sing'},
            'gata': {'cat': 'n', 'gen': 'fem', 'num': 'sing'},
            'corre': {'cat': 'v', 'num': 'sing', 'accion': 'correr'}
        }
        parser = Parser(lexico, debug=False)
        oracion = parser.analizar_s(['la', 'gata', 'corre'])
        intencion = parser.extraer_intencion(oracion)
        
        assert 'la gata' in intencion
        assert 'correr' in intencion
        print("✓ test_extraer_intencion")


class TestDAG:
    """Tests para estructuras de rasgos (DAGs)"""
    
    @staticmethod
    def test_feature_structure():
        """Crear y acceder a estructura de rasgos"""
        fs = FeatureStructure({'cat': 'n', 'gen': 'masc'})
        assert fs['cat'] == 'n'
        assert fs['gen'] == 'masc'
        print("✓ test_feature_structure")
    
    @staticmethod
    def test_crear_dag_palabra():
        """Crear DAG para una palabra"""
        dag = crear_dag_palabra('gato', 'n', {'gen': 'masc', 'num': 'sing'})
        assert dag['cat'] == 'n'
        assert dag['forma'] == 'gato'
        assert dag['gen'] == 'masc'
        print("✓ test_crear_dag_palabra")
    
    @staticmethod
    def test_crear_dag_sintagma():
        """Crear DAG para un sintagma"""
        det = {'forma': 'el', 'cat': 'det'}
        n = {'forma': 'gato', 'cat': 'n'}
        dag = crear_dag_sintagma('np', {'det': det, 'n': n})
        assert dag['cat'] == 'np'
        assert 'det' in dag['componentes']
        print("✓ test_crear_dag_sintagma")
    
    @staticmethod
    def test_estadisticas_dag():
        """Calcular estadísticas de DAG"""
        dag = {
            'cat': 'S',
            'np': {'cat': 'np', 'det': 'el', 'n': 'gato'},
            'vp': {'cat': 'vp', 'v': 'corre'}
        }
        stats = estadisticas_dag(dag)
        assert stats['nodos'] > 0
        assert stats['profundidad'] > 0
        print("✓ test_estadisticas_dag")


def run_all_tests():
    """Ejecuta todos los tests"""
    print("\n" + "="*70)
    print("TESTS: Unificación, Parser DCG y DAGs")
    print("="*70 + "\n")
    
    print("Tests de Unificación:")
    print("-" * 70)
    TestUnificacion.test_unificacion_basica()
    TestUnificacion.test_unificacion_complementaria()
    TestUnificacion.test_unificacion_conflicto_genero()
    TestUnificacion.test_unificacion_conflicto_numero()
    TestUnificacion.test_unificacion_anidada()
    TestUnificacion.test_extraer_rasgos()
    TestUnificacion.test_combinar_multiples_dags()
    
    print("\nTests del Parser DCG:")
    print("-" * 70)
    TestParser.test_parser_np_valido()
    TestParser.test_parser_np_conflicto_genero()
    TestParser.test_parser_vp_valido()
    TestParser.test_parser_oracion_valida()
    TestParser.test_parser_oracion_conflicto_numero()
    TestParser.test_extraer_intencion()
    
    print("\nTests de DAG:")
    print("-" * 70)
    TestDAG.test_feature_structure()
    TestDAG.test_crear_dag_palabra()
    TestDAG.test_crear_dag_sintagma()
    TestDAG.test_estadisticas_dag()
    
    print("\n" + "="*70)
    print("✓ TODOS LOS TESTS PASARON")
    print("="*70 + "\n")


if __name__ == "__main__":
    run_all_tests()

