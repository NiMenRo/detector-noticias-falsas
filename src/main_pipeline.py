"""
Interfaz de consola para ejecutar el pipeline.

Solo ofrece una accion: anadir texto. El texto puede ser un titulo corto
("!el virus amenaza!") o una noticia con cuerpo en varias lineas.
"""

from pathlib import Path
import sys


sys.path.insert(0, str(Path(__file__).resolve().parent))

from pipeline import PipelineNoticias


def leer_texto() -> str:
    print("\nOPCION UNICA: Anadir texto")
    print("Escribe un titulo o una noticia completa.")
    print("Para terminar la entrada, presiona Enter en una linea vacia.\n")

    lineas = []
    while True:
        try:
            linea = input("> ")
        except EOFError:
            break

        if not linea.strip():
            break
        lineas.append(linea.strip())

    return " ".join(lineas).strip()


def mostrar_resultado(resultado: dict) -> None:
    clasificacion = resultado["clasificacion"]
    ambiguedad = resultado["ambiguedad"]
    patrones = resultado["patrones"]
    pcfg = resultado["pcfg"]
    rasgos = resultado["rasgos"]
    dag = resultado["caracteristicas_dag"]
    normalizacion = resultado.get("normalizacion", {})
    estadisticas = resultado["estadisticas_basicas"]

    print("\n" + "=" * 60)
    print("RESULTADO DEL ANALISIS")
    print("=" * 60)
    print(f"Texto: {resultado['texto_original']}")
    print(f"Palabras: {estadisticas['num_palabras']}")
    print(f"Oraciones: {estadisticas['num_oraciones']}")
    

    print(f"\nNormalizacion (DCG + DAG):")
    estado = "VALIDO" if normalizacion.get('texto_gramaticalmente_valido', True) else "ERROR DE CONCORDANCIA"
    print(f"- Estado gramatical: {estado}")
    print(f"- Oraciones validas: {normalizacion.get('num_oraciones_validas', 0)}")
    print(f"- Oraciones invalidas: {normalizacion.get('num_oraciones_invalidas', 0)}")
    for err in normalizacion.get('oraciones_invalidas', []):
        print(f"  * [{err['oracion_idx'] + 1}] {' '.join(err['tokens'])} -> {err['error']}")

    print(f"\nClasificacion: {clasificacion['categoria']}")
    print(f"Score final: {clasificacion['score_final']:.3f}")
    print(f"Confianza: {clasificacion['confianza'] * 100:.1f}%")

    print("\nAmbiguedad:")
    print(f"- Score: {ambiguedad['score_ambiguedad']:.3f}")
    print(f"- Interpretaciones: {ambiguedad['num_interpretaciones']}")
    print(f"- Palabras ambiguas: {len(ambiguedad['palabras_ambiguas'])}")

    for item in ambiguedad["desambiguaciones"]:
        cats = ", ".join(item["categorias_posibles"])
        print(
            "- "
            f"{item['palabra']} ({cats}) -> "
            f"{item['categoria_mas_probable']} "
            f"P={item['probabilidad']:.3f}"
        )

    print("\nPatrones sospechosos:")
    print(f"- Total: {patrones['resumen']['total_patrones']}")
    print(f"- Score: {patrones['score_total_patrones']:.3f}")

    print("\nPCFG:")
    print(f"- Score: {pcfg['score_pcfg']:.3f}")
    print(f"- Reglas aplicadas: {pcfg['num_reglas_aplicadas']}")
    for regla in pcfg["reglas_aplicadas"]:
        print(f"- {regla['regla']} peso={regla['peso']:.2f}")

    print("\nRecomendacion:")
    print(clasificacion["recomendacion"])
    print("=" * 60)


def main() -> int:
    texto = leer_texto()
    if not texto:
        print("No se ingreso texto para analizar.")
        return 0

    pipeline = PipelineNoticias(verbose=False)
    resultado = pipeline.procesa_noticia(texto)
    mostrar_resultado(resultado)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
