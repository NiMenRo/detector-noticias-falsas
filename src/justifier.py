# Justificador - Genera explicaciones lingüísticas detalladas
# Problema 9: Explicaciones insuficientes

class Justifier:
    """Genera justificaciones lingüísticas basadas en análisis PCFG."""
    
    def __init__(self, pcfg=None):
        self.pcfg = pcfg
    
    def generar_justificacion(self, texto, arbol, ambiguedad, clasificacion):
        """
        Genera explicación completa sobre por qué el texto es sospechoso.
        
        Problema 9: Explicar árbol, reglas, probabilidades y relación
        con corpus.
        
        Args:
            texto: Oración original
            arbol: Árbol sintáctico seleccionado
            ambiguedad: Resultado del análisis de ambigüedad
            clasificacion: Resultado de clasificación
        
        Returns:
            Explicación detallada
        """
        justificacion = {
            'texto_original': texto,
            'resumen': self._generar_resumen(clasificacion),
            'arbol_sintactico': self._describir_arbol(arbol),
            'reglas_activadas': self._listar_reglas(arbol),
            'ambiguedad': self._explicar_ambiguedad(ambiguedad),
            'patrones_sospechosos': self._detectar_patrones(texto, arbol),
            'recomendacion': self._generar_recomendacion(clasificacion)
        }
        return justificacion
    
    def _generar_resumen(self, clasificacion):
        """Genera resumen del análisis."""
        riesgo = clasificacion.get('riesgo', 0.0)
        if riesgo >= 0.7:
            nivel = 'ALTO'
            emoji = '🚨'
        elif riesgo >= 0.4:
            nivel = 'MEDIO'
            emoji = '⚠️'
        else:
            nivel = 'BAJO'
            emoji = '✓'
        
        return f"{emoji} Nivel de sospecha: {nivel} (P={riesgo:.1%})"
    
    def _describir_arbol(self, arbol):
        """Describe la estructura del árbol."""
        if not arbol:
            return "Sin árbol sintáctico disponible"
        
        return {
            'simbolo_raiz': arbol.get('simbolo', 'S'),
            'profundidad': self._calcular_profundidad(arbol),
            'num_hojas': self._contar_hojas(arbol),
            'estructura': self._texto_arbol(arbol, indent=0)
        }
    
    def _listar_reglas(self, arbol):
        """Lista todas las reglas sintácticas utilizadas."""
        reglas = []
        self._extraer_reglas_recursivo(arbol, reglas)
        return reglas
    
    def _extraer_reglas_recursivo(self, nodo, reglas):
        """Extrae reglas recursivamente."""
        if not isinstance(nodo, dict):
            return
        
        regla = nodo.get('regla')
        if regla:
            prob = nodo.get('prob_regla', 0.0)
            reglas.append({
                'regla': regla,
                'probabilidad': prob,
                'frecuencia_corpus': self._clasificar_frecuencia(prob)
            })
        
        hijos = nodo.get('hijos', [])
        for hijo in hijos:
            self._extraer_reglas_recursivo(hijo, reglas)
    
    def _clasificar_frecuencia(self, prob):
        """Clasifica la frecuencia de una regla."""
        if prob >= 0.5:
            return 'MUY FRECUENTE'
        elif prob >= 0.2:
            return 'FRECUENTE'
        elif prob >= 0.05:
            return 'POCO FRECUENTE'
        else:
            return 'RARA'
    
    def _explicar_ambiguedad(self, ambiguedad):
        """Explica el análisis de ambigüedad."""
        if not ambiguedad or ambiguedad.get('num_arboles', 0) <= 1:
            return "Sin ambigüedad sintáctica relevante"
        
        return {
            'num_interpretaciones': ambiguedad['num_arboles'],
            'entropía': f"{ambiguedad['entropía']:.3f}",
            'nivel': ambiguedad['nivel_ambiguedad'],
            'explicacion': self._texto_ambiguedad(ambiguedad)
        }
    
    def _texto_ambiguedad(self, ambiguedad):
        """Texto explicativo de la ambigüedad."""
        nivel = ambiguedad['nivel_ambiguedad']
        num = ambiguedad['num_arboles']
        
        if nivel == 'ALTA':
            return f"La oración tiene {num} interpretaciones sintácticas muy distintas, lo que indica falta de claridad o ambigüedad deliberada."
        elif nivel == 'MEDIA':
            return f"La oración tiene {num} interpretaciones posibles, mostrando cierta ambigüedad estructural."
        else:
            return f"La estructura es principalmente clara, con pocas alternativas de interpretación."
    
    def _detectar_patrones(self, texto, arbol):
        """Detecta patrones sospechosos en el texto."""
        patrones = []
        tokens = texto.lower().split()
        
        # Patrones de modalidad vaga
        modales_vagos = ['podría', 'aparentemente', 'posiblemente', 'quizás', 
                        'supuestamente', 'según', 'dicen', 'parece']
        for modal in modales_vagos:
            if modal in tokens:
                patrones.append({
                    'tipo': 'MODALIDAD VAGA',
                    'elemento': modal,
                    'riesgo': 'Reduce certeza de la afirmación',
                    'frecuencia': 'Alto en corpus sospechoso'
                })
        
        # Patrones de afirmación absoluta
        adv_abs = ['siempre', 'nunca', 'definitivamente', 'absolutamente',
                   'claramente', 'obviamente', 'evidentemente']
        for adv in adv_abs:
            if adv in tokens:
                patrones.append({
                    'tipo': 'AFIRMACION ABSOLUTA',
                    'elemento': adv,
                    'riesgo': 'Afirmación sin matización',
                    'frecuencia': 'Alto en corpus sospechoso'
                })
        
        # Patrones de fuente indefinida
        fuentes_indef = ['según', 'dicen', 'rumorea', 'anónimas', 'informalmente']
        for fuente in fuentes_indef:
            if fuente in tokens:
                patrones.append({
                    'tipo': 'FUENTE INDEFINIDA',
                    'elemento': fuente,
                    'riesgo': 'Información sin fuente verificable',
                    'frecuencia': 'Alto en corpus sospechoso'
                })
        
        return patrones
    
    def _generar_recomendacion(self, clasificacion):
        """Genera recomendación basada en el análisis."""
        riesgo = clasificacion.get('riesgo', 0.0)
        
        if riesgo >= 0.7:
            return "Se recomienda VERIFICAR esta información en múltiples fuentes confiables antes de compartir."
        elif riesgo >= 0.4:
            return "Se recomienda CONTRASTAR esta información con fuentes oficiales verificadas."
        else:
            return "Esta información parece verificada. Proceder con prudencia normal."
    
    def _calcular_profundidad(self, nodo):
        """Calcula profundidad del árbol."""
        if not isinstance(nodo, dict) or 'hijos' not in nodo:
            return 1
        
        if not nodo['hijos']:
            return 1
        
        return 1 + max(self._calcular_profundidad(h) for h in nodo['hijos'])
    
    def _contar_hojas(self, nodo):
        """Cuenta nodos hoja del árbol."""
        if not isinstance(nodo, dict):
            return 1
        
        hijos = nodo.get('hijos', [])
        if not hijos:
            return 1
        
        return sum(self._contar_hojas(h) for h in hijos)
    
    def _texto_arbol(self, nodo, indent=0):
        """Representa el árbol en texto."""
        if not isinstance(nodo, dict):
            return "  " * indent + str(nodo)
        
        simbolo = nodo.get('simbolo', '?')
        regla = nodo.get('regla', '')
        resultado = "  " * indent + f"{simbolo}"
        if regla:
            resultado += f" [{regla}]"
        
        hijos = nodo.get('hijos', [])
        for hijo in hijos:
            resultado += "\n" + self._texto_arbol(hijo, indent + 1)
        
        return resultado


def crear_justifier(pcfg=None):
    """Crea una instancia de Justifier."""
    return Justifier(pcfg)
