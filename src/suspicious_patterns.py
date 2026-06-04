"""
Detector de Patrones Sospechosos en Noticias Falsas

Identifica construcciones lingüísticas comúnmente asociadas con fake news:
- Afirmaciones absolutas (sin matices)
- Verbos modales vagos
- Ausencia de fuentes
- Estructuras anómalas
- Exceso de negaciones
"""

import re
from typing import List, Dict, Any, Tuple


class DetectorPatronesSospechosos:
    """Detecta patrones lingüísticos indicadores de fake news."""
    
    def __init__(self):
        # Palabras que indican afirmaciones absolutas
        self.absolutas = {
            'siempre', 'nunca', 'todos', 'ninguno', 'absolutamente',
            'definitivamente', 'ciertamente', 'sin duda', 'es un hecho'
        }
        
        # Verbos modales vagos (expresan incertidumbre o vaguedad)
        self.modales_vagos = {
            'puede', 'podría', 'probablemente', 'quizás', 'tal vez',
            'parece', 'aparentemente', 'posiblemente', 'supuestamente',
            'al parecer', 'según dicen', 'se dice que'
        }
        
        # Frases que indican falta de fuente
        self.sin_fuente = {
            'se dice que', 'la gente dice', 'según fuentes',
            'al parecer', 'supuestamente', 'se rumorea',
            'se reporta que', 'aparentemente', 'dicen que'
        }
        
        # Patrones regex para detectar problemas
        self.patrones_regex = {
            'exclamaciones': r'[!]{2,}',  # !! o más
            'caps_excesivas': r'[A-Z]{3,}(?:\s+[A-Z]{3,}){2,}',  # PALABRAS EN CAPS
            'puntos_suspension': r'\.{2,}',  # ... o más
        }
    
    def detecta_afirmaciones_absolutas(self, tokens: List[List[str]]) -> List[Dict[str, Any]]:
        """
        Detecta afirmaciones absolutas (sin matices).
        
        Args:
            tokens: Lista de oraciones tokenizadas [[palabra1, palabra2], ...]
            
        Returns:
            Lista de dicts:
            [
                {
                    'oracion_idx': 0,
                    'palabra': 'siempre',
                    'tipo': 'absoluta',
                    'score': 0.8
                },
                ...
            ]
        """
        afirmaciones = []
        
        for idx_oracion, tokens_oracion in enumerate(tokens):
            palabras_lower = [p.lower().strip('.,!?;:') for p in tokens_oracion]
            
            for idx_palabra, palabra in enumerate(palabras_lower):
                if palabra in self.absolutas:
                    afirmaciones.append({
                        'oracion_idx': idx_oracion,
                        'palabra_idx': idx_palabra,
                        'palabra': palabra,
                        'tipo': 'absoluta',
                        'score': 0.8
                    })
        
        return afirmaciones
    
    def detecta_modales_vagos(self, tokens: List[List[str]]) -> List[Dict[str, Any]]:
        """
        Detecta verbos modales que expresan vaguedad.
        
        Args:
            tokens: Oraciones tokenizadas
            
        Returns:
            Lista de dicts con modales vagos encontrados
        """
        modales = []
        
        for idx_oracion, tokens_oracion in enumerate(tokens):
            palabras_lower = [p.lower().strip('.,!?;:') for p in tokens_oracion]
            
            for idx_palabra, palabra in enumerate(palabras_lower):
                if palabra in self.modales_vagos:
                    modales.append({
                        'oracion_idx': idx_oracion,
                        'palabra_idx': idx_palabra,
                        'palabra': palabra,
                        'tipo': 'modal_vago',
                        'score': 0.5
                    })
        
        return modales
    
    def detecta_ausencia_fuentes(self, tokens: List[List[str]]) -> List[Dict[str, Any]]:
        """
        Detecta frases que indican ausencia de fuentes verificables.
        
        Args:
            tokens: Oraciones tokenizadas
            
        Returns:
            Lista de dicts con frases sin fuente
        """
        sin_fuente_list = []
        
        for idx_oracion, tokens_oracion in enumerate(tokens):
            # Crear texto de oración para búsqueda de frases
            texto_oracion = ' '.join(tokens_oracion).lower()
            
            for frase in self.sin_fuente:
                if frase in texto_oracion:
                    sin_fuente_list.append({
                        'oracion_idx': idx_oracion,
                        'frase': frase,
                        'tipo': 'sin_fuente',
                        'score': 0.7
                    })
        
        return sin_fuente_list
    
    def detecta_oraciones_cortas_contexto(self, tokens: List[List[str]]) -> List[Dict[str, Any]]:
        """
        Detecta oraciones muy cortas sin contexto (típico de sensacionalismo).
        
        Args:
            tokens: Oraciones tokenizadas
            
        Returns:
            Lista de oraciones sospechosamente cortas
        """
        cortas = []
        
        for idx_oracion, tokens_oracion in enumerate(tokens):
            num_palabras = len(tokens_oracion)
            
            # Oración muy corta (< 4 palabras) sin verbo conjugado
            if num_palabras < 4 and num_palabras >= 1:
                cortas.append({
                    'oracion_idx': idx_oracion,
                    'num_palabras': num_palabras,
                    'texto': ' '.join(tokens_oracion),
                    'tipo': 'oracion_corta',
                    'score': 0.3  # Menos crítico que otros
                })
        
        return cortas
    
    def detecta_negaciones_multiples(self, tokens: List[List[str]]) -> List[Dict[str, Any]]:
        """
        Detecta múltiples negaciones en una oración (confusión intencional).
        
        Args:
            tokens: Oraciones tokenizadas
            
        Returns:
            Lista de oraciones con negaciones múltiples
        """
        negaciones_mult = []
        negacion_palabras = {'no', 'nunca', 'ni', 'nadie', 'nada', 'ningún', 'ninguno'}
        
        for idx_oracion, tokens_oracion in enumerate(tokens):
            palabras_lower = [p.lower().strip('.,!?;:') for p in tokens_oracion]
            num_negaciones = sum(1 for p in palabras_lower if p in negacion_palabras)
            
            if num_negaciones >= 2:
                negaciones_mult.append({
                    'oracion_idx': idx_oracion,
                    'num_negaciones': num_negaciones,
                    'tipo': 'negaciones_multiples',
                    'score': 0.6
                })
        
        return negaciones_mult
    
    def detecta_patrones_tipograficos(self, texto: str) -> Dict[str, Any]:
        """
        Detecta patrones tipográficos sospechosos.
        
        Args:
            texto: Texto original
            
        Returns:
            Dict con patrones encontrados y sus scores
        """
        patrones_encontrados = {
            'exclamaciones_multiples': 0,
            'caps_excesivas': 0,
            'puntos_suspension': 0
        }
        
        # Contar exclamaciones múltiples
        exclamaciones = re.findall(self.patrones_regex['exclamaciones'], texto)
        patrones_encontrados['exclamaciones_multiples'] = len(exclamaciones)
        
        # Contar CAPS excesivas
        caps = re.findall(self.patrones_regex['caps_excesivas'], texto)
        patrones_encontrados['caps_excesivas'] = len(caps)
        
        # Contar puntos suspensivos
        suspensivos = re.findall(self.patrones_regex['puntos_suspension'], texto)
        patrones_encontrados['puntos_suspension'] = len(suspensivos)
        
        return patrones_encontrados
    
    def calcula_score_total_patrones(
        self,
        afirmaciones_abs: List[Dict],
        modales: List[Dict],
        sin_fuente: List[Dict],
        negaciones: List[Dict],
        tipografia: Dict[str, int]
    ) -> float:
        """
        Calcula score total de sospecha por patrones (0-1).
        
        Ponderación:
        - Afirmaciones absolutas: +0.15 cada una
        - Verbos modales vagos: +0.10 cada una
        - Ausencia de fuente: +0.20 cada una
        - Negaciones múltiples: +0.15 cada una
        - Tipografía sospechosa: +0.10 cada patrón
        
        Cap máximo: 1.0
        """
        score = 0.0
        
        score += len(afirmaciones_abs) * 0.15
        score += len(modales) * 0.10
        score += len(sin_fuente) * 0.20
        score += len(negaciones) * 0.15
        
        # Tipografía
        score += tipografia.get('exclamaciones_multiples', 0) * 0.05
        score += tipografia.get('caps_excesivas', 0) * 0.08
        score += tipografia.get('puntos_suspension', 0) * 0.05
        
        return min(score, 1.0)
    
    def analiza_completo(
        self,
        texto: str,
        tokens: List[List[str]]
    ) -> Dict[str, Any]:
        """
        Análisis completo de patrones sospechosos.
        
        Args:
            texto: Texto original
            tokens: Oraciones tokenizadas
            
        Returns:
            Dict completo con todos los patrones y scores
        """
        afirmaciones = self.detecta_afirmaciones_absolutas(tokens)
        modales = self.detecta_modales_vagos(tokens)
        sin_fuente = self.detecta_ausencia_fuentes(tokens)
        oraciones_cortas = self.detecta_oraciones_cortas_contexto(tokens)
        negaciones = self.detecta_negaciones_multiples(tokens)
        tipografia = self.detecta_patrones_tipograficos(texto)
        
        score_total = self.calcula_score_total_patrones(
            afirmaciones, modales, sin_fuente, negaciones, tipografia
        )
        
        return {
            'afirmaciones_absolutas': {
                'encontradas': len(afirmaciones),
                'detalle': afirmaciones
            },
            'modales_vagos': {
                'encontrados': len(modales),
                'detalle': modales
            },
            'ausencia_fuentes': {
                'encontradas': len(sin_fuente),
                'detalle': sin_fuente
            },
            'oraciones_cortas': {
                'encontradas': len(oraciones_cortas),
                'detalle': oraciones_cortas
            },
            'negaciones_multiples': {
                'encontradas': len(negaciones),
                'detalle': negaciones
            },
            'tipografia_sospechosa': tipografia,
            'score_total_patrones': score_total,
            'resumen': {
                'total_patrones': (
                    len(afirmaciones) + len(modales) + len(sin_fuente) +
                    len(oraciones_cortas) + len(negaciones)
                ),
                'es_sospechoso': score_total > 0.5
            }
        }


# Función auxiliar de uso directo
def detecta_patrones(texto: str, tokens: List[List[str]]) -> float:
    """
    Detección rápida de patrones sospechosos.
    
    Returns:
        Score total (0-1)
    """
    detector = DetectorPatronesSospechosos()
    resultado = detector.analiza_completo(texto, tokens)
    return resultado['score_total_patrones']
