class Graph:
    """图类，使用邻接表存储，支持DFS遍历"""

    def __init__(self, graph_dict=None):
        """
        初始化图
        :param graph_dict: 可选的初始邻接表，例如 {0: [1, 2], 1: [2], 2: [3]}
        """
        self.graph = graph_dict if graph_dict else {}

    def add_edge(self, u, v):
        """添加有向边 u -> v（可重写为无向图）"""
        if u not in self.graph:
            self.graph[u] = []
        if v not in self.graph:
            self.graph[v] = []
        self.graph[u].append(v)

    def dfs_recursive(self, start, visited=None):
        """
        递归DFS遍历
        :param start: 起始节点
        :param visited: 内部使用的访问集合
        :return: 访问过的节点集合
        """
        if visited is None:
            visited = set()
        visited.add(start)
        print(start, end=' ')  # 访问节点

        for neighbor in self.graph.get(start, []):
            if neighbor not in visited:
                self.dfs_recursive(neighbor, visited)
        return visited

    def dfs_iterative(self, start):
        """
        迭代DFS遍历（使用栈）
        :param start: 起始节点
        :return: 访问过的节点集合
        """
        visited = set()
        stack = [start]

        while stack:
            node = stack.pop()
            if node not in visited:
                visited.add(node)
                print(node, end=' ')  # 访问节点
                # 逆序入栈以保持与递归一致的顺序（可选）
                for neighbor in reversed(self.graph.get(node, [])):
                    if neighbor not in visited:
                        stack.append(neighbor)
        return visited

    def find_path(self, start, target, path=None):
        """
        查找是否存在从start到target的路径（递归DFS）
        :param start: 起始节点
        :param target: 目标节点
        :param path: 当前路径（内部使用）
        :return: 如果存在路径返回True，否则False
        """
        if path is None:
            path = set()
        path.add(start)

        if start == target:
            return True

        for neighbor in self.graph.get(start, []):
            if neighbor not in path:
                if self.find_path(neighbor, target, path):
                    return True
        return False

    def has_cycle(self):
        """
        检测图中是否存在环（适用于有向图）
        :return: 是否存在环
        """
        visited = set()
        rec_stack = set()

        def dfs_cycle(node):
            visited.add(node)
            rec_stack.add(node)
            for neighbor in self.graph.get(node, []):
                if neighbor not in visited:
                    if dfs_cycle(neighbor):
                        return True
                elif neighbor in rec_stack:  # 回溯栈中再次遇到 => 有环
                    return True
            rec_stack.remove(node)
            return False

        for node in self.graph:
            if node not in visited:
                if dfs_cycle(node):
                    return True
        return False