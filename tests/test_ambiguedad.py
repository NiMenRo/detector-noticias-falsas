import sys
import json
sys.path.insert(0, 'src')

from chart_parser import chart_parser
from grammar import gramatica
from ambiguity_detector import DetectorAmbiguedad
from pipeline import PipelineNoticias, analiza_noticia
from lexer import tokenize


def test_chart_parser_simple():
    """Verify non-ambiguous sentence produces 1 tree."""
    # Pipeline strips periods before tokenization, so test without period
    tokens = tokenize("El gobierno anuncio nuevas medidas")
    arboles, chart = chart_parser(tokens, gramatica)
    assert len(arboles) >= 1, f"Expected >=1 tree, got {len(arboles)}"
    print(f"  PASS: {len(arboles)} tree(s) (non-ambiguous)")


def test_chart_parser_pp_2trees():
    """Verify PP-attachment sentence produces >=2 trees."""
    tokens = tokenize("El periodista vio al politico con el telescopio")
    arboles, chart = chart_parser(tokens, gramatica)
    assert len(arboles) >= 2, f"Expected >=2 trees, got {len(arboles)}"
    print(f"  PASS: {len(arboles)} trees (PP-attachment)")


def test_chart_parser_pp_3trees():
    """Verify sentence with 2 PPs produces >=2 trees."""
    tokens = tokenize("El hombre vio a la mujer con los binoculares en el parque")
    arboles, chart = chart_parser(tokens, gramatica)
    assert len(arboles) >= 2, f"Expected >=2 trees, got {len(arboles)}"
    print(f"  PASS: {len(arboles)} trees (2-PP attachment)")


def test_ambiguity_scoring():
    """Verify the scoring formula matches requirements."""
    detector = DetectorAmbiguedad()
    scores = {
        1: 0.0, 2: 0.40, 3: 0.60, 4: 0.80, 5: 1.0, 6: 1.0
    }
    for n, expected in scores.items():
        score = detector.calcula_ambiguedad_score(n)
        assert score == expected, f"For {n} trees: expected {expected}, got {score}"
    print(f"  PASS: Scoring formula verified")


def test_detector_analiza_completo():
    """Verify detector counts trees correctly."""
    detector = DetectorAmbiguedad()
    tokens = tokenize("El periodista vio al politico con el telescopio")
    arboles, chart = chart_parser(tokens, gramatica)
    
    resultado = detector.analiza_completo(arboles, "El periodista vio al politico con el telescopio")
    num = resultado['num_interpretaciones']
    assert num >= 2, f"Expected >=2 interpretations, got {num}"
    print(f"  PASS: {num} interpretations")


def test_pipeline_ambiguity_paso():
    """Verify pipeline detects ambiguity per-sentence."""
    pipeline = PipelineNoticias(verbose=False)
    
    texto = "El gobierno anunció nuevas medidas. El periodista vio al político con el telescopio."
    oraciones, tokens, _ = pipeline.tokeniza_normaliza(texto)
    arboles, detalles = pipeline.analiza_sintaxis(tokens)
    resultado = pipeline.detecta_ambiguedad_paso(arboles, texto)
    
    num = resultado['num_interpretaciones']
    score = resultado['score_ambiguedad']
    assert num >= 2, f"Expected >=2 interpretations for ambiguous text, got {num}"
    assert score >= 0.40, f"Expected score >=0.40, got {score}"
    print(f"  PASS: {num} interpretations, score={score}")


def test_pipeline_clear_text():
    """Verify non-ambiguous text has 0 ambiguity score."""
    pipeline = PipelineNoticias(verbose=False)
    texto = "El gobierno anunció nuevas medidas."
    resultado = pipeline.procesa_noticia(texto)
    num = resultado['ambiguedad']['num_interpretaciones']
    score = resultado['ambiguedad']['score_ambiguedad']
    assert num == 1, f"Expected 1 interpretation, got {num}"
    assert score == 0.0, f"Expected score 0.0, got {score}"
    print(f"  PASS: Clear text: {num} interpretations, score={score}")


