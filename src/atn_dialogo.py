"""
ATN de Diálogo - Motor de procesamiento de conversaciones
Basado en la lógica de la Universidad del Valle
Implementa máquinas de estados aumentadas para diálogos interactivos
"""


# ============================================================
# PARTE 1: CLASIFICADOR DE INTENCIONES
# ============================================================

class ClasificadorIntencion:
    """
    Transforma texto libre en intenciones y extrae datos relevantes.
    Base para el procesamiento de diálogos.
    """
    
    def __init__(self):
        """Inicializa el clasificador con patrones base"""
        self.patrones = {}
    
    def agregar_patron(self, intencion, palabras_clave, datos_extractor=None):
        """
        Agrega un patrón de reconocimiento.
        
        Args:
            intencion (str): Identificador de la intención
            palabras_clave (list): Palabras que disparan esta intención
            datos_extractor (callable): Función que extrae datos del texto
        """
        self.patrones[intencion] = {
            "palabras": palabras_clave,
            "extractor": datos_extractor
        }
    
    def clasificar(self, texto):
        """
        Clasifica el texto en una intención y extrae datos.
        
        Args:
            texto (str): Texto a clasificar
        
        Retorna:
            tuple: (intención, datos_dict) o (None, {}) si no se reconoce
        """
        texto_lower = texto.lower()
        
        for intencion, config in self.patrones.items():
            palabras = config["palabras"]
            
            # Verificar si alguna palabra clave está en el texto
            if any(palabra in texto_lower for palabra in palabras):
                # Extraer datos si hay un extractor definido
                datos = {}
                if config["extractor"]:
                    datos = config["extractor"](texto_lower)
                
                return intencion, datos
        
        return None, {}
    
    def clasificar_con_confianza(self, texto):
        """
        Clasifica con información de confianza.
        
        Args:
            texto (str): Texto a clasificar
        
        Retorna:
            dict: {"intención": ..., "confianza": ..., "datos": ...}
        """
        intencion, datos = self.clasificar(texto)
        
        if intencion:
            return {
                "intencion": intencion,
                "confianza": 1.0,  # En producción, sería un modelo ML
                "datos": datos
            }
        else:
            return {
                "intencion": None,
                "confianza": 0.0,
                "datos": {}
            }


def crear_clasificador_horarios():
    """
    Crea un clasificador especializado para consultas de horarios.
    
    Retorna:
        ClasificadorIntencion: Clasificador configurado
    """
    clasificador = ClasificadorIntencion()
    
    # Intención: saludo
    clasificador.agregar_patron(
        "saludo",
        ["hola", "buenos", "buenas", "hey", "hi"],
        None
    )
    
    # Intención: pedir horario (con extractor que busca materias)
    def extractor_materia(texto):
        materias = ["pln", "calculo", "algoritmos"]
        for materia in materias:
            if materia in texto:
                return {"materia": materia}
        return {}
    
    clasificador.agregar_patron(
        "pedir_horario",
        ["horario", "cuándo", "cuando", "clases"],
        extractor_materia
    )
    
    # Intención: repetir
    clasificador.agregar_patron(
        "repetir",
        ["repite", "repetir", "de nuevo", "otra vez"],
        None
    )
    
    # Intención: confirmar
    clasificador.agregar_patron(
        "confirmar",
        ["sí", "si", "ok", "perfecto", "gracias", "listo"],
        None
    )
    
    # Intención: despedida
    clasificador.agregar_patron(
        "despedida",
        ["adiós", "adios", "chao", "hasta", "bye"],
        None
    )
    
    return clasificador


# ============================================================
# PARTE 2: MÁQUINA DE ESTADOS ATN DE DIÁLOGO
# ============================================================

class EstadoDialogo:
    """
    Representa un estado en la máquina de diálogo.
    Define transiciones disponibles y acciones asociadas.
    """
    
    def __init__(self, nombre):
        """
        Inicializa un estado.
        
        Args:
            nombre (str): Identificador del estado
        """
        self.nombre = nombre
        self.transiciones = {}  # {intención: estado_siguiente}
        self.acciones = {}      # {intención: función_acción}
    
    def agregar_transicion(self, intencion, estado_siguiente, accion=None):
        """
        Agrega una transición desde este estado.
        
        Args:
            intencion (str): Intención que dispara la transición
            estado_siguiente (str): Nombre del estado destino
            accion (callable): Función a ejecutar en la transición
        """
        self.transiciones[intencion] = estado_siguiente
        if accion:
            self.acciones[intencion] = accion
    
    def obtener_siguiente(self, intencion):
        """
        Obtiene el estado siguiente para una intención.
        
        Args:
            intencion (str): Intención de entrada
        
        Retorna:
            str: Nombre del estado siguiente, o None si no hay transición
        """
        return self.transiciones.get(intencion, None)
    
    def ejecutar_accion(self, intencion, contexto):
        """
        Ejecuta la acción asociada a una intención.
        
        Args:
            intencion (str): Intención que disparó la acción
            contexto (dict): Contexto del diálogo para acceder a datos
        
        Retorna:
            dict: Resultado de la acción o contexto sin cambios
        """
        if intencion in self.acciones:
            return self.acciones[intencion](contexto)
        return contexto
    
    def __repr__(self):
        return f"Estado({self.nombre}, transiciones={len(self.transiciones)})"


