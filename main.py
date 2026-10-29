"""
Calisthenics & Streetlifting Skill Tree.

A Streamlit web application that models a skill progression as an n-ary
tree (each skill can unlock any number of advanced progressions) and renders
it as an interactive graph with streamlit-agraph.

Run with:
    streamlit run main.py
"""

from __future__ import annotations

from collections import deque
from typing import Dict, Iterator, List, Optional, Tuple

import streamlit as st
from streamlit_agraph import Config, Edge, Node, agraph


# ---------------------------------------------------------------------------
# Data structure layer
# ---------------------------------------------------------------------------
class SkillNode:
    """A single skill in the progression tree (n-ary tree node)."""

    def __init__(
        self,
        node_id: str,
        name: str,
        description: str,
        difficulty: str = "Intermedio",
    ) -> None:
        self.id: str = node_id
        self.name: str = name
        self.description: str = description
        self.difficulty: str = difficulty
        self.children: List[SkillNode] = []
        self.parent: Optional[SkillNode] = None

    def add_child(self, child: SkillNode) -> None:
        """Attach a child node and set its parent reference."""
        child.parent = self
        self.children.append(child)

    def is_leaf(self) -> bool:
        """A leaf skill has no further progressions."""
        return len(self.children) == 0

    def is_root(self) -> bool:
        return self.parent is None

    def __repr__(self) -> str:
        return f"SkillNode(id={self.id!r}, name={self.name!r}, children={len(self.children)})"


class SkillTree:
    """
    N-ary tree that manages skill progressions.

    A dictionary index (id -> node) is kept alongside the tree so lookups are
    O(1); traversal methods (DFS / BFS) walk the actual tree structure.
    """

    def __init__(self, root: SkillNode) -> None:
        self.root: SkillNode = root
        self._index: Dict[str, SkillNode] = {root.id: root}

    # ----- Mutation -------------------------------------------------------
    def add_node(self, parent_id: str, node: SkillNode) -> SkillNode:
        """Insert `node` as a child of the node identified by `parent_id`."""
        if node.id in self._index:
            raise ValueError(f"Duplicate node id: {node.id!r}")
        parent = self.find_node(parent_id)
        if parent is None:
            raise KeyError(f"Parent node not found: {parent_id!r}")
        parent.add_child(node)
        self._index[node.id] = node
        return node

    # ----- Queries --------------------------------------------------------
    def find_node(self, node_id: str) -> Optional[SkillNode]:
        """Return the node with the given id, or None if it does not exist."""
        return self._index.get(node_id)

    def find_node_dfs(self, node_id: str) -> Optional[SkillNode]:
        """Same as find_node but searching the tree itself (O(n) DFS)."""
        for node in self.traverse_preorder():
            if node.id == node_id:
                return node
        return None

    def traverse_preorder(self) -> Iterator[SkillNode]:
        """Iterative depth-first (pre-order) traversal."""
        stack: List[SkillNode] = [self.root]
        while stack:
            node = stack.pop()
            yield node
            # Push children in reverse so the leftmost child is visited first.
            stack.extend(reversed(node.children))

    def traverse_level_order(self) -> Iterator[Tuple[SkillNode, int]]:
        """Breadth-first traversal yielding (node, depth) pairs."""
        queue: deque[Tuple[SkillNode, int]] = deque([(self.root, 0)])
        while queue:
            node, depth = queue.popleft()
            yield node, depth
            for child in node.children:
                queue.append((child, depth + 1))

    def get_depth(self, node_id: str) -> int:
        """Number of edges between the root and the given node."""
        return len(self.get_path_from_root(node_id)) - 1

    def get_path_from_root(self, node_id: str) -> List[SkillNode]:
        """Ordered list of nodes from the root down to `node_id` (prerequisites)."""
        node = self.find_node(node_id)
        if node is None:
            raise KeyError(f"Node not found: {node_id!r}")
        path: List[SkillNode] = []
        while node is not None:
            path.append(node)
            node = node.parent
        return list(reversed(path))

    def get_leaves(self) -> List[SkillNode]:
        return [node for node in self.traverse_preorder() if node.is_leaf()]

    def height(self) -> int:
        """Height of the tree (edges on the longest root-to-leaf path)."""
        return max(depth for _, depth in self.traverse_level_order())

    def size(self) -> int:
        return len(self._index)

    def get_edges(self) -> List[Tuple[str, str]]:
        """List of (parent_id, child_id) pairs for every edge in the tree."""
        return [
            (node.id, child.id)
            for node in self.traverse_preorder()
            for child in node.children
        ]

    def get_all_nodes(self) -> List[SkillNode]:
        return list(self.traverse_preorder())


