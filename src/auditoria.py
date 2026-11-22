"""Auditoría conservadora de la telemetría sin modificar los archivos originales."""

import csv
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "data" / "raw" / "solicitudes.csv"
OUTPUT = ROOT / "outputs" / "A1"
COLUMNS = ["id_solicitud", "t_llegada_s", "tam_kb", "cache_hit", "version",
           "red_ms", "gpu_ms", "latencia_ms", "intentos", "exito"]


def audit():
    OUTPUT.mkdir(parents=True, exist_ok=True)
    with SOURCE.open(encoding="utf-8-sig", newline="") as file:
        reader = csv.DictReader(file)
        if reader.fieldnames != COLUMNS:
            raise ValueError("El esquema del CSV no coincide con el esperado")
        rows = list(reader)
    counts = Counter()
    distinct = []
    seen = set()
    for row in rows:
        signature = tuple(row.items())
        if signature in seen:
            counts["duplicado exacto eliminado"] += 1
        else:
            seen.add(signature)
            distinct.append(row)

    by_id = defaultdict(list)
    for row in distinct:
        by_id[row["id_solicitud"]].append(row)

    clean = []
    for identifier, versions in by_id.items():
        row = versions[0].copy()
        reasons = []
        if len(versions) > 1:
            counts["identificador con registros diferentes"] += 1
            for col in COLUMNS[1:]:
                if len({v[col] for v in versions}) > 1:
                    row[col] = ""
                    reasons.append(f"{col}: valores contradictorios para el mismo identificador")

        def invalidate(col, reason):
            if row[col] != "":
                row[col] = ""
            reasons.append(f"{col}: {reason}")
            counts[f"{col}: {reason}"] += 1

        def number(col):
            if not row[col].strip():
                counts[f"{col}: ausente o contradictorio"] += 1
                return None
            try:
                value = float(row[col])
                if not __import__("math").isfinite(value):
                    raise ValueError
                return value
            except ValueError:
                invalidate(col, "valor no numérico o no finito")
                return None

        time, size, red, gpu, latency = (number(c) for c in
            ("t_llegada_s", "tam_kb", "red_ms", "gpu_ms", "latencia_ms"))
        if time is not None and not 0 <= time <= 1200:
            invalidate("t_llegada_s", "fuera de la ventana de 1200 s")
        if size is not None and size <= 0:
            invalidate("tam_kb", "tamaño no positivo")
        # Grupo aislado: desde 31.221,76 KB; el resto llega hasta 1.776,07 KB.
        # Hay evidencia de escala 1024, pero no se puede probar la unidad original.
        if size is not None and size > 5000:
            invalidate("tam_kb", "tamaño extremo con posible error de escala")
        for col, value in (("red_ms", red), ("gpu_ms", gpu), ("latencia_ms", latency)):
            if value is not None and value < 0:
                invalidate(col, "tiempo negativo")
        if row["cache_hit"] not in {"0", "1"}:
            invalidate("cache_hit", "valor fuera de 0 y 1")
        if row["version"] not in {"A", "B"}:
            invalidate("version", "valor distinto de A o B")
        if row["intentos"] not in {"1", "2", "3"}:
            invalidate("intentos", "fuera de 1 a 3")
        if row["exito"] not in {"0", "1"}:
            invalidate("exito", "valor fuera de 0 y 1")
        if row["cache_hit"] == "1" and row["gpu_ms"] and float(row["gpu_ms"]) != 0:
            invalidate("gpu_ms", "caché con tiempo de GPU distinto de cero")
        if row["cache_hit"] == "0" and row["gpu_ms"] and float(row["gpu_ms"]) <= 0:
            invalidate("gpu_ms", "sin caché con tiempo de GPU no positivo")
        if row["exito"] == "0" and row["intentos"] in {"1", "2"}:
            invalidate("exito", "abandono antes de tres intentos")
            invalidate("intentos", "abandono antes de tres intentos")
        # Tres mediciones redondeadas a centésimas pueden acumular hasta 0,015 ms de error.
        if all(row[c] for c in ("red_ms", "gpu_ms", "latencia_ms")):
            if float(row["latencia_ms"]) + 0.015001 < float(row["red_ms"]) + float(row["gpu_ms"]):
                invalidate("latencia_ms", "inferior a red más GPU, fuera del redondeo")
        row["motivos_auditoria"] = " | ".join(reasons)
        clean.append(row)

    with (OUTPUT / "solicitudes_auditadas.csv").open("w", encoding="utf-8", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=COLUMNS + ["motivos_auditoria"])
        writer.writeheader()
        writer.writerows(clean)
    with (OUTPUT / "resumen_auditoria.csv").open("w", encoding="utf-8", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(["criterio", "cantidad"])
        writer.writerows(sorted(counts.items()))
    print(f"Filas originales: {len(rows)}; solicitudes tras consolidar ID: {len(clean)}")
    for reason, count in sorted(counts.items()):
        print(f"{reason}: {count}")
    return clean, counts


if __name__ == "__main__":
    audit()
