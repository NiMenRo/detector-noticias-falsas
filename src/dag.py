"""
DAGs como Estructuras de Rasgos (Feature Structures)
Basado en la lógica de la Universidad del Valle
Representación de información lingüística mediante diccionarios anidados
"""


class FeatureStructure:
    """
    Estructura de rasgos (DAG) como diccionario anidado.
    Representa información lingüística de palabras y sintagmas.
    """
    
    def __init__(self, rasgos=None):
        """
        Inicializa una estructura de rasgos.
        
        Args:
            rasgos (dict): Diccionario con los rasgos lingüísticos
        """
        self.rasgos = rasgos if rasgos else {}
    
    def __repr__(self):
        """Representación textual de la estructura"""
        return str(self.rasgos)
    
    def __getitem__(self, key):
        """Acceso a rasgos como diccionario"""
        return self.rasgos[key]
    
    def get(self, key, default=None):
        """Get con valor por defecto"""
        return self.rasgos.get(key, default)
    
    def items(self):
        """Iterar sobre pares rasgo-valor"""
        return self.rasgos.items()
    
    def mostrar(self, indent=0):
        """
        Imprime la estructura de forma legible y anidada.
        
        Args:
            indent (int): Nivel de indentación
        """
        espacios = "  " * indent
        for rasgo, valor in self.rasgos.items():
            if isinstance(valor, dict):
                print(f"{espacios}{rasgo}:")
                self._mostrar_dict(valor, indent + 1)
            elif isinstance(valor, FeatureStructure):
                print(f"{espacios}{rasgo}:")
                valor.mostrar(indent + 1)
            else:
                print(f"{espacios}{rasgo}: {valor}")
    
    def _mostrar_dict(self, d, indent):
        """Ayuda para mostrar diccionarios anidados"""
        espacios = "  " * indent
        for rasgo, valor in d.items():
            if isinstance(valor, dict):
                print(f"{espacios}{rasgo}:")
                self._mostrar_dict(valor, indent + 1)
            else:
                print(f"{espacios}{rasgo}: {valor}")


def crear_dag_palabra(palabra, categoria, rasgos_adicionales=None):
    """
    Crea un DAG para una palabra individual.
    
    Args:
        palabra (str): La palabra
        categoria (str): Categoría gramatical (det, n, v, adj, etc.)
        rasgos_adicionales (dict): Rasgos adicionales específicos
    
    Retorna:
        dict: DAG con la estructura de la palabra
    """
    dag = {
        'cat': categoria,
        'forma': palabra
    }
    
    if rasgos_adicionales:
        dag.update(rasgos_adicionales)
    
    return dag


def crear_dag_sintagma(categoria, componentes, rasgos_concordancia=None):
    """
    Crea un DAG para un sintagma.
    
    Args:
        categoria (str): Categoría del sintagma (np, vp, pp, etc.)
        componentes (dict): Componentes del sintagma
        rasgos_concordancia (dict): Rasgos de concordancia
    
    Retorna:
        dict: DAG del sintagma
    """
    dag = {
        'cat': categoria,
        'componentes': componentes
    }
    
    if rasgos_concordancia:
        dag['concordancia'] = rasgos_concordancia
    
    return dag


def crear_dag_oracion(np, vp, rasgos_adicionales=None):
    """
    Crea un DAG para una oración completa.
    
    Args:
        np (dict): DAG del sintagma nominal
        vp (dict): DAG del sintagma verbal
        rasgos_adicionales (dict): Información adicional
    
    Retorna:
        dict: DAG de la oración
    """
    oracion = {
        'cat': 'S',
        'sujeto': np,
        'predicado': vp,
        'concordancia': {
            'numero': np.get('num')
        }
    }
    
    if rasgos_adicionales:
        oracion.update(rasgos_adicionales)
    
    return oracion


def extraer_subcadena_dag(dag, ruta):
    """
    Extrae un sub-DAG siguiendo una ruta de acceso.
    
    Args:
        dag (dict): DAG de entrada
        ruta (list): Ruta de claves (ej: ['np', 'det'])
    
    Retorna:
        dict: Sub-DAG encontrado, o None si no existe
    
    Ejemplo:
        >>> dag = {'np': {'det': 'el', 'n': 'gato'}, 'vp': {'v': 'corre'}}
        >>> extraer_subcadena_dag(dag, ['np', 'det'])
        'el'
    """
    actual = dag
    
    for clave in ruta:
        if isinstance(actual, dict) and clave in actual:
            actual = actual[clave]
        else:
            return None
    
    return actual


def contar_nodos(dag):
    """
    Cuenta el número total de nodos en un DAG.
    
    Args:
        dag (dict): DAG a contar
    
    Retorna:
        int: Número de nodos
    """
    if not isinstance(dag, dict):
        return 1
    
    count = 1
    for valor in dag.values():
        if isinstance(valor, dict):
            count += contar_nodos(valor)
        elif isinstance(valor, (list, tuple)):
            for item in valor:
                if isinstance(item, dict):
                    count += contar_nodos(item)
    
    return count


def profundidad_dag(dag):
    """
    Calcula la profundidad máxima de un DAG.
    
    Args:
        dag (dict): DAG a analizar
    
    Retorna:
        int: Profundidad máxima
    """
    if not isinstance(dag, dict):
        return 0
    
    if not dag:
        return 1
    
    max_prof = 1
    for valor in dag.values():
        if isinstance(valor, dict):
            prof = profundidad_dag(valor)
            max_prof = max(max_prof, prof + 1)
    
    return max_prof


def comparar_dags(dag1, dag2):
    """
    Compara dos DAGs y retorna sus diferencias.
    
    Args:
        dag1 (dict): Primer DAG
        dag2 (dict): Segundo DAG
    
    Retorna:
        dict: Información sobre diferencias
    """
    diferencias = {
        'solo_en_dag1': [],
        'solo_en_dag2': [],
        'valores_diferentes': []
    }
    
    todas_claves = set(dag1.keys()) | set(dag2.keys())
    
    for clave in todas_claves:
        if clave not in dag1:
            diferencias['solo_en_dag2'].append(clave)
        elif clave not in dag2:
            diferencias['solo_en_dag1'].append(clave)
        elif dag1[clave] != dag2[clave]:
            diferencias['valores_diferentes'].append(clave)
    
    return diferencias


def estadisticas_dag(dag):
    """
    Calcula estadísticas de un DAG.
    
    Args:
        dag (dict): DAG a analizar
    
    Retorna:
        dict: Estadísticas incluye nodos, profundidad, etc.
    """
    return {
        'nodos': contar_nodos(dag),
        'profundidad': profundidad_dag(dag),
        'rasgos_top': len(dag) if isinstance(dag, dict) else 0
    }

