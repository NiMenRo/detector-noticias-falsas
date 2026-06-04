"""
Clasificador de Noticias Falsas

Genera clasificación final (FAKE / SUSPICIOUS / CREDIBLE) basada en:
- Score de ambigüedad (10%)
- Score de patrones sospechosos (60%)
- Score de rasgos/concordancia (20%)
- Score de otros análisis (10%)

La clasificación incluye justificación detallada de cada factor.
"""

from typing import Dict, Any, Tuple
from enum import Enum


class CategoriaNoticia(Enum):
    """Categorías de clasificación."""
    CREDIBLE = "CREDIBLE"      # Score < 0.40
    SUSPICIOUS = "SUSPICIOUS"  # 0.40 <= Score < 0.70
    FAKE = "FAKE"              # Score >= 0.70


class ClasificadorFakeNews:
    """Clasifica noticias como FAKE, SUSPICIOUS o CREDIBLE."""
    
    def __init__(self):
        # Pesos del modelo de scoring (deben sumar 1.0)
        self.peso_ambiguedad = 0.10
        self.peso_patrones = 0.60
        self.peso_rasgos = 0.20
        self.peso_otros = 0.10
        
        # Umbrales de clasificación
        self.umbral_credible = 0.40
        self.umbral_suspicious = 0.70
    
    def calcula_score_final(
        self,
        score_ambiguedad: float,
        score_patrones: float,
        score_rasgos: float,
        score_otros: float = 0.0
    ) -> float:
        """
        Calcula score final combinando todos los análisis.
        
        Args:
            score_ambiguedad: 0-1, detecta múltiples interpretaciones
            score_patrones: 0-1, patrones sospechosos encontrados
            score_rasgos: 0-1, problemas de concordancia/estructura
            score_otros: 0-1, otros indicadores (por defecto 0)
            
        Returns:
            Score final entre 0 y 1
            
        Fórmula:
            score = (ambigüedad * 0.1) + (patrones * 0.6) + 
                    (rasgos * 0.2) + (otros * 0.1)
        """
        # Normalizar inputs a [0, 1]
        scores = [score_ambiguedad, score_patrones, score_rasgos, score_otros]
        scores_normalizados = [min(max(s, 0.0), 1.0) for s in scores]
        
        score_final = (
            scores_normalizados[0] * self.peso_ambiguedad +
            scores_normalizados[1] * self.peso_patrones +
            scores_normalizados[2] * self.peso_rasgos +
            scores_normalizados[3] * self.peso_otros
        )
        
        return round(score_final, 4)
    
    def clasifica(self, score_final: float) -> CategoriaNoticia:
        """
        Clasifica según el score.
        
        Args:
            score_final: Score entre 0 y 1
            
        Returns:
            Categoría: CREDIBLE, SUSPICIOUS o FAKE
        """
        if score_final < self.umbral_credible:
            return CategoriaNoticia.CREDIBLE
        elif score_final < self.umbral_suspicious:
            return CategoriaNoticia.SUSPICIOUS
        else:
            return CategoriaNoticia.FAKE
    
    def genera_justificacion_ambiguedad(
        self,
        score_ambiguedad: float,
        num_interpretaciones: int,
        es_sospechoso: bool
    ) -> str:
        """
        Genera justificación para el análisis de ambigüedad.
        """
        if num_interpretaciones <= 1:
            return "Texto sintácticamente claro (una única interpretación posible)."
        
        if num_interpretaciones <= 3:
            if es_sospechoso:
                return (
                    f"Ambigüedad moderada detectada ({num_interpretaciones} interpretaciones). "
                    "Puede indicar redacción confusa o poco clara."
                )
            else:
                return (
                    f"Ambigüedad leve ({num_interpretaciones} interpretaciones). "
                    "Normalmente aceptable en textos informales."
                )
        
        return (
            f"Ambigüedad alta detectada ({num_interpretaciones} interpretaciones). "
            "Texto muy confuso. Podría indicar intención de ofuscar información."
        )
    
    def genera_justificacion_patrones(
        self,
        score_patrones: float,
        patrones_dict: Dict[str, Any]
    ) -> str:
        """
        Genera justificación para patrones sospechosos.
        """
        if score_patrones < 0.2:
            return "Sin patrones sospechosos detectados."
        
        justificaciones = []
        
        # Afirmaciones absolutas
        num_abs = patrones_dict.get('afirmaciones_absolutas', {}).get('encontradas', 0)
        if num_abs > 0:
            justificaciones.append(
                f"Afirmaciones absolutas detectadas ({num_abs}): "
                "sin matices, sin probabilidades, sin contexto."
            )
        
        # Modales vagos
        num_modales = patrones_dict.get('modales_vagos', {}).get('encontradas', 0)
        if num_modales > 0:
            justificaciones.append(
                f"Verbos modales vagos ({num_modales}): 'podría', 'probablemente', 'al parecer'. "
                "Indica incertidumbre pero sin aclaración."
            )
        
        # Sin fuentes
        num_sin_fuente = patrones_dict.get('ausencia_fuentes', {}).get('encontradas', 0)
        if num_sin_fuente > 0:
            justificaciones.append(
                f"Ausencia de fuentes ({num_sin_fuente}): afirmaciones sin citar origen. "
                "Indicador crítico de posible fake news."
            )
        
        # Negaciones múltiples
        num_negaciones = patrones_dict.get('negaciones_multiples', {}).get('encontradas', 0)
        if num_negaciones > 0:
            justificaciones.append(
                f"Negaciones múltiples en {num_negaciones} oraciones: "
                "puede causar confusión o intención de ofuscar."
            )
        
        # Tipografía
        tipografia = patrones_dict.get('tipografia_sospechosa', {})
        if tipografia.get('exclamaciones_multiples', 0) > 0:
            justificaciones.append(
                f"Exclamaciones múltiples ({tipografia['exclamaciones_multiples']}): "
                "estilo sensacionalista."
            )
        
        if tipografia.get('caps_excesivas', 0) > 0:
            justificaciones.append(
                f"Uso excesivo de MAYÚSCULAS ({tipografia['caps_excesivas']}): "
                "típico de clickbait."
            )
        
        if not justificaciones:
            return "Patrones detectados pero sin detalle específico."
        
        return " ".join(justificaciones)
    
    def genera_justificacion_rasgos(
        self,
        score_rasgos: float,
        problemas_rasgos: Dict[str, Any] = None
    ) -> str:
        """
        Genera justificación para análisis de rasgos.
        """
        if score_rasgos < 0.1:
            return "Concordancia de rasgos (género, número) correcta."
        
        if problemas_rasgos is None:
            problemas_rasgos = {}
        
        justificaciones = []
        
        if problemas_rasgos.get('concordancia_fallida', False):
            justificaciones.append(
                "Problemas de concordancia (género/número). "
                "Podría indicar redacción apresurada o automática."
            )
        
        if problemas_rasgos.get('estructura_inusual', False):
            justificaciones.append(
                "Estructura sintáctica inusual. "
                "Puede ser resultado de traducción automática o manipulación textual."
            )
        
        return " ".join(justificaciones) if justificaciones else "Rasgos diversos detectados."
    
    def genera_recomendacion(
        self,
        categoria: CategoriaNoticia,
        score_final: float
    ) -> str:
        """
        Genera recomendación de acción.
        """
        if categoria == CategoriaNoticia.CREDIBLE:
            return "Noticia verificada como creíble. Se recomienda considerar como fuente confiable."
        
        elif categoria == CategoriaNoticia.SUSPICIOUS:
            confianza = (1.0 - score_final) * 100
            return (
                f"SOSPECHOSO (confianza: {confianza:.0f}%). "
                "Se recomienda verificación manual y búsqueda de fuentes adicionales."
            )
        
        else:  # FAKE
            confianza = score_final * 100
            return (
                f"FAKE NEWS (confianza: {confianza:.0f}%). "
                "No se recomienda compartir. Verificar con fuentes independientes."
            )
    
    def clasifica_completo(
        self,
        texto_original: str,
        score_ambiguedad: float,
        num_interpretaciones: int,
        es_sospechoso_amb: bool,
        patrones_dict: Dict[str, Any],
        score_rasgos: float = 0.0,
        problemas_rasgos: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """
        Clasificación completa con justificación detallada.
        
        Args:
            texto_original: Texto analizado
            score_ambiguedad: Score de ambigüedad (0-1)
            num_interpretaciones: Número de interpretaciones sintácticas
            es_sospechoso_amb: ¿La ambigüedad es sospechosa?
            patrones_dict: Dict con análisis de patrones sospechosos
            score_rasgos: Score de problemas de rasgos (0-1)
            problemas_rasgos: Dict con problemas específicos
            
        Returns:
            Dict completo con clasificación y justificación
        """
        if problemas_rasgos is None:
            problemas_rasgos = {}
        
        # Extraer score de patrones del dict
        score_patrones = patrones_dict.get('score_total_patrones', 0.0)
        
        # Calcular score final
        score_final = self.calcula_score_final(
            score_ambiguedad,
            score_patrones,
            score_rasgos,
            score_otros=0.0
        )
        
        # Clasificar
        categoria = self.clasifica(score_final)
        
        # Generar justificaciones
        justif_ambiguedad = self.genera_justificacion_ambiguedad(
            score_ambiguedad,
            num_interpretaciones,
            es_sospechoso_amb
        )
        
        justif_patrones = self.genera_justificacion_patrones(
            score_patrones,
            patrones_dict
        )
        
        justif_rasgos = self.genera_justificacion_rasgos(
            score_rasgos,
            problemas_rasgos
        )
        
        recomendacion = self.genera_recomendacion(categoria, score_final)
        
        # Desglose de scores
        desglose = {
            'ambiguedad': {
                'score': score_ambiguedad,
                'peso': self.peso_ambiguedad,
                'aporte': round(score_ambiguedad * self.peso_ambiguedad, 4),
                'justificacion': justif_ambiguedad
            },
            'patrones': {
                'score': score_patrones,
                'peso': self.peso_patrones,
                'aporte': round(score_patrones * self.peso_patrones, 4),
                'justificacion': justif_patrones,
                'detalle': patrones_dict
            },
            'rasgos': {
                'score': score_rasgos,
                'peso': self.peso_rasgos,
                'aporte': round(score_rasgos * self.peso_rasgos, 4),
                'justificacion': justif_rasgos
            }
        }
        
        return {
            'categoria': categoria.value,
            'score_final': score_final,
            'confianza': round(
                (1.0 - score_final) if categoria == CategoriaNoticia.CREDIBLE
                else score_final
            , 4),
            'desglose': desglose,
            'justificacion_completa': (
                f"ANÁLISIS DE FAKE NEWS:\n"
                f"1. Ambigüedad: {justif_ambiguedad}\n"
                f"2. Patrones: {justif_patrones}\n"
                f"3. Rasgos: {justif_rasgos}\n\n"
                f"RECOMENDACIÓN: {recomendacion}"
            ),
            'recomendacion': recomendacion
        }


# Funciones auxiliares de uso directo
def clasifica_noticia(
    score_ambiguedad: float,
    score_patrones: float,
    score_rasgos: float = 0.0
) -> Tuple[str, float]:
    """
    Clasificación rápida.
    
    Returns:
        (categoria, score_final)
    """
    clasificador = ClasificadorFakeNews()
    score = clasificador.calcula_score_final(
        score_ambiguedad,
        score_patrones,
        score_rasgos
    )
    categoria = clasificador.clasifica(score)
    
    return (categoria.value, score)
