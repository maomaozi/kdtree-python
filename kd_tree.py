import numpy as np


class Vec2:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __getitem__(self, i: int):
        if i == 0:
            return self.x
        return self.y


class KdTree:
    def __init__(self, top_left: Vec2, down_right: Vec2, split_threshold: int = 5, depth: int = 0, max_depth: int = 8):
        self._depth = depth
        self._max_depth = max_depth

        self._values = []
        self._top_left = top_left
        self._down_right = down_right

        self._l_child: KdTree = None
        self._r_child: KdTree = None

        self.split_threshold = split_threshold

    def walk(self, callback):
        callback(self._values, self._top_left, self._down_right)
        if self._l_child is not None:
            self._l_child.walk(callback)
        if self._r_child is not None:
            self._r_child.walk(callback)

    def is_leaf(self):
        return self._l_child is None

    def insert(self, point: Vec2):
        # 是否属于当前范围
        if not self._is_belong(point):
            return False

        if self.is_leaf():
            # 若是叶子节点
            self._values.append(point)
            if len(self._values) > self.split_threshold and self._depth < self._max_depth:
                # 检查是否需要分裂
                self._split()
        else:
            # 如果有子节点，尝试在左右两个子节点插入
            self._insert_to_child(point)

        return True

    def query(self, x, y):
        pass

    def _intersection(self, point: Vec2, direct: Vec2):
        t_min = 0
        t_max = 999999999.0
        for i in range(2):
            if direct[i] < 1e-6 and (direct[i] < self._top_left[i] or direct[i] > self._down_right[i]):
                # 垂直或水平线在范围之外
                return False

            n = 1.0 / direct[i]
            t1 = (self._top_left[i] - point[i]) * n
            t2 = (self._down_right[i] - point[i]) * n

            if t1 > t2:
                t1, t2 = t2, t1
            if t1 > t_min:
                t_min = t1
            if t2 < t_max:
                t_max = t2
            if t_min > t_max:
                return False
        return True

    def ray_intersection(self, point: Vec2, direct: Vec2):
        if self._intersection(point, direct):
            if self.is_leaf():
                return [(self._top_left, self._down_right)]
            return self._l_child.ray_intersection(point, direct) + self._r_child.ray_intersection(point, direct)
        return []

    def possible_values(self):
        pass

    def _split(self):
        x_pos = list(map(lambda it: it.x, self._values))
        y_pos = list(map(lambda it: it.y, self._values))

        # 按照方差大的维度划分
        if np.var(x_pos) > np.var(y_pos):
            # 按中位数选取划分点
            split_value = int(np.median(x_pos))
            self._l_child = KdTree(self._top_left, Vec2(split_value, self._down_right.y),
                                   self.split_threshold, self._depth + 1, self._max_depth)
            self._r_child = KdTree(Vec2(split_value, self._top_left.y),
                                   self._down_right, self.split_threshold, self._depth + 1, self._max_depth)
        else:
            split_value = int(np.median(y_pos))
            self._l_child = KdTree(self._top_left, Vec2(self._down_right.x, split_value), self.split_threshold)
            self._r_child = KdTree(Vec2(self._top_left.x, split_value), self._down_right, self.split_threshold)

        for item in self._values:
            self._insert_to_child(item)
        self._values = []

    def _insert_to_child(self, point):
        # 尝试在两个子树上插入
        self._l_child.insert(point) or self._r_child.insert(point)

    def _is_belong(self, point):
        return self._top_left.x < point.x <= self._down_right.x and self._top_left.y < point.y <= self._down_right.y


if __name__ == '__main__':
    tree = KdTree(Vec2(0, 0), Vec2(100, 100))

    tree.insert(Vec2(10, 10))
    tree.insert(Vec2(20, 10))
    tree.insert(Vec2(60, 10))
    tree.insert(Vec2(15, 30))
    tree.insert(Vec2(55, 80))
    tree.insert(Vec2(35, 50))
    tree.insert(Vec2(50, 50))
    tree.insert(Vec2(20, 90))
    tree.insert(Vec2(20, 80))
    tree.insert(Vec2(30, 10))

    print(tree)
