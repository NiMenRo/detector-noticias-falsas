# Detector de Noticias Falsas — Refactorización PCFG Completa

Implementación completa de un sistema de detección de noticias falsas basado en **Gramáticas Probabilísticas Libres de Contexto (PCFG)** como núcleo central, alineado con los requisitos académicos.

## ✓ Estado: Todos los 10 Problemas Resueltos

### Problemas Solucionados

1. ✓ **CFG auténtica** — Reemplazada por sintaxis real del español
2. ✓ **Cálculo de P(árbol)** — Implementado: P = Π P(regla)
3. ✓ **Parser + PCFG integrados** — Árboles anotados con probabilidades
4. ✓ **Ambigüedad natural** — Desde múltiples árboles sintácticos
5. ✓ **Patrones en gramática** — MODAL, ADV_ABS, FUENTE_INDEFINIDA
6. ✓ **Corpus entrenamiento** — 40 oraciones (neutral + sospechoso)
7. ✓ **Entrenador PCFG** — Calcula probabilidades automáticamente
8. ✓ **Clasificación desde PCFG** — P(árbol) es el 50% del score
9. ✓ **Justificaciones lingüísticas** — Explica árbol, reglas y patrones
10. ✓ **Pipeline completo** — 7 pasos integrados correctamente

## Arquitectura

```
Texto
  ↓
Tokenización y normalización
  ↓
CFG + Chart Parser → múltiples árboles
  ↓
Detección de ambigüedad → entropía
  ↓
PCFG entrenada desde corpus → P(árbol)
  ↓
Clasificación basada en P(árbol)
  ↓
Justificación lingüística detallada
```

## Módulos Principales

### Core PCFG
- **`src/grammar.py`** — CFG auténtica con sintaxis real
- **`src/pcfg.py`** — Cálculo de P(árbol) = Π P(regla)
- **`src/pcfg_trainer.py`** — Entrena PCFG desde corpus

### Análisis
- **`src/ambiguity_detector.py`** — Detecta ambigüedad natural (entropía)
- **`src/classifier.py`** — Clasificación con PCFG como núcleo (50%)
- **`src/justifier.py`** — Justificaciones lingüísticas

### Orquestación
- **`src/pipeline_pcfg.py`** — Pipeline integrado 7 pasos

### Datos
- **`data/corpus_neutral.txt`** — 20 oraciones verificadas
- **`data/corpus_sospechoso.txt`** — 20 oraciones sospechosas

## Cómo Usar

### 1. Instancia Mínima
```python
from src.pipeline_pcfg import crear_pipeline
from src.pcfg import obtener_pcfg

pipeline = crear_pipeline(pcfg=obtener_pcfg())
resultado = pipeline.procesar("El gobierno anunció nuevas políticas")
```

### 2. Con Todos los Módulos
```python
from src.pipeline_pcfg import crear_pipeline
from src.pcfg import obtener_pcfg
from src.ambiguity_detector import AmbiguityDetectorSyntactic
from src.justifier import crear_justifier
from src.classifier import ClasificadorFakeNews

pipeline = crear_pipeline(
    pcfg=obtener_pcfg(),
    ambiguity_detector=AmbiguityDetectorSyntactic(),
    justifier=crear_justifier(),
    classifier=ClasificadorFakeNews()
)

resultado = pipeline.procesar(texto)
print(f"Categoría: {resultado['clasificacion']['categoria']}")
print(f"P(árbol): {resultado['p_arbol']:.4f}")
```

### 3. Entrenar PCFG Personalizado
```python
from src.pcfg_trainer import PCFGTrainer

trainer = PCFGTrainer()
pcfg = trainer.entrenar_desde_corpus('data/corpus_neutral.txt')
trainer.mostrar_pcfg()
```

## Estructura de Salida

```json
{
  "texto": "...",
  "tokens": ["el", "gobierno", "..."],
  "num_arboles": 2,
  "ambiguedad": {
    "num_arboles": 2,
    "entropía": 0.521,
    "nivel_ambiguedad": "MEDIA"
  },
  "p_arbol": 0.374,
  "clasificacion": {
    "categoria": "SUSPICIOUS",
    "score_final": 0.52
  },
  "justificacion": {
    "resumen": "⚠️ Nivel de sospecha: MEDIO",
    "reglas_activadas": [...],
    "patrones_sospechosos": [...]
  }
}
```

## Fórmulas Clave

### Probabilidad de Árbol
```
P(árbol) = P(S→NP VP) × P(NP→Det N) × P(VP→V NP) × ...
```

### Entropía de Ambigüedad
```
H = -Σ P(árbolᵢ) × log₂(P(árbolᵢ))
```

### Clasificación Final
```
Score = 0.50 × P_PCFG + 0.15 × ambiguedad + 0.20 × patrones + 0.10 × rasgos + 0.05 × otros
```

## Documentación Completa

- **`docs/ESPECIFICACION_PCFG.md`** — Especificación detallada
- **`docs/SOLUCION_10_PROBLEMAS.md`** — Solución de cada problema

## Validación de Requisitos Académicos

✓ CFG modela la sintaxis  
✓ Chart Parser genera árboles  
✓ Ambigüedad surge naturalmente  
✓ PCFG calcula probabilidades reales  
✓ Corpus determina los pesos  
✓ Clasificación basada en teoría de PCFG  
✓ Justificaciones lingüísticas rigurosas  
✓ Documentación técnica completa  

## Próximos Pasos

- [ ] Expandir corpus a 500+ oraciones
- [ ] Validar F1-score contra ground truth
- [ ] Ajustar umbrales de clasificación
- [ ] Integración con dataset externo
- [ ] Optimización de performance

## Autor

Refactorización completada: Junio 2026  
Requisitos académicos cumplidos ✓
