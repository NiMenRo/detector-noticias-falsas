#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
demo.py - Punto de entrada unico para el Detector de Noticias Falsas

Ejecutar desde la raiz del proyecto:
    python demo.py

Requiere:
    - pipeline.py, nodes.py, tree_converter.py, pcfg.py y demas modulos en src/
    - data/corpus_neutral.txt y data/corpus_sospechoso.txt
"""

import sys
import os

sys.path.insert(0, os.path.dirname(__file__))


CASOS_DE_PRUEBA = [
    {
        "titulo": "NOTICIA NEUTRAL",
        "texto": "el gobierno declara la crisis",
        "descripcion": "Oracion declarativa simple sin marcas de sensacionalismo"
    },
    {
        "titulo": "NOTICIA SOSPECHOSA",
        "texto": "el gobierno supuestamente oculta la crisis",
        "descripcion": "Contiene verbo modal (supuestamente) indicando especulacion"
    },
    {
        "titulo": "NOTICIA SENSACIONALISTA",
        "texto": "el virus amenaza",
        "descripcion": "Oracion corta sin matices, tipica de titulo alarmista"
    },
    {
        "titulo": "CASO AMBIGUO (PP attachment)",
        "texto": "el periodista vio al politico con el telescopio",
        "descripcion": "Dos interpretaciones: 'vio con el telescopio' o 'politico con el telescopio'"
    },
    {
        "titulo": "ENTRADA INVALIDA (DCG)",
        "texto": "una gobierno alerta",
        "descripcion": "Error de concordancia: 'una' (fem sing) + 'gobierno' (masc sing)"
    },
    {
        "titulo": "ENTRADA INESPERADA",
        "texto": "12345 !!! ??? ###",
        "descripcion": "Texto sin estructura linguistica reconocible"
    },
]


def pausa():
    try:
        input("\nPresione Enter para continuar...")
    except EOFError:
        pass


def mostrar_arbol_consola(arboles_parse):
    if not arboles_parse:
        print("  (sin arboles sintacticos)")
        return None
    for idx_oracion, arboles_oracion in enumerate(arboles_parse):
        for idx_arbol, arbol in enumerate(arboles_oracion):
            print("  Arbol oracion {}, interpretacion {}:".format(idx_oracion + 1, idx_arbol + 1))
            for linea in arbol.mostrar().split("\n"):
                if linea.strip():
                    print("    {}".format(linea))
    if arboles_parse and arboles_parse[0]:
        return arboles_parse[0][0]
    return None


def mostrar_pcfg_real(pcfg, arbol):
    if arbol is None:
        print("  PCFG real: (no aplicable, no hay arbol)")
        return
    try:
        from tree_converter import nodo_a_dict
        arbol_dict = nodo_a_dict(arbol)
        p_neutral = pcfg.calcular_p_arbol(arbol_dict, corpus="neutral")
        p_sospechoso = pcfg.calcular_p_arbol(arbol_dict, corpus="sospechoso")
        if p_neutral < 1e-4 and p_neutral > 0:
            print("  P(arbol) en corpus neutral:    {:.2e}".format(p_neutral))
        else:
            print("  P(arbol) en corpus neutral:    {:.6f}".format(p_neutral))
        if p_sospechoso < 1e-4 and p_sospechoso > 0:
            print("  P(arbol) en corpus sospechoso: {:.2e}".format(p_sospechoso))
        else:
            print("  P(arbol) en corpus sospechoso: {:.6f}".format(p_sospechoso))
        if p_neutral > 0 and p_sospechoso > 0:
            ratio = p_sospechoso / p_neutral
            if ratio >= 100 or ratio <= 0.01:
                print("  Ratio sospechoso/neutral:      {:.2e}x".format(ratio))
            else:
                print("  Ratio sospechoso/neutral:      {:.2f}x".format(ratio))
            if ratio > 1.5:
                print("  >> La estructura se asemeja mas a noticias sospechosas")
            elif ratio < 0.7:
                print("  >> La estructura se asemeja mas a noticias verificadas")
            else:
                print("  >> La estructura no es concluyente")
        print("  Reglas PCFG disponibles (neutral):")
        for lhs in sorted(pcfg.pcfg_neutral.keys()):
            for rhs, prob in pcfg.pcfg_neutral[lhs]:
                print("    {} -> {}  [p={:.4f}]".format(lhs, " ".join(rhs), prob))
    except Exception as e:
        print("  PCFG real: error - {}".format(e))


def mostrar_resultado_pipeline(texto, resultado, pcfg):
    stats = resultado["estadisticas_basicas"]
    clasif = resultado["clasificacion"]
    amb = resultado["ambiguedad"]
    pat = resultado["patrones"]
    pcfg_res = resultado["pcfg"]
    norm = resultado.get("normalizacion", {})

    print("\n" + "=" * 60)
    print("RESULTADOS DEL ANALISIS")
    print("=" * 60)
    print("Texto: {}".format(texto))
    print("Palabras: {} | Oraciones: {}".format(stats["num_palabras"], stats["num_oraciones"]))

    print("\n--- Validacion gramatical (DCG + DAG) ---")
    estado = "VALIDO" if norm.get("texto_gramaticalmente_valido", True) else "ERROR DE CONCORDANCIA"
    print("  Estado: {}".format(estado))
    if norm.get("oraciones_invalidas"):
        for err in norm["oraciones_invalidas"]:
            print("  * Oracion {}: {} -> {}".format(
                err["oracion_idx"] + 1,
                " ".join(err.get("tokens", [])),
                err.get("error", "error de concordancia")
            ))

    print("\n--- Clasificacion ---")
    print("  Categoria: {}".format(clasif["categoria"]))
    print("  Score final: {:.4f}".format(clasif["score_final"]))
    print("  Confianza: {:.1f}%".format(clasif["confianza"] * 100))

    print("\n--- Desglose de scores ---")
    for k, v in clasif["desglose"].items():
        print("  {}: score={:.3f} x peso={:.2f} = aporte={:.4f}".format(
            k.capitalize(), v["score"], v["peso"], v["aporte"]
        ))

    print("\n--- Ambiguedad ---")
    print("  Interpretaciones: {}".format(amb["num_interpretaciones"]))
    print("  Score: {:.3f}".format(amb["score_ambiguedad"]))
    if amb.get("palabras_ambiguas"):
        for p in amb["palabras_ambiguas"]:
            print("  * {}: categorias posibles = {}".format(p[0], ", ".join(p[1])))

    print("\n--- Patrones sospechosos ---")
    print("  Total patrones: {}".format(pat["resumen"]["total_patrones"]))
    print("  Score: {:.3f}".format(pat["score_total_patrones"]))
    for k in ["afirmaciones_absolutas", "modales_vagos", "ausencia_fuentes", "negaciones_multiples"]:
        v = pat.get(k, {})
        if v.get("encontradas", 0) > 0:
            print("  * {}: {}".format(k, v["encontradas"]))

    print("\n--- PCFG (sospecha, pipeline actual) ---")
    print("  Score: {:.3f}".format(pcfg_res["score_pcfg"]))
    for r in pcfg_res.get("reglas_aplicadas", []):
        print("  * {} peso={:.2f}".format(r["regla"], r["peso"]))

    print("\n--- PCFG (real, entrenada desde corpus) ---")
    arbol = mostrar_arbol_consola(resultado.get("arboles_parse", []))
    mostrar_pcfg_real(pcfg, arbol)

    print("\n--- Justificacion ---")
    print("  {}".format(clasif.get("justificacion_completa", clasif.get("recomendacion", ""))))

    print("=" * 60)


def modo_manual(pipeline, pcfg):
    print("\n" + "=" * 60)
    print("MODO: ANALISIS MANUAL")
    print("=" * 60)
    print("Escriba el texto a analizar y presione Enter.")
    print()
    texto = input("> ").strip()
    if not texto:
        print("No se ingreso texto.")
        return
    try:
        resultado = pipeline.procesa_noticia(texto)
        mostrar_resultado_pipeline(texto, resultado, pcfg)
        arboles = resultado.get("arboles_parse", [])
        if arboles and arboles[0]:
            try:
                from tree_viz import visualizar
                visualizar(arboles[0][0], "Arbol sintactico - 1ra interpretacion")
            except Exception:
                pass
    except Exception as e:
        print("Error al procesar: {}".format(e))


def modo_pruebas(pipeline, pcfg):
    print("\n" + "=" * 60)
    print("MODO: EJECUTAR CASOS DE PRUEBA")
    print("=" * 60)
    for i, caso in enumerate(CASOS_DE_PRUEBA):
        print("\n" + "-" * 60)
        print("CASO {}".format(i + 1))
        print("Titulo: {}".format(caso["titulo"]))
        print("Descripcion: {}".format(caso["descripcion"]))
        print("-" * 60)
        print("Texto: {}".format(caso["texto"]))
        try:
            resultado = pipeline.procesa_noticia(caso["texto"])
            mostrar_resultado_pipeline(caso["texto"], resultado, pcfg)
        except Exception as e:
            print("Error: {}".format(e))
        pausa()


def main():
    os.environ["PYTHONIOENCODING"] = "utf-8"

    print("Inicializando sistema...")
    try:
        pipeline = __import__("pipeline", fromlist=["PipelineNoticias"]).PipelineNoticias(verbose=False)
        pcfg = __import__("pcfg", fromlist=["obtener_pcfg"]).obtener_pcfg()
        print("Sistema listo. PCFG entrenada ({} simbolos neutral, {} sospechoso).\n".format(
            len(pcfg.pcfg_neutral), len(pcfg.pcfg_sospechoso)
        ))
    except Exception as e:
        print("Error al inicializar: {}".format(e))
        sys.exit(1)

    while True:
        print("\n" + "=" * 60)
        print("DETECTOR DE NOTICIAS FALSAS")
        print("Herramientas PLN: CFG | Chart Parser | DCG | DAG | PCFG | Ambiguedad")
        print("=" * 60)
        print()
        print("1. Analizar texto manualmente")
        print("2. Ejecutar casos de prueba (6 casos)")
        print("3. Salir")
        print()
        try:
            opcion = input("Seleccione una opcion: ").strip()
        except EOFError:
            print("\nSaliendo...")
            break

        if opcion == "1":
            modo_manual(pipeline, pcfg)
        elif opcion == "2":
            modo_pruebas(pipeline, pcfg)
        elif opcion == "3":
            print("Saliendo...")
            break
        else:
            print("Opcion no valida. Intente de nuevo.")

    sys.exit(0)


if __name__ == "__main__":
    main()
