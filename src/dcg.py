"""
Definite Clause Grammar (DCG) con unificacion de rasgos.

Analiza sintagmas nominales, verbales y oraciones simples. La parte clave
para el proyecto es que rechaza concordancias incorrectas como
"una gobierno mentirosa" y deja un mensaje de error explicito.
"""

from unification import extraer_rasgos, unificar


class Parser:
    """Parser DCG con rasgos de genero y numero."""

    def __init__(self, lexico, debug=True):
        self.lexico = lexico
        self.debug = debug
        self.ultimo_error = None

    def _error(self, mensaje):
        self.ultimo_error = mensaje
        if self.debug:
            print(f"    X {mensaje}")

    def analizar_np(self, tokens, pos):
        """Analiza NP -> Det N | Det N Adj."""
        if pos + 1 >= len(tokens):
            self._error("NP: no hay suficientes tokens")
            return None, pos

        palabra_det = tokens[pos]
        palabra_n = tokens[pos + 1]

        if palabra_det not in self.lexico:
            self._error(f"NP: '{palabra_det}' no esta en el lexico")
            return None, pos

        if palabra_n not in self.lexico:
            self._error(f"NP: '{palabra_n}' no esta en el lexico")
            return None, pos

        rasgos_det = self.lexico[palabra_det]
        rasgos_n = self.lexico[palabra_n]

        if rasgos_det.get("cat") != "det":
            self._error(f"NP: '{palabra_det}' no es determinante")
            return None, pos

        if rasgos_n.get("cat") != "n":
            self._error(f"NP: '{palabra_n}' no es sustantivo")
            return None, pos

        concord_det = extraer_rasgos(rasgos_det, ["gen", "num"])
        concord_n = extraer_rasgos(rasgos_n, ["gen", "num"])
        unificado = unificar(concord_det, concord_n)

        if unificado is None:
            self._error(
                f"NP: conflicto de concordancia entre '{palabra_det}' "
                f"{concord_det} y '{palabra_n}' {concord_n}"
            )
            return None, pos

        np = {
            "cat": "np",
            "gen": unificado["gen"],
            "num": unificado["num"],
            "det": palabra_det,
            "n": palabra_n,
        }

        nueva_pos = pos + 2
        if nueva_pos < len(tokens):
            palabra_adj = tokens[nueva_pos]
            if palabra_adj in self.lexico and self.lexico[palabra_adj].get("cat") == "adj":
                rasgos_adj = self.lexico[palabra_adj]
                concord_adj = extraer_rasgos(rasgos_adj, ["gen", "num"])
                unificado_adj = unificar(unificado, concord_adj)

                if unificado_adj is None:
                    self._error(
                        f"NP: conflicto de concordancia entre '{palabra_n}' "
                        f"{concord_n} y adjetivo '{palabra_adj}' {concord_adj}"
                    )
                    return None, pos

                np["gen"] = unificado_adj["gen"]
                np["num"] = unificado_adj["num"]
                np["adj"] = palabra_adj
                nueva_pos += 1

        if self.debug:
            partes = [palabra_det, palabra_n]
            if "adj" in np:
                partes.append(np["adj"])
            print(f"    OK NP: [{' + '.join(partes)}] rasgos={unificado}")

        return np, nueva_pos

    def analizar_vp(self, tokens, pos):
        """Analiza VP -> V."""
        if pos >= len(tokens):
            self._error("VP: no hay tokens")
            return None, pos

        palabra_v = tokens[pos]

        if palabra_v not in self.lexico:
            self._error(f"VP: '{palabra_v}' no esta en el lexico")
            return None, pos

        rasgos_v = self.lexico[palabra_v]
        if rasgos_v.get("cat") != "v":
            self._error(f"VP: '{palabra_v}' no es verbo")
            return None, pos

        vp = {
            "cat": "vp",
            "num": rasgos_v["num"],
            "accion": rasgos_v["accion"],
            "v": palabra_v,
        }

        if self.debug:
            print(f"    OK VP: [{palabra_v}] accion='{rasgos_v['accion']}', num={rasgos_v['num']}")

        return vp, pos + 1

    def analizar_s(self, tokens):
        """Analiza S -> NP VP."""
        self.ultimo_error = None
        if self.debug:
            print(f"\n  Analizando: '{' '.join(tokens)}'")

        np, pos = self.analizar_np(tokens, 0)
        if np is None:
            if not self.ultimo_error:
                self._error("S: no se reconocio el NP")
            return None

        vp, pos = self.analizar_vp(tokens, pos)
        if vp is None:
            if not self.ultimo_error:
                self._error("S: no se reconocio el VP")
            return None

        if pos != len(tokens):
            self._error(f"S: tokens sobrantes: {tokens[pos:]}")
            return None

        concordancia = unificar({"num": np["num"]}, {"num": vp["num"]})
        if concordancia is None:
            self._error(f"S: conflicto sujeto-verbo: NP={np['num']} vs VP={vp['num']}")
            return None

        oracion = {
            "cat": "S",
            "np": np,
            "vp": vp,
            "accion": vp["accion"],
        }

        if self.debug:
            print("    OK Oracion valida")

        return oracion

    def analizar_fragmento(self, tokens):
        """Analiza una oracion completa o un NP aislado."""
        oracion = self.analizar_s(tokens)
        if oracion is not None:
            return oracion

        error_s = self.ultimo_error
        self.ultimo_error = None
        np, pos = self.analizar_np(tokens, 0)
        if np is not None and pos == len(tokens):
            return {"cat": "FRAG_NP", "np": np}

        if np is not None and pos != len(tokens):
            self._error(f"FRAG_NP: tokens sobrantes: {tokens[pos:]}")

        if self.ultimo_error is None:
            self.ultimo_error = error_s

        return None

    def extraer_intencion(self, oracion):
        if oracion is None:
            return "Oracion no valida"

        np = oracion.get("np", {})
        sujeto = f"{np.get('det', '')} {np.get('n', '')}".strip()
        if np.get("adj"):
            sujeto = f"{sujeto} {np['adj']}"

        if oracion.get("cat") == "FRAG_NP":
            return f"Fragmento nominal: '{sujeto}'"

        return f"Sujeto: '{sujeto}' | Accion: '{oracion.get('accion')}'"


