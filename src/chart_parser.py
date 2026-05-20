from nodes import Nodo


class Edge:

    def __init__(self, lhs, found, waiting, start, end, hijos=None):

        self.lhs = lhs
        self.found = found
        self.waiting = waiting
        self.start = start
        self.end = end

        self.hijos = hijos if hijos else []


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



                # Scanner

                elif siguiente is not None:

                    if i < len(tokens) and tokens[i] == siguiente:

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

    for edge in chart[len(tokens)]:

        if (
            edge.lhs == "S" and
            edge.completo() and
            edge.start == 0
        ):

            arbol = Nodo("S", edge.hijos)

            arboles.append(arbol)


    return arboles, chart