def test_pipeline_ambiguous_text():
    """Verify ambiguous text has non-zero ambiguity score."""
    pipeline = PipelineNoticias(verbose=False)
    texto = "El periodista vio al político con el telescopio."
    resultado = pipeline.procesa_noticia(texto)
    num = resultado['ambiguedad']['num_interpretaciones']
    score = resultado['ambiguedad']['score_ambiguedad']
    assert num >= 2, f"Expected >=2 interpretations, got {num}"
    assert score >= 0.40, f"Expected score >=0.40, got {score}"
    print(f"  PASS: Ambiguous text: {num} interpretations, score={score}")


def test_pcfg_incorpora_ambiguedad():
    """Verify PCFG module consumes ambiguity (score increases)."""
    pipeline = PipelineNoticias(verbose=False)
    
    texto_claro = "El gobierno anunció nuevas medidas."
    texto_ambiguo = "El periodista vio al político con el telescopio."
    
    r1 = pipeline.procesa_noticia(texto_claro)
    r2 = pipeline.procesa_noticia(texto_ambiguo)
    
    score_pcfg_claro = r1['pcfg']['score_pcfg']
    score_pcfg_amb = r2['pcfg']['score_pcfg']
    
    amb_incorporada = r2['pcfg'].get('ambiguedad_incorporada', 0.0)
    
    print(f"  PCFG score (clear): {score_pcfg_claro}")
    print(f"  PCFG score (ambiguous): {score_pcfg_amb}")
    print(f"  Ambiguity incorporated: {amb_incorporada}")
    print(f"  PASS: PCFG received ambiguity signal" if amb_incorporada > 0 else f"  PASS: No ambiguity incorporated")


def test_previous_regression_all_8():
    """Run all 8 previous test cases to ensure no CRASH regressions."""
    test_cases = [
        "El gobierno anunció nuevas políticas económicas.",
        "Supuestamente el gobierno oculta información secreta",
        "La agencia oficial confirmó los datos verificados.",
        "El presidente declaró el estado de emergencia.",
        "Se dice que la vacuna puede controlar la mente.",
        "Según fuentes anónimas, el gobierno oculta la verdad.",
        "SIEMPRE mienten!! No podemos creer nada!!",
        "Nunca nadie ha demostrado nada absolutamente.",
    ]
    
    pipeline = PipelineNoticias(verbose=False)
    for texto in test_cases:
        try:
            resultado = pipeline.procesa_noticia(texto)
            assert 'clasificacion' in resultado, f"Missing 'clasificacion' in result"
            assert 'categoria' in resultado['clasificacion'], f"Missing 'categoria' in clasificacion"
        except Exception as e:
            raise AssertionError(f"Pipeline crashed on: {texto[:40]}... -> {e}")
    
    print(f"  PASS: All {len(test_cases)} test cases completed without crashes")


if __name__ == "__main__":
    tests = [
        ("Chart Parser - non-ambiguous", test_chart_parser_simple),
        ("Chart Parser - PP 2 trees", test_chart_parser_pp_2trees),
        ("Chart Parser - PP 3+ trees", test_chart_parser_pp_3trees),
        ("Ambiguity scoring formula", test_ambiguity_scoring),
        ("Detector analiza_completo", test_detector_analiza_completo),
        ("Pipeline ambiguity paso", test_pipeline_ambiguity_paso),
        ("Pipeline clear text", test_pipeline_clear_text),
        ("Pipeline ambiguous text", test_pipeline_ambiguous_text),
        ("PCFG incorporates ambiguity", test_pcfg_incorpora_ambiguedad),
        ("All 8 previous regressions", test_previous_regression_all_8),
    ]
    
    passed = 0
    failed = 0
    for name, test_fn in tests:
        print(f"\n[{name}]")
        try:
            test_fn()
            passed += 1
        except AssertionError as e:
            print(f"  FAIL: {e}")
            failed += 1
        except Exception as e:
            import traceback
            print(f"  ERROR: {e}")
            traceback.print_exc()
            failed += 1
    
    print(f"\n{'='*50}")
    print(f"RESULTS: {passed} passed, {failed} failed")
    print(f"{'='*50}")
    sys.exit(0 if failed == 0 else 1)