def crear_lexico_fake_news():
    """Lexico con rasgos para el dominio de noticias falsas."""
    return {
        "el": {"cat": "det", "gen": "masc", "num": "sing"},
        "la": {"cat": "det", "gen": "fem", "num": "sing"},
        "los": {"cat": "det", "gen": "masc", "num": "plur"},
        "las": {"cat": "det", "gen": "fem", "num": "plur"},
        "un": {"cat": "det", "gen": "masc", "num": "sing"},
        "una": {"cat": "det", "gen": "fem", "num": "sing"},

        "virus": {"cat": "n", "gen": "masc", "num": "sing", "tema": "salud"},
        "gobierno": {"cat": "n", "gen": "masc", "num": "sing", "tema": "politica"},
        "crisis": {"cat": "n", "gen": "fem", "num": "sing", "tema": "economia"},
        "celula": {"cat": "n", "gen": "fem", "num": "sing", "tema": "salud"},
        "cura": {"cat": "n", "gen": "masc", "num": "sing", "tema": "salud"},
        "noticia": {"cat": "n", "gen": "fem", "num": "sing", "tema": "media"},
        "plan": {"cat": "n", "gen": "masc", "num": "sing", "tema": "conspiracy"},

        "mentiroso": {"cat": "adj", "gen": "masc", "num": "sing", "rasgo": "descalificacion"},
        "mentirosa": {"cat": "adj", "gen": "fem", "num": "sing", "rasgo": "descalificacion"},
        "peligroso": {"cat": "adj", "gen": "masc", "num": "sing", "rasgo": "alarma"},
        "peligrosa": {"cat": "adj", "gen": "fem", "num": "sing", "rasgo": "alarma"},
        "falso": {"cat": "adj", "gen": "masc", "num": "sing", "rasgo": "desconfianza"},
        "falsa": {"cat": "adj", "gen": "fem", "num": "sing", "rasgo": "desconfianza"},

        "amenaza": {"cat": "v", "num": "sing", "accion": "amenazar",  "sensacionalismo": True},
        "amenazan": {"cat": "v", "num": "plur", "accion": "amenazar", "sensacionalismo": True},
        "revela": {"cat": "v", "num": "sing", "accion": "revelar", "sensacionalismo": True},
        "revelan": {"cat": "v", "num": "plur", "accion": "revelar", "sensacionalismo": True},
        "causa": {"cat": "v", "num": "sing", "accion": "causar", "sensacionalismo": True},
        "causan": {"cat": "v", "num": "plur", "accion": "causar", "sensacionalismo": True},
        "descubre": {"cat": "v", "num": "sing", "accion": "descubrir", "sensacionalismo": True},
        "descubren": {"cat": "v", "num": "plur", "accion": "descubrir", "sensacionalismo": True},
        "oculta": {"cat": "v", "num": "sing", "accion": "ocultar", "sensacionalismo": True},
        "ocultan": {"cat": "v", "num": "plur", "accion": "ocultar", "sensacionalismo": True},
        "amenazas": {"cat": "v", "num": "plur", "accion": "amenazar", "sensacionalismo": True},
    }
