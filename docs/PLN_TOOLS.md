# Herramientas de Procesamiento de Lenguaje Natural (PLN)

## Descripción General

Este módulo implementa **tres herramientas fundamentales** para PLN sin usar librerías externas:

1. **Unificación** - Motor de matching con MGU (Most General Unifier)
2. **DCGs** - Definite Clause Grammars con diferencia de listas
3. **DAGs** - Directed Acyclic Graphs para compresión de árboles

---

## 1. Sistema de Unificación (`unification.py`)

### Concepto
La unificación es el mecanismo fundamental en la programación lógica. Permite:
- Buscar sustituciones que hagan dos términos idénticos
- Hacer matching de patrones
- Resolver variables en cláusulas

### Componentes

#### `Variable`
Representa una variable lógica (Ej: X, Y, Z).
```python
from unification import Variable, Atom, Compound, unify

x = Variable("X")
y = Variable("Y")
```

#### `Atom`
Representa un símbolo atómico (Ej: 'juan', 'maria').
```python
juan = Atom("juan")
maria = Atom("maria")
```

#### `Compound`
Representa un término compuesto (Ej: padre(juan, maria)).
```python
padre_juan_maria = Compound("padre", [juan, maria])
```

#### `Substitution`
Representa bindings de variables a términos.
```python
subst = Substitution()
subst = subst.bind(Variable("X"), Atom("valor"))

# Aplicar sustitución
resultado = subst.apply(Variable("X"))  # → Atom("valor")
```

### Función Principal: `unify()`

```python
def unify(term1, term2, subst=None):
    """
    Unifica dos términos.
    Retorna una Substitution (MGU) si es posible.
    Retorna None si falla.
    """
```

#### Ejemplo 1: Unificación Simple
```python
x = Variable("X")
y = Variable("Y")

# Patrón
pattern = Compound("padre", [x, y])

# Instancia
instance = Compound("padre", [Atom("juan"), Atom("maria")])

# Unificación
subst = unify(pattern, instance)
# Resultado: {X: juan, Y: maria}

print(subst.apply(x))  # → juan
print(subst.apply(y))  # → maria
```

#### Ejemplo 2: Términos Compuestos
```python
# Unificar f(a, X) con f(Y, g(b))
t1 = Compound("f", [Atom("a"), Variable("X")])
t2 = Compound("f", [Variable("Y"), Compound("g", [Atom("b")])])

subst = unify(t1, t2)
# Resultado: {Y: a, X: g(b)}
```

#### Ejemplo 3: Occur Check (Previene Ciclos)
```python
# Evita unificaciones circulares como X = f(X)
x = Variable("X")
circular = Compound("f", [x])

result = unify(x, circular)
# Resultado: None (falla por occur check)
```

### Funciones Auxiliares

#### `get_variables(term)`
Extrae todas las variables de un término.
```python
term = Compound("vive", [Variable("X"), Atom("roma")])
vars_found = get_variables(term)
# Resultado: {Variable("X")}
```

#### `rename_variables(term, suffix)`
Renombra variables para evitar conflictos.
```python
original = Compound("ama", [Variable("X"), Variable("Y")])
renamed = rename_variables(original, "1")
# Resultado: ama(X_1, Y_1)
```

---

## 2. Definite Clause Grammars - DCG (`dcg.py`)

### Concepto
DCG es una notación para escribir parsers mediante reglas gramaticales con **diferencia de listas** para threading eficiente de estado.

### Ejemplo DCG
```
s --> np, vp
np --> det, n
vp --> v, np
det --> [el] | [la]
n --> [gato] | [ratón]
v --> [come]
```

Se expande a cláusulas Prolog con threading:
```prolog
s(S0, S) :- np(S0, S1), vp(S1, S).
np(S0, S) :- det(S0, S1), n(S1, S).
```

### Componentes

#### `DCGRule`
Representa una regla DCG individual.
```python
from dcg import DCGGrammar

dcg = DCGGrammar()
dcg.add_rule("s", [], ["np", "vp"])
dcg.add_rule("np", [], ["det", "n"])
```

