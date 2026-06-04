"""
Definite Clause Grammars (DCG) con Unificación de DAGs
Basado en la lógica de la Universidad del Valle
Parser que usa unificación de rasgos lingüísticos
"""

from unification import unificar, extraer_rasgos


class Parser:
    """
    Parser DCG que implementa unificación de rasgos.
    Analiza sintagmas nominales (NP), sintagmas verbales (VP) y oraciones (S).
    """
    
    def __init__(self, lexico, debug=True):
        """
        Inicializa el parser con un léxico de rasgos.
        
        Args:
            lexico (dict): Diccionario con palabras y sus DAGs de rasgos
            debug (bool): Si muestra pasos intermedios del análisis
        """
        self.lexico = lexico
        self.debug = debug
    
    def analizar_np(self, tokens, pos):
        """
        Analiza un Sintagma Nominal (NP = Determinante + Sustantivo).
        Verifica concordancia de género y número.
        
        Args:
            tokens (list): Lista de palabras
            pos (int): Posición inicial de análisis
        
        Retorna:
            tuple: (dag_np, nueva_posición) o (None, pos) si falla
        """
        if pos + 1 >= len(tokens):
            if self.debug:
                print(f"    ✗ NP: No hay suficientes tokens")
            return None, pos
        
        palabra_det = tokens[pos]
        palabra_n = tokens[pos + 1]
        
        # Verificar que ambas palabras estén en el léxico
        if palabra_det not in self.lexico:
            if self.debug:
                print(f"    ✗ NP: '{palabra_det}' no está en el léxico")
            return None, pos
        
        if palabra_n not in self.lexico:
            if self.debug:
                print(f"    ✗ NP: '{palabra_n}' no está en el léxico")
            return None, pos
        
        rasgos_det = self.lexico[palabra_det]
        rasgos_n = self.lexico[palabra_n]
        
        # Verificar que sean determinante y sustantivo
        if rasgos_det.get('cat') != 'det':
            if self.debug:
                print(f"    ✗ NP: '{palabra_det}' no es determinante")
            return None, pos
        
        if rasgos_n.get('cat') != 'n':
            if self.debug:
                print(f"    ✗ NP: '{palabra_n}' no es sustantivo")
            return None, pos
        
        # Extraer rasgos de concordancia
        concord_det = extraer_rasgos(rasgos_det, ['gen', 'num'])
        concord_n = extraer_rasgos(rasgos_n, ['gen', 'num'])
        
        # Unificar rasgos de concordancia
        unificado = unificar(concord_det, concord_n)
        
        if unificado is None:
            if self.debug:
                print(f"    ✗ NP: Conflicto '{palabra_det}' {concord_det} ≠ '{palabra_n}' {concord_n}")
            return None, pos
        
        # Construir estructura del NP
        np = {
            'cat': 'np',
            'gen': unificado['gen'],
            'num': unificado['num'],
            'det': palabra_det,
            'n': palabra_n
        }
        
        if self.debug:
            print(f"    ✓ NP: [{palabra_det} + {palabra_n}]  rasgos={unificado}")
        
        return np, pos + 2
    
    def analizar_vp(self, tokens, pos):
        """
        Analiza un Sintagma Verbal (VP = Verbo).
        Extrae número y acción semántica.
        
        Args:
            tokens (list): Lista de palabras
            pos (int): Posición inicial de análisis
        
        Retorna:
            tuple: (dag_vp, nueva_posición) o (None, pos) si falla
        """
        if pos >= len(tokens):
            if self.debug:
                print(f"    ✗ VP: No hay tokens")
            return None, pos
        
        palabra_v = tokens[pos]
        
        if palabra_v not in self.lexico:
            if self.debug:
                print(f"    ✗ VP: '{palabra_v}' no está en el léxico")
            return None, pos
        
        rasgos_v = self.lexico[palabra_v]
        
        if rasgos_v.get('cat') != 'v':
            if self.debug:
                print(f"    ✗ VP: '{palabra_v}' no es verbo")
            return None, pos
        
        vp = {
            'cat': 'vp',
            'num': rasgos_v['num'],
            'accion': rasgos_v['accion'],
            'v': palabra_v
        }
        
        if self.debug:
            print(f"    ✓ VP: [{palabra_v}]  accion='{rasgos_v['accion']}', num={rasgos_v['num']}")
        
        return vp, pos + 1
    
    def analizar_s(self, tokens):
        """
        Analiza una Oración (S = NP + VP).
        Verifica concordancia de número entre sujeto y predicado.
        
        Args:
            tokens (list): Lista de palabras
        
        Retorna:
            dict: DAG de la oración si es válida, None si falla
        """
        if self.debug:
            print(f"\n  Analizando: '{' '.join(tokens)}'")
        
        # Analizar NP (sujeto)
        np, pos = self.analizar_np(tokens, 0)
        if np is None:
            if self.debug:
                print(f"    ✗ S: No se reconoció el NP")
            return None
        
        # Analizar VP (predicado)
        vp, pos = self.analizar_vp(tokens, pos)
        if vp is None:
            if self.debug:
                print(f"    ✗ S: No se reconoció el VP")
            return None
        
        # Verificar que no haya tokens sobrantes
        if pos != len(tokens):
            if self.debug:
                print(f"    ✗ S: Tokens sobrantes: {tokens[pos:]}")
            return None
        
        # Verificar concordancia NP-VP
        concordancia = unificar({'num': np['num']}, {'num': vp['num']})
        if concordancia is None:
            if self.debug:
                print(f"    ✗ S: Conflicto sujeto-verbo: NP={np['num']} vs VP={vp['num']}")
            return None
        
        # Construir oración
        oracion = {
            'cat': 'S',
            'np': np,
            'vp': vp,
            'accion': vp['accion']
        }
        
        if self.debug:
            print(f"    ✓ Oración válida")
        
        return oracion
    
    def extraer_intencion(self, oracion):
        """
        Extrae la intención semántica de una oración parseada.
        
        Args:
            oracion (dict): DAG de la oración
        
        Retorna:
            str: Descripción de sujeto y acción
        """
        if oracion is None:
            return "→ Oración no válida"
        
        sujeto = f"{oracion['np']['det']} {oracion['np']['n']}"
        accion = oracion['accion']
        
        return f"→ Sujeto: '{sujeto}'  |  Acción: '{accion}'"


