import matplotlib.pyplot as plt
from nodes import Nodo


def _leaf_count(nodo):
    if not nodo.hijos:
        return 1
    return sum(_leaf_count(h) if isinstance(h, Nodo) else 1 for h in nodo.hijos)


def _profundidad(nodo):
    if not nodo.hijos:
        return 0
    return 1 + max(
        _profundidad(h) if isinstance(h, Nodo) else 0 for h in nodo.hijos
    )


def _layout(nodo, x_izq, y, posiciones, leaf_offsets):
    if not nodo.hijos:
        posiciones[id(nodo)] = (x_izq + 0.5, y)
        leaf_offsets[id(nodo)] = (x_izq, x_izq + 1)
        return 1

    x_actual = x_izq
    leaf_inicio = x_izq
    for h in nodo.hijos:
        if isinstance(h, Nodo):
            ancho = _layout(h, x_actual, y - 1, posiciones, leaf_offsets)
            x_actual += ancho
        else:
            posiciones[id(h)] = (x_actual + 0.5, y - 1)
            leaf_offsets[id(h)] = (x_actual, x_actual + 1)
            x_actual += 1

    leaf_fin = x_actual
    medio = (leaf_inicio + leaf_fin) / 2
    posiciones[id(nodo)] = (medio, y)
    leaf_offsets[id(nodo)] = (leaf_inicio, leaf_fin)
    return leaf_fin - leaf_inicio


def _draw(ax, nodo, posiciones):
    x, y = posiciones[id(nodo)]
    ax.text(x, y, nodo.etiqueta, ha="center", va="center",
            fontsize=10, fontweight="bold",
            bbox=dict(boxstyle="round,pad=0.3", facecolor="lightblue"))
    for h in nodo.hijos:
        if isinstance(h, Nodo):
            hx, hy = posiciones[id(h)]
            ax.plot([x, hx], [y - 0.15, hy + 0.15], "k-", linewidth=1.2)
            _draw(ax, h, posiciones)
        else:
            hx, hy = posiciones[id(h)]
            ax.plot([x, hx], [y - 0.15, hy + 0.15], "k-", linewidth=1.2)
            ax.text(hx, hy, str(h), ha="center", va="center",
                    fontsize=9, fontstyle="italic",
                    bbox=dict(boxstyle="round,pad=0.3", facecolor="lightyellow"))


def visualizar(arbol, titulo="Árbol de Análisis Sintáctico"):
    posiciones = {}
    leaf_offsets = {}
    total_hojas = _leaf_count(arbol)
    _layout(arbol, 0, 0, posiciones, leaf_offsets)

    fig, ax = plt.subplots(figsize=(max(6, total_hojas * 1.2), max(4, _profundidad(arbol) * 1.5)))
    ax.set_xlim(-0.5, total_hojas + 0.5)
    ax.set_ylim(-_profundidad(arbol) - 0.5, 0.5)
    ax.axis("off")
    ax.set_title(titulo, fontsize=13, fontweight="bold", pad=10)

    _draw(ax, arbol, posiciones)
    plt.tight_layout()
    plt.show()
