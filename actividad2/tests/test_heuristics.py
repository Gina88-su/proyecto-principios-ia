"""Admisibilidad de la Manhattan y optimalidad de BFS y A*."""

from __future__ import annotations

import unittest

from aima.search import (
    InstrumentedProblem,
    Problem,
    astar_search,
    breadth_first_graph_search,
    depth_first_graph_search,
)
from src.benchmark_runner import distancias_a_la_meta, evaluar_heuristica, simular
from src.grid_problem import ANCHO, META, OBSTACULOS, ExplorerGridProblem


class Rejilla(unittest.TestCase):
    def setUp(self) -> None:
        self.problema = ExplorerGridProblem()

    def test_hereda_de_problem_en_aima(self) -> None:
        self.assertIsInstance(self.problema, Problem)

    def test_el_caso_pide_ocho_por_ocho_y_diez_bloqueos(self) -> None:
        self.assertEqual(self.problema.width, 8)
        self.assertEqual(self.problema.height, 8)
        self.assertEqual(len(OBSTACULOS), 10)
        self.assertEqual(self.problema.initial, (0, 0))
        self.assertEqual(self.problema.goal, META)
        self.assertTrue(self.problema.is_passable(self.problema.initial))
        self.assertTrue(self.problema.is_passable(self.problema.goal))

    def test_arriba_aumenta_y(self) -> None:
        self.assertEqual(self.problema.result((0, 0), "Arriba"), (0, 1))
        self.assertEqual(self.problema.result((0, 0), "Derecha"), (1, 0))

    def test_no_hay_accion_hacia_un_bloqueo_ni_fuera_del_mapa(self) -> None:
        for y in range(ANCHO):
            for x in range(ANCHO):
                if not self.problema.is_passable((x, y)):
                    continue
                for accion in self.problema.actions((x, y)):
                    siguiente = self.problema.result((x, y), accion)
                    self.assertTrue(self.problema.is_passable(siguiente))

    def test_manhattan_admisible_consistente_y_dominante(self) -> None:
        reporte = evaluar_heuristica(self.problema)
        self.assertEqual(reporte["inconsistencias"], 0)
        self.assertEqual(reporte["dominadas"], reporte["celdas_libres"])
        self.assertLessEqual(reporte["h_inicio"], reporte["h_estrella_inicio"])
        optimo = distancias_a_la_meta(self.problema)
        for estado, restante in optimo.items():
            ejes = int(estado[0] != META[0]) + int(estado[1] != META[1])
            self.assertGreaterEqual(self.problema.h(estado), ejes)
            self.assertLessEqual(self.problema.h(estado), restante)


class Busquedas(unittest.TestCase):
    def setUp(self) -> None:
        self.problema = ExplorerGridProblem()

    def test_bfs_y_a_estrella_son_optimas_y_dfs_no_mejora_el_costo(self) -> None:
        def correr(funcion):
            medido = InstrumentedProblem(self.problema)
            nodo = funcion(medido)
            return nodo, medido

        bfs, medido_bfs = correr(breadth_first_graph_search)
        dfs, _ = correr(depth_first_graph_search)
        estrella, medido_estrella = correr(astar_search)
        self.assertIsNotNone(bfs)
        self.assertIsNotNone(dfs)
        self.assertIsNotNone(estrella)
        self.assertEqual(bfs.path_cost, self.problema.h(self.problema.initial))
        self.assertEqual(estrella.path_cost, bfs.path_cost)
        self.assertGreaterEqual(dfs.path_cost, bfs.path_cost)
        self.assertLess(medido_estrella.succs, medido_bfs.succs)
        for nodo in (bfs, dfs, estrella):
            self.assertEqual(simular(self.problema, nodo.solution()), self.problema.goal)
            self.assertEqual(len(nodo.solution()), nodo.path_cost)


if __name__ == "__main__":
    unittest.main()
