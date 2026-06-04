"""
Augmented Transition Network (ATN) - Parser lingüístico avanzado
Basado en la lógica de la Universidad del Valle
Implementa redes de transición aumentadas para análisis sintáctico
"""


# ============================================================
# PARTE 1: LÉXICO Y FUNCIONES AUXILIARES
# ============================================================

class LexicoATN:
    """
    Gestiona el léxico para análisis ATN.
    Mapea palabras a categorías gramaticales.
    """
    
    def __init__(self, palabras=None):
        """
        Inicializa el léxico.
        
        Args:
            palabras (dict): Diccionario {palabra: categoría_gramatical}
        """
        self.palabras = palabras if palabras else {}
    
    def agregar(self, palabra, categoria):
        """Agrega una palabra al léxico"""
        self.palabras[palabra] = categoria
    
    def categoria(self, palabra):
        """
        Obtiene la categoría gramatical de una palabra.
        
        Args:
            palabra (str): La palabra a buscar
        
        Retorna:
            str: Categoría gramatical, o None si no está en el léxico
        """
        return self.palabras.get(palabra, None)
    
    def contiene(self, palabra):
        """Verifica si una palabra está en el léxico"""
        return palabra in self.palabras
    
    def __repr__(self):
        return f"LexicoATN({len(self.palabras)} palabras)"


def crear_lexico_sintactico():
    """
    Crea un léxico estándar para análisis sintáctico.
    Contiene determinantes, sustantivos y verbos.
    
    Retorna:
        LexicoATN: Léxico configurado
    """
    lexico = LexicoATN()
    
    # Determinantes
    for palabra in ["la", "el", "las", "los"]:
        lexico.agregar(palabra, "Det")
    
    # Sustantivos
    palabras_n = ["estudiante", "estudiantes", "libro", "libros", "gato", "gatos"]
    for palabra in palabras_n:
        lexico.agregar(palabra, "N")
    
    # Verbos
    verbos = ["lee", "leen", "ve", "ven"]
    for palabra in verbos:
        lexico.agregar(palabra, "V")
    
    return lexico


# ============================================================
# PARTE 2: SUBREDES ATN (NP, VP)
# ============================================================

class SubredATN:
    """
    Subred de la ATN que implementa un patrón de reconocimiento.
    Encapsula la lógica de análisis de un componente específico.
    """
    
    def __init__(self, nombre, lexico):
        """
        Inicializa una subred.
        
        Args:
            nombre (str): Identificador de la subred
            lexico (LexicoATN): Léxico compartido
        """
        self.nombre = nombre
        self.lexico = lexico
    
    def analizar(self, tokens, pos):
        """
        Analiza tokens desde una posición.
        Debe ser implementado por subclases.
        
        Args:
            tokens (list): Lista de palabras
            pos (int): Posición inicial
        
        Retorna:
            tuple: (resultado, nueva_posición) o (None, pos) si falla
        """
        raise NotImplementedError


class SubredNP(SubredATN):
    """
    Subred para Sintagmas Nominales.
    Patrón: Det → N
    """
    
    def analizar(self, tokens, pos):
        """
        Analiza un NP = Determinante + Sustantivo
        
        Arcos:
            1. CAT Det: verifica que el token sea determinante
            2. CAT N:   verifica que el siguiente sea sustantivo
            3. POP:     retorna estructura [det, n]
        """
        # Verificar que hay tokens disponibles
        if pos >= len(tokens):
            return None, pos
        
        # Arco 1: CAT Det
        if self.lexico.categoria(tokens[pos]) == "Det":
            det = tokens[pos]
            pos1 = pos + 1
            
            # Arco 2: CAT N
            if pos1 < len(tokens) and self.lexico.categoria(tokens[pos1]) == "N":
                n = tokens[pos1]
                
                # Arco 3: POP - retorna la estructura
                return [det, n], pos1 + 1
        
        # Si ningún arco funcionó, fallar limpiamente
        return None, pos


class SubredVP(SubredATN):
    """
    Subred para Sintagmas Verbales.
    Patrón: V → NP (verbo + objeto)
    """
    
    def __init__(self, nombre, lexico, subred_np=None):
        """
        Inicializa la subred VP.
        
        Args:
            nombre (str): Identificador
            lexico (LexicoATN): Léxico compartido
            subred_np (SubredNP): Referencia a la subred NP
        """
        super().__init__(nombre, lexico)
        self.subred_np = subred_np
    
    def analizar(self, tokens, pos):
        """
        Analiza un VP = Verbo + NP(objeto)
        
        Arcos:
            1. CAT V:      verifica que el token sea verbo
            2. PUSH NP:    llama recursivamente a red_np para el objeto
            3. POP:        retorna [verbo, objeto]
        """
        # Verificar que hay tokens disponibles
        if pos >= len(tokens):
            return None, pos
        
        # Arco 1: CAT V
        if self.lexico.categoria(tokens[pos]) == "V":
            v = tokens[pos]
            
            # Arco 2: PUSH NP (llamada recursiva a subred NP)
            if self.subred_np is not None:
                np, pos2 = self.subred_np.analizar(tokens, pos + 1)
                if np is not None:
                    # Arco 3: POP - retorna [verbo, objeto_np]
                    return [v, np], pos2
        
        # Si ningún arco funcionó, fallar
        return None, pos


# ============================================================
# PARTE 3: RED ATN PRINCIPAL
# ============================================================