class MaquinaDialogoATN:
    """
    Máquina de estados aumentada para gestionar diálogos.
    Implementa la tabla de transiciones y el motor de procesamiento.
    """
    
    def __init__(self, estado_inicial="inicio"):
        """
        Inicializa la máquina de diálogo.
        
        Args:
            estado_inicial (str): Nombre del estado inicial
        """
        self.estado_inicial = estado_inicial
        self.estado_actual = estado_inicial
        self.estados = {}
        self.contexto = {}
        self.historial = []
    
    def crear_estado(self, nombre):
        """
        Crea un nuevo estado en la máquina.
        
        Args:
            nombre (str): Identificador del estado
        
        Retorna:
            EstadoDialogo: El estado creado
        """
        estado = EstadoDialogo(nombre)
        self.estados[nombre] = estado
        return estado
    
    def obtener_estado(self, nombre):
        """
        Obtiene un estado existente.
        
        Args:
            nombre (str): Identificador del estado
        
        Retorna:
            EstadoDialogo: El estado, o None si no existe
        """
        return self.estados.get(nombre, None)
    
    def procesar_intencion(self, intencion, datos=None):
        """
        Procesa una intención en el contexto del estado actual.
        
        Args:
            intencion (str): Intención a procesar
            datos (dict): Datos asociados a la intención
        
        Retorna:
            dict: {"transicion": bool, "estado_anterior": ..., 
                   "estado_nuevo": ..., "contexto": ...}
        """
        estado = self.estados.get(self.estado_actual)
        if estado is None:
            return {"transicion": False, "error": f"Estado {self.estado_actual} no existe"}
        
        # Obtener estado siguiente
        estado_siguiente = estado.obtener_siguiente(intencion)
        
        if estado_siguiente is None:
            # Sin transición válida: el estado actúa como guarda
            return {
                "transicion": False,
                "estado_anterior": self.estado_actual,
                "estado_nuevo": self.estado_actual,
                "razon": f"No hay arco para '{intencion}' desde {self.estado_actual}",
                "contexto": self.contexto
            }
        
        # Guardar estado anterior
        estado_anterior = self.estado_actual
        
        # Actualizar contexto con datos de la intención
        if datos:
            self.contexto.update(datos)
        
        # Ejecutar acción asociada
        self.contexto = estado.ejecutar_accion(intencion, self.contexto)
        
        # Avanzar al nuevo estado
        self.estado_actual = estado_siguiente
        
        # Registrar en historial
        entrada_historial = {
            "intencion": intencion,
            "estado_anterior": estado_anterior,
            "estado_nuevo": estado_siguiente,
            "datos": datos
        }
        self.historial.append(entrada_historial)
        
        return {
            "transicion": True,
            "estado_anterior": estado_anterior,
            "estado_nuevo": estado_siguiente,
            "contexto": self.contexto
        }
    
    def resetear(self):
        """
        Resetea la máquina al estado inicial con contexto limpio.
        Simula el fin de una conversación y preparación para la siguiente.
        """
        self.estado_actual = self.estado_inicial
        self.contexto = {}
        self.historial = []
    
    def obtener_estado_actual(self):
        """Retorna el estado actual"""
        return self.estado_actual
    
    def obtener_contexto(self):
        """Retorna el contexto actual"""
        return self.contexto.copy()
    
    def obtener_historial(self):
        """Retorna el historial de transiciones"""
        return self.historial.copy()


# ============================================================
# PARTE 3: MOTOR DE DIÁLOGO INTEGRADO
# ============================================================