#### `DCGGrammar`
Gestor de colección de reglas DCG.
```python
grammar = DCGGrammar()

# Añadir reglas
grammar.add_rule("s", [], ["np", "vp"])
grammar.add_rule("np", [], ["det", "n"])
grammar.add_rule("np", [], ["det", "adj", "n"])

# Obtener reglas para un símbolo
s_rules = grammar.get_rules("s")
```

#### `DCGParser`
Parser con backtracking que implementa SLD resolution.
```python
from dcg import DCGParser

parser = DCGParser(grammar)
tokens = ["el", "gato", "come"]
solutions = parser.parse(tokens, "s")

for solution in solutions:
    print(solution)
```

### Expansión de Reglas DCG

```python
from dcg import expand_dcg_rule

rule = grammar.get_rules("s")[0]
clause_head, body_goals = expand_dcg_rule(rule)

print(f"Cabeza: {clause_head}")  # s(S0, S)
print(f"Cuerpo: {body_goals}")   # [np goal, vp goal]
```

### Conversión desde CFG

```python
from dcg import convert_cfg_to_dcg

cfg = {
    "S": [["NP", "VP"]],
    "NP": [["Det", "N"]],
}

dcg = convert_cfg_to_dcg(cfg)
```

---

## 3. Directed Acyclic Graphs - DAG (`dag.py`)

### Concepto
DAG comprime representación de árboles identificando y compartiendo subárboles duplicados.

**Ventajas:**
- Reduce memoria (comparte subárboles)
- Más eficiente para análisis
- Evita redundancia

### Componentes

#### `DAGNode`
Nodo del DAG con ID único y hash estructural.
```python
from dag import DAGNode, DAG

node = DAGNode("NP", [
    DAGNode("Det", ["el"]),
    DAGNode("N", ["gato"])
])
```

#### `DAG`
Gestor de grafo acíclico dirigido con deduplicación automática.
```python
dag = DAG()

# Construir desde árbol Nodo
from nodes import Nodo

tree = Nodo("S", [
    Nodo("NP", [Nodo("Det", ["el"]), Nodo("N", ["gato"])]),
    Nodo("VP", [Nodo("V", ["come"])])
])

root = dag.build_from_tree(tree)

print(f"Nodos en DAG: {len(dag.nodes)}")
print(dag.get_statistics())
```

#### `DAGCompressor`
Comprime un DAG eliminando redundancias.
```python
from dag import DAGCompressor

compressor = DAGCompressor()
compressed = compressor.compress(dag)
```

### Ejemplos

#### Ejemplo 1: Árbol a DAG
```python
from dag import DAG, dag_to_string
from nodes import Nodo

# Crear árbol con subtree duplicado
det_n = Nodo("NP", [
    Nodo("Det", ["el"]),
    Nodo("N", ["gato"])
])

tree = Nodo("S", [det_n, det_n])  # Subtree duplicado

# Convertir a DAG
dag = DAG()
root = dag.build_from_tree(tree)

# El DAG debe tener menos nodos que el árbol original
print(f"Árbol: 7 nodos")
print(f"DAG: {len(dag.nodes)} nodos (comprimido)")
```

#### Ejemplo 2: Visualizar DAG
```python
print(dag_to_string(dag.root))
```

#### Ejemplo 3: Estadísticas de Compresión
```python
from dag import tree_to_dag_stats

stats = tree_to_dag_stats(tree, dag)
print(f"Compresión: {stats['compression_ratio']}")
```

#### Ejemplo 4: Fusionar DAGs
```python
from dag import merge_dags

dag1 = DAG()
dag1.build_from_tree(tree1)

dag2 = DAG()
dag2.build_from_tree(tree2)

merged = merge_dags([dag1, dag2])
```

---

## Integración con Chart Parser Actual

### Conversión Árbol → DAG

