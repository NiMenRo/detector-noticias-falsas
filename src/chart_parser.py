import unicodedata
from nodes import Nodo


def _sin_acentos(texto):
    """Normaliza eliminando acentos para matching insensible."""
    nfkd = unicodedata.normalize('NFKD', texto)
    return ''.join(c for c in nfkd if not unicodedata.combining(c))


class Edge:

    def __init__(self, lhs, found, waiting, start, end, hijos=None):

        self.lhs = lhs
        self.found = found
        self.waiting = waiting
        self.start = start
        self.end = end

        self.hijos = hijos if hijos else []
        self.alternativas = []  # Otras formas de derivar el mismo edge


    def completo(self):

        return len(self.waiting) == 0


    def siguiente(self):

        if self.waiting:
            return self.waiting[0]

        return None


    def __repr__(self):

        antes = " ".join(self.found)

        despues = " ".join(self.waiting)

        return f"[{self.lhs} -> {antes} • {despues}, ({self.start}, {self.end})]"



def chart_parser(tokens, gramatica):

    chart = [[] for _ in range(len(tokens) + 1)]


    def agregar_edge(edge, posicion):

        for existente in chart[posicion]:

            if (
                existente.lhs == edge.lhs and
                existente.found == edge.found and
                existente.waiting == edge.waiting and
                existente.start == edge.start and
                existente.end == edge.end
            ):
                # Si tiene diferentes hijos, guardamos como alternativa
                if existente.hijos != edge.hijos and edge.hijos:
                    existente.alternativas.append(edge.hijos)
                return False

        chart[posicion].append(edge)

        return True



    # Inicialización

    for produccion in gramatica["S"]:

        edge = Edge(
            lhs="S",
            found=[],
            waiting=produccion,
            start=0,
            end=0
        )

        agregar_edge(edge, 0)



    # Algoritmo principal

    for i in range(len(chart)):

        cambios = True

        while cambios:

            cambios = False

            edges_actuales = list(chart[i])


            for edge in edges_actuales:


                # Predictor

                siguiente = edge.siguiente()

                if siguiente in gramatica:

                    for produccion in gramatica[siguiente]:

                        nuevo = Edge(
                            lhs=siguiente,
                            found=[],
                            waiting=produccion,
                            start=i,
                            end=i
                        )

                        if agregar_edge(nuevo, i):
                            cambios = True



                # Scanner (insensible a acentos)

                elif siguiente is not None:

                    if i < len(tokens) and _sin_acentos(tokens[i]) == _sin_acentos(siguiente):

                        nuevo = Edge(
                            lhs=edge.lhs,
                            found=edge.found + [siguiente],
                            waiting=edge.waiting[1:],
                            start=edge.start,
                            end=i + 1,
                            hijos=edge.hijos + [siguiente]
                        )

                        if agregar_edge(nuevo, i + 1):
                            cambios = True



                # Completer

                if edge.completo():

                    nodo = Nodo(edge.lhs, edge.hijos)

                    for anterior in chart[edge.start]:

                        esperado = anterior.siguiente()

                        if esperado == edge.lhs:

                            nuevo = Edge(
                                lhs=anterior.lhs,
                                found=anterior.found + [edge.lhs],
                                waiting=anterior.waiting[1:],
                                start=anterior.start,
                                end=edge.end,
                                hijos=anterior.hijos + [nodo]
                            )

                            if agregar_edge(nuevo, edge.end):
                                cambios = True



    # Buscar árboles completos

    arboles = []

    def generar_arboles(edge_lhs, hijos_listas):
        """Genera todas las combinaciones de árboles a partir de listas de hijos alternativos."""
        if not hijos_listas:
            return [Nodo(edge_lhs, [])]
        
        primeros_hijos = hijos_listas[0]
        resto_hijos = hijos_listas[1:]
        
        arboles_resto = generar_arboles(edge_lhs, resto_hijos) if resto_hijos else [Nodo(edge_lhs, [])]
        
        resultados = []
        for hijos in primeros_hijos:
            for arbol_r in arboles_resto:
                nuevos = Nodo(edge_lhs, hijos)
                resultados.append(nuevos)
        
        return resultados if resultados else [Nodo(edge_lhs, primeros_hijos[0]) if primeros_hijos else Nodo(edge_lhs, [])]

    for edge in chart[len(tokens)]:

        if (
            edge.lhs == "S" and
            edge.completo() and
            edge.start == 0
        ):

            arbol = Nodo("S", edge.hijos)
            arboles.append(arbol)
            
            # Generar árboles alternativos
            for alt_hijos in edge.alternativas:
                arbol_alt = Nodo("S", alt_hijos)
                # Evitar duplicados
                es_duplicado = False
                for existente in arboles:
                    if str(existente) == str(arbol_alt):
                        es_duplicado = True
                        break
                if not es_duplicado:
                    arboles.append(arbol_alt)


    return arboles, chart