"""Parámetros del grupo derivados de las identificaciones del enunciado."""

C1 = 1137978133
C2 = 1141914189
S = C1 + C2
CONFIANZA = {0: 0.90, 1: 0.95, 2: 0.99}[S % 3]
ALPHA = 1 - CONFIANZA
TAU_MS = 180 + 10 * (S % 9)
EPSILON = 0.01 * (1 + S % 3)
CRECIMIENTO = 1.4 + 0.1 * (S % 7)
T1_KB = 80 + 10 * (S % 5)
T2_KB = 400 + 25 * (S % 5)
PREVALENCIA = (4 + S % 6) / 1000
KMAX = 4 + S % 5
R = S % 6
N = 10 + S % 11
