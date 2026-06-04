"""
PCFG de sospecha linguistica.

Este modulo asigna pesos probabilisticos a construcciones frecuentes en
noticias falsas: afirmaciones absolutas, modales vagos, ausencia de fuente,
negaciones multiples y tipografia sensacionalista.
"""

from typing import Any, Dict, List


PESOS_REGLAS = {
    "S -> S_SIN_FUENTE": 0.90,
    "S -> S_ABSOLUTA": 0.85,
    "S -> S_NEGACION_MULTIPLE": 0.75,
    "S -> S_MODAL_VAGO": 0.65,
    "S -> S_TIPOGRAFIA_SOSPECHOSA": 0.60,
    "S -> S_CORTA_SIN_CONTEXTO": 0.45,
    "S -> S_NEUTRAL": 0.15,
}


class AnalizadorPCFGSospecha:
    """Calcula una probabilidad de sospecha a partir de reglas ponderadas."""

    def __init__(self, pesos_reglas: Dict[str, float] = None):
        self.pesos_reglas = pesos_reglas or PESOS_REGLAS

    def _agrega_regla(
        self,
        reglas: List[Dict[str, Any]],
        nombre: str,
        oracion_idx: int,
        evidencia: Any,
    ) -> None:
        reglas.append({
            "regla": nombre,
            "peso": self.pesos_reglas[nombre],
            "oracion_idx": oracion_idx,
            "evidencia": evidencia,
        })

    def _score_desde_reglas(self, reglas: List[Dict[str, Any]]) -> float:
        if not reglas:
            return 0.0

        prob_no_sospecha = 1.0
        for regla in reglas:
            prob_no_sospecha *= 1.0 - regla["peso"]
        return round(min(1.0 - prob_no_sospecha, 1.0), 3)

    def analiza(self, patrones: Dict[str, Any], num_oraciones: int) -> Dict[str, Any]:
        reglas = []

        for item in patrones.get("ausencia_fuentes", {}).get("detalle", []):
            self._agrega_regla(reglas, "S -> S_SIN_FUENTE", item["oracion_idx"], item)

        for item in patrones.get("afirmaciones_absolutas", {}).get("detalle", []):
            self._agrega_regla(reglas, "S -> S_ABSOLUTA", item["oracion_idx"], item)

        for item in patrones.get("negaciones_multiples", {}).get("detalle", []):
            self._agrega_regla(reglas, "S -> S_NEGACION_MULTIPLE", item["oracion_idx"], item)

        for item in patrones.get("modales_vagos", {}).get("detalle", []):
            self._agrega_regla(reglas, "S -> S_MODAL_VAGO", item["oracion_idx"], item)

        for item in patrones.get("oraciones_cortas", {}).get("detalle", []):
            self._agrega_regla(reglas, "S -> S_CORTA_SIN_CONTEXTO", item["oracion_idx"], item)

        tipografia = patrones.get("tipografia_sospechosa", {})
        total_tipografia = sum(tipografia.values()) if tipografia else 0
        for idx in range(total_tipografia):
            self._agrega_regla(
                reglas,
                "S -> S_TIPOGRAFIA_SOSPECHOSA",
                -1,
                {"patron_idx": idx + 1, "detalle": tipografia},
            )

        if not reglas and num_oraciones > 0:
            reglas.append({
                "regla": "S -> S_NEUTRAL",
                "peso": self.pesos_reglas["S -> S_NEUTRAL"],
                "oracion_idx": 0,
                "evidencia": "sin patrones sospechosos",
            })

        reglas_sospechosas = [r for r in reglas if r["regla"] != "S -> S_NEUTRAL"]
        score = self._score_desde_reglas(reglas_sospechosas)

        return {
            "score_pcfg": score,
            "num_reglas_aplicadas": len(reglas),
            "reglas_aplicadas": reglas,
            "reglas_sospechosas": reglas_sospechosas,
            "es_sospechoso": score >= 0.5,
            "explicacion": self.genera_explicacion(reglas_sospechosas, score),
        }

    def genera_explicacion(self, reglas: List[Dict[str, Any]], score: float) -> str:
        if not reglas:
            return "La PCFG no encontro construcciones sospechosas ponderadas."

        nombres = {}
        for regla in reglas:
            nombres[regla["regla"]] = nombres.get(regla["regla"], 0) + 1

        partes = [
            f"{regla} x{cantidad}"
            for regla, cantidad in sorted(nombres.items())
        ]
        return f"PCFG sospechosa={score:.3f}; reglas activadas: " + ", ".join(partes)
