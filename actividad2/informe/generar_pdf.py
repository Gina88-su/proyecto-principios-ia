"""Genera el informe en PDF de la fase 2.

La guía del caso indica el método: abstraer la rejilla, formalizar P,
implementar Problem de AIMA y medir BFS, DFS y A*. El texto es la
solución de la actividad, con las cifras de esta corrida.

Salida: Actividad2_Fase2_CasoB.pdf
Tipografía: Liberation Sans 11 pt, métrica de Arial, interlineado 1,5
y márgenes de 2,54 cm.
"""

from __future__ import annotations

import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))

from fpdf import FPDF
from fpdf.enums import XPos, YPos
from fpdf.fonts import FontFace

from src.benchmark_runner import ejecutar

FUENTES = Path("/usr/share/fonts/truetype/liberation")
SALIDA = RAIZ / "Actividad2_Fase2_CasoB.pdf"

ESTUDIANTES = (
    ("Gina Paola Susatama Molineros", "200595"),
    ("Jaime Alberto Carreño Camacho", "200565"),
)
ENLACE_REPOSITORIO = (
    "Pendiente de la URL pública. El código es este proyecto: python main.py"
)

CODIGO = """\
from aima.search import Problem

class ExplorerGridProblem(Problem):
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
        return (x + dx, y + dy)

    def goal_test(self, state):
        return state == self.goal

    def path_cost(self, c, state1, action, state2):
        return c + 1

    def h(self, node):
        x1, y1 = node.state
        x2, y2 = self.goal
        return abs(x1 - x2) + abs(y1 - y2)
"""


def miles(valor: int) -> str:
    return f"{valor:,}".replace(",", ".")


def coma(valor: float, decimales: int = 3) -> str:
    return f"{valor:.{decimales}f}".replace(".", ",")


def coordenadas(pares) -> str:
    return ", ".join(f"({x}, {y})" for x, y in pares)


