**Especificación Formal — Detector de Noticias Sospechosas**

Documento breve (1–2 páginas) que resume los formalismos aplicados y las herramientas integradas.

**Herramientas usadas:**
- **`lexer.tokenize()`**: tokenizador por expresiones regulares (módulo: [src/lexer.py](src/lexer.py#L1)).
- **DCG con unificación**: parser de rasgos (género/numero) para validación de concordancia (módulo: [src/dcg.py](src/dcg.py#L1)).
- **CFG + Chart Parser**: gramática libre de contexto + algoritmo de chart parsing (módulos: [src/grammar.py](src/grammar.py#L1), [src/chart_parser.py](src/chart_parser.py#L1)).
- **PCFG (entrenador + uso)**: cálculo de probabilidades de reglas y anotación de árboles (módulos: [src/pcfg_trainer.py](src/pcfg_trainer.py#L1), [src/pcfg.py](src/pcfg.py#L1)).
- **Detector de ambigüedad léxica/sintáctica**: heurísticas y conteo de interpretaciones (módulo: [src/ambiguity_detector.py](src/ambiguity_detector.py#L1)).
- **Patrones sospechosos y clasificador**: módulos que extraen patrones y combinan puntajes para la decisión final (módulos: [src/suspicious_patterns.py](src/suspicious_patterns.py#L1), [src/classifier.py](src/classifier.py#L1)).

**1) Autómata (5-tupla) — Tokenizador (aplicable)**
El tokenizador está implementado mediante una expresión regular; puede modelarse como un AFD simple que reconoce palabras, números y signos de puntuación.

Formalmente, el autómata determinista M = (Q, Σ, δ, q0, F):
- Q = {q0, q_word, q_num, q_punct}
- Σ = Unicode letters ∪ digits ∪ {.,!?,;:¡¿"'()[]}
- q0 = q0
- F = {q_word, q_num, q_punct}
- δ (resumen):
  - δ(q0, letra) = q_word
  - δ(q0, dígito) = q_num
  - δ(q0, signo_puntuación) = q_punct
  - δ(q_word, letra) = q_word
  - δ(q_word, '.') = q_word  (permite abreviaturas como "ee.uu.")
  - δ(q_num, dígito) = q_num
  - cualquier entrada no coincidente reinicia a q0 y genera un token terminado.

Nota: la implementación real usa `re.findall` en [src/lexer.py](src/lexer.py#L1) en vez de construir explícitamente la tabla δ.

**2) Gramática CFG usada (G = (V, T, P, S))**
- V (no terminales): {S, NP, VP, PP, PREP, PUNC, Det, ADJ, N, V, MODAL, ADV_ABS, FUENTE_INDEFINIDA, CONJ, FUNC}
- T (terminales): conjunto de tokens concretos definidos en la gramática (ej.: el, la, gobierno, alerta, peligro, de, en, ., ...). Se usan ejemplos en el fichero [src/grammar.py](src/grammar.py#L1).
- S (símbolo inicial): `S`.

Producciones (lista representativa extraída de `gramatica` en [src/grammar.py](src/grammar.py#L1)):

- S → NP VP
- S → NP VP PUNC

- NP → Det N
- NP → Det ADJ N
- NP → N
- NP → ADJ N
- NP → N ADJ
- NP → NP PREP NP
- NP → Det N PP
- NP → N PP

- VP → V NP
- VP → V
- VP → V NP PP
- VP → VP PP
- VP → V PP
- VP → MODAL VP
- VP → ADV_ABS VP
- VP → VP FUENTE_INDEFINIDA
- VP → V ADJ

- PP → PREP NP

- PREP → {de, en, con, sin, para, por, sobre, a, al}
- PUNC → {., !, ?}

- Det → {el, la, los, las, un, una, unos, unas, al, lo}
- ADJ → {secreto, peligroso, mortal, oculto, ...}
- N → {gobierno, oms, presidente, vacuna, noticia, ...}
- V → {alerta, amenaza, muere, descubre, revela, ...}
- MODAL → {podria, aparentemente, posiblemente, ...}
- ADV_ABS → {siempre, nunca, definitivamente, ...}
- FUENTE_INDEFINIDA → {segun fuentes, se rumorea, fuentes anonimas, ...}
- CONJ → {que, y, pero, aunque, porque}
- FUNC → {se, no, lo, le, me, ...}

Las listas completas de terminales y producciones están en [src/grammar.py](src/grammar.py#L1).

**3) DCG con unificación (rasgos)**
El proyecto incluye un parser DCG (módulo [src/dcg.py](src/dcg.py#L1)) que incorpora rasgos de `gen` y `num` y realiza unificación para validar concordancia. En notación esquemática:

- NP(gen:G, num:N) → Det(gen:G, num:N) N(gen:G, num:N) [
    requiere unificación de rasgos gen/num entre el determinante y el sustantivo
  ]
- VP(num:N) → V(num:N)
- S(num:N) → NP(num:N) VP(num:N)

La unificación se implementa mediante estructuras de rasgos (mappings dict) y la función `unificar` en [src/unification.py] (usa `extraer_rasgos` y `unificar`) para detectar conflictos (p. ej. "una gobierno" → rechazo por conflicto de `gen`).

**4) PCFG y cálculo de probabilidades**
- El entrenador ([src/pcfg_trainer.py](src/pcfg_trainer.py#L1)) extrae reglas heurísticas desde corpus y calcula P(LHS → RHS) por frecuencias normalizadas.
- El componente PCFG ([src/pcfg.py](src/pcfg.py#L1)) usa esas probabilidades para anotar árboles y estimar P(árbol) como producto de probabilidades de reglas aplicadas (con suavizado si hace falta).

**5) Integración de herramientas (flujo y responsabilidades)**n+- Flujo general (origen: `PipelineNoticias` en [src/pipeline.py](src/pipeline.py#L1)):
  1. Tokenización: `lexer.tokenize()` → tokens por oración.
  2. Validación DCG/DAG: `dcg.Parser` + `dag.crear_dag_oracion()` valida concordancia y extrae DAGs (rechaza oraciones con conflicto de rasgos).
  3. Análisis CFG: `chart_parser.chart_parser(tokens, gramatica)` genera árboles sintácticos usando la gramática en `grammar.py`.
  4. Detección de ambigüedad: `ambiguity_detector` cuenta múltiples árboles (ambigüedad sintáctica) y aplica frecuencias léxicas para desambiguar.
  5. PCFG: `pcfg_trainer` entrena PCFGs (corpus neutral y sospechoso); `pcfg` anota árboles y produce puntuaciones de sospecha.
  6. Detección de patrones: `suspicious_patterns` busca expresiones y construcciones típicas de desinformación.
  7. Clasificador final: `classifier` combina scores de ambigüedad, PCFG, patrones y rasgos para decidir y justificar la etiqueta.

Cada módulo está implementado como una unidad independiente (módulos en `src/`) y `PipelineNoticias` coordina el paso de datos y agregación de scores.

**Referencias a archivos clave:**
- Gramática CFG: [src/grammar.py](src/grammar.py#L1)
- Chart Parser: [src/chart_parser.py](src/chart_parser.py#L1)
- DCG / Unificación: [src/dcg.py](src/dcg.py#L1) y [src/unification.py](src/unification.py#L1)
- PCFG / Entrenador: [src/pcfg.py](src/pcfg.py#L1), [src/pcfg_trainer.py](src/pcfg_trainer.py#L1)
- Pipeline (orquestador): [src/pipeline.py](src/pipeline.py#L1)

---
Documento conciso preparado para la entrega de la demo; si quieres, lo adapto a PDF o lo reduzco a una página exactamente.
