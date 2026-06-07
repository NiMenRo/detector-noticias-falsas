from nodes import Nodo


def nodo_a_dict(arbol):
    hijos = []
    for h in arbol.hijos:
        if isinstance(h, Nodo):
            hijos.append(nodo_a_dict(h))
        else:
            hijos.append(str(h))

    resultado = {
        'simbolo': arbol.etiqueta,
        'hijos': hijos
    }

    etiquetas_hijos = [
        h.etiqueta if isinstance(h, Nodo) else str(h) for h in arbol.hijos
    ]
    if etiquetas_hijos:
        resultado['regla'] = "{} -> {}".format(
            arbol.etiqueta, " ".join(etiquetas_hijos)
        )

    return resultado
