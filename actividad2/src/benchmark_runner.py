"""Corre BFS, DFS y A* sobre la rejilla de 8 × 8 del caso."""

from __future__ import annotations

import math
import time
from collections import deque

from aima.search import (
    InstrumentedProblem,
    astar_search,
    breadth_first_graph_search,
    depth_first_graph_search,
)
from src.grid_problem import ExplorerGridProblem

ALGORITMOS = {
    "BFS": breadth_first_graph_search,
    "DFS": depth_first_graph_search,
    "A*": astar_search,
}


def simular(problema: ExplorerGridProblem, acciones: list[str]):
    estado = problema.initial
    for accion in acciones:
        if accion not in problema.actions(estado):
            raise RuntimeError(f"{accion} no es aplicable en {estado}.")
        estado = problema.result(estado, accion)
        if estado in problema.obstacles:
            raise RuntimeError(f"El camino entra en el bloqueo {estado}.")
    if not problema.goal_test(estado):
        raise RuntimeError("El camino no llega a la meta.")
    return estado


def distancias_a_la_meta(problema: ExplorerGridProblem) -> dict[tuple[int, int], int]:
    """h* de cada celda libre: la rejilla no está dirigida."""
    distancia = {problema.goal: 0}
    cola = deque([problema.goal])
    while cola:
        x, y = cola.popleft()
        for dx, dy in problema.directions.values():
            vecino = (x + dx, y + dy)
            if vecino in distancia or not problema.is_passable(vecino):
                continue
            distancia[vecino] = distancia[(x, y)] + 1
            cola.append(vecino)
    return distancia


def evaluar_heuristica(problema: ExplorerGridProblem) -> dict:
    optimo = distancias_a_la_meta(problema)
    if problema.initial not in optimo:
        raise RuntimeError("La meta no es alcanzable desde el inicio.")
    holguras = []
    inconsistencias = 0
    aristas = 0
    dominadas = 0
    for estado, restante in optimo.items():
        estimacion = problema.h(estado)
        if estimacion > restante:
            raise RuntimeError(f"Manhattan sobreestima en {estado}: {estimacion} > {restante}.")
        holguras.append(restante - estimacion)
        ejes = int(estado[0] != problema.goal[0]) + int(estado[1] != problema.goal[1])
        if estimacion >= ejes:
            dominadas += 1
        for accion in problema.actions(estado):
            siguiente = problema.result(estado, accion)
            aristas += 1
            if problema.h(estado) > 1 + problema.h(siguiente):
                inconsistencias += 1
    return {
        "celdas_libres": len(optimo),
        "aristas": aristas,
        "ramificacion_media": aristas / len(optimo),
        "holgura_media": sum(holguras) / len(holguras),
        "holgura_max": max(holguras),
        "inconsistencias": inconsistencias,
        "dominadas": dominadas,
        "h_inicio": problema.h(problema.initial),
        "h_estrella_inicio": optimo[problema.initial],
    }


def factor_efectivo(nodos: int, profundidad: int) -> float:
    if profundidad <= 0:
        return 0.0
    if nodos <= profundidad + 1:
        return 1.0

    def arbol(ramificacion: float) -> float:
        if ramificacion <= 1.0:
            return float(profundidad + 1)
        log_potencia = (profundidad + 1) * math.log(ramificacion)
        if log_potencia > 700:
            return math.inf
        return (math.exp(log_potencia) - 1.0) / (ramificacion - 1.0)

    bajo, alto = 1.0, 2.0
    while arbol(alto) < nodos:
        alto *= 2.0
    for _ in range(80):
        medio = (bajo + alto) / 2
        if arbol(medio) < nodos:
            bajo = medio
        else:
            alto = medio
    return (bajo + alto) / 2


def _una_corrida(funcion, problema):
    """Una búsqueda de AIMA medida con InstrumentedProblem.

    succs cuenta las llamadas a actions: son los nodos expandidos.
    states cuenta las llamadas a result: son los estados generados.
    """
    medido = InstrumentedProblem(problema)
    nodo = funcion(medido)
    if nodo is None:
        raise RuntimeError(f"{funcion.__name__} no encontró la meta.")
    return nodo, medido


def _medir(funcion, problema, repeticiones: int):
    _una_corrida(funcion, problema)
    muestras = []
    ultima = None
    for _ in range(repeticiones):
        inicio = time.perf_counter()
        ultima = _una_corrida(funcion, problema)
        muestras.append((time.perf_counter() - inicio) * 1000)
    return ultima, sum(muestras) / len(muestras)


def ejecutar(repeticiones: int = 30) -> dict:
    problema = ExplorerGridProblem()
    heuristica = evaluar_heuristica(problema)
    filas = []
    crudas = []
    for nombre in ("BFS", "DFS", "A*"):
        (nodo, medido), tiempo = _medir(ALGORITMOS[nombre], problema, repeticiones)
        acciones = nodo.solution()
        simular(problema, acciones)
        crudas.append((nombre, nodo, medido, tiempo, acciones))
    costo_optimo = next(nodo.path_cost for nombre, nodo, _, _, _ in crudas if nombre == "BFS")
    for nombre, nodo, medido, tiempo, acciones in crudas:
        filas.append(
            {
                "algoritmo": nombre,
                "nodos_expandidos": medido.succs,
                "nodos_generados": medido.states,
                "pruebas_meta": medido.goal_tests,
                "tiempo_ms": tiempo,
                "costo": nodo.path_cost,
                "optimo": nodo.path_cost == costo_optimo,
                "b_estrella": factor_efectivo(medido.succs, nodo.path_cost),
                "acciones": acciones,
            }
        )
    return {
        "ancho": problema.width,
        "alto": problema.height,
        "inicio": problema.initial,
        "meta": problema.goal,
        "obstaculos": sorted(problema.obstacles),
        "mapa": problema.texto().splitlines(),
        "orden_acciones": list(problema.directions),
        "repeticiones": repeticiones,
        "heuristica": heuristica,
        "resultados": filas,
    }


def informe_texto(datos: dict) -> str:
    lineas = [
        "Caso B. Rejilla 8 x 8",
        "Mapa (y crece hacia arriba, (0, 0) abajo a la izquierda):",
        *datos["mapa"],
        "",
        f"Inicio: {datos['inicio']}   Meta: {datos['meta']}",
        f"Bloqueos ({len(datos['obstaculos'])}): {datos['obstaculos']}",
        f"Celdas libres alcanzables: {datos['heuristica']['celdas_libres']}",
        (
            "h(inicio) = "
            f"{datos['heuristica']['h_inicio']}, h* = {datos['heuristica']['h_estrella_inicio']}"
        ),
        f"Inconsistencias: {datos['heuristica']['inconsistencias']}",
        "",
        f"{'Algoritmo':<10}{'Nodos':>8}{'Generados':>10}{'ms':>10}{'Costo':>8}{'Óptimo':>8}{'b*':>8}",
    ]
    for fila in datos["resultados"]:
        lineas.append(
            f"{fila['algoritmo']:<10}{fila['nodos_expandidos']:>8}"
            f"{fila['nodos_generados']:>10}{fila['tiempo_ms']:>10.3f}{fila['costo']:>8}"
            f"{('Sí' if fila['optimo'] else 'No'):>8}{fila['b_estrella']:>8.3f}"
        )
    optimo = next(fila for fila in datos["resultados"] if fila["algoritmo"] == "BFS")
    lineas.append("")
    lineas.append("Camino óptimo: " + " → ".join(optimo["acciones"]))
    return "\n".join(lineas)
