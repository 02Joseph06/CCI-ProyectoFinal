"""Pruebas de trazabilidad de la conversión de tamaños antes de deduplicar."""
import csv
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
import auditoria


class ConversionTamanoTest(unittest.TestCase):
    def test_conversion_precede_deduplicacion_sin_alterar_fuente(self):
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory) / "original.csv"
            output = Path(directory) / "salidas"
            row = dict(id_solicitud="1", t_llegada_s="1", tam_kb="403240.96",
                       cache_hit="0", version="B", red_ms="29.42", gpu_ms="78.81",
                       latencia_ms="108.23", intentos="1", exito="1")
            duplicate = {**row, "tam_kb": "393.79"}
            with source.open("w", encoding="utf-8", newline="") as file:
                writer = csv.DictWriter(file, fieldnames=auditoria.COLUMNS)
                writer.writeheader()
                writer.writerows([row, duplicate])
            original = source.read_bytes()
            old_source, old_output = auditoria.SOURCE, auditoria.OUTPUT
            try:
                auditoria.SOURCE, auditoria.OUTPUT = source, output
                clean, counts = auditoria.audit()
            finally:
                auditoria.SOURCE, auditoria.OUTPUT = old_source, old_output
            self.assertEqual(source.read_bytes(), original)
            self.assertEqual(counts["tam_kb: convertido de bytes a KB"], 1)
            self.assertEqual(counts["duplicado exacto eliminado"], 1)
            self.assertEqual(len(clean), 1)
            self.assertEqual(clean[0]["tam_kb"], "393.79")

    def test_tolerancia_y_exclusion_de_faltantes(self):
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory) / "original.csv"
            row = dict(id_solicitud="1", t_llegada_s="1", tam_kb="100",
                       cache_hit="0", version="A", red_ms="30", gpu_ms="10",
                       latencia_ms="39.99", intentos="1", exito="1")
            rows = [row, {**row, "id_solicitud": "2", "latencia_ms": "39.98"},
                    {**row, "id_solicitud": "3", "red_ms": ""}]
            with source.open("w", encoding="utf-8", newline="") as file:
                writer = csv.DictWriter(file, fieldnames=auditoria.COLUMNS)
                writer.writeheader()
                writer.writerows(rows)
            old_source, old_output = auditoria.SOURCE, auditoria.OUTPUT
            try:
                auditoria.SOURCE, auditoria.OUTPUT = source, Path(directory) / "salidas"
                clean, counts = auditoria.audit()
            finally:
                auditoria.SOURCE, auditoria.OUTPUT = old_source, old_output
            self.assertEqual([r["id_solicitud"] for r in clean], ["1"])
            self.assertEqual(counts["filas excluidas por datos de latencia inválidos o ausentes"], 2)
            self.assertEqual(counts["latencia_ms: inferior a red más GPU, fuera del redondeo"], 1)


if __name__ == "__main__":
    unittest.main()
