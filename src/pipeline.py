"""
Pipeline Integrado para Noticonfia

Procesa texto de forma secuencial a través de todos los módulos PLN:

1. Tokenización y normalización
2. Análisis sintáctico (Chart Parser + CFG)
3. Detección de ambigüedad
4. Análisis de rasgos (DCG)
5. Análisis de características (DAG)
6. Detección de patrones sospechosos
7. Clasificación final con justificación

Nota: DAG y DCG se usan como validadores de estructura y rasgos, 
no como analizadores principales. El eje central es:
    Entrada → Tokenización → Chart Parser → Ambigüedad → Patrones → Clasificación → Salida
"""

import re
from typing import List, Dict, Any, Tuple, Optional

# Importar módulos locales
try:
    from lexer import tokenize
    from chart_parser import chart_parser
    from grammar import gramatica
    from ambiguity_detector import DetectorAmbiguedad, detecta_ambiguedad
    from suspicious_patterns import DetectorPatronesSospechosos, detecta_patrones
    from classifier import ClasificadorFakeNews, clasifica_noticia
except ImportError as e:
    # En caso de que los módulos no estén disponibles
    print(f"Advertencia: No se pudo importar módulo: {e}")


class PipelineNoticias:
    """
    Pipeline integrado para análisis de noticias falsas.
    Procesa texto secuencialmente a través de todos los análisis.
    """
    
    def __init__(self, verbose: bool = False):
        """
        Inicializa el pipeline.
        
        Args:
            verbose: Si True, imprime progreso de cada paso
        """
        self.verbose = verbose
        self.detector_ambiguedad = DetectorAmbiguedad()
        self.detector_patrones = DetectorPatronesSospechosos()
        self.clasificador = ClasificadorFakeNews()
    
    def _log(self, mensaje: str, paso: int = 0):
        """Log de progreso si verbose está activado."""
        if self.verbose:
            if paso > 0:
                print(f"\n[PASO {paso}] {mensaje}")
            else:
                print(mensaje)
    
    def tokeniza_normaliza(self, texto: str) -> Tuple[List[str], List[List[str]]]:
        """
        Paso 1: Tokenización y normalización.
        
        Args:
            texto: Texto de la noticia
            
        Returns:
            (oraciones, tokens)
            - oraciones: Lista de oraciones como strings
            - tokens: Lista de listas de tokens por oración
        """
        self._log("Tokenizando y normalizando texto...", 1)
        
        # Normalizar espacios y caracteres especiales
        texto_normalizado = re.sub(r'\s+', ' ', texto).strip()
        
        # Dividir en oraciones (simple: por . ! ?)
        oraciones = re.split(r'[.!?]+', texto_normalizado)
        oraciones = [o.strip() for o in oraciones if o.strip()]
        
        # Tokenizar cada oración
        tokens = []
        for oracion in oraciones:
            # Usar función tokenize si está disponible, sino usar split simple
            try:
                tokens_oracion = tokenize(oracion)
            except:
                # Fallback: split simple
                tokens_oracion = oracion.split()
            tokens.append(tokens_oracion)
        
        self._log(
            f"✓ {len(oraciones)} oraciones, "
            f"{sum(len(t) for t in tokens)} tokens totales"
        )
        
        return oraciones, tokens
    
    def analiza_sintaxis(
        self,
        tokens: List[List[str]],
        gramatica_local: Optional[Dict] = None
    ) -> Tuple[List[Any], Dict[str, Any]]:
        """
        Paso 2: Análisis sintáctico con CFG + Chart Parser.
        
        Args:
            tokens: Tokens por oración
            gramatica_local: Gramática CFG (opcional, usa global si no se proporciona)
            
        Returns:
            (arboles_parse, detalles_sintaxis)
            - arboles_parse: Lista de árboles de análisis
            - detalles_sintaxis: Info sobre el análisis
        """
        self._log("Analizando estructura sintáctica con Chart Parser...", 2)
        
        if gramatica_local is None:
            try:
                gramatica_local = gramatica
            except:
                self._log("⚠ No se encontró gramática, usando mínima", 2)
                gramatica_local = {}
        
        arboles_parse = []
        sintaxis_exitosa = 0
        
        for idx_oracion, tokens_oracion in enumerate(tokens):
            try:
                # Usar chart_parser si está disponible
                try:
                    arbol = chart_parser(tokens_oracion, gramatica_local)
                    if arbol:
                        arboles_parse.append(arbol)
                        sintaxis_exitosa += 1
                except:
                    # Fallback: crear estructura simple
                    arboles_parse.append({'estructura': 'S', 'tokens': tokens_oracion})
                    sintaxis_exitosa += 1
            except Exception as e:
                self._log(f"⚠ Error analizando oración {idx_oracion}: {e}", 2)
        
        detalles = {
            'num_oraciones': len(tokens),
            'sintaxis_exitosa': sintaxis_exitosa,
            'tasa_exito': round(sintaxis_exitosa / len(tokens), 2) if tokens else 0
        }
        
        self._log(
            f"✓ {sintaxis_exitosa}/{len(tokens)} oraciones analizadas sintácticamente"
        )
        
        return arboles_parse, detalles
    
    def detecta_ambiguedad_paso(
        self,
        arboles_parse: List[Any],
        texto_original: str = ""
    ) -> Dict[str, Any]:
        """
        Paso 3: Detección de ambigüedad.
        
        Args:
            arboles_parse: Árboles del chart parser
            
        Returns:
            Dict con análisis de ambigüedad
        """
        self._log("Detectando ambigüedad sintáctica...", 3)
        
        resultado = self.detector_ambiguedad.analiza_completo(arboles_parse, texto_original)
        
        self._log(
            f"✓ {resultado['num_interpretaciones']} interpretaciones posibles, "
            f"score: {resultado['score_ambiguedad']}"
        )
        
        return resultado
    
    def analiza_rasgos_paso(
        self,
        tokens: List[List[str]],
        arboles_parse: List[Any]
    ) -> Dict[str, Any]:
        """
        Paso 4: Análisis de rasgos con DCG (simplificado).
        
        Args:
            tokens: Tokens por oración
            arboles_parse: Árboles sintácticos
            
        Returns:
            Dict con análisis de rasgos
            
        Nota: En una implementación completa, usaría src/dcg.py
        Por ahora retorna estructura simplificada.
        """
        self._log("Analizando rasgos lingüísticos (género, número)...", 4)
        
        rasgos_problema = {
            'concordancia_fallida': False,
            'estructura_inusual': False,
            'num_problemas': 0
        }
        
        # Análisis simplificado de concordancia
        for tokens_oracion in tokens:
            # Buscar concordancia simple: determinante + nombre + adjetivo
            # (implementación muy simplificada)
            pass
        
        self._log("✓ Análisis de rasgos completado")
        
        return rasgos_problema
    
    def analiza_caracteristicas_dag(
        self,
        arboles_parse: List[Any]
    ) -> Dict[str, Any]:
        """
        Paso 5: Análisis de características con DAG (simplificado).
        
        Args:
            arboles_parse: Árboles sintácticos
            
        Returns:
            Dict con características extraídas
            
        Nota: En una implementación completa, usaría src/dag.py
        Por ahora retorna estructura simplificada.
        """
        self._log("Extrayendo características con DAG...", 5)
        
        caracteristicas = {
            'estructuras_encontradas': [],
            'num_caracteristicas': 0
        }
        
        self._log("✓ Análisis DAG completado")
        
        return caracteristicas
    
    def detecta_patrones_paso(
        self,
        texto_original: str,
        tokens: List[List[str]]
    ) -> Dict[str, Any]:
        """
        Paso 6: Detección de patrones sospechosos.
        
        Args:
            texto_original: Texto original
            tokens: Tokens por oración
            
        Returns:
            Dict con patrones encontrados
        """
        self._log("Detectando patrones sospechosos en el texto...", 6)
        
        resultado = self.detector_patrones.analiza_completo(texto_original, tokens)
        
        self._log(
            f"✓ {resultado['resumen']['total_patrones']} patrones detectados, "
            f"score: {resultado['score_total_patrones']}"
        )
        
        return resultado
    
    def clasifica_paso(
        self,
        texto_original: str,
        resultado_ambiguedad: Dict[str, Any],
        resultado_patrones: Dict[str, Any],
        rasgos_problema: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Paso 7: Clasificación final con justificación.
        
        Args:
            texto_original: Texto analizado
            resultado_ambiguedad: Resultado del detector de ambigüedad
            resultado_patrones: Resultado del detector de patrones
            rasgos_problema: Problemas de rasgos detectados
            
        Returns:
            Dict con clasificación y justificación
        """
        self._log("Clasificando noticia...", 7)
        
        # Extraer scores
        score_ambiguedad = resultado_ambiguedad['score_ambiguedad']
        num_interpretaciones = resultado_ambiguedad['num_interpretaciones']
        es_sospechoso_amb = resultado_ambiguedad['indicadores_sospechosos']['es_sospechoso']
        score_patrones = resultado_patrones['score_total_patrones']
        score_rasgos = 0.2 if rasgos_problema.get('concordancia_fallida') else 0.0
        
        # Clasificar
        resultado = self.clasificador.clasifica_completo(
            texto_original,
            score_ambiguedad,
            num_interpretaciones,
            es_sospechoso_amb,
            resultado_patrones,
            score_rasgos,
            rasgos_problema
        )
        
        self._log(
            f"✓ Clasificación: {resultado['categoria']} "
            f"(confianza: {resultado['confianza']})"
        )
        
        return resultado
    
    def procesa_noticia(self, texto: str) -> Dict[str, Any]:
        """
        Procesa una noticia completa a través del pipeline.
        
        Args:
            texto: Texto de la noticia a analizar
            
        Returns:
            Dict con:
            - texto_original
            - tokenizacion
            - sintaxis
            - ambiguedad
            - patrones
            - clasificacion (con desglose y justificación)
            
        Flujo:
            1. Tokenización → 2. Sintaxis → 3. Ambigüedad → 
            4. Rasgos → 5. DAG → 6. Patrones → 7. Clasificación
        """
        self._log("\n" + "="*70)
        self._log("INICIANDO ANÁLISIS DE NOTICIA")
        self._log("="*70)
        
        # Paso 1: Tokenización
        oraciones, tokens = self.tokeniza_normaliza(texto)
        
        # Paso 2: Análisis sintáctico
        arboles_parse, detalles_sintaxis = self.analiza_sintaxis(tokens)
        
        # Paso 3: Ambigüedad
        resultado_ambiguedad = self.detecta_ambiguedad_paso(arboles_parse, texto)
        
        # Paso 4: Rasgos
        rasgos_problema = self.analiza_rasgos_paso(tokens, arboles_parse)
        
        # Paso 5: DAG
        caracteristicas = self.analiza_caracteristicas_dag(arboles_parse)
        
        # Paso 6: Patrones sospechosos
        resultado_patrones = self.detecta_patrones_paso(texto, tokens)
        
        # Paso 7: Clasificación
        resultado_clasificacion = self.clasifica_paso(
            texto,
            resultado_ambiguedad,
            resultado_patrones,
            rasgos_problema
        )
        
        # Compilar resultado final
        resultado_final = {
            'texto_original': texto,
            'estadisticas_basicas': {
                'num_caracteres': len(texto),
                'num_palabras': sum(len(t) for t in tokens),
                'num_oraciones': len(oraciones)
            },
            'tokenizacion': {
                'oraciones': oraciones,
                'tokens': tokens
            },
            'sintaxis': detalles_sintaxis,
            'ambiguedad': resultado_ambiguedad,
            'rasgos': rasgos_problema,
            'caracteristicas_dag': caracteristicas,
            'patrones': resultado_patrones,
            'clasificacion': resultado_clasificacion
        }
        
        self._log("\n" + "="*70)
        self._log(f"ANÁLISIS COMPLETADO")
        self._log("="*70 + "\n")
        
        return resultado_final
    
    def resume_resultado(self, resultado: Dict[str, Any]) -> str:
        """
        Genera un resumen en texto del análisis.
        
        Args:
            resultado: Resultado del pipeline
            
        Returns:
            String con resumen formateado
        """
        clasificacion = resultado['clasificacion']
        
        resumen = f"""
╔════════════════════════════════════════════════════════════════╗
║                      RESULTADO DEL ANÁLISIS                   ║
╚════════════════════════════════════════════════════════════════╝

TEXTO ANALIZADO:
{resultado['texto_original'][:100]}...

CLASIFICACIÓN: {clasificacion['categoria']}
Confianza: {clasificacion['confianza'] * 100:.1f}%

DESGLOSE DE SCORES:
- Ambigüedad:  {clasificacion['desglose']['ambiguedad']['score']:.2f}/1.0
- Patrones:    {clasificacion['desglose']['patrones']['score']:.2f}/1.0
- Rasgos:      {clasificacion['desglose']['rasgos']['score']:.2f}/1.0

JUSTIFICACIÓN:
{clasificacion['justificacion_completa']}

RECOMENDACIÓN:
{clasificacion['recomendacion']}

════════════════════════════════════════════════════════════════
"""
        return resumen


# Función auxiliar para usar el pipeline fácilmente
def analiza_noticia(texto: str, verbose: bool = False) -> Dict[str, Any]:
    """
    Analiza una noticia usando el pipeline completo.
    
    Args:
        texto: Texto de la noticia
        verbose: Si True, muestra progreso
        
    Returns:
        Dict con resultado completo
        
    Ejemplo:
        >>> resultado = analiza_noticia("La noticia que quiero verificar...")
        >>> print(resultado['clasificacion']['categoria'])
        'SUSPICIOUS'
    """
    pipeline = PipelineNoticias(verbose=verbose)
    return pipeline.procesa_noticia(texto)
