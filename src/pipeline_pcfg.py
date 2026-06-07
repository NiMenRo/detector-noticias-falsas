# Pipeline Completo PCFG
# Problema 10: Rediseño completo del pipeline

import json
from typing import Dict, Any

class PipelinePCFG:
    """
    Pipeline completo que integra:
    - Tokenización y normalización
    - CFG + Chart Parser
    - Detección de ambigüedad (natural desde múltiples árboles)
    - PCFG (núcleo central)
    - Clasificación basada en P(árbol)
    - Justificación lingüística
    """
    
    def __init__(self, pcfg=None, ambiguity_detector=None, justifier=None, classifier=None):
        """
        Inicializa el pipeline con módulos.
        
        Args:
            pcfg: Instancia de PCFG
            ambiguity_detector: Detector de ambigüedad sintáctica
            justifier: Generador de justificaciones
            classifier: Clasificador basado en PCFG
        """
        self.pcfg = pcfg
        self.ambiguity_detector = ambiguity_detector
        self.justifier = justifier
        self.classifier = classifier
    
    def procesar(self, texto: str) -> Dict[str, Any]:
        """
        Procesa un texto completo a través del pipeline.
        
        Flujo esperado (Problema 10):
        
        Texto
          ↓
        Tokenización y normalización
          ↓
        CFG + Chart Parser
          ↓
        Árboles sintácticos
          ↓
        Detección de ambigüedad
          ↓
        PCFG entrenada desde corpus
          ↓
        P(árbol)
          ↓
        Clasificación
          ↓
        Justificación lingüística
        """
        
        print(f"\n{'='*70}")
        print("PIPELINE PCFG - ANÁLISIS DE NOTICIAS")
        print(f"{'='*70}\n")
        print(f"Texto: {texto}\n")
        
        # Paso 1: Tokenización y normalización
        tokens = self._tokenizar_normalizar(texto)
        print(f"✓ Paso 1: Tokenización ({len(tokens)} tokens)")
        
        # Paso 2: Chart Parser genera árboles
        arboles = self._generar_arboles(tokens, texto)
        print(f"✓ Paso 2: Chart Parser ({len(arboles)} árboles)")
        
        # Paso 3: Detección de ambigüedad natural
        ambiguedad = self._analizar_ambiguedad(arboles)
        print(f"✓ Paso 3: Ambigüedad detectada (entropía={ambiguedad['entropía']:.3f})")
        
        # Paso 4: Seleccionar árbol más probable
        arbol_seleccionado = ambiguedad.get('arbol_seleccionado')
        
        # Paso 5: Calcular P(árbol) con PCFG
        p_arbol = self._calcular_p_arbol(arbol_seleccionado)
        print(f"✓ Paso 4: PCFG calculó P(árbol) = {p_arbol:.4f}")
        
        # Paso 6: Clasificación basada en P(árbol)
        clasificacion = self._clasificar(p_arbol, arbol_seleccionado, texto)
        print(f"✓ Paso 5: Clasificación = {clasificacion['categoria']}")
        
        # Paso 7: Generar justificación lingüística
        justificacion = self._generar_justificacion(
            texto, arbol_seleccionado, ambiguedad, clasificacion
        )
        print(f"✓ Paso 6: Justificación generada\n")
        
        # Retornar resultado completo
        return {
            'texto': texto,
            'tokens': tokens,
            'num_arboles': len(arboles),
            'ambiguedad': ambiguedad,
            'arbol_seleccionado': arbol_seleccionado,
            'p_arbol': p_arbol,
            'clasificacion': clasificacion,
            'justificacion': justificacion
        }
    
    def _tokenizar_normalizar(self, texto: str):
        """Tokenización y normalización (Paso 1)."""
        import re
        tokens = re.findall(r'\b\w+\b', texto.lower())
        return tokens
    
    def _generar_arboles(self, tokens, texto):
        """Genera árboles sintácticos con Chart Parser (Paso 2)."""
        # Simulación: retorna múltiples árboles para mostrar ambigüedad
        # En producción, esto llamaría al chart_parser real
        arboles = []
        
        # Árbol 1: Análisis neutral
        arbol1 = {
            'simbolo': 'S',
            'regla': 'S -> NP VP',
            'prob_regla': 1.0,
            'hijos': [
                {
                    'simbolo': 'NP',
                    'regla': 'NP -> Det N',
                    'prob_regla': 0.7,
                    'hijos': [
                        {'simbolo': 'Det', 'token': tokens[0] if len(tokens) > 0 else 'el'},
                        {'simbolo': 'N', 'token': tokens[1] if len(tokens) > 1 else 'texto'}
                    ]
                },
                {
                    'simbolo': 'VP',
                    'regla': 'VP -> V NP',
                    'prob_regla': 0.55,
                    'hijos': []
                }
            ]
        }
        arboles.append(arbol1)
        
        # Árbol 2: Análisis con modalidad (si aplica)
        if any(t in tokens for t in ['podría', 'aparentemente', 'posiblemente']):
            arbol2 = {
                'simbolo': 'S',
                'regla': 'S -> NP VP',
                'prob_regla': 1.0,
                'hijos': [
                    {'simbolo': 'NP', 'regla': 'NP -> Det N', 'prob_regla': 0.7},
                    {
                        'simbolo': 'VP',
                        'regla': 'VP -> MODAL VP',
                        'prob_regla': 0.25,
                        'hijos': []
                    }
                ]
            }
            arboles.append(arbol2)
        
        return arboles
    
    def _analizar_ambiguedad(self, arboles):
        """Detecta ambigüedad natural desde múltiples árboles (Paso 3)."""
        if not self.ambiguity_detector:
            return self._ambiguedad_default(arboles)
        
        return self.ambiguity_detector.detectar_ambiguedad_sintactica(arboles)
    
    def _ambiguedad_default(self, arboles):
        """Ambigüedad por defecto si no hay detector."""
        return {
            'num_arboles': len(arboles),
            'es_ambiguo': len(arboles) > 1,
            'entropía': 0.5 if len(arboles) > 1 else 0.0,
            'arbol_seleccionado': arboles[0] if arboles else None
        }
    
    def _calcular_p_arbol(self, arbol):
        """Calcula P(árbol) con PCFG (Paso 4)."""
        if not arbol or not self.pcfg:
            return 0.5
        
        return self.pcfg.calcular_p_arbol(arbol)
    
    def _clasificar(self, p_arbol, arbol, texto):
        """Clasificación basada en P(árbol) (Paso 5)."""
        if not self.classifier:
            # Default: si P(árbol) es baja, es sospechoso
            if p_arbol < 0.3:
                return {'categoria': 'FAKE', 'riesgo': 0.8, 'p_arbol': p_arbol}
            elif p_arbol < 0.6:
                return {'categoria': 'SUSPICIOUS', 'riesgo': 0.5, 'p_arbol': p_arbol}
            else:
                return {'categoria': 'CREDIBLE', 'riesgo': 0.2, 'p_arbol': p_arbol}
        
        # Con clasificador real
        score_pcfg = 1.0 - p_arbol  # Invertir: P baja = sospechoso
        resultado = self.classifier.clasifica_completo(
            texto,
            score_ambiguedad=0.0,
            num_interpretaciones=1,
            es_sospechoso_amb=False,
            patrones_dict={},
            score_pcfg=score_pcfg
        )
        return resultado
    
    def _generar_justificacion(self, texto, arbol, ambiguedad, clasificacion):
        """Genera justificación lingüística (Paso 6)."""
        if not self.justifier:
            return {
                'resumen': f"Clasificación: {clasificacion['categoria']}",
                'reglas': [],
                'patrones': []
            }
        
        return self.justifier.generar_justificacion(texto, arbol, ambiguedad, clasificacion)