class MotorDialogo:
    """
    Integra el clasificador de intenciones con la máquina ATN.
    Proporciona la interfaz completa para procesar diálogos.
    """
    
    def __init__(self, maquina, clasificador):
        """
        Inicializa el motor de diálogo.
        
        Args:
            maquina (MaquinaDialogoATN): Máquina de estados
            clasificador (ClasificadorIntencion): Clasificador de intenciones
        """
        self.maquina = maquina
        self.clasificador = clasificador
        self.turnos = []
    
    def procesar_turno(self, texto_usuario):
        """
        Procesa un turno de diálogo: texto → intención → transición → respuesta.
        
        Args:
            texto_usuario (str): Texto ingresado por el usuario
        
        Retorna:
            dict: Información del turno procesado
        """
        # Paso 1: Clasificar intención
        intencion, datos = self.clasificador.clasificar(texto_usuario)
        
        if intencion is None:
            return {
                "texto_usuario": texto_usuario,
                "intencion": None,
                "procesado": False,
                "razon": "No se reconoció intención"
            }
        
        # Paso 2: Procesar en máquina
        resultado_transicion = self.maquina.procesar_intencion(intencion, datos)
        
        # Registrar turno
        turno_info = {
            "texto_usuario": texto_usuario,
            "intencion": intencion,
            "datos": datos,
            "estado_anterior": resultado_transicion.get("estado_anterior"),
            "estado_nuevo": resultado_transicion.get("estado_nuevo"),
            "transicion_realizada": resultado_transicion.get("transicion", False),
            "contexto": self.maquina.contexto.copy()
        }
        self.turnos.append(turno_info)
        
        return turno_info
    
    def obtener_turnos(self):
        """Retorna todos los turnos procesados"""
        return self.turnos.copy()
    
    def resetear(self):
        """Resetea el motor para una nueva conversación"""
        self.maquina.resetear()
        self.turnos = []


# ============================================================
# PARTE 4: CONSTRUCTORES Y FUNCIONES AUXILIARES
# ============================================================

def crear_maquina_horarios():
    """
    Crea una máquina de diálogo para consultas de horarios.
    
    Retorna:
        MaquinaDialogoATN: Máquina configurada
    """
    maquina = MaquinaDialogoATN("inicio")
    
    # Base de datos simulada de horarios
    bd_horarios = {
        "pln": "Martes y Jueves 8:00-10:00am — Sala 201",
        "calculo": "Lunes y Miércoles 10:00-12:00m — Sala 305",
        "algoritmos": "Viernes 2:00-5:00pm — Lab 102",
    }
    
    # Crear estados
    estado_inicio = maquina.crear_estado("inicio")
    estado_esperando = maquina.crear_estado("esperando")
    estado_consultando = maquina.crear_estado("consultando")
    estado_fin = maquina.crear_estado("fin")
    
    # Definir acciones
    def accion_saludo(contexto):
        print("  → Sistema: ¡Hola! ¿En qué puedo ayudarte?")
        return contexto
    
    def accion_pedir_horario(contexto):
        materia = contexto.get("materia", "desconocida")
        respuesta = bd_horarios.get(materia, None)
        
        if respuesta:
            contexto["respuesta"] = respuesta
            print(f"  → Sistema: El horario de {materia} es: {respuesta}")
        else:
            print(f"  → Sistema: No encontré '{materia}'. ¿Cuál materia buscás?")
        
        return contexto
    
    def accion_repetir(contexto):
        respuesta = contexto.get("respuesta", None)
        if respuesta:
            print(f"  → Sistema (repite): {respuesta}")
        else:
            print(f"  → Sistema: No tengo información que repetir.")
        return contexto
    
    def accion_confirmar(contexto):
        print(f"  → Sistema: Perfecto. ¿Necesitas algo más?")
        return contexto
    
    def accion_despedida(contexto):
        print(f"  → Sistema: ¡Hasta luego!")
        return {}
    
    # Configurar transiciones
    estado_inicio.agregar_transicion("saludo", "esperando", accion_saludo)
    
    estado_esperando.agregar_transicion("pedir_horario", "consultando", accion_pedir_horario)
    
    estado_consultando.agregar_transicion("confirmar", "fin", accion_confirmar)
    estado_consultando.agregar_transicion("repetir", "consultando", accion_repetir)
    
    estado_fin.agregar_transicion("despedida", "inicio", accion_despedida)
    
    return maquina


def extraer_estadisticas_dialogo(motor):
    """
    Extrae estadísticas de un diálogo procesado.
    
    Args:
        motor (MotorDialogo): Motor de diálogo
    
    Retorna:
        dict: Estadísticas del diálogo
    """
    turnos = motor.obtener_turnos()
    turnos_exitosos = sum(1 for t in turnos if t["transicion_realizada"])
    
    return {
        "total_turnos": len(turnos),
        "turnos_exitosos": turnos_exitosos,
        "tasa_exito": turnos_exitosos / len(turnos) if turnos else 0,
        "intenciones_unicas": len(set(t["intencion"] for t in turnos if t["intencion"])),
        "estado_final": motor.maquina.obtener_estado_actual()
    }
