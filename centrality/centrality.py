import json, random
import igraph as ig
import pandas as pd

# === Вспомогательная функция ===
def extract_local_subgraph(friends_map, start_ids: list[str], depth=2):
    current_level = set(str(x) for x in start_ids)
    visited = set(current_level)

    for _ in range(depth):
        next_level = set()
        for user in current_level:
            if user in friends_map:
                for friend in friends_map[user]:
                    f = str(friend)
                    if f not in visited:
                        next_level.add(f)
        if not next_level:
            break
        visited.update(next_level)
        current_level = next_level

    # Формируем локальный friends_map только для узлов из visited
    local_map = {}
    for user in visited:
        if user in friends_map:
            # Оставляем только друзей, которые тоже в visited
            local_map[user] = [str(f) for f in friends_map[user] if str(f) in visited]
        else:
            local_map[user] = []
    return local_map

# === 1. Загрузка данных ===
def load_data(file_name: str):
    fname = file_name

    try:
        with open(fname, "r", encoding="utf-8") as f:
            friends_map = json.load(f)
    except FileNotFoundError as e:
        print(f"Не удалось открыть файл {e}")
        return None

    return friends_map

# === 2. Построение графа ===
def build_graph(friends_map):
    edges = set()
    vertex = set()

    for user_id, friends in friends_map.items():
        user = str(user_id)
        vertex.add(user)
        for friend_id in friends:
            friend = str(friend_id)
            if user != friend:
                vertex.add(friend)
                edge = tuple(sorted((user, friend)))
                edges.add(edge)

    vertices = list(vertex)
    vertex_to_index = {v: i for i, v in enumerate(vertices)}
    edge_indices = [(vertex_to_index[u], vertex_to_index[v]) for u, v in edges]

    g = ig.Graph(directed=False)
    g.add_vertices(len(vertices))
    g.add_edges(edge_indices)
    g.vs["name"] = vertices

    print(f"Граф: {g.vcount():,} узлов, {g.ecount():,} рёбер")

    if g.vcount() == 0:
        print(f"Граф пуст: friends_map не содержит валидных данных")

    return g

# === 3. Аппроксимация centrality через случайные источники ===
def betweenness_calculation(graph: ig.Graph):
    k = 2000  # число случайных источников
    n_nodes = graph.vcount()

    if k >= n_nodes:
        print("Граф небольшой — считаем точные центральности.")
        betweenness = graph.betweenness()
    else:
        print(f"Аппроксимация betweenness по {k} случайным источникам...")
        random_sources = random.sample(range(n_nodes), k)
        # Считаем centrality, используя ТОЛЬКО пути от random_sources ко всем остальным
        betweenness = graph.betweenness(sources=random_sources, targets=None)
        # Нормализуем: умножаем на (n-1)/(k-1), чтобы оценка была несмещённой
        if k > 1:
            scale = (n_nodes - 1) / (k - 1)
            betweenness = [b * scale for b in betweenness]
        else:
            betweenness = [0.0] * n_nodes

    return betweenness

# === 4. Closeness с cutoff ===
def closeness_calculation(graph: ig.Graph):
    closeness = graph.closeness(cutoff=10)
    return closeness

# === 5. Eigenvector centrality ===
def eigenvector_calculation(graph: ig.Graph):
    # Получаем все компоненты связности
    components = graph.connected_components()
    largest_comp_indices = max(components, key=len)  # список индексов узлов

    # Создаём подграф ТОЛЬКО из крупнейшей компоненты
    graph_largest = graph.subgraph(largest_comp_indices)

    try:
        ev_values = graph_largest.eigenvector_centrality()
    except Exception as e:
        print(f"Ошибка при расчёте eigenvector centrality: {e}")
        ev_values = [1.0 / graph_largest.vcount()] * graph_largest.vcount()

    # Создаём полный список для всех узлов графа g
    eigenvector_full = [0.0] * graph.vcount()
    for local_idx, global_idx in enumerate(largest_comp_indices):
        eigenvector_full[global_idx] = ev_values[local_idx]

    return eigenvector_full

seed_uids = ["258814756", '292134122', "154151541"]

# === 6. Вывод и сохранение ===
def print_result(file_name: str) -> None:
    full_data = load_data(file_name)
    if full_data is None:
        return

    global seed_uids
    local_data = extract_local_subgraph(full_data, seed_uids, depth=1)
    graph = build_graph(local_data)

    if graph.vcount() == 0:
        print("Локальный граф пуст!")
        return

    names = graph.vs["name"]

    def print_top(metric_name, values, top_n=10):
        combined = list(zip(names, values))
        # Фильтруем NaN/inf
        combined = [(n, v) for n, v in combined if pd.notna(v) and abs(v) != float('inf')]
        top = sorted(combined, key=lambda x: x[1], reverse=True)[:top_n]
        print(f"\n--- Топ-{top_n} по {metric_name} ---")
        for node, val in top:
            print(f"Пользователь {node}: {val:.6f}")

    betweenness = betweenness_calculation(graph)
    closeness = closeness_calculation(graph)
    eigenvector = eigenvector_calculation(graph)

    print_top("посредничеству", betweenness)
    print_top("близости", closeness)
    print_top("собственному вектору", eigenvector)

    # Сохранение
    df = pd.DataFrame({
        "user_id": names,
        "centrality": betweenness,
        "closeness": closeness,
        "eigenvector": eigenvector,
    })
    df = df.fillna(0.0).replace([float('inf'), -float('inf')], 0.0)
    df.to_csv("centrality/centrality_results_fast.csv", index=False, encoding="utf-8-sig")

def get_centrality(file_name: str) -> None:
    print_result(file_name)