class RedATN:
    """
    Red ATN completa que orquesta las subredes.
    Implementa el patrón: NP → VP
    """
    
    def __init__(self, lexico=None):
        """
        Inicializa la red ATN.
        
        Args:
            lexico (LexicoATN): Léxico a usar (crea uno por defecto si no se proporciona)
        """
        self.lexico = lexico if lexico else crear_lexico_sintactico()
        
        # Crear subredes
        self.subred_np = SubredNP("NP", self.lexico)
        self.subred_vp = SubredVP("VP", self.lexico, self.subred_np)
    
    def analizar_oracion(self, tokens):
        """
        Analiza una oración completa.
        
        Arcos principales:
            1. PUSH NP:  llama a red_np para obtener el sujeto
            2. PUSH VP:  llama a red_vp para obtener el predicado
            3. Validación: verifica que se consuman todos los tokens
            4. POP:      retorna {"SUBJ": np, "VP": vp}
        
        Args:
            tokens (list): Palabras de la oración
        
        Retorna:
            dict: Estructura de análisis, o None si falla
        """
        # Caso borde: lista vacía
        if not tokens:
            return None
        
        # Arco 1: PUSH NP (sujeto)
        np, pos1 = self.subred_np.analizar(tokens, 0)
        if np is None:
            return None
        
        # Arco 2: PUSH VP (predicado)
        vp, pos2 = self.subred_vp.analizar(tokens, pos1)
        if vp is None:
            return None
        
        # Validación: todos los tokens deben ser consumidos
        if pos2 != len(tokens):
            return None
        
        # Arco 3: POP final con estructura aumentada
        return {
            "cat": "S",
            "SUBJ": np,
            "VP": vp
        }
    
    def analizar_oracion_debug(self, tokens):
        """
        Versión con información de debugging.
        
        Args:
            tokens (list): Palabras de la oración
        
        Retorna:
            dict: Resultado del análisis con detalles
        """
        resultado = self.analizar_oracion(tokens)
        return {
            "tokens": tokens,
            "resultado": resultado,
            "exitoso": resultado is not None
        }


# ============================================================
# PARTE 4: FUNCIONES AUXILIARES DE ANÁLISIS
# ============================================================

def extraer_estructura_np(np):
    """
    Extrae componentes de una estructura NP.
    
    Args:
        np (list): Estructura [det, n]
    
    Retorna:
        dict: {"det": ..., "n": ...} o None si inválido
    """
    if isinstance(np, list) and len(np) == 2:
        return {"det": np[0], "n": np[1]}
    return None


def extraer_estructura_vp(vp):
    """
    Extrae componentes de una estructura VP.
    
    Args:
        vp (list): Estructura [v, np]
    
    Retorna:
        dict: {"v": ..., "objeto": ...} o None si inválido
    """
    if isinstance(vp, list) and len(vp) == 2:
        v, np = vp
        np_struct = extraer_estructura_np(np) if isinstance(np, list) else None
        return {
            "v": v,
            "objeto": np_struct if np_struct else np
        }
    return None


def generar_representacion_natural(oracion_atn):
    """
    Genera una representación natural de la salida de la ATN.
    
    Args:
        oracion_atn (dict): Salida de RedATN.analizar_oracion()
    
    Retorna:
        str: Descripción legible de la estructura analizada
    """
    if oracion_atn is None:
        return "Análisis fallido"
    
    subj = oracion_atn.get("SUBJ")
    vp = oracion_atn.get("VP")
    
    if not subj or not vp:
        return "Estructura incompleta"
    
    # Extraer componentes
    det_s, n_s = subj[0], subj[1]
    v, vp_obj = vp[0], vp[1]
    
    if isinstance(vp_obj, list) and len(vp_obj) == 2:
        det_o, n_o = vp_obj[0], vp_obj[1]
        return f"Sujeto: [{det_s} {n_s}] | Verbo: {v} | Objeto: [{det_o} {n_o}]"
    else:
        return f"Sujeto: [{det_s} {n_s}] | Verbo: {v}"


# ============================================================
# PARTE 5: ESTADÍSTICAS Y ANÁLISIS
# ============================================================

def estadisticas_analisis_atn(oracion_atn):
    """
    Calcula estadísticas del análisis ATN.
    
    Args:
        oracion_atn (dict): Resultado del análisis
    
    Retorna:
        dict: Estadísticas incluidas profundidad, complejidad, etc.
    """
    if oracion_atn is None:
        return {"valido": False, "profundidad": 0, "nodos": 0}
    
    def contar_nodos(estructura):
        if isinstance(estructura, dict):
            return 1 + sum(contar_nodos(v) for v in estructura.values())
        elif isinstance(estructura, list):
            return len(estructura) + sum(contar_nodos(item) for item in estructura if isinstance(item, (list, dict)))
        return 1
    
    def calcular_profundidad(estructura, prof=0):
        if isinstance(estructura, dict):
            if not estructura:
                return prof
            return max(calcular_profundidad(v, prof + 1) for v in estructura.values())
        elif isinstance(estructura, list):
            if not estructura:
                return prof
            return max((calcular_profundidad(item, prof + 1) 
                       for item in estructura 
                       if isinstance(item, (list, dict))), default=prof)
        return prof
    
    return {
        "valido": oracion_atn is not None,
        "nodos": contar_nodos(oracion_atn),
        "profundidad": calcular_profundidad(oracion_atn),
        "tipo": oracion_atn.get("cat", "desconocido")
    }
