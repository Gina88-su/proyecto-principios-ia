"""Llena la plantilla Actividad 2.docx con la solución del Caso B.

La plantilla conserva tablas, encabezados y cajas. Este script solo
escribe las respuestas y los números de una corrida real.
"""

from __future__ import annotations

import shutil
import sys
from pathlib import Path

from docx import Document
from docx.oxml import OxmlElement
from docx.shared import Pt, RGBColor
from docx.text.paragraph import Paragraph

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))

from src.benchmark_runner import ejecutar  # noqa: E402

PLANTILLA = Path(
    "/home/ubuntu/.cursor/projects/workspace/uploads/Actividad_2_f41a.docx"
)
SALIDA = RAIZ / "Actividad 2.docx"

OSCURO = RGBColor(0x1E, 0x29, 0x3B)
CODIGO = RGBColor(0x33, 0x41, 0x55)


def coma(valor: float, decimales: int = 3) -> str:
    return f"{valor:.{decimales}f}".replace(".", ",")


def escribir(parrafo, texto: str, tamano: float, color: RGBColor, fuente: str | None, negrita: bool = False) -> None:
    run = parrafo.add_run(texto)
    run.bold = negrita
    run.font.size = Pt(tamano)
    run.font.color.rgb = color
    if fuente:
        run.font.name = fuente
    formato = parrafo.paragraph_format
    formato.space_before = Pt(0)
    formato.space_after = Pt(2)
    formato.line_spacing = 1.0


def llenar(
    celda,
    lineas: list[str],
    tamano: float = 10,
    color: RGBColor = OSCURO,
    fuente: str | None = None,
    negrita: bool = False,
) -> None:
    celda._tc.clear_content()
    for linea in lineas:
        parrafo = celda.add_paragraph()
        escribir(parrafo, linea, tamano, color, fuente, negrita)


def insertar_despues(parrafo, texto: str) -> Paragraph:
    nuevo = OxmlElement("w:p")
    parrafo._p.addnext(nuevo)
    creado = Paragraph(nuevo, parrafo._parent)
    escribir(creado, texto, 10.5, OSCURO, None)
    creado.paragraph_format.space_before = Pt(6)
    creado.paragraph_format.space_after = Pt(6)
    return creado


CODIGO_CLASE = """\
from aima.search import Node, Problem

class ExplorerGridProblem(Problem):
    def __init__(self, initial=(0, 0), goal=(7, 7), width=8, height=8, obstacles=None):
        super().__init__(initial, goal)
        self.width = width
        self.height = height
        self.obstacles = set(obstacles or {
            (0, 2), (1, 1), (1, 2), (2, 4), (2, 6),
            (3, 3), (4, 2), (5, 2), (6, 5), (6, 7),
        })
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
        return [
            accion
            for accion, (dx, dy) in self.directions.items()
            if self.is_passable((x + dx, y + dy))
        ]

    def result(self, state, action):
        x, y = state
        dx, dy = self.directions[action]
        return (x + dx, y + dy)

    def goal_test(self, state):
        return state == self.goal

    def path_cost(self, c, state1, action, state2):
        return c + 1

    def h(self, node):
        estado = node.state if isinstance(node, Node) else node
        x1, y1 = estado
        x2, y2 = self.goal
        return abs(x1 - x2) + abs(y1 - y2)
""".rstrip().splitlines()

CODIGO_BUSQUEDA = """\
from aima.search import (
    InstrumentedProblem,
    astar_search,
    breadth_first_graph_search,
    depth_first_graph_search,
)

problema = ExplorerGridProblem()
busquedas = (
    ("BFS", breadth_first_graph_search),
    ("DFS", depth_first_graph_search),
    ("A*", astar_search),
)
for nombre, buscar in busquedas:
    medido = InstrumentedProblem(problema)
    nodo = buscar(medido)
    print(nombre, medido.succs, nodo.path_cost, nodo.solution())
""".rstrip().splitlines()


