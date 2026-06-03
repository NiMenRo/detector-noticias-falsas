# Implementación de Augmented Transition Networks (ATN)

## Descripción General

Este proyecto implementa **Augmented Transition Networks (ATN)** basándose en la referencia del curso de Procesamiento de Lenguaje Natural de la Universidad del Valle.

ATN es un formalism de análisis sintáctico que combina:
- **Transiciones de estado** para reconocimiento sintáctico
- **Registros aumentados** para manipulación de datos
- **Recursión** a través de subredes (PUSH/POP)
- **Máquinas de estado** para gestión de diálogos

## Archivos Generados

### 1. `src/atn.py` - Parser ATN Sintáctico

Implementa análisis sintáctico de oraciones con estructura Sujeto-Verbo-Objeto.

**Componentes:**

```python
# Gestión de léxico
lexico = LexicoATN()
lexico.agregar("palabra", "Categoria")
categoria = lexico.categoria("palabra")

# Subredes especializadas
subred_np = SubredNP("NP", lexico)
resultado, pos = subred_np.analizar(tokens, 0)

subred_vp = SubredVP("VP", lexico, subred_np)
resultado, pos = subred_vp.analizar(tokens, 0)

# Red principal
red = RedATN(lexico)
oracion_analizada = red.analizar_oracion(tokens)
```

**Ejemplo:**

```python
from atn import RedATN, crear_lexico_sintactico

red = RedATN()  # Usa léxico por defecto
resultado = red.analizar_oracion(["la", "estudiante", "lee", "el", "libro"])

# Resultado:
# {
#   "cat": "S",
#   "SUBJ": ["la", "estudiante"],
#   "VP": ["lee", ["el", "libro"]]
# }
```

### 2. `src/atn_dialogo.py` - Motor de Diálogo ATN

Implementa procesamiento de diálogos mediante máquinas de estado y clasificación de intenciones.

**Componentes:**

```python
# Clasificador de intenciones
clasificador = ClasificadorIntencion()
clasificador.agregar_patron("saludo", ["hola", "buenos"])

# Máquina de estados
maquina = MaquinaDialogoATN("inicio")
estado = maquina.crear_estado("esperando")
estado.agregar_transicion("saludo", "confirmando", accion_saludo)

# Motor integrado
motor = MotorDialogo(maquina, clasificador)
resultado = motor.procesar_turno("hola mundo")
```

**Ejemplo:**

```python
from atn_dialogo import MotorDialogo, crear_maquina_horarios, crear_clasificador_horarios

motor = MotorDialogo(
    crear_maquina_horarios(),
    crear_clasificador_horarios()
)

motor.procesar_turno("hola")
motor.procesar_turno("¿cuál es el horario de pln?")
motor.procesar_turno("gracias")
motor.procesar_turno("adiós")
```

## Estructura de Transiciones

### Análisis Sintáctico

```
red_s:
  ├── PUSH NP (sujeto)
  │   ├── CAT Det
  │   ├── CAT N
  │   └── POP [det, n]
  │
  ├── PUSH VP (predicado)
  │   ├── CAT V
  │   ├── PUSH NP (objeto)
  │   └── POP [v, np]
  │
  ├── Validar pos == len(tokens)
  └── POP {"SUBJ": np, "VP": vp}
```

### Diálogos

```
inicio --[saludo]--> esperando
esperando --[pedir_horario]--> consultando
consultando --[repetir]--> consultando (bucle)
consultando --[confirmar]--> fin
fin --[despedida]--> inicio
```

## Uso Rápido

### Análisis de una oración

```python
from atn import RedATN

red = RedATN()
resultado = red.analizar_oracion(["la", "estudiante", "lee", "el", "libro"])

if resultado:
    print(f"Sujeto: {resultado['SUBJ']}")
    print(f"Predicado: {resultado['VP']}")
else:
    print("Análisis fallido")
```

### Procesamiento de diálogo

