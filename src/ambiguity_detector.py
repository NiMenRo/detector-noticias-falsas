"""
Detector de ambiguedad para el pipeline de noticias.

Basado en contexto/Ambiguo_y_PCFG..py. Se conserva la idea central del
archivo de clase: detectar palabras con varias categorias posibles y usar
frecuencias para elegir la categoria mas probable. Ademas, la clase
DetectorAmbiguedad mantiene la interfaz que usa pipeline.py.
"""

import math
import re
from collections import defaultdict
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Tuple


LEXICO_AMBIGUO = {
    "la": ["Det"], "el": ["Det"], "las": ["Det"], "los": ["Det"],
    "un": ["Det"], "una": ["Det"], "unos": ["Det"], "unas": ["Det"],
    "de": ["Prep"], "en": ["Prep"], "con": ["Prep"], "por": ["Prep"],
    "para": ["Prep"],

    "estudiante": ["N"], "libro": ["N"], "papas": ["N"],
    "profesor": ["N"], "medico": ["N"], "banco": ["N"],
    "gato": ["N"], "mesa": ["N"], "virus": ["N"], "noticia": ["N"],
    "gobierno": ["N"], "presidente": ["N"], "ministro": ["N"],

    "pelo": ["N", "V"],
    "nota": ["N", "V"],
    "sobre": ["N", "V", "Prep"],
    "como": ["V", "Conj"],
    "bajo": ["Adj", "V", "Prep"],
    "ataque": ["N", "V"],
    "amenaza": ["N", "V"],
    "alerta": ["N", "V", "Adj"],
    "cambio": ["N", "V"],
    "control": ["N", "V"],
    "cura": ["N", "V"],
    "denuncia": ["N", "V"],
    "fuerza": ["N", "V"],
    "golpe": ["N", "V"],
    "orden": ["N", "V"],
    "reporte": ["N", "V"],
    "vacuna": ["N", "V"],

    "lee": ["V"], "ve": ["V"], "dice": ["V"], "revela": ["V"],
}


FRECUENCIAS_DEFAULT = {
    "pelo": {"N": 300, "V": 50},
    "nota": {"N": 380, "V": 70},
    "sobre": {"Prep": 400, "N": 50, "V": 10},
    "como": {"V": 150, "Conj": 100},
    "bajo": {"Prep": 200, "Adj": 150, "V": 50},
    "ataque": {"N": 200, "V": 30},
    "amenaza": {"N": 120, "V": 160},
    "alerta": {"N": 120, "V": 60, "Adj": 80},
    "cambio": {"N": 220, "V": 35},
    "control": {"N": 220, "V": 80},
    "cura": {"N": 120, "V": 110},
    "denuncia": {"N": 150, "V": 90},
    "fuerza": {"N": 250, "V": 40},
    "golpe": {"N": 190, "V": 60},
    "orden": {"N": 180, "V": 50},
    "reporte": {"N": 170, "V": 80},
    "vacuna": {"N": 180, "V": 35},
}


def normaliza_token(token: str) -> str:
    return token.lower().strip(".,;:!?()[]{}\"'")


def tokenizar_texto(texto: str) -> List[str]:
    return re.findall(r"\b\w+\b", texto.lower(), flags=re.UNICODE)


def categorias(token: str) -> List[str]:
    return LEXICO_AMBIGUO.get(normaliza_token(token), [])


def es_ambiguo(token: str) -> bool:
    return len(categorias(token)) > 1


def detectar_ambiguedad(oracion: str) -> List[Tuple[str, List[str]]]:
    return [(t, categorias(t)) for t in tokenizar_texto(oracion) if es_ambiguo(t)]


def construir_frecuencias(ruta_corpus: str) -> Dict[str, Dict[str, int]]:
    conteos = defaultdict(lambda: defaultdict(int))
    with open(ruta_corpus, encoding="utf-8") as archivo:
        for linea in archivo:
            linea = linea.strip()
            if not linea or linea.startswith("#"):
                continue
            partes = linea.split()
            if len(partes) == 2:
                palabra, categoria = partes
                conteos[palabra.lower()][categoria] += 1
    return {palabra: dict(cats) for palabra, cats in conteos.items()}


def cargar_frecuencias(ruta_corpus: Optional[str] = None) -> Dict[str, Dict[str, int]]:
    if ruta_corpus is None:
        ruta_corpus = str(Path(__file__).resolve().parent.parent / "contexto" / "corpus_ambiguo.txt")
    try:
        return construir_frecuencias(ruta_corpus)
    except FileNotFoundError:
        return FRECUENCIAS_DEFAULT


def prob_categoria(
    palabra: str,
    categoria: str,
    frecuencias: Optional[Dict[str, Dict[str, int]]] = None,
) -> float:
    frecuencias = frecuencias or FRECUENCIAS_DEFAULT
    palabra = normaliza_token(palabra)
    if palabra not in frecuencias:
        return 0.0
    conteos = frecuencias[palabra]
    total = sum(conteos.values())
    return conteos.get(categoria, 0) / total if total else 0.0