def main() -> None:
    datos = ejecutar()
    heuristica = datos["heuristica"]
    por_nombre = {fila["algoritmo"]: fila for fila in datos["resultados"]}
    bfs, dfs, estrella = por_nombre["BFS"], por_nombre["DFS"], por_nombre["A*"]
    reduccion = 100 * (1 - estrella["nodos_expandidos"] / bfs["nodos_expandidos"])
    bloqueos = ", ".join(f"({x}, {y})" for x, y in datos["obstaculos"])

    shutil.copyfile(PLANTILLA, SALIDA)
    documento = Document(str(SALIDA))
    tablas = documento.tables

    datos_equipo = tablas[1]
    datos_equipo.rows[0].cells[1].text = ""
    llenar(
        datos_equipo.rows[0].cells[1],
        ["Gina Paola Susatama Molineros", "Jaime Alberto Carreño Camacho"],
    )
    llenar(datos_equipo.rows[1].cells[1], ["200595", "200565"])
    llenar(datos_equipo.rows[3].cells[1], ["Caso B: El juego del explorador"])
    llenar(
        datos_equipo.rows[4].cells[1],
        [
            "Pendiente de la URL pública de GitHub o GitLab.",
            "El código de este proyecto se ejecuta con: python main.py",
        ],
    )

    for parrafo in documento.paragraphs:
        if parrafo.text.startswith("Describa el proceso de abstracción"):
            insertar_despues(
                parrafo,
                "P = {S, s0, ACTIONS, RESULT, GOAL, c}. "
                f"El camino óptimo mide {heuristica['h_estrella_inicio']} pasos, la Manhattan de s0. "
                "Los cinco componentes son los de la tabla.",
            )
            insertar_despues(
                parrafo,
                "En la fase 1 el explorador sensa brisa y destellos y evita "
                "hoyos y trampas. Esas señales sirven para la celda vecina. Para trazar la ruta se "
                "quita la masa del robot, el roce y el viento. Queda un mundo de rejilla discreto, "
                "estático, determinista y de un solo agente: el mapa de bloqueos se conoce y la meta "
                "es una celda. Hoyos y trampas se tratan igual, como celdas que no se pisan. "
                f"El estado es (x, y) en una rejilla de {datos['ancho']} x {datos['alto']}. "
                "S = {(x, y) | 0 <= x < 8, 0 <= y < 8} menos los diez bloqueos "
                f"{{{bloqueos}}}. El eje x crece a la derecha y el eje y hacia arriba. "
                f"Hay {heuristica['celdas_libres']} celdas libres y todas se alcanzan desde el inicio.",
            )
            break

    formal = tablas[2]
    llenar(formal.rows[1].cells[1], ["s0 = (0, 0). Esquina inferior izquierda. La celda no está bloqueada."])
    llenar(
        formal.rows[2].cells[1],
        [
            "ACTIONS(s) es un subconjunto de {Arriba, Abajo, Izquierda, Derecha}.",
            "Se descarta el paso que sale de la rejilla o cae en un bloqueo.",
        ],
    )
    llenar(
        formal.rows[3].cells[1],
        [
            "RESULT(s, a) devuelve un único sucesor.",
            "Arriba: (x, y + 1). Abajo: (x, y - 1). Derecha: (x + 1, y). Izquierda: (x - 1, y).",
        ],
    )
    llenar(formal.rows[4].cells[1], ["IS-GOAL(s) es verdadero si y solo si s = (7, 7)."])
    llenar(
        formal.rows[5].cells[1],
        ["c(s, a, s') = 1 por cada movimiento ortogonal. g(n) es el número de pasos."],
    )

    llenar(
        tablas[3].rows[0].cells[0],
        ["# 1. Clase del problema. ExplorerGridProblem hereda Problem de AIMA. h es la Manhattan."] + CODIGO_CLASE,
        9,
        CODIGO,
        "Courier New",
    )
    llenar(
        tablas[4].rows[0].cells[0],
        ["# 2. Las tres búsquedas salen de aima.search y parten del mismo s0."] + CODIGO_BUSQUEDA,
        9,
        CODIGO,
        "Courier New",
    )

    for parrafo in documento.paragraphs:
        if parrafo.text.startswith("Ejecute su script"):
            insertar_despues(
                parrafo,
                "Se corre BFS, DFS y A* desde (0, 0) hasta (7, 7), sobre el mismo mapa. "
                "El tiempo es la media de 30 ejecuciones. Los nodos no cambian de una máquina a otra.",
            )
            break

    benchmark = tablas[5]
    for fila, resultado in ((1, bfs), (2, dfs), (3, estrella)):
        celdas = benchmark.rows[fila].cells
        llenar(celdas[1], [str(resultado["nodos_expandidos"])])
        llenar(celdas[2], [coma(resultado["tiempo_ms"])])
        llenar(celdas[3], [str(resultado["costo"])])
        llenar(celdas[4], ["Sí" if resultado["optimo"] else "No"])

    llenar(
        tablas[6].rows[0].cells[0],
        [
            "b es el máximo de sucesores. Aquí b <= 4, porque solo hay cuatro direcciones. "
            f"d = {bfs['costo']} es la profundidad de la solución óptima. m es la profundidad "
            f"que puede alcanzar DFS; la meta que encontró está a profundidad {dfs['costo']}.",
            "BFS toma tiempo O(b^d) y espacio O(b^d): la cola guarda la frontera del nivel en curso. "
            "En un espacio grande esa frontera no cabe en memoria. No hace falta recorrer todo el "
            "mapa: basta con que el nivel d no quepa. Por eso la anchura sufre riesgo de desbordamiento "
            "de RAM cuando la rejilla crece o cuando no se marcan los estados visitados.",
            "DFS toma tiempo O(b^m) y espacio O(b*m). La cota espacial guarda el camino y los hermanos "
            "de cada nivel. Si m > d, puede tardar más que BFS y el camino no tiene por qué ser el corto. "
            f"En esta corrida DFS expandió {dfs['nodos_expandidos']} nodos con costo {dfs['costo']}, "
            f"y BFS expandió {bfs['nodos_expandidos']} nodos con costo {bfs['costo']}.",
            "A* se escribe O(b^(d - k_h)), donde k_h es el ahorro que aporta la heurística. Con h = 0 "
            "esa reducción se anula y A* coincide con la búsqueda de costo uniforme. Con b = 4 y "
            f"d = {bfs['costo']}, b^d supera los 200 millones de nodos en el árbol. Al buscar en grafo "
            f"el techo es el número de celdas libres, {heuristica['celdas_libres']}. A* bajó de "
            f"{bfs['nodos_expandidos']} expansiones a {estrella['nodos_expandidos']}.",
        ],
    )
    llenar(
        tablas[7].rows[0].cells[0],
        [
            "h(n) = |x - 7| + |y - 7|. Un paso ortogonal cambia una sola coordenada en 1, así que "
            "reduce esa suma en a lo sumo 1. Cualquier camino desde n hasta la meta tiene al menos "
            "h(n) pasos. Los bloqueos quitan recorridos; no crean un atajo más corto que la Manhattan. "
            "Por tanto h(n) <= h*(n) en toda celda.",
            "La misma cuenta da la consistencia. En un paso legal la Manhattan cambia en exactamente 1, "
            "y se cumple h(n) <= c(n, a, n') + h(n') con c = 1. Una heurística consistente es admisible, "
            "y el primer g con el que A* cierra un estado ya es óptimo, sin reapertura.",
            f"Se revisaron las {heuristica['celdas_libres']} celdas libres. h* se obtuvo por anchura "
            f"desde la meta. No hubo sobreestimación ni arista inconsistente. En el inicio, h = h* = "
            f"{heuristica['h_inicio']}. La holgura media de h* menos h fue {coma(heuristica['holgura_media'], 2)} "
            f"y la máxima fue {heuristica['holgura_max']}.",
            "Si h(n) sobreestimara el costo real, A* podría descartar el camino de 14 pasos y devolver "
            "otro más largo: perdería la garantía de optimalidad. Frente al conteo de coordenadas distintas "
            "(1 si x difiere de 7, más 1 si y difiere), la Manhattan es mayor o igual en las "
            f"{heuristica['dominadas']} celdas y distingue un paso de catorce. Si el robot pudiera "
            "moverse en diagonal con costo 1, la Manhattan dejaría de ser admisible y la heurística "
            "admisible pasaría a ser la de Chebyshev, max(|dx|, |dy|).",
        ],
    )
    llenar(
        tablas[8].rows[0].cells[0],
        [
            "b* cumple 1 + b* + ... + (b*)^d = N, donde N son los nodos expandidos y d la profundidad de la "
            f"solución hallada. Sale {coma(bfs['b_estrella'])} para BFS, {coma(dfs['b_estrella'])} para DFS "
            f"y {coma(estrella['b_estrella'])} para A*.",
            f"A* expandió {estrella['nodos_expandidos']} nodos frente a {bfs['nodos_expandidos']} de BFS, "
            f"el {coma(100 * estrella['nodos_expandidos'] / bfs['nodos_expandidos'], 1)} %, una reducción del "
            f"{coma(reduccion, 1)} %. Generó {estrella['nodos_generados']} estados y BFS "
            f"{bfs['nodos_generados']}. La heurística poda las celdas cuyo f(n) = g(n) + h(n) supera el "
            "costo óptimo, así que no entran a la frontera.",
            f"El b* de DFS también está cerca de 1 y no indica una buena poda: su solución cuesta "
            f"{dfs['costo']} pasos. En el grafo, el promedio de sucesores es "
            f"{coma(heuristica['ramificacion_media'], 2)}, por debajo de 4, porque el borde y los bloqueos "
            "quitan direcciones. Los tiempos son fracciones de milisegundo y cambian de una corrida a otra. "
            "La comparación estable es la de expansiones.",
        ],
    )

    for fila in range(1, 5):
        llenar(tablas[9].rows[fila].cells[1], ["X"], negrita=True)

    documento.save(str(SALIDA))
    print(f"Archivo: {SALIDA}")
    print(
        "BFS",
        bfs["nodos_expandidos"],
        coma(bfs["tiempo_ms"]),
        bfs["costo"],
        "DFS",
        dfs["nodos_expandidos"],
        dfs["costo"],
        "A*",
        estrella["nodos_expandidos"],
        estrella["costo"],
    )


if __name__ == "__main__":
    main()
