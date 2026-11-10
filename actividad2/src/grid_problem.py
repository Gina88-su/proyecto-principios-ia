"""Rejilla N × N del Caso B.

El eje x crece hacia la derecha y el eje y hacia arriba. El inicio es
la esquina inferior izquierda. Arriba suma 1 a y, como en la
formalización del caso: RESULT((x, y), Arriba) = (x, y + 1).
"""

from __future__ import annotations

from aima.search import Node, Problem

ANCHO = 8
ALTO = 8
INICIO = (0, 0)
META = (7, 7)
# Diez celdas bloqueadas. El camino óptimo sigue midiendo 14, la Manhattan
# del inicio, pero varios recovecos quedan fuera de ese camino.
OBSTACULOS = frozenset(
    {
        (0, 2),
        (1, 1),
        (1, 2),
        (2, 4),
        (2, 6),
        (3, 3),
        (4, 2),
        (5, 2),
        (6, 5),
        (6, 7),
    }
)


class ExplorerGridProblem(Problem):
    """Camino ortogonal desde el inicio hasta la celda meta, sin bloqueos."""

    def __init__(
        self,
        initial=INICIO,
        goal=META,
        width=ANCHO,
        height=ALTO,
        obstacles=OBSTACULOS,
    ):
        super().__init__(initial, goal)
        self.width = width
        self.height = height
        self.obstacles = set(obstacles)
        self.directions = {
            "Arriba": (0, 1),
            "Abajo": (0, -1),
            "Izquierda": (-1, 0),
            "Derecha": (1, 0),
        }

    def is_passable(self, cell):
        x, y = cell
        return 0 <= x < self.width and 0 <= y < self.height and cell not in self.obstacles

    def actions(self, state):
        x, y = state
        validas = []
        for action, (dx, dy) in self.directions.items():
            if self.is_passable((x + dx, y + dy)):
                validas.append(action)
        return validas

    def result(self, state, action):
        x, y = state
        dx, dy = self.directions[action]
        siguiente = (x + dx, y + dy)
        if not self.is_passable(siguiente):
            raise ValueError(f"{action} no es aplicable en {state}.")
        return siguiente

    def goal_test(self, state):
        return state == self.goal

    def path_cost(self, cost, state1, action, state2):
        return cost + 1

    def h(self, node):
        """Distancia de Manhattan hasta la meta. Admisible y consistente."""
        estado = node.state if isinstance(node, Node) else node
        x1, y1 = estado
        x2, y2 = self.goal
        return abs(x1 - x2) + abs(y1 - y2)

    def texto(self):
        lineas = []
        for y in range(self.height - 1, -1, -1):
            celdas = []
            for x in range(self.width):
                celda = (x, y)
                if celda == self.initial:
                    celdas.append("S")
                elif celda == self.goal:
                    celdas.append("G")
                elif celda in self.obstacles:
                    celdas.append("#")
                else:
                    celdas.append(".")
            lineas.append("".join(celdas))
        return "\n".join(lineas)