def crear_lexico_fake_news():
    """
    Crea un léxico especializado para detectar noticias falsas/sensacionalistas.
    
    Retorna:
        dict: Léxico con palabras y sus DAGs de rasgos
    """
    return {
        # Determinantes
        'el': {'cat': 'det', 'gen': 'masc', 'num': 'sing'},
        'la': {'cat': 'det', 'gen': 'fem', 'num': 'sing'},
        'los': {'cat': 'det', 'gen': 'masc', 'num': 'plur'},
        'las': {'cat': 'det', 'gen': 'fem', 'num': 'plur'},
        'un': {'cat': 'det', 'gen': 'masc', 'num': 'sing'},
        'una': {'cat': 'det', 'gen': 'fem', 'num': 'sing'},
        
        # Sustantivos (tema fake news)
        'virus': {'cat': 'n', 'gen': 'masc', 'num': 'sing', 'tema': 'salud'},
        'gobierno': {'cat': 'n', 'gen': 'masc', 'num': 'sing', 'tema': 'política'},
        'crisis': {'cat': 'n', 'gen': 'fem', 'num': 'sing', 'tema': 'economía'},
        'celula': {'cat': 'n', 'gen': 'fem', 'num': 'sing', 'tema': 'salud'},
        'cura': {'cat': 'n', 'gen': 'masc', 'num': 'sing', 'tema': 'salud'},
        'noticia': {'cat': 'n', 'gen': 'fem', 'num': 'sing', 'tema': 'media'},
        'plan': {'cat': 'n', 'gen': 'masc', 'num': 'sing', 'tema': 'conspiracy'},
        
        # Verbos (acciones sospechosas)
        'amenaza': {'cat': 'v', 'num': 'sing', 'accion': 'amenazar', 'sensacionalismo': True},
        'amenazan': {'cat': 'v', 'num': 'plur', 'accion': 'amenazar', 'sensacionalismo': True},
        'revela': {'cat': 'v', 'num': 'sing', 'accion': 'revelar', 'sensacionalismo': True},
        'revelan': {'cat': 'v', 'num': 'plur', 'accion': 'revelar', 'sensacionalismo': True},
        'causa': {'cat': 'v', 'num': 'sing', 'accion': 'causar', 'sensacionalismo': True},
        'causan': {'cat': 'v', 'num': 'plur', 'accion': 'causar', 'sensacionalismo': True},
        'descubre': {'cat': 'v', 'num': 'sing', 'accion': 'descubrir', 'sensacionalismo': True},
        'descubren': {'cat': 'v', 'num': 'plur', 'accion': 'descubrir', 'sensacionalismo': True},
        'oculta': {'cat': 'v', 'num': 'sing', 'accion': 'ocultar', 'sensacionalismo': True},
        'ocultan': {'cat': 'v', 'num': 'plur', 'accion': 'ocultar', 'sensacionalismo': True},
    }

