# Árbol de Habilidades: Calistenia y Streetlifting

Aplicación web en Streamlit que representa una progresión de habilidades de calistenia y streetlifting como un **árbol n-ario** y la dibuja de forma interactiva con `streamlit-agraph`.

## Estructura

- `SkillNode`: nodo del árbol (id, nombre, descripción, dificultad, lista de hijos y referencia al padre).
- `SkillTree`: administra la raíz, inserta nodos con `add_node`, busca nodos y ofrece recorridos en preorden (DFS) y por niveles (BFS), ruta desde la raíz, altura, hojas y aristas para el grafo.

Datos de ejemplo (progresión de dominadas):

```
Dominada Estricta
├── Dominada con Lastre
│   └── Dominada a un Brazo
└── Dominada Explosiva
    └── Muscle-up Estricto
```

## Cómo ejecutarlo

```bash
python -m venv .venv
# Windows: .venv\Scripts\activate   |   macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
streamlit run main.py
```

Haz clic en cualquier nodo para ver la descripción del ejercicio, su ruta de progresión y qué habilidades desbloquea. Desde la barra lateral puedes agregar nuevas habilidades al árbol.
