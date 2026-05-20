class Nodo:

    def __init__(self, etiqueta, hijos=None):

        self.etiqueta = etiqueta
        self.hijos = hijos if hijos else []


    def mostrar(self, nivel=0):

        sangria = "  " * nivel

        resultado = sangria + self.etiqueta + "\n"

        for hijo in self.hijos:

            if isinstance(hijo, Nodo):
                resultado += hijo.mostrar(nivel + 1)

            else:
                resultado += "  " * (nivel + 1) + str(hijo) + "\n"

        return resultado


    def __repr__(self):

        return self.mostrar()