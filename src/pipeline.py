"""
Pipeline Integrado para Noticonfia

Procesa texto de forma secuencial a través de todos los módulos PLN:

1. Tokenización y normalización con validación DCG/DAG
2. Análisis sintáctico (Chart Parser + CFG)
3. Detección de ambigüedad
4. Análisis de rasgos (basado en DCG/DAG de normalización)
5. Análisis de características (DAG)
6. Detección de patrones sospechosos
7. Clasificación final con justificación

DCG y DAG integrados en la normalización para rechazar errores de concordancia
(como "una gobierno miente") mediante unificación de rasgos de género y número.
El eje central es:
    Entrada → Tokenización + DCG/DAG → Chart Parser → Ambigüedad → Patrones → Clasificación → Salida
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
    from dcg import Parser as ParserDCG, crear_lexico_fake_news
    from dag import estadisticas_dag, crear_dag_oracion
    from pcfg_suspicion import AnalizadorPCFGSospecha
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
        self.analizador_pcfg = AnalizadorPCFGSospecha()
        self.clasificador = ClasificadorFakeNews()
        self.lexico_dcg = crear_lexico_fake_news()
        self.parser_dcg = ParserDCG(self.lexico_dcg, debug=False)
    
    def _log(self, mensaje: str, paso: int = 0):
        """Log de progreso si verbose está activado."""
        if self.verbose:
            if paso > 0:
                print(f"\n[PASO {paso}] {mensaje}")
            else:
                print(mensaje)
    
    def tokeniza_normaliza(self, texto: str) -> Tuple[List[str], List[List[str]], Dict[str, Any]]:
        """
        Paso 1: Tokenización y normalización + validación DCG/DAG.
        
        Args:
            texto: Texto de la noticia
            
        Returns:
            (oraciones, tokens, normalizacion)
            - oraciones: Lista de oraciones como strings
            - tokens: Lista de listas de tokens por oración
            - normalizacion: Dict con validación DCG/DAG (concordancia gramatical)
        """
        self._log("Tokenizando y normalizando texto...", 1)
        
        texto_normalizado = re.sub(r'\s+', ' ', texto).strip()
        
        oraciones = re.split(r'[.!?]+', texto_normalizado)
        oraciones = [o.strip() for o in oraciones if o.strip()]
        
        tokens = []
        for oracion in oraciones:
            try:
                tokens_oracion = tokenize(oracion)
            except:
                tokens_oracion = oracion.split()
            tokens.append(tokens_oracion)
        
        normalizacion = self._valida_normalizacion_dcg(tokens)
        
        self._log(
            f"✓ {len(oraciones)} oraciones, "
            f"{sum(len(t) for t in tokens)} tokens totales"
        )
        if normalizacion['oraciones_invalidas']:
            self._log(
                f"⚠ {len(normalizacion['oraciones_invalidas'])} oraciones con "
                f"errores de concordancia"
            )
        
        return oraciones, tokens, normalizacion
    
    def _valida_normalizacion_dcg(self, tokens: List[List[str]]) -> Dict[str, Any]:
        """
        Valida concordancia gramatical con DCG + DAG.
        Rechaza errores como "una gobierno miente" mediante unificación de rasgos.
        """
        self._log("     Validando concordancia gramatical (DCG + DAG)...", 1)
        lexico = self.lexico_dcg
        parser = self.parser_dcg

        oraciones_validas = []
        oraciones_invalidas = []
        errores = []
        dags_generados = []

        for idx, tokens_oracion in enumerate(tokens):
            tokens_limpios = [
                t.lower().strip('.,!?;:\u00bf\u00a1"\'()[]')
                for t in tokens_oracion
                if t.strip('.,!?;:\u00bf\u00a1"\'()[]')
            ]

            if not tokens_limpios:
                oraciones_validas.append(idx)
                continue

            resultado = parser.analizar_s(tokens_limpios)

            if resultado is not None:
                oro_dag = crear_dag_oracion(
                    resultado.get('np', {}),
                    resultado.get('vp', {}),
                    {'accion': resultado.get('accion', '')}
                )
                dags_generados.append({
                    'oracion_idx': idx,
                    'tokens': tokens_limpios,
                    'dag': oro_dag,
                    'intencion': parser.extraer_intencion(resultado)
                })
                oraciones_validas.append(idx)
            else:
                error_msg = parser.ultimo_error or 'Estructura no reconocida'

                es_error_concordancia = any(p in error_msg.lower() for p in [
                    'concordancia', 'conflicto'
                ])

                if es_error_concordancia:
                    oraciones_invalidas.append({
                        'oracion_idx': idx,
                        'tokens': tokens_limpios,
                        'error': error_msg,
                        'tipo': 'concordancia'
                    })
                    errores.append(error_msg)
                else:
                    oraciones_validas.append(idx)

        return {
            'oraciones_validas': oraciones_validas,
            'oraciones_invalidas': oraciones_invalidas,
            'errores_concordancia': errores,
            'dags_generados': dags_generados,
            'texto_gramaticalmente_valido': len(oraciones_invalidas) == 0,
            'num_oraciones_validas': len(oraciones_validas),
            'num_oraciones_invalidas': len(oraciones_invalidas)
        }
    
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
        charts = []
        sintaxis_exitosa = 0
        
        for idx_oracion, tokens_oracion in enumerate(tokens):
            try:
                # Usar chart_parser si está disponible
                try:
                    arboles_oracion, chart = chart_parser(tokens_oracion, gramatica_local)
                    charts.append(chart)
                    if arboles_oracion:
                        arboles_parse.extend(arboles_oracion)
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
            'tasa_exito': round(sintaxis_exitosa / len(tokens), 2) if tokens else 0,
            'num_arboles': len(arboles_parse),
            'num_charts': len(charts)
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
        arboles_parse: List[Any],
        normalizacion: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Paso 4: Análisis de rasgos con DCG.
        Usa los resultados de validación DCG/DAG del paso 1 (normalización).
        
        Args:
            tokens: Tokens por oración
            arboles_parse: Árboles sintácticos
            normalizacion: Resultados de validación DCG/DAG del paso 1
            
        Returns:
            Dict con análisis de rasgos
        """
        self._log("Analizando rasgos lingüísticos (género, número)...", 4)
        
        if normalizacion and normalizacion.get('dags_generados'):
            dags_dcg = normalizacion['dags_generados']
            oraciones_fallidas = normalizacion.get('oraciones_invalidas', [])
            problemas = ['concordancia'] if normalizacion.get('oraciones_invalidas') else []
            
            rasgos_problema = {
                'concordancia_fallida': bool(oraciones_fallidas),
                'estructura_inusual': bool(oraciones_fallidas),
                'num_problemas': len(oraciones_fallidas),
                'oraciones_analizadas': len(tokens),
                'oraciones_dcg_validas': len(dags_dcg),
                'oraciones_dcg_fallidas': oraciones_fallidas,
                'dags_dcg': dags_dcg,
                'problemas': problemas
            }
        else:
            rasgos_problema = {
                'concordancia_fallida': False,
                'estructura_inusual': False,
                'num_problemas': 0,
                'oraciones_analizadas': len(tokens),
                'oraciones_dcg_validas': 0,
                'oraciones_dcg_fallidas': [],
                'dags_dcg': [],
                'problemas': []
            }
        
        self._log("✓ Análisis de rasgos completado")
        
        return rasgos_problema
    
    def analiza_caracteristicas_dag(
        self,
        arboles_parse: List[Any],
        rasgos_problema: Optional[Dict[str, Any]] = None
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
        
        dags_dcg = (rasgos_problema or {}).get('dags_dcg', [])
        estructuras = []

        for item in dags_dcg:
            dag_oracion = item['dag']
            estructuras.append({
                'oracion_idx': item['oracion_idx'],
                'tokens': item['tokens'],
                'intencion': item['intencion'],
                'estadisticas': estadisticas_dag(dag_oracion),
                'dag': dag_oracion
            })

        caracteristicas = {
            'estructuras_encontradas': estructuras,
            'num_caracteristicas': len(estructuras),
            'num_arboles_cfg': len(arboles_parse),
            'usa_dcg': True,
            'usa_dag': True
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

    def analiza_pcfg_paso(
        self,
        resultado_patrones: Dict[str, Any],
        num_oraciones: int,
        resultado_ambiguedad: Dict[str, Any] = None,
        rasgos_problema: Dict[str, Any] = None,
        normalizacion: Dict[str, Any] = None,
    ) -> Dict[str, Any]:
        """
        Paso 7: PCFG que integra patrones, ambigüedad, DCG/DAG y normalización.
        Sigue el enfoque de la Clase 10: P(árbol) = Π P(regla).
        """
        self._log("Aplicando PCFG — integrando patrones, ambigüedad, DCG/DAG...", 7)

        score_amb = (resultado_ambiguedad or {}).get('score_ambiguedad', 0.0)

        resultado = self.analizador_pcfg.analiza(
            resultado_patrones,
            num_oraciones,
            rasgos_problema=rasgos_problema,
            score_ambiguedad=score_amb,
            normalizacion=normalizacion,
        )

        self._log(
            f"✓ PCFG score: {resultado['score_pcfg']} "
            f"({resultado['num_reglas_aplicadas']} reglas)"
        )

        return resultado
    
    def clasifica_paso(
        self,
        texto_original: str,
        resultado_ambiguedad: Dict[str, Any],
        resultado_patrones: Dict[str, Any],
        rasgos_problema: Dict[str, Any],
        resultado_pcfg: Optional[Dict[str, Any]] = None,
        normalizacion: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Paso 7: Clasificación final con justificación.
        
        Args:
            texto_original: Texto analizado
            resultado_ambiguedad: Resultado del detector de ambigüedad
            resultado_patrones: Resultado del detector de patrones
            rasgos_problema: Problemas de rasgos detectados
            resultado_pcfg: Resultado del análisis PCFG
            normalizacion: Resultados de validación DCG/DAG del paso 1
            
        Returns:
            Dict con clasificación y justificación
        """
        self._log("Clasificando noticia...", 8)
        
        score_ambiguedad = resultado_ambiguedad['score_ambiguedad']
        num_interpretaciones = resultado_ambiguedad['num_interpretaciones']
        es_sospechoso_amb = resultado_ambiguedad['indicadores_sospechosos']['es_sospechoso']
        score_patrones = resultado_patrones['score_total_patrones']
        score_rasgos = min(rasgos_problema.get('num_problemas', 0) * 0.25, 1.0)
        score_pcfg = (resultado_pcfg or {}).get('score_pcfg', 0.0)
        
        resultado = self.clasificador.clasifica_completo(
            texto_original,
            score_ambiguedad,
            num_interpretaciones,
            es_sospechoso_amb,
            resultado_patrones,
            score_rasgos,
            rasgos_problema,
            score_pcfg,
            resultado_pcfg
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
        
        # Paso 1: Tokenización + validación DCG/DAG
        oraciones, tokens, normalizacion = self.tokeniza_normaliza(texto)

        if not normalizacion['texto_gramaticalmente_valido']:
            self._log("⚠ Se detectaron errores de concordancia gramatical", 1)

        # Paso 2: Análisis sintáctico
        arboles_parse, detalles_sintaxis = self.analiza_sintaxis(tokens)

        # Paso 3: Ambigüedad
        resultado_ambiguedad = self.detecta_ambiguedad_paso(arboles_parse, texto)

        # Paso 4: Rasgos (usa DCG/DAG de normalización)
        rasgos_problema = self.analiza_rasgos_paso(tokens, arboles_parse, normalizacion)

        # Paso 5: DAG
        caracteristicas = self.analiza_caracteristicas_dag(arboles_parse, rasgos_problema)

        # Paso 6: Patrones sospechosos
        resultado_patrones = self.detecta_patrones_paso(texto, tokens)

        resultado_pcfg = self.analiza_pcfg_paso(
            resultado_patrones,
            len(oraciones),
            resultado_ambiguedad=resultado_ambiguedad,
            rasgos_problema=rasgos_problema,
            normalizacion=normalizacion,
        )

        # Paso 7: Clasificación
        resultado_clasificacion = self.clasifica_paso(
            texto,
            resultado_ambiguedad,
            resultado_patrones,
            rasgos_problema,
            resultado_pcfg,
            normalizacion
        )
        
        # Compilar resultado final
        resultado_final = {
            'texto_original': texto,
            'estadisticas_basicas': {
                'num_caracteres': len(texto),
                'num_palabras': sum(len(t) for t in tokens),
                'num_oraciones': len(oraciones)
            },
            'normalizacion': normalizacion,
            'tokenizacion': {
                'oraciones': oraciones,
                'tokens': tokens
            },
            'sintaxis': detalles_sintaxis,
            'ambiguedad': resultado_ambiguedad,
            'rasgos': rasgos_problema,
            'caracteristicas_dag': caracteristicas,
            'patrones': resultado_patrones,
            'pcfg': resultado_pcfg,
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
        
        normalizacion = resultado.get('normalizacion', {})
        num_validas = normalizacion.get('num_oraciones_validas', 0)
        num_invalidas = normalizacion.get('num_oraciones_invalidas', 0)
        estado_gramatical = "VÁLIDO" if normalizacion.get('texto_gramaticalmente_valido', True) else f"ERROR ({num_invalidas} oración(es) con fallo de concordancia)"

        resumen = f"""
╔════════════════════════════════════════════════════════════════╗
║                      RESULTADO DEL ANÁLISIS                   ║
╚════════════════════════════════════════════════════════════════╝

TEXTO ANALIZADO:
{resultado['texto_original'][:100]}...

CLASIFICACIÓN: {clasificacion['categoria']}
Confianza: {clasificacion['confianza'] * 100:.1f}%

VALIDACIÓN GRAMATICAL (DCG + DAG): {estado_gramatical}
- Oraciones válidas: {num_validas}
- Oraciones con error: {num_invalidas}

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