class Informe(FPDF):
    def __init__(self):
        super().__init__(format="A4", unit="mm")
        self.add_font("Arial", "", str(FUENTES / "LiberationSans-Regular.ttf"))
        self.add_font("Arial", "B", str(FUENTES / "LiberationSans-Bold.ttf"))
        self.add_font("Arial", "I", str(FUENTES / "LiberationSans-Italic.ttf"))
        self.add_font("Arial", "BI", str(FUENTES / "LiberationSans-BoldItalic.ttf"))
        self.add_font("Mono", "", str(FUENTES / "LiberationMono-Regular.ttf"))
        self.set_margins(25.4, 20, 25.4)
        self.set_auto_page_break(auto=True, margin=16)
        self.alias_nb_pages()

    def footer(self):
        self.set_y(-12)
        self.set_font("Arial", "I", 9)
        self.set_text_color(70, 70, 70)
        self.cell(0, 6, f"{self.page_no()} de {{nb}}", align="C")
        self.set_text_color(0, 0, 0)

    def parrafo(self, texto: str, espacio: float = 1.3) -> None:
        self.set_font("Arial", "", 11)
        self.set_text_color(0, 0, 0)
        self.multi_cell(0, 5.5, texto, align="J", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        self.ln(espacio)

    def seccion(self, texto: str) -> None:
        if self.get_y() > 255:
            self.add_page()
        self.ln(0.4)
        self.set_font("Arial", "B", 12)
        self.multi_cell(0, 6, texto, new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        self.ln(1.0)

    def subseccion(self, texto: str) -> None:
        if self.get_y() > 262:
            self.add_page()
        self.set_font("Arial", "B", 11)
        self.multi_cell(0, 5.4, texto, new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        self.ln(0.6)

    def caption(self, texto: str) -> None:
        self.set_font("Arial", "I", 10)
        self.multi_cell(0, 4.5, texto, align="C", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        self.ln(1.4)

    def mapa(self, filas: list[str]) -> None:
        lado = 5.2
        n = len(filas[0])
        alto = len(filas) * lado + 10
        if self.get_y() + alto > 278:
            self.add_page()
        ancho = n * lado
        x0 = (self.w - ancho) / 2
        y0 = self.get_y()
        relleno = {
            "S": (27, 107, 74),
            "G": (184, 132, 36),
            "#": (45, 45, 48),
            ".": (250, 250, 248),
        }
        tinta = {"S": (255, 255, 255), "G": (255, 255, 255), "#": (255, 255, 255), ".": (90, 90, 90)}
        self.set_font("Arial", "B", 8)
        self.set_draw_color(190, 190, 190)
        for fila, texto in enumerate(filas):
            for columna, simbolo in enumerate(texto):
                x = x0 + columna * lado
                y = y0 + fila * lado
                self.set_fill_color(*relleno[simbolo])
                self.rect(x, y, lado, lado, style="DF")
                self.set_text_color(*tinta[simbolo])
                self.set_xy(x, y + 0.7)
                self.cell(lado, lado - 1, simbolo, align="C", new_x=XPos.RIGHT, new_y=YPos.TOP)
        self.set_text_color(0, 0, 0)
        self.set_y(y0 + len(filas) * lado + 1.3)
        self.caption(
            "Figura 1. Rejilla 8 x 8. S es (0, 0), abajo a la izquierda. G es (7, 7). "
            "La marca # es una celda bloqueada. El eje y crece hacia arriba."
        )

    def codigo(self, texto: str) -> None:
        lineas = texto.strip("\n").split("\n")
        alto_linea = 3.15
        alto = len(lineas) * alto_linea + 2.2
        if self.get_y() + alto > 278:
            self.add_page()
        y = self.get_y()
        self.set_fill_color(244, 244, 242)
        self.rect(self.l_margin, y, self.epw, alto, style="F")
        self.set_font("Mono", "", 7.5)
        self.set_text_color(20, 20, 20)
        self.set_xy(self.l_margin + 1.4, y + 1.0)
        for linea in lineas:
            self.cell(0, alto_linea, linea if linea else " ", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
            self.set_x(self.l_margin + 1.4)
        self.set_text_color(0, 0, 0)
        self.set_y(y + alto + 1.3)

    def tabla(self, filas: list[tuple[str, ...]], anchos: tuple[float, ...]) -> None:
        estilo = FontFace(
            family="Arial",
            emphasis="B",
            size_pt=10,
            color=(255, 255, 255),
            fill_color=(32, 74, 64),
        )
        self.set_font("Arial", "", 10)
        with self.table(
            col_widths=anchos,
            headings_style=estilo,
            line_height=4.7,
            first_row_as_headings=True,
            text_align="LEFT",
            width=sum(anchos),
            align="L",
        ) as tabla:
            for fila in filas:
                renglon = tabla.row()
                for texto in fila:
                    renglon.cell(texto)
        self.ln(1.4)

    def referencia(self, segmentos: list[tuple[str, str]]) -> None:
        sangria = 12.7
        alto = 5.4
        palabras: list[tuple[str, str]] = []
        for texto, estilo in segmentos:
            for trozo in texto.split(" "):
                if trozo:
                    palabras.append((trozo, estilo))
        x_base = self.l_margin
        ancho = self.epw
        y = self.get_y()
        x = x_base
        for indice, (palabra, estilo) in enumerate(palabras):
            self.set_font("Arial", estilo, 11)
            token = palabra + (" " if indice < len(palabras) - 1 else "")
            medida = self.get_string_width(token)
            if x > x_base and x + medida > x_base + ancho:
                y += alto
                x = x_base + sangria
                if y > self.page_break_trigger:
                    self.add_page()
                    y = self.get_y()
                    x = x_base + sangria
            self.set_xy(x, y)
            self.cell(medida, alto, token)
            x += medida
        self.set_y(y + alto + 1.4)


def construir(datos: dict) -> Informe:
    por_nombre = {fila["algoritmo"]: fila for fila in datos["resultados"]}
    bfs, dfs, estrella = por_nombre["BFS"], por_nombre["DFS"], por_nombre["A*"]
    heuristica = datos["heuristica"]
    reduccion = 100 * (1 - estrella["nodos_expandidos"] / bfs["nodos_expandidos"])

    pdf = Informe()
    pdf.add_page()
    pdf.set_font("Arial", "", 10)
    for linea in (
        "Universidad Militar Nueva Granada",
        "Facultad de Estudios a Distancia · Ingeniería Informática",
        "Inteligencia Artificial I · Grupo A · Unidad 2",
    ):
        pdf.multi_cell(0, 4.5, linea, align="C", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.ln(1.2)
    pdf.set_font("Arial", "B", 13)
    pdf.multi_cell(
        0,
        6,
        "Fase 2. Búsqueda en el juego del explorador",
        align="C",
        new_x=XPos.LMARGIN,
        new_y=YPos.NEXT,
    )
    pdf.ln(1)
    pdf.set_font("Arial", "", 11)
    for nombre, codigo in ESTUDIANTES:
        pdf.multi_cell(0, 5, f"{nombre}  ·  {codigo}", align="C", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    for linea in (
        "Caso B: El juego del explorador",
        "Docente: Ing. Oscar Iván Varela Vélez",
    ):
        pdf.multi_cell(0, 5, linea, align="C", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.set_font("Arial", "", 10)
    pdf.multi_cell(0, 4.6, f"Repositorio: {ENLACE_REPOSITORIO}", align="C", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.multi_cell(0, 4.6, "Bogotá D.C., noviembre de 2026", align="C", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.ln(0.8)

    pdf.seccion("1. Espacio de estados")
    pdf.parrafo(
        "En la fase 1 el explorador sensa brisa y destellos y evita hoyos y trampas. "
        "Para planificar la ruta se deja el entorno discreto, estático y determinista: "
        "un solo agente, el mapa de bloqueos conocido y la meta en una celda "
        "(Universidad Militar Nueva Granada [UMNG], 2026). Hoyos y trampas se tratan "
        "igual, como celdas que no se pisan. El estado es la posición (x, y)."
    )
    pdf.parrafo(
        f"La rejilla mide {datos['ancho']} x {datos['alto']}, con diez bloqueos, salida en "
        f"{datos['inicio']} y meta en {datos['meta']}. El eje x crece a la derecha y el eje y "
        "hacia arriba, así que RESULT((x, y), Arriba) = (x, y + 1). "
        f"Los bloqueos son {coordenadas(datos['obstaculos'])}. En este mapa el camino óptimo "
        f"mide {heuristica['h_estrella_inicio']} pasos, la Manhattan del inicio. Hay "
        f"{heuristica['celdas_libres']} celdas libres y todas se alcanzan desde el inicio."
    )
    pdf.mapa(datos["mapa"])
    pdf.parrafo(
        "P = (S, s0, ACTIONS, RESULT, IS-GOAL, c) "
        "(Russell y Norvig, 2010; Lucci y Kopec, 2016). "
        "S = {(x, y) | 0 <= x < 8, 0 <= y < 8} menos los diez bloqueos."
    )
    pdf.tabla(
        [
            ("Componente", "Especificación para la rejilla 8 x 8"),
            ("Estado inicial s0", "(0, 0), la esquina inferior izquierda. La celda no está bloqueada."),
            (
                "ACTIONS(s)",
                "Subconjunto de {Arriba, Abajo, Izquierda, Derecha}. Se descarta el paso que sale "
                "del mapa o cae en un bloqueo.",
            ),
            (
                "RESULT(s, a)",
                "Arriba: (x, y + 1). Abajo: (x, y - 1). Derecha: (x + 1, y). Izquierda: (x - 1, y). "
                "El sucesor es único.",
            ),
            ("IS-GOAL(s)", "Verdadero si y solo si s = (7, 7)."),
            ("Costo c(s, a, s')", "1 por cada movimiento ortogonal. g(n) es el número de pasos."),
        ],
        (38, 121),
    )

    pdf.seccion("2. Implementación")
    pdf.parrafo(
        "ExplorerGridProblem hereda Problem de aima.search e implementa actions, result, "
        "goal_test, path_cost y h (Russell y Norvig, 2010). Las búsquedas son las de "
        "AIMA-Python 4.0.0: breadth_first_graph_search, depth_first_graph_search y "
        "astar_search. BFS usa una cola, DFS una pila y A* una cola de prioridad con "
        "f(n) = g(n) + h(n). DFS apila los hijos en el orden Arriba, Abajo, Izquierda, "
        "Derecha y desapila el último, así que el primer paso que prueba es Derecha."
    )
    pdf.parrafo(
        "Las tres son búsquedas en grafo: un estado ya expandido no vuelve a la frontera. "
        "Sin ese registro, DFS puede alternar entre dos celdas vecinas y no terminar. "
        "InstrumentedProblem cuenta una expansión por cada llamada a actions. La meta no "
        "suma si se reconoce antes de generar sus hijos. Con una heurística consistente, "
        "A* no reabre estados. La clase del problema es esta."
    )
    pdf.codigo(CODIGO)
    pdf.parrafo(
        "Se ejecuta con python main.py. Las pruebas de admisibilidad, consistencia y "
        "optimalidad están en tests/test_heuristics.py."
    )

    pdf.seccion("3. Benchmark")
    pdf.parrafo(
        "Los tres algoritmos parten de (0, 0) y buscan (7, 7) en el mapa de la figura. "
        f"El tiempo es la media de {datos['repeticiones']} ejecuciones en Python 3.12, "
        "con time.perf_counter. Los nodos expandidos no dependen de la máquina. "
        "La tabla corresponde a esta corrida."
    )
    pdf.tabla(
        [
            ("Algoritmo", "Nodos expandidos", "Tiempo (ms)", "Costo g(n)", "Optimalidad"),
            ("BFS", str(bfs["nodos_expandidos"]), coma(bfs["tiempo_ms"]), str(bfs["costo"]), "Sí"),
            ("DFS", str(dfs["nodos_expandidos"]), coma(dfs["tiempo_ms"]), str(dfs["costo"]), "No"),
            ("A*", str(estrella["nodos_expandidos"]), coma(estrella["tiempo_ms"]), str(estrella["costo"]), "Sí"),
        ],
        (28, 38, 32, 28, 33),
    )
    pdf.parrafo(
        f"BFS y A* cuestan {bfs['costo']} pasos, la Manhattan del inicio. DFS llega en "
        f"{dfs['costo']} pasos: la pila entra por la derecha y cierra la meta por un rodeo. "
        f"A* expandió {estrella['nodos_expandidos']} nodos frente a {bfs['nodos_expandidos']} "
        f"de BFS, el {coma(100 * estrella['nodos_expandidos'] / bfs['nodos_expandidos'], 1)} %, "
        f"una reducción del {coma(reduccion, 1)} %. Generó {estrella['nodos_generados']} estados "
        f"y BFS {bfs['nodos_generados']}. En esta máquina A* tardó {coma(estrella['tiempo_ms'])} ms "
        f"y BFS {coma(bfs['tiempo_ms'])} ms. Son fracciones de milisegundo y cambian de una "
        "corrida a otra: el grafo tiene 54 celdas. La comparación estable es la de "
        "expansiones. En este tamaño la frontera cabe en memoria. El costo espacial de BFS "
        "crece como O(b^d) cuando la rejilla es mayor o cuando no se marcan los visitados."
    )

    pdf.seccion("4. Complejidad, admisibilidad y factor efectivo")
    pdf.subseccion("4.1 Notación Big O")
    pdf.parrafo(
        "b es el máximo de sucesores. Aquí b <= 4, porque solo hay cuatro direcciones. "
        f"d = {bfs['costo']} es la profundidad de la solución óptima y coincide con su "
        f"costo. m es la profundidad que puede alcanzar DFS; la meta que encontró está "
        f"a profundidad {dfs['costo']}."
    )
    pdf.parrafo(
        "En el árbol, BFS toma tiempo O(b^d) y espacio O(b^d): la cola guarda la frontera "
        "del nivel en curso (Russell y Norvig, 2010). DFS toma tiempo O(b^m) y espacio "
        "O(b · m). La cota espacial guarda el camino y los hermanos de cada nivel; la "
        "temporal es O(b^m). Si m > d, DFS puede tardar más que BFS y el camino no tiene "
        "por qué ser el corto. Su memoria crece con la profundidad. En esta corrida DFS "
        f"expandió {dfs['nodos_expandidos']} nodos y BFS {bfs['nodos_expandidos']}, con "
        f"costos {dfs['costo']} y {bfs['costo']}."
    )
    pdf.parrafo(
        f"Al buscar en grafo, el techo es el número de celdas libres, "
        f"{heuristica['celdas_libres']}, y no un árbol infinito. BFS terminó en "
        f"{bfs['nodos_expandidos']} expansiones. Sin el conjunto de explorados, DFS puede "
        "no terminar. La poda de A* se escribe O(b^(d - k_h)), donde k_h es el ahorro que "
        "aporta la heurística (UMNG, 2026). Con h = 0 esa reducción se anula y A* coincide "
        f"con la búsqueda de costo uniforme. Con b = 4 y d = {bfs['costo']}, b^d supera "
        "los 200 millones de nodos en el árbol. En el grafo, A* bajó de "
        f"{bfs['nodos_expandidos']} expansiones a {estrella['nodos_expandidos']}."
    )

    pdf.subseccion("4.2 Admisibilidad y consistencia de la Manhattan")
    pdf.parrafo(
        "h(n) = |x - 7| + |y - 7|. Un paso ortogonal cambia una sola coordenada en 1, "
        "así que reduce esa suma en a lo sumo 1. Cualquier camino desde n hasta la meta "
        "tiene al menos h(n) pasos. Los bloqueos quitan atajos; no crean un atajo más "
        "corto que la Manhattan. Por tanto h(n) <= h*(n) en toda celda. Si h sobreestimara, "
        "A* podría descartar el camino de 14 pasos y devolver otro más largo."
    )
    pdf.parrafo(
        "La misma cuenta da la consistencia. En un paso legal, la Manhattan cambia en "
        "exactamente 1. Si el paso acerca a la meta, h(n) = 1 + h(n'). Si la aleja, "
        "h(n) = h(n') - 1, que sigue siendo menor o igual que 1 + h(n'). Se cumple "
        "h(n) <= c(n, a, n') + h(n') con c = 1. Una heurística consistente es admisible, "
        "y el primer g con el que A* cierra un estado ya es óptimo, sin reapertura "
        "(Russell y Norvig, 2010)."
    )
    pdf.parrafo(
        f"Se revisaron las {heuristica['celdas_libres']} celdas libres. h* se obtuvo por "
        f"anchura desde la meta, al revés de las cuatro direcciones. No hubo sobreestimación "
        f"ni arista inconsistente. En el inicio, h = h* = {heuristica['h_inicio']}. La "
        f"holgura media de h* menos h fue {coma(heuristica['holgura_media'], 2)} y la máxima "
        f"fue {heuristica['holgura_max']}: en algunas celdas el camino que falta mide hasta "
        f"{heuristica['holgura_max']} pasos más que la Manhattan. DFS, que no consulta h, termina en "
        f"{dfs['costo']} pasos. Frente al "
        "conteo de coordenadas distintas, "
        "h_ejes = 1 si x difiere de 7, más 1 si y difiere, la Manhattan es mayor o igual "
        f"en las {heuristica['dominadas']} celdas. Las dos son admisibles y la Manhattan "
        "domina a ese conteo: informa más, porque distingue un paso de catorce. Es el mismo "
        "motivo por el que, en el 8-puzzle, la Manhattan domina al número de piezas fuera "
        "de lugar. Si el robot pudiera moverse en diagonal con costo 1, la Manhattan "
        "dejaría de ser admisible: de (0, 0) a (1, 1) un diagonal cuesta 1 y la Manhattan "
        "vale 2. La heurística admisible pasaría a ser la de Chebyshev, max(|dx|, |dy|)."
    )

    pdf.subseccion("4.3 Factor de ramificación efectivo")
    pdf.parrafo(
        "b* cumple 1 + b* + ... + (b*)^d = N, con N los nodos expandidos y d la "
        f"profundidad de la solución hallada. Sale {coma(bfs['b_estrella'], 3)} para BFS, "
        f"{coma(dfs['b_estrella'], 3)} para DFS y {coma(estrella['b_estrella'], 3)} para A*. "
        f"El de A* queda cerca de 1: {estrella['nodos_expandidos']} expansiones para una "
        f"solución de {estrella['costo']} pasos, poco por encima del camino. El de DFS "
        f"también se acerca a 1 y no mide una buena poda, porque su solución cuesta "
        f"{dfs['costo']} pasos. En el grafo, el promedio de sucesores es "
        f"{coma(heuristica['ramificacion_media'], 2)}, por debajo de 4, porque el borde "
        "y los bloqueos quitan direcciones."
    )

    pdf.seccion("5. Lista de verificación")
    pdf.tabla(
        [
            ("Criterio", "Hecho", "Dónde queda", "Puntos"),
            ("Formalización del entorno", "X", "Sección 1, con los componentes de P", "20"),
            ("Código Python ejecutable", "X", "Sección 2 y el paquete src/", "30"),
            ("Benchmark y heurística", "X", "Secciones 3 y 4.2", "30"),
            ("Sustentación Big O", "X", "Sección 4", "20"),
        ],
        (52, 16, 74, 17),
    )

    pdf.seccion("Referencias")
    pdf.referencia(
        [
            ("Lucci, S. y Kopec, D. (2016). ", ""),
            ("Artificial intelligence in the 21st century: A living introduction", "I"),
            (" (2.ª ed.). Mercury Learning and Information.", ""),
        ]
    )
    pdf.referencia(
        [
            ("Russell, S. y Norvig, P. (2010). ", ""),
            ("Artificial intelligence: A modern approach", "I"),
            (" (3.ª ed.). Prentice Hall.", ""),
        ]
    )
    pdf.referencia(
        [
            ("Universidad Militar Nueva Granada. (2026). ", ""),
            ("Caso B: El juego del explorador en mundo de rejilla (N x N)", "I"),
            (" [Material de curso]. Inteligencia Artificial I, Unidad 2, Facultad de Estudios a Distancia.", ""),
        ]
    )
    return pdf


def main() -> None:
    pdf = construir(ejecutar())
    pdf.output(str(SALIDA))
    print(f"Páginas: {pdf.pages_count}")
    print(f"Archivo: {SALIDA}")


if __name__ == "__main__":
    main()