# ---------------------------------------------------------------------------
# Seed data (UI-facing content is in Spanish)
# ---------------------------------------------------------------------------
def build_default_tree() -> SkillTree:
    """Create the sample pull-up progression tree."""
    root = SkillNode(
        node_id="dominada_estricta",
        name="Dominada Estricta",
        description=(
            "Desde colgado con los brazos completamente extendidos, sube hasta "
            "que la barbilla supere la barra sin balanceo ni impulso de piernas. "
            "Escápulas activas al inicio y control total en la bajada. Es la base "
            "de toda la progresión de tirón: apunta a 10-12 repeticiones limpias "
            "antes de avanzar."
        ),
        difficulty="Principiante",
    )
    tree = SkillTree(root)

    tree.add_node(
        "dominada_estricta",
        SkillNode(
            node_id="dominada_lastre",
            name="Dominada con Lastre",
            description=(
                "Dominada estricta añadiendo peso externo con cinturón de lastre o "
                "chaleco. Es el movimiento de competencia en Streetlifting. Progresa "
                "con cargas pequeñas (2,5-5 kg) y rangos de 3-6 repeticiones, "
                "manteniendo la técnica estricta y la extensión completa abajo."
            ),
            difficulty="Intermedio",
        ),
    )
    tree.add_node(
        "dominada_estricta",
        SkillNode(
            node_id="dominada_explosiva",
            name="Dominada Explosiva",
            description=(
                "Dominada ejecutada con la máxima velocidad posible para llevar el "
                "pecho (o incluso la cadera) a la altura de la barra. Desarrolla la "
                "potencia necesaria para la transición del muscle-up. Trabaja en "
                "series cortas (3-5 reps) priorizando la velocidad sobre el volumen."
            ),
            difficulty="Intermedio",
        ),
    )
    tree.add_node(
        "dominada_explosiva",
        SkillNode(
            node_id="muscle_up_estricto",
            name="Muscle-up Estricto",
            description=(
                "Tirón explosivo seguido de la transición por encima de la barra y "
                "un fondo hasta bloquear los brazos, sin kipping ni balanceo. "
                "Requiere una dominada explosiva sólida, agarre ligeramente falso y "
                "fuerza en fondos en barra recta."
            ),
            difficulty="Avanzado",
        ),
    )
    tree.add_node(
        "dominada_lastre",
        SkillNode(
            node_id="dominada_un_brazo",
            name="Dominada a un Brazo",
            description=(
                "Dominada completa con un solo brazo, desde extensión total hasta "
                "superar la barra con la barbilla. Exige una fuerza relativa "
                "enorme: como referencia, poder hacer una dominada con lastre de "
                "alrededor del 50-60 % del peso corporal. Progresiones útiles: "
                "dominada arquero, asistida con toalla y negativas a un brazo."
            ),
            difficulty="Élite",
        ),
    )
    return tree


# ---------------------------------------------------------------------------
# Presentation layer (Streamlit)
# ---------------------------------------------------------------------------
DIFFICULTY_COLORS: Dict[str, str] = {
    "Principiante": "#4CAF50",
    "Intermedio": "#2196F3",
    "Avanzado": "#FF9800",
    "Élite": "#E53935",
}
DIFFICULTY_LEVELS: List[str] = list(DIFFICULTY_COLORS.keys())


def get_tree() -> SkillTree:
    """Keep a single tree instance per user session."""
    if "skill_tree" not in st.session_state:
        st.session_state.skill_tree = build_default_tree()
    return st.session_state.skill_tree


def build_graph_elements(tree: SkillTree, selected_id: Optional[str]) -> Tuple[List[Node], List[Edge]]:
    """Convert the tree into streamlit-agraph nodes and edges."""
    nodes: List[Node] = []
    for skill in tree.get_all_nodes():
        is_selected = skill.id == selected_id
        nodes.append(
            Node(
                id=skill.id,
                label=skill.name,
                title=f"{skill.name} — {skill.difficulty}",
                size=32 if is_selected else 24,
                color=DIFFICULTY_COLORS.get(skill.difficulty, "#9E9E9E"),
                shape="dot",
                borderWidth=4 if is_selected else 1,
                font={"size": 16, "face": "sans-serif"},
            )
        )
    edges = [
        Edge(source=parent_id, target=child_id, color="#9E9E9E", width=2)
        for parent_id, child_id in tree.get_edges()
    ]
    return nodes, edges