```python
from atn_dialogo import MotorDialogo, crear_maquina_horarios, crear_clasificador_horarios

motor = MotorDialogo(
    crear_maquina_horarios(),
    crear_clasificador_horarios()
)

# Procesar turnos
motor.procesar_turno("hola")
motor.procesar_turno("horario de pln")
motor.procesar_turno("gracias")
```

### Crear léxico personalizado

```python
from atn import LexicoATN, RedATN

lexico = LexicoATN()
lexico.agregar("película", "N")
lexico.agregar("ve", "V")
lexico.agregar("la", "Det")

red = RedATN(lexico)
resultado = red.analizar_oracion(["la", "película", "ve", "el", "trailer"])
```

### Crear máquina de diálogo personalizada

```python
from atn_dialogo import MaquinaDialogoATN, ClasificadorIntencion

# Crear máquina
maquina = MaquinaDialogoATN("inicio")
estado_inicio = maquina.crear_estado("inicio")
estado_fin = maquina.crear_estado("fin")

# Definir acción
def accion_saludar(contexto):
    print("¡Hola!")
    return contexto

# Agregar transición
estado_inicio.agregar_transicion("saludo", "fin", accion_saludar)

# Procesar
maquina.procesar_intencion("saludo", {})
```

## Casos de Uso

### 1. Análisis sintáctico

```python
red = RedATN()
resultado = red.analizar_oracion(tokens)
# Detecta oraciones gramaticales
# Extrae componentes sintácticos
# Identifica errores de concordancia
```

### 2. Procesamiento de diálogos

```python
motor = MotorDialogo(maquina, clasificador)
motor.procesar_turno(texto_usuario)
# Clasifica intención del usuario
# Navega máquina de estados
# Ejecuta acciones asociadas
# Mantiene contexto entre turnos
```

### 3. Extracción de datos

```python
clasificador.agregar_patron("consulta", 
                           ["horario", "cuándo"],
                           lambda t: {"materia": extraer_materia(t)})
# Extrae información de texto libre
# Usa patrones personalizables
```

## Resultados de Verificación

✅ **Parser ATN Sintáctico**: 11/11 pruebas (100%)
✅ **Clasificador de Intenciones**: 7/7 pruebas (100%)
✅ **Máquina de Diálogo**: 9/9 turnos (100%)

## Archivos de Ejemplo

- `ejemplos_atn.py` - 4 ejemplos completos de uso

Para ejecutar:
```bash
python ejemplos_atn.py
```

## Documentos Relacionados

- `VERIFICACION_ATN.md` - Reporte detallado de implementación
- `VERIFICACION_DAG_DCG.md` - Verificación de DAG y DCG
- `contexto/ATN (1).py` - Implementación de referencia

## Integración con Proyecto Fake News

ATN se puede usar en el proyecto para:

1. **Clasificar consultas de usuario**
   - "¿Es esta noticia falsa?" → intención: verificar
   - "Muéstrame noticias de política" → intención: filtrar

2. **Mantener contexto de conversación**
   - Usuario pregunta sobre noticia X
   - Usuario luego dice "¿Más información?"
   - Sistema recuerda contexto

3. **Guiar el flujo de diálogo**
   - Inicio → Recibir noticia → Analizar → Resultado → Fin
   - Estados de validación, procesamiento, respuesta

4. **Extraer información específica**
   - Materia, palabras clave, dominio
   - Metadata de la noticia

## Notas Técnicas

- **Lexicografía**: Mediante `LexicoATN`, fácil de extender
- **Subredes recursivas**: PUSH/POP automáticos en subredes
- **Contexto persistente**: Dict que se propaga entre estados
- **Máquina sin ciclos infinitos**: Estados actúan como guardias
- **Encoding**: Compatible con Python 3.x, UTF-8

## Referencias

- Curso PLN - Universidad del Valle
- Implementación de referencia: `contexto/ATN (1).py`
- Libros: "Speech and Language Processing" (Jurafsky & Martin)
