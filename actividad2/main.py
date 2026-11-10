"""Benchmark del Caso B.

Uso:
    python main.py
"""

from src.benchmark_runner import ejecutar, informe_texto


def main() -> None:
    print(informe_texto(ejecutar()))


if __name__ == "__main__":
    main()