def categoria_mas_probable(
    palabra: str,
    frecuencias: Optional[Dict[str, Dict[str, int]]] = None,
) -> Optional[str]:
    frecuencias = frecuencias or FRECUENCIAS_DEFAULT
    palabra = normaliza_token(palabra)
    if palabra not in frecuencias:
        cats = categorias(palabra)
        return cats[0] if cats else None
    return max(frecuencias[palabra], key=frecuencias[palabra].get)


def desambiguar(
    oracion: str,
    frecuencias: Optional[Dict[str, Dict[str, int]]] = None,
) -> Dict[str, Any]:
    frecuencias = frecuencias or FRECUENCIAS_DEFAULT
    tokens = tokenizar_texto(oracion)
    ambiguas = detectar_ambiguedad(oracion)

    desambiguaciones = []
    for palabra, cats in ambiguas:
        categoria = categoria_mas_probable(palabra, frecuencias)
        prob = prob_categoria(palabra, categoria, frecuencias) if categoria else 0.0
        desambiguaciones.append({
            "palabra": palabra,
            "categorias_posibles": cats,
            "categoria_mas_probable": categoria,
            "probabilidad": round(prob, 3),
        })

    ratio = len(ambiguas) / len(tokens) if tokens else 0.0
    return {
        "tokens": tokens,
        "palabras_ambiguas": ambiguas,
        "desambiguaciones": desambiguaciones,
        "num_ambiguas": len(ambiguas),
        "num_total_palabras": len(tokens),
        "ambiguedad_ratio": round(ratio, 3),
        "es_ambiguo_text": ratio > 0.1,
        "score_ambiguedad": round(ratio, 3),
    }


def estadisticas(oracion: str) -> Dict[str, Any]:
    tokens = tokenizar_texto(oracion)
    ambiguos = [t for t in tokens if es_ambiguo(t)]
    desconocidos = [t for t in tokens if not categorias(t)]
    conocidos = [t for t in tokens if categorias(t) and not es_ambiguo(t)]
    total = len(tokens)

    return {
        "total_tokens": total,
        "no_ambiguos": {
            "cantidad": len(conocidos),
            "porcentaje": round(100 * len(conocidos) / total, 1) if total else 0,
        },
        "ambiguos": {
            "cantidad": len(ambiguos),
            "porcentaje": round(100 * len(ambiguos) / total, 1) if total else 0,
            "palabras": ambiguos,
        },
        "desconocidos": {
            "cantidad": len(desconocidos),
            "porcentaje": round(100 * len(desconocidos) / total, 1) if total else 0,
            "palabras": desconocidos,
        },
        "indicador_sospechoso": bool(ambiguos),
    }


class DetectorAmbiguedad:
    """Analiza ambiguedad lexica y cantidad de parses sintacticos."""

    def __init__(self, frecuencias: Optional[Dict[str, Dict[str, int]]] = None):
        self.frecuencias = frecuencias or cargar_frecuencias()

    def calcula_ambiguedad_score(self, num_interpretaciones: int) -> float:
        if num_interpretaciones <= 1:
            return 0.0
        mapping = {2: 0.40, 3: 0.60, 4: 0.80}
        return mapping.get(num_interpretaciones, 1.0)

    def _cuenta_interpretaciones(self, arboles_parse: Optional[Iterable[Any]]) -> int:
        if not arboles_parse:
            return 1
        arboles = list(arboles_parse)
        if len(arboles) == 1 and isinstance(arboles[0], list):
            return max(len(arboles[0]), 1)
        return max(len(arboles), 1)

    def analiza_texto(self, texto: str) -> Dict[str, Any]:
        return desambiguar(texto, self.frecuencias)

    def analiza_completo(
        self,
        arboles_parse: Optional[Iterable[Any]] = None,
        texto: str = "",
    ) -> Dict[str, Any]:
        num_interpretaciones = self._cuenta_interpretaciones(arboles_parse)
        score_sintactico = self.calcula_ambiguedad_score(num_interpretaciones)
        analisis_lexico = self.analiza_texto(texto)
        score_lexico = analisis_lexico["score_ambiguedad"]
        score_total = round(min((score_sintactico * 0.45) + (score_lexico * 0.55), 1.0), 3)
        es_sospechoso = score_total >= 0.2 or analisis_lexico["num_ambiguas"] >= 2

        return {
            "num_interpretaciones": num_interpretaciones,
            "score_ambiguedad": score_total,
            "score_sintactico": score_sintactico,
            "score_lexico": score_lexico,
            "palabras_ambiguas": analisis_lexico["palabras_ambiguas"],
            "desambiguaciones": analisis_lexico["desambiguaciones"],
            "estadisticas_lexicas": estadisticas(texto),
            "indicadores_sospechosos": {
                "es_sospechoso": es_sospechoso,
                "ambiguedad_lexica": analisis_lexico["es_ambiguo_text"],
                "ambiguedad_sintactica": num_interpretaciones > 1,
                "motivo": (
                    "Texto con varias palabras ambiguas o multiples interpretaciones"
                    if es_sospechoso else
                    "No se encontro ambiguedad relevante"
                ),
            },
        }


