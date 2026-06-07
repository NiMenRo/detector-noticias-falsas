# PCFG - Manejo de probabilidades y cálculo de P(árbol)
# Problema 2: Implementar cálculo real de P(árbol)

import math
from pcfg_trainer import PCFGTrainer

class PCFG:
    """Maneja probabilidades de reglas y calcula P(árbol)."""
    
    def __init__(self):
        self.pcfg_neutral = {}
        self.pcfg_sospechoso = {}
        self.trainer_neutral = PCFGTrainer()
        self.trainer_sospechoso = PCFGTrainer()
    
    def entrenar(self, corpus_neutral, corpus_sospechoso):
        """Entrena PCFG desde ambos corpus."""
        print("[PCFG] Entrenando desde corpus...")
        self.trainer_neutral.entrenar_desde_corpus(corpus_neutral)
        self.trainer_sospechoso.entrenar_desde_corpus(corpus_sospechoso)
        
        self.pcfg_neutral = self.trainer_neutral.pcfg
        self.pcfg_sospechoso = self.trainer_sospechoso.pcfg
    
    def obtener_prob_regla_neutral(self, lhs, rhs):
        """Obtiene probabilidad de regla en corpus neutral."""
        return self.trainer_neutral.obtener_probabilidad_regla(lhs, rhs)
    
    def obtener_prob_regla_sospechoso(self, lhs, rhs):
        """Obtiene probabilidad de regla en corpus sospechoso."""
        return self.trainer_sospechoso.obtener_probabilidad_regla(lhs, rhs)
    
    def calcular_p_arbol(self, arbol, corpus='neutral'):
        """
        Calcula P(árbol) = Π P(regla usada en cada nodo)
        
        Problema 2: Implementa el cálculo real de P(árbol).
        
        Args:
            arbol: Árbol anotado con reglas y probabilidades
            corpus: 'neutral' o 'sospechoso'
        
        Returns:
            P(árbol): producto de probabilidades de reglas
        """
        if corpus == 'neutral':
            probas = self.pcfg_neutral
        else:
            probas = self.pcfg_sospechoso
        
        return self._calcular_p_recursivo(arbol, probas, corpus)
    
    def _calcular_p_recursivo(self, nodo, probas, corpus='neutral'):
        """Calcula probabilidad recursivamente desde el árbol."""
        if not isinstance(nodo, dict):
            return 1.0
        
        # Obtener probabilidad de la regla en este nodo
        simbolo = nodo.get('simbolo')
        regla = nodo.get('regla')
        
        if not simbolo or not regla:
            return 1.0
        
        # Extraer LHS y RHS de la regla (formato: "LHS -> RHS1 RHS2 ...")
        partes = regla.split(' -> ')
        if len(partes) != 2:
            return 1.0
        
        lhs = partes[0].strip()
        rhs_str = partes[1].strip()
        rhs_tuple = tuple(rhs_str.split())
        
        # Obtener probabilidad de esta regla
        if corpus == 'neutral':
            prob_regla = self.obtener_prob_regla_neutral(lhs, rhs_tuple)
        else:
            prob_regla = self.obtener_prob_regla_sospechoso(lhs, rhs_tuple)
        if prob_regla == 0.0:
            prob_regla = 0.0001  # Suavizado Laplace
        
        # Multiplicar por probabilidades de hijos
        prob_hijos = 1.0
        hijos = nodo.get('hijos', [])
        for hijo in hijos:
            prob_hijos *= self._calcular_p_recursivo(hijo, probas, corpus)
        
        return prob_regla * prob_hijos
    
    def anotar_arbol_con_probabilidades(self, arbol, corpus='neutral'):
        """
        Anota cada nodo del árbol con su probabilidad.
        Problema 3: Integra Parser con PCFG anotando probabilidades.
        """
        if corpus == 'neutral':
            probas = self.pcfg_neutral
        else:
            probas = self.pcfg_sospechoso
        
        return self._anotar_recursivo(arbol, probas)
    
    def _anotar_recursivo(self, nodo, probas):
        """Anota recursivamente cada nodo."""
        if not isinstance(nodo, dict):
            return nodo
        
        simbolo = nodo.get('simbolo')
        regla = nodo.get('regla')
        
        # Calcular probabilidad de la regla
        if regla:
            partes = regla.split(' -> ')
            if len(partes) == 2:
                lhs = partes[0].strip()
                rhs_tuple = tuple(partes[1].strip().split())
                prob = self.obtener_prob_regla_neutral(lhs, rhs_tuple)
                if prob == 0.0:
                    prob = 0.0001
                nodo['prob_regla'] = prob
        
        # Anotar hijos recursivamente
        if 'hijos' in nodo:
            nodo['hijos'] = [self._anotar_recursivo(h, probas) for h in nodo['hijos']]
        
        return nodo
    
    def comparar_corpora(self, regla):
        """
        Compara probabilidad de una regla en corpus neutral vs sospechoso.
        Usa para detectar patrones sospechosos.
        """
        lhs, rhs = regla
        prob_neutral = self.obtener_prob_regla_neutral(lhs, rhs)
        prob_sospechoso = self.obtener_prob_regla_sospechoso(lhs, rhs)
        
        return {
            'regla': f"{lhs} -> {' '.join(rhs)}",
            'prob_neutral': prob_neutral,
            'prob_sospechoso': prob_sospechoso,
            'ratio': prob_sospechoso / max(prob_neutral, 0.0001)
        }


# Inicialización global de PCFG
_pcfg_global = None

def obtener_pcfg():
    """Obtiene instancia global de PCFG."""
    global _pcfg_global
    if _pcfg_global is None:
        _pcfg_global = PCFG()
        _pcfg_global.entrenar('data/corpus_neutral.txt', 'data/corpus_sospechoso.txt')
    return _pcfg_global
