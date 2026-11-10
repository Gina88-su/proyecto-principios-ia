# Caso B. El juego del explorador

Fase 2 del proyecto integrador de Inteligencia Artificial I (Universidad Militar Nueva Granada, Grupo A). El Rover-X planea una ruta en una rejilla de 8 × 8 con diez celdas bloqueadas: sale de (0, 0) y debe llegar a (7, 7) sin pisar un bloqueo. El programa compara búsqueda en anchura (BFS), búsqueda en profundidad (DFS) y A* con distancia de Manhattan.

El documento para entregar es `Actividad 2.docx`, diligenciado sobre la plantilla de la actividad. El PDF `Actividad2_Fase2_CasoB.pdf` es una copia de lectura del mismo trabajo.

## Cómo correrlo

Hace falta Python 3.12. Las búsquedas salen de `aima.search`. Numpy entra porque `utils.py` de AIMA lo importa; el benchmark no usa otro paquete.

```bash
python main.py
python -m unittest discover -s tests -v
```

`python main.py` imprime el mapa, los nodos expandidos, el tiempo medio, el costo y si el camino es óptimo.

## Cómo regenerar el informe

```bash
pip install -r requirements.txt
python informe/llenar_docx.py
python informe/generar_pdf.py
```

`llenar_docx.py` vuelve a escribir `Actividad 2.docx` con los números de una corrida nueva. Antes de subirlo a la plataforma, sustituye el enlace pendiente por la URL pública de GitHub o GitLab, en la primera tabla del documento y en `ENLACE_REPOSITORIO` dentro de `informe/generar_pdf.py`.

## Qué hay en cada archivo

- `aima/`: la base AIMA-Python 4.0.0, sin cambios. Entran `search.py` y `utils.py`, con licencia MIT. De ahí salen `Problem`, `Node`, `breadth_first_graph_search`, `depth_first_graph_search`, `astar_search` e `InstrumentedProblem`.
- `src/grid_problem.py`: la clase `ExplorerGridProblem`, con el mapa, las cuatro acciones y la Manhattan.
- `src/benchmark_runner.py`: llama a las búsquedas de AIMA y arma la tabla.
- `tests/test_heuristics.py`: pruebas de admisibilidad, consistencia y optimalidad.

Si ya tienes otra copia de AIMA-Python 4 y su carpeta `aima` está en el `PYTHONPATH` antes que esta, se usa esa. La incluida aquí es la misma base, recortada a los dos módulos que el caso necesita, para no arrastrar TensorFlow ni Jupyter.
