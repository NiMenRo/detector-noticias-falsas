# Entrenador PCFG - Calcula probabilidades de reglas desde corpus
# Problema 7: Crear entrenador automático de PCFG

from collections import defaultdict
import re
from grammar import gramatica

class PCFGTrainer:
    """Entrena PCFG calculando probabilidades desde corpus."""
    
    def __init__(self):
        self.regla_frecuencias = defaultdict(lambda: defaultdict(int))
        self.pcfg = {}
    
    def extraer_reglas_corpus(self, ruta_corpus):
        """Extrae reglas sintácticas del corpus mediante parsing simple."""
        try:
            with open(ruta_corpus, 'r', encoding='utf-8') as f:
                for linea in f:
                    linea = linea.strip()
                    if not linea or linea.startswith('#'):
                        continue
                    self._extraer_reglas_oracion(linea)
        except FileNotFoundError:
            print(f"[PCFG] Corpus no encontrado: {ruta_corpus}")
    
    def _extraer_reglas_oracion(self, oracion):
        """Extrae reglas representativas de una oración."""
        tokens = re.findall(r'\w+', oracion.lower())
        if not tokens:
            return
        
        # Reglas heurísticas basadas en la estructura observada
        # S → NP VP (siempre)
        self.regla_frecuencias['S'][('NP', 'VP')] += 1
        
        # Detectar presencia de modales, adverbios absolutos, fuentes indefinidas
        tiene_modal = any(t in ['podría', 'aparentemente', 'posiblemente', 'quizás', 
                               'supuestamente', 'según', 'dicen', 'parece'] for t in tokens)
        tiene_adv_abs = any(t in ['siempre', 'nunca', 'definitivamente', 'absolutamente',
                                   'claramente', 'obviamente', 'evidentemente'] for t in tokens)
        tiene_fuente_indef = any(t in ['supuestamente', 'según', 'dicen', 'rumorea',
                                        'anónimas', 'informalmente'] for t in tokens)
        
        # VP tiene múltiples expansiones
        if tiene_modal:
            self.regla_frecuencias['VP'][('MODAL', 'VP')] += 1
        if tiene_adv_abs:
            self.regla_frecuencias['VP'][('ADV_ABS', 'VP')] += 1
        if tiene_fuente_indef:
            self.regla_frecuencias['VP'][('VP', 'FUENTE_INDEFINIDA')] += 1
        else:
            # VP → V NP es más común cuando no hay patrones especiales
            self.regla_frecuencias['VP'][('V', 'NP')] += 1
        
        # NP → Det N es muy frecuente
        self.regla_frecuencias['NP'][('Det', 'N')] += 0.8
        self.regla_frecuencias['NP'][('Det', 'ADJ', 'N')] += 0.15
        self.regla_frecuencias['NP'][('N',)] += 0.05
    
    def calcular_probabilidades(self):
        """Calcula P(regla) = frecuencia(regla) / frecuencia(lhs)."""
        for lhs, rhs_dict in self.regla_frecuencias.items():
            total = sum(rhs_dict.values())
            if total == 0:
                continue
            
            self.pcfg[lhs] = []
            for rhs, freq in rhs_dict.items():
                prob = freq / total
                self.pcfg[lhs].append((rhs, round(prob, 4)))
            
            # Ordenar por probabilidad descendente
            self.pcfg[lhs].sort(key=lambda x: -x[1])
    
    def entrenar_desde_corpus(self, ruta_corpus):
        """Pipeline completo: extrae reglas → calcula probabilidades."""
        print(f"[PCFG] Entrenando desde corpus: {ruta_corpus}")
        self.extraer_reglas_corpus(ruta_corpus)
        self.calcular_probabilidades()
        print(f"[PCFG] Entrenamiento completado. {len(self.pcfg)} símbolos con reglas.")
        return self.pcfg
    
    def obtener_probabilidad_regla(self, lhs, rhs):
        """Obtiene P(lhs → rhs). Si no existe, retorna 0.0."""
        if lhs not in self.pcfg:
            return 0.0
        
        for regla_rhs, prob in self.pcfg[lhs]:
            if regla_rhs == rhs:
                return prob
        
        return 0.0
    
    def mostrar_pcfg(self):
        """Imprime la PCFG entrenada con probabilidades."""
        print("\n" + "="*60)
        print("PCFG ENTRENADA")
        print("="*60)
        for lhs in sorted(self.pcfg.keys()):
            suma = sum(p for _, p in self.pcfg[lhs])
            print(f"\n{lhs}  (suma={suma:.2f}):")
            for rhs, prob in self.pcfg[lhs]:
                rhs_str = ' '.join(rhs) if isinstance(rhs, tuple) else rhs
                print(f"  → {rhs_str:30s} [{prob:.4f}]")


# Función auxiliar para entrenar ambos corpus
def entrenar_pcfg_completa():
    """Entrena PCFG desde corpus neutral y sospechoso."""
    trainer_neutral = PCFGTrainer()
    trainer_sospechoso = PCFGTrainer()
    
    trainer_neutral.entrenar_desde_corpus('data/corpus_neutral.txt')
    trainer_sospechoso.entrenar_desde_corpus('data/corpus_sospechoso.txt')
    
    return trainer_neutral, trainer_sospechoso


if __name__ == "__main__":
    trainer = PCFGTrainer()
    trainer.entrenar_desde_corpus('data/corpus_neutral.txt')
    trainer.mostrar_pcfg()
