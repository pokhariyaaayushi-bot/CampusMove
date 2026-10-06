from typing import Dict, List, Optional


class ResourceAllocationGraph:
    def __init__(self):
        self.adj_list: Dict[str, List[str]] = {}

    def add_edge(self, from_node: str, to_node: str):
        if from_node not in self.adj_list:
            self.adj_list[from_node] = []

        if to_node not in self.adj_list:
            self.adj_list[to_node] = []

        self.adj_list[from_node].append(to_node)

    def detect_cycle(self) -> Optional[List[str]]:
        # 0 = WHITE (unvisited)
        # 1 = GRAY (visiting, in current recursion stack)
        # 2 = BLACK (visited and all descendants verified)

        color: Dict[str, int] = {
            node: 0 for node in self.adj_list
        }

        parent: Dict[str, Optional[str]] = {
            node: None for node in self.adj_list
        }

        cycle_path: List[str] = []

        def dfs(node: str) -> bool:
            color[node] = 1  # Mark GRAY (active stack)

            for neighbor in self.adj_list.get(node, []):

                if color.get(neighbor, 0) == 1:
                    # Gray neighbor found => Back-edge => Cycle exists
                    cur = node

                    cycle_path.append(neighbor)

                    while cur != neighbor and cur is not None:
                        cycle_path.append(cur)
                        cur = parent.get(cur)

                    cycle_path.append(neighbor)
                    cycle_path.reverse()

                    return True

                if color.get(neighbor, 0) == 0:
                    parent[neighbor] = node

                    if dfs(neighbor):
                        return True

            color[node] = 2  # Mark BLACK (finished)

            return False

        for node in list(self.adj_list.keys()):
            if color[node] == 0:

                if dfs(node):
                    return cycle_path

        return None


def resolve_deadlock(
    cycle_path: List[str],
    requests: List[Dict]
) -> Optional[Dict]:

    priority_order = {
        "P1": 1,
        "P2": 2,
        "P3": 3
    }

    participating = [
        r for r in requests
        if r.get("request_id") in cycle_path
    ]

    if not participating:
        return requests[0] if requests else None

    # Victim: lowest priority and latest arrival timestamp
    victim = max(
        participating,
        key=lambda r: (
            priority_order.get(
                r.get("priority_level", "P3"),
                99
            ),
            r.get("created_at", "")
        )
    )

    return victim