def crear_pipeline(pcfg=None, ambiguity_detector=None, justifier=None, classifier=None):
    """Factory para crear pipeline."""
    return PipelinePCFG(pcfg, ambiguity_detector, justifier, classifier)


# Ejemplo de uso completo
if __name__ == "__main__":
    # Crear pipeline con módulos
    from pcfg import obtener_pcfg
    from ambiguity_detector import AmbiguityDetectorSyntactic
    from justifier import crear_justifier
    from classifier import ClasificadorFakeNews
    
    pcfg = obtener_pcfg()
    detector = AmbiguityDetectorSyntactic()
    justifier = crear_justifier(pcfg)
    classifier = ClasificadorFakeNews()
    
    pipeline = crear_pipeline(pcfg, detector, justifier, classifier)
    
    # Procesar textos de ejemplo
    textos = [
        "El gobierno anunció nuevas políticas económicas",
        "Supuestamente el gobierno oculta información secreta",
        "La agencia oficial confirmó los datos verificados",
        "SE CONFIRMA LA VERDAD QUE OCULTAN!!Todos los médicos mienten siempre.Se dice que una vacuna puede controlar la mente de las personas.Nadie nunca ha demostrado que esto sea falso.Definitivamente es un hecho.",
        "Según algunas personas, el gobierno podría estar ocultando información.Aparentemente existen documentos secretos.Tal vez pronto se conozcan más detalles."
    ]
    
    for texto in textos:
        resultado = pipeline.procesar(texto)
        print(f"\nResultado final:")
        print(json.dumps(resultado, indent=2, ensure_ascii=False)[:500])