def render_sidebar(tree: SkillTree) -> None:
    """Sidebar with tree stats, legend and a form to add new skills."""
    st.sidebar.header("📊 Estadísticas del árbol")
    col_a, col_b, col_c = st.sidebar.columns(3)
    col_a.metric("Habilidades", tree.size())
    col_b.metric("Altura", tree.height())
    col_c.metric("Hojas", len(tree.get_leaves()))

    st.sidebar.header("🎨 Dificultad")
    for level, color in DIFFICULTY_COLORS.items():
        st.sidebar.markdown(
            f"<span style='color:{color}; font-size:20px;'>●</span> {level}",
            unsafe_allow_html=True,
        )

    st.sidebar.header("➕ Agregar habilidad")
    all_nodes = tree.get_all_nodes()
    with st.sidebar.form("add_skill_form", clear_on_submit=True):
        parent = st.selectbox(
            "Habilidad previa (padre)",
            options=all_nodes,
            format_func=lambda n: n.name,
        )
        name = st.text_input("Nombre de la habilidad")
        description = st.text_area("Descripción")
        difficulty = st.selectbox("Dificultad", DIFFICULTY_LEVELS, index=2)
        submitted = st.form_submit_button("Agregar al árbol")

    if submitted:
        if not name.strip():
            st.sidebar.error("El nombre no puede estar vacío.")
            return
        new_id = _slugify(name)
        if tree.find_node(new_id) is not None:
            st.sidebar.error("Ya existe una habilidad con ese nombre.")
            return
        tree.add_node(
            parent.id,
            SkillNode(new_id, name.strip(), description.strip() or "Sin descripción.", difficulty),
        )
        st.session_state.selected_id = new_id
        st.rerun()

    if st.sidebar.button("🔄 Restaurar árbol de ejemplo"):
        st.session_state.skill_tree = build_default_tree()
        st.session_state.selected_id = None
        st.rerun()


def render_skill_details(tree: SkillTree, node_id: Optional[str]) -> None:
    """Show the description and context of the selected skill."""
    if node_id is None or tree.find_node(node_id) is None:
        st.info("👆 Haz clic en un nodo del árbol para ver la descripción del ejercicio.")
        return

    skill = tree.find_node(node_id)
    color = DIFFICULTY_COLORS.get(skill.difficulty, "#9E9E9E")

    st.subheader(skill.name)
    st.markdown(
        f"<span style='background:{color}; color:white; padding:3px 10px; "
        f"border-radius:12px; font-size:13px;'>{skill.difficulty}</span> "
        f"&nbsp; Nivel {tree.get_depth(skill.id)} del árbol",
        unsafe_allow_html=True,
    )
    st.write("")
    st.write(skill.description)

    path = tree.get_path_from_root(skill.id)
    st.markdown("**🧗 Ruta de progresión**")
    st.markdown(" → ".join(f"**{n.name}**" if n is skill else n.name for n in path))

    st.markdown("**🔓 Desbloquea**")
    if skill.is_leaf():
        st.caption("Habilidad final de esta rama: no tiene progresiones posteriores.")
    else:
        for child in skill.children:
            st.markdown(f"- {child.name} _({child.difficulty})_")


def _slugify(text: str) -> str:
    """Build a simple ASCII id from a display name."""
    replacements = str.maketrans("áéíóúüñÁÉÍÓÚÜÑ", "aeiouunAEIOUUN")
    cleaned = text.strip().lower().translate(replacements)
    return "_".join("".join(c if c.isalnum() else " " for c in cleaned).split())


def main() -> None:
    st.set_page_config(
        page_title="Árbol de Habilidades",
        page_icon="💪",
        layout="wide",
    )
    st.title("💪 Árbol de Habilidades: Calistenia y Streetlifting")
    st.caption(
        "Progresión de dominadas representada como un árbol n-ario: cada habilidad "
        "base puede desbloquear varias progresiones avanzadas."
    )

    tree = get_tree()
    if "selected_id" not in st.session_state:
        st.session_state.selected_id = tree.root.id

    render_sidebar(tree)

    graph_col, detail_col = st.columns([3, 2], gap="large")

    with graph_col:
        nodes, edges = build_graph_elements(tree, st.session_state.selected_id)
        config = Config(
            width=750,
            height=550,
            directed=True,
            physics=False,
            hierarchical=True,
            direction="UD",
            sortMethod="directed",
            levelSeparation=140,
            nodeSpacing=220,
            interaction={"hover": True, "zoomView": True, "dragView": True},
        )
        clicked_id = agraph(nodes=nodes, edges=edges, config=config)
        if clicked_id and clicked_id != st.session_state.selected_id:
            st.session_state.selected_id = clicked_id
            st.rerun()

    with detail_col:
        render_skill_details(tree, st.session_state.selected_id)

    with st.expander("🌳 Recorridos del árbol (estructura de datos)"):
        pre_col, bfs_col = st.columns(2)
        with pre_col:
            st.markdown("**Preorden (DFS)**")
            for i, skill in enumerate(tree.traverse_preorder(), start=1):
                st.markdown(f"{i}. {skill.name}")
        with bfs_col:
            st.markdown("**Por niveles (BFS)**")
            for skill, depth in tree.traverse_level_order():
                st.markdown(f"{'&nbsp;' * 4 * depth}└ Nivel {depth}: {skill.name}", unsafe_allow_html=True)


if __name__ == "__main__":
    main()
