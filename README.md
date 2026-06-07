# Detector de Noticias Falsas — PLN

Sistema de detección de noticias falsas basado en CFG, Chart Parser, DCG, DAG, PCFG y clasificación por pesos.

## Ejecución

```bash
python src/demo.py
```

Menú interactivo con 3 opciones:
1. **Analizar texto manualmente** — ingresa cualquier texto, muestra árbol sintáctico (ventana gráfica), clasificación y PCFG real desde corpus.
2. **Ejecutar 6 casos de prueba** — ejecuta toda la batería sin ventanas.
3. **Salir**

## Dependencias

- Python 3.10+
- `matplotlib` (solo para visualización de árboles en modo manual)

## Componentes

| Módulo | Función |
|---|---|
| `src/pipeline.py` | Orquestador de 7 pasos: tokenización → sintaxis → ambigüedad → rasgos → DAG → patrones → clasificación |
| `src/grammar.py` | CFG del español con 50+ reglas (PP, MODAL, ADV_ABS, etc.) |
| `src/chart_parser.py` | Algoritmo CYK para análisis sintáctico |
| `src/dcg.py` | DCG con unificación de rasgos (género, número) |
| `src/nodes.py` | Clase `Nodo` para árboles sintácticos |
| `src/ambiguity_detector.py` | Detección de ambigüedad léxica y sintáctica |
| `src/suspicious_patterns.py` | Patrones lingüísticos sospechosos (modales, absolutas, negaciones, tipografía) |
| `src/pcfg_suspicion.py` | PCFG de sospecha con reglas ponderadas (score 0-1) |
| `src/pcfg.py` | PCFG real entrenada desde corpus: cálculo de P(árbol) = Π P(regla) |
| `src/pcfg_trainer.py` | Entrenador: cuenta frecuencias de reglas desde corpus etiquetado |
| `src/classifier.py` | Clasificador: score_final = amb×0.05 + pat×0.20 + rasgos×0.03 + pcfg×0.70 |
| `src/tree_viz.py` | Visualización matplotlib de árboles sintácticos |
| `src/tree_converter.py` | Convierte `Nodo` → dict para PCFG real |
| `src/main_pipeline.py` | CLI alternativa (solo entrada manual) |

## Pesos de clasificación

`classifier.py`:
- PCFG: **70%**
- Patrones sospechosos: **20%**
- Ambigüedad: **5%**
- Rasgos DCG/DAG: **3%**
- Otros: **2%**

Umbrales: CREDIBLE < 0.40 ≤ SUSPICIOUS < 0.70 ≤ FAKE.

## Datos

- `data/corpus_neutral.txt` — 23 oraciones verificadas
- `data/corpus_sospechoso.txt` — 23 oraciones sospechosas

## DCG / DAG

El pipeline valida concordancia gramatical (género, número) mediante DCG + DAG. Si falla, la clasificación se sobrescribe a `INVALID_INPUT`.

## Archivos de documentación

- `docs/ESPECIFICACION_PCFG.md`
- `docs/SOLUCION_10_PROBLEMAS.md`
- `docs/RESUMEN_FINAL.md`