```python
from chart_parser import chart_parser
from grammar import gramatica
from lexer import tokenize
from dag import DAG, dag_to_string

# Parseo original
tokens = tokenize("¡el virus amenaza!")
arboles, chart = chart_parser(tokens, gramatica)

# Convertir árboles a DAGs
for tree in arboles:
    dag = DAG()
    root = dag.build_from_tree(tree)
    
    print(dag_to_string(root))
    print(f"Compresión: {dag.get_statistics()}")
```

### Aplicación: Análisis Sintáctico con Unificación

```python
from unification import Compound, Variable, Atom, unify

# Patrón de oración
pattern = Compound("s", [Variable("NP"), Variable("VP")])

# Instancia parseada
instance = Compound("s", [
    Compound("np", [Atom("el"), Atom("gato")]),
    Compound("vp", [Atom("come")])
])

# Unificar para extraer componentes
subst = unify(pattern, instance)

np_component = subst.apply(Variable("NP"))
vp_component = subst.apply(Variable("VP"))
```

---

## Flujo Completo de PLN

```
Texto → Tokenización → Parsing (Chart) → Árbol
                                          ↓
                                    Unificación
                                          ↓
                                      DAG
                                          ↓
                                    Análisis
```

### Ejemplo Completo

```python
from lexer import tokenize
from grammar import gramatica
from chart_parser import chart_parser
from dag import DAG, dag_to_string, tree_to_dag_stats
from unification import Compound, Variable, unify

# 1. Tokenización
texto = "¡el virus amenaza!"
tokens = tokenize(texto)

# 2. Parsing
arboles, chart = chart_parser(tokens, gramatica)

# 3. Para cada árbol
for arbol in arboles:
    # 4. Convertir a DAG
    dag = DAG()
    root = dag.build_from_tree(arbol)
    
    # 5. Visualizar
    print(dag_to_string(root))
    
    # 6. Estadísticas
    stats = tree_to_dag_stats(arbol, dag)
    print(f"Compresión: {stats['compression_ratio']}")
```

---

## Ejecución de Pruebas

### Tests Unitarios
```bash
cd src
python test_tools.py
```

Valida:
- ✓ Unificación (8 tests)
- ✓ DCGs (3 tests)
- ✓ DAGs (6 tests)

### Demostraciones
```bash
cd src
python demo_tools.py
```

Incluye:
- DEMO 1: Sistema de Unificación
- DEMO 2: DCGs
- DEMO 3: DAGs
- DEMO 4: Integración con Chart Parser
- DEMO 5: Unificación en Análisis Sintáctico

---

## Archivos del Módulo

| Archivo | Descripción |
|---------|-------------|
| `unification.py` | Motor de unificación con MGU |
| `dcg.py` | Definite Clause Grammars |
| `dag.py` | Directed Acyclic Graphs |
| `test_tools.py` | Tests unitarios (17 tests) |
| `demo_tools.py` | Demostraciones interactivas |
| `PLN_TOOLS.md` | Esta documentación |

---

## Referencias Teóricas

### Unificación
- **Algoritmo**: Robinson (1965)
- **MGU**: Most General Unifier
- **Occur Check**: Previene unificaciones circulares

### DCGs
- **Base**: Warren (1980)
- **Diferencia de Listas**: Patrón común en Prolog
- **SLD Resolution**: Estrategia de prueba

### DAGs
- **Ventaja**: Compresión de estructura
- **Hash Estructural**: Identificación de duplicados
- **Aplicación**: Parsing eficiente

---

## Notas de Implementación

1. **Sin librerías externas**: Todo código está escrito en Python puro
2. **Backtracking**: DCGParser implementa backtracking completo
3. **Deduplicación automática**: DAG comprime automáticamente duplicados
4. **Compatibility**: Integración total con Chart Parser existente

---

## Próximas Mejoras (Opcionales)

- [ ] Optimización de DCGParser con tabulation (memoización)
- [ ] Compresión adicional de DAG con graph coloring
- [ ] Visualización gráfica de DAGs
- [ ] Constrain solving para unificación
- [ ] Análisis semántico con atributos

