"""
PCFG de sospecha lingüística — formato Clase 10 (Luz Carime Lucumí).

Sigue la estructura de la profesora:
  gramatica = { LHS: [(RHS_tuple, probabilidad), ...] }
  Las probabilidades de cada LHS suman 1.0.
  P(árbol) = Π P(regla) para cada regla usada en el árbol.

Cada regla modela un patrón de lenguaje sospechoso.
Las probabilidades determinan el nivel de alerta:
  - Reglas con probabilidad ALTA = patrón muy sospechoso
  - Reglas con probabilidad BAJA = patrón leve o normal
"""

from typing import Any, Dict, List, Tuple


SOS_PCFG = {
    "S": [
        (("S_NEUTRAL",), 0.15),
        (("S_SIN_FUENTE",), 0.25),
        (("S_ABSOLUTA",), 0.20),
        (("S_MODAL_VAGO",), 0.15),
        (("S_NEGACION",), 0.10),
        (("S_CORTA",), 0.08),
        (("S_TIPOGRAFIA",), 0.05),
        (("S_CONCORDANCIA",), 0.02),
    ],
    "S_NEUTRAL": [
        (("NP", "VP"), 1.0),
    ],
    "S_SIN_FUENTE": [
        (("NP", "VP"), 0.60),
        (("V",), 0.25),
        (("V", "NP"), 0.15),
    ],
    "S_ABSOLUTA": [
        (("ADV_ABS", "VP"), 0.50),
        (("V", "ADV_ABS"), 0.30),
        (("NP", "ADV_ABS"), 0.20),
    ],
    "S_MODAL_VAGO": [
        (("MODAL", "VP"), 0.55),
        (("V", "MODAL"), 0.30),
        (("MODAL", "NP"), 0.15),
    ],
    "S_NEGACION": [
        (("NEG", "VP"), 0.50),
        (("NP", "NEG", "VP"), 0.30),
        (("VP", "NEG"), 0.20),
    ],
    "S_CORTA": [
        (("FRAG",), 0.60),
        (("EXCL",), 0.40),
    ],
    "S_TIPOGRAFIA": [
        (("EXCL_MULT",), 0.50),
        (("CAPS",), 0.30),
        (("SUSP",), 0.20),
    ],
    "S_CONCORDANCIA": [
        (("ERR_CONC",), 1.0),
    ],
}


