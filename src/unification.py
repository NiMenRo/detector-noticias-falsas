"""
Sistema de Unificación de DAGs (Diccionarios)
Basado en la lógica de la Universidad del Valle
Unifica dos DAGs (diccionarios de rasgos lingüísticos)
"""


def unificar(dag1, dag2):
    """
    Unifica dos DAGs (diccionarios de rasgos).
    
    La idea es combinar dos DAGs en uno:
    - Si ambos tienen el mismo rasgo con el mismo valor → se fusionan
    - Si tienen el mismo rasgo con valores distintos → conflicto, retorna None
    - Si un rasgo solo existe en uno → se agrega al resultado
    
    Arg:
        dag1 (dict): Primer DAG con rasgos lingüísticos
        dag2 (dict): Segundo DAG con rasgos lingüísticos
    
    Retorna:
        dict: DAG unificado, o None si hay conflicto
    
    Ejemplo:
        >>> unificar({'gen': 'masc', 'num': 'sing'}, {'gen': 'masc'})
        {'gen': 'masc', 'num': 'sing'}
        
        >>> unificar({'gen': 'masc'}, {'gen': 'fem'})
        None  # Conflicto
    """
    # Empezamos con una copia de dag1
    resultado = dict(dag1)
    
    # Recorremos cada rasgo del segundo DAG
    for rasgo, valor in dag2.items():
        
        if rasgo in resultado:
            # El rasgo ya existe en resultado — verificar compatibilidad
            
            if isinstance(resultado[rasgo], dict) and isinstance(valor, dict):
                # Ambos valores son sub-DAGs → unificar recursivamente
                sub = unificar(resultado[rasgo], valor)
                if sub is None:
                    return None
                resultado[rasgo] = sub
            
            elif resultado[rasgo] != valor:
                # Mismo rasgo, valores distintos → CONFLICTO
                return None
            
            # Si los valores son iguales, no hay nada que hacer
        
        else:
            # El rasgo no existía en dag1, agregarlo
            resultado[rasgo] = valor
    
    return resultado


def extraer_rasgos(dag, rasgos_lista):
    """
    Extrae solo ciertos rasgos de un DAG.
    
    Args:
        dag (dict): DAG de entrada
        rasgos_lista (list): Lista de claves a extraer
    
    Retorna:
        dict: DAG con solo los rasgos solicitados
    
    Ejemplo:
        >>> dag = {'cat': 'n', 'gen': 'masc', 'num': 'sing', 'sem': 'animal'}
        >>> extraer_rasgos(dag, ['gen', 'num'])
        {'gen': 'masc', 'num': 'sing'}
    """
    return {rasgo: dag[rasgo] for rasgo in rasgos_lista if rasgo in dag}


def combinar_dags(lista_dags):
    """
    Combina múltiples DAGs en uno solo (si es posible).
    
    Args:
        lista_dags (list): Lista de DAGs a combinar
    
    Retorna:
        dict: DAG combinado, o None si hay conflictos
    """
    if not lista_dags:
        return {}
    
    resultado = dict(lista_dags[0])
    
    for dag in lista_dags[1:]:
        resultado = unificar(resultado, dag)
        if resultado is None:
            return None
    
    return resultado


def dag_compatible(dag1, dag2):
    """
    Verifica si dos DAGs son compatibles (unificables).
    
    Args:
        dag1 (dict): Primer DAG
        dag2 (dict): Segundo DAG
    
    Retorna:
        bool: True si se pueden unificar, False si hay conflicto
    """
    return unificar(dag1, dag2) is not None


def mostrar_dag(dag, indent=0):
    """
    Imprime un DAG de forma legible.
    
    Args:
        dag (dict): DAG a mostrar
        indent (int): Nivel de indentación
    """
    espacios = "  " * indent
    for rasgo, valor in dag.items():
        if isinstance(valor, dict):
            print(f"{espacios}{rasgo}:")
            mostrar_dag(valor, indent + 1)
        else:
            print(f"{espacios}{rasgo}: {valor}")