def detecta_ambiguedad(texto: str) -> Dict[str, Any]:
    return DetectorAmbiguedad().analiza_completo(texto=texto)


def detecta_ambiguedad_rapido(oracion: str) -> Tuple[int, float, bool]:
    resultado = detecta_ambiguedad(oracion)
    return (
        len(resultado["palabras_ambiguas"]),
        resultado["score_ambiguedad"],
        resultado["indicadores_sospechosos"]["es_sospechoso"],
    )


# ============================================================
# Problema 4: Detección de ambigüedad sintáctica desde árboles
# La ambigüedad debe surgir naturalmente de múltiples árboles
# ============================================================

class AmbiguityDetectorSyntactic:
    """Detecta ambigüedad sintáctica analizando múltiples árboles."""
    
    def __init__(self):
        self.arboles = []
    
    def detectar_ambiguedad_sintactica(self, arboles):
        """
        Analiza conjunto de árboles para detectar ambigüedad.
        
        Problema 4: La ambigüedad surge naturalmente cuando existen
        múltiples árboles válidos para la misma oración.
        
        Args:
            arboles: Lista de árboles sintácticos posibles
        
        Returns:
            Dict con métricas de ambigüedad
        """
        if not arboles or len(arboles) == 0:
            return self._resultado_sin_ambiguedad()
        
        # Calcular probabilidades de cada árbol
        probabilidades = self._calcular_probabilidades_arboles(arboles)
        
        # Calcular métricas
        num_arboles = len(arboles)
        entropía = self._calcular_entropia(probabilidades)
        confianza = max(probabilidades) if probabilidades else 0.0
        
        arbol_mas_probable_idx = probabilidades.index(max(probabilidades))
        arbol_seleccionado = arboles[arbol_mas_probable_idx]
        
        return {
            'num_arboles': num_arboles,
            'probabilidades': probabilidades,
            'entropía': entropía,
            'confianza': confianza,
            'arbol_seleccionado': arbol_seleccionado,
            'arbol_idx': arbol_mas_probable_idx,
            'es_ambiguo': entropía > 0.5,
            'nivel_ambiguedad': self._clasificar_ambiguedad(entropía)
        }
    
    def _calcular_probabilidades_arboles(self, arboles):
        """Calcula P(árbol) para cada árbol."""
        probabilidades = []
        for arbol in arboles:
            prob = self._estimar_prob_arbol(arbol)
            probabilidades.append(prob)
        
        # Normalizar probabilidades
        total = sum(probabilidades) if probabilidades else 1.0
        if total > 0:
            probabilidades = [p / total for p in probabilidades]
        
        return probabilidades
    
    def _estimar_prob_arbol(self, arbol):
        """Estima P(árbol) contando nodos (fallback sin PCFG)."""
        return self._contar_nodos_recursivo(arbol) / 10.0
    
    def _contar_nodos_recursivo(self, nodo):
        """Cuenta nodos en el árbol."""
        if not isinstance(nodo, dict):
            return 1
        
        count = 1
        if 'hijos' in nodo:
            for hijo in nodo['hijos']:
                count += self._contar_nodos_recursivo(hijo)
        
        return count
    
    def _calcular_entropia(self, probabilidades):
        """
        Calcula entropía: H = -Σ P(árbol) * log₂(P(árbol))
        
        - H = 0: Una única interpretación (sin ambigüedad)
        - H > 0: Múltiples interpretaciones (ambigüedad)
        - H máxima: Todas las interpretaciones igual probables
        """
        if not probabilidades or len(probabilidades) <= 1:
            return 0.0
        
        entropía = 0.0
        for p in probabilidades:
            if p > 0:
                entropía -= p * math.log2(p)
        
        return entropía
    
    def _clasificar_ambiguedad(self, entropía):
        """Clasifica el nivel de ambigüedad."""
        if entropía < 0.2:
            return 'BAJA'
        elif entropía < 0.7:
            return 'MEDIA'
        else:
            return 'ALTA'
    
    def _resultado_sin_ambiguedad(self):
        """Resultado cuando no hay múltiples árboles."""
        return {
            'num_arboles': 0,
            'probabilidades': [],
            'entropía': 0.0,
            'confianza': 0.0,
            'arbol_seleccionado': None,
            'arbol_idx': -1,
            'es_ambiguo': False,
            'nivel_ambiguedad': 'NINGUNA'
        }