class AnalizadorPCFGSospecha:
    """
    Analizador PCFG que calcula P(sospecha) siguiendo el método de la Clase 10:
      P(árbol) = Π P(regla_i) para cada regla i en el árbol de sospecha.
    
    Reglas con probabilidad alta → más peso en la sospecha total.
    """

    def __init__(self, gramatica: Dict[str, List[Tuple[Tuple[str, ...], float]]] = None):
        self.gramatica = gramatica or SOS_PCFG.copy()

    def prob_regla(self, lhs: str, rhs: Tuple[str, ...]) -> float:
        """Retorna P(regla) = probabilidad de lhs → rhs, siguiendo Clase 10."""
        for produccion, prob in self.gramatica.get(lhs, []):
            if produccion == rhs:
                return prob
        return 0.0

    def prob_arbol(self, reglas: List[Dict[str, Any]]) -> float:
        """
        Calcula P(al menos una regla sospechosa se active).
        
        Dado que las reglas de sospecha son detecciones independientes
        (a diferencia de un árbol sintáctico donde las reglas son alternativas),
        combinamos como:
            P(sospecha) = 1 - Π (1 - P(regla_i))
        
        Esto da un valor en [0, 1] que refleja cuántas reglas
        de alto peso se activaron.
        """
        if not reglas:
            return 0.0

        prob_ninguna = 1.0
        for regla in reglas:
            nombre = regla["regla"]
            partes = nombre.split(" -> ")
            if len(partes) == 2:
                lhs = partes[0]
                rhs = tuple(partes[1].split(" "))
                p = self.prob_regla(lhs, rhs)
            else:
                p = self.prob_regla("S", (nombre,))

            prob_ninguna *= 1.0 - max(p, 0.001)

        return round(min(1.0 - prob_ninguna, 1.0), 6)

    def _arma_regla(
        self,
        nombre: str,
        oracion_idx: int,
        evidencia: Any,
    ) -> Dict[str, Any]:
        partes = nombre.split(" -> ")
        if len(partes) == 2:
            lhs = partes[0]
            rhs = tuple(partes[1].split(" "))
            peso = self.prob_regla(lhs, rhs)
        else:
            peso = self.prob_regla("S", (nombre,))

        return {
            "regla": nombre,
            "peso": peso,
            "oracion_idx": oracion_idx,
            "evidencia": evidencia,
        }

    def analiza(
        self,
        patrones: Dict[str, Any],
        num_oraciones: int,
        rasgos_problema: Dict[str, Any] = None,
        score_ambiguedad: float = 0.0,
        normalizacion: Dict[str, Any] = None,
    ) -> Dict[str, Any]:
        """
        Analiza el texto y calcula P(sospecha) integrando todos los módulos.
        Sigue el flujo de la Clase 10:
          1. Identificar qué reglas dispara cada patrón
          2. Calcular P(árbol) = Π P(regla)
          3. Determinar nivel de alerta

        Args:
            patrones: Resultado del detector de patrones sospechosos
            num_oraciones: Número de oraciones en el texto
            rasgos_problema: Resultado del análisis DCG/DAG
            score_ambiguedad: Score de ambigüedad léxica
            normalizacion: Resultados de validación gramatical

        Returns:
            Dict con score_pcfg, reglas aplicadas, explicación
        """
        reglas = []

        # --- Patrones sospechosos → reglas PCFG ---
        for item in patrones.get("ausencia_fuentes", {}).get("detalle", []):
            reglas.append(self._arma_regla("S -> S_SIN_FUENTE", item["oracion_idx"], item))

        for item in patrones.get("afirmaciones_absolutas", {}).get("detalle", []):
            reglas.append(self._arma_regla("S -> S_ABSOLUTA", item["oracion_idx"], item))

        for item in patrones.get("negaciones_multiples", {}).get("detalle", []):
            reglas.append(self._arma_regla("S -> S_NEGACION", item["oracion_idx"], item))

        for item in patrones.get("modales_vagos", {}).get("detalle", []):
            reglas.append(self._arma_regla("S -> S_MODAL_VAGO", item["oracion_idx"], item))

        for item in patrones.get("oraciones_cortas", {}).get("detalle", []):
            reglas.append(self._arma_regla("S -> S_CORTA", item["oracion_idx"], item))

        tipografia = patrones.get("tipografia_sospechosa", {})
        if tipografia.get("exclamaciones_multiples", 0) > 0:
            reglas.append(self._arma_regla("S -> S_TIPOGRAFIA", -1, tipografia))

        # --- DCG/DAG: errores de concordancia → S_CONCORDANCIA ---
        if normalizacion:
            for inv in normalizacion.get("oraciones_invalidas", []):
                reglas.append(self._arma_regla(
                    "S -> S_CONCORDANCIA",
                    inv["oracion_idx"],
                    inv["error"]
                ))

        if rasgos_problema:
            for fallo in rasgos_problema.get("oraciones_dcg_fallidas", []):
                reglas.append(self._arma_regla(
                    "S -> S_CONCORDANCIA",
                    fallo.get("oracion_idx", 0),
                    fallo.get("error", "fallo DCG")
                ))

        # --- Ambigüedad: ajusta S_NEUTRAL ---
        # Alta ambigüedad = menos neutral = más sospechoso
        if score_ambiguedad > 0.3:
            reglas.append(self._arma_regla(
                "S -> S_ABSOLUTA",
                -1,
                {"tipo": "ambiguedad_alta", "score": score_ambiguedad}
            ))

        # --- Si no hay reglas sospechosas, aplicar S_NEUTRAL ---
        if not reglas and num_oraciones > 0:
            reglas.append(self._arma_regla("S -> S_NEUTRAL", 0, "sin patrones"))

        # --- Calcular P(árbol) siguiendo Clase 10 ---
        reglas_sospechosas = [r for r in reglas if r["regla"] != "S -> S_NEUTRAL"]
        score_pcfg = self.prob_arbol(reglas_sospechosas)

        return {
            "score_pcfg": score_pcfg,
            "num_reglas_aplicadas": len(reglas),
            "reglas_aplicadas": reglas,
            "reglas_sospechosas": reglas_sospechosas,
            "es_sospechoso": score_pcfg >= 0.5,
            "explicacion": self._genera_explicacion(reglas_sospechosas, score_pcfg),
        }

    def _genera_explicacion(self, reglas: List[Dict[str, Any]], score: float) -> str:
        if not reglas:
            return "PCFG: ninguna regla de sospecha activada."

        nombres = {}
        for regla in reglas:
            nombres[regla["regla"]] = nombres.get(regla["regla"], 0) + 1

        partes = [
            f"{nombre} x{conteo} (P={self.prob_regla(nombre.split(' -> ')[0], tuple(nombre.split(' -> ')[1].split(' '))):.2f})"
            if " -> " in nombre
            else f"{nombre} x{conteo}"
            for nombre, conteo in sorted(nombres.items())
        ]
        return f"PCFG P(sospecha)={score:.3f}; reglas activadas: " + ", ".join(partes)
