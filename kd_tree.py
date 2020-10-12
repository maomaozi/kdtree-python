import numpy as np


class Vec:
    def __init__(self, dim: int, *values):
        self.dim = dim
        self.values = list(values)

    def clone(self):
        return Vec(self.dim, *self.values)

    def __getitem__(self, i: int):
        return self.values[i]

    def __setitem__(self, i: int, value):
        self.values[i] = value


class AaBb:
    def __init__(self, dim, top_left: Vec, down_right: Vec):
        self._top_left = top_left
        self._down_right = down_right
        self._dim = dim

    @property
    def top_left(self):
        return self._top_left

    @property
    def down_right(self):
        return self._down_right

    def point_intersection(self, point: Vec):
        for i in range(self._dim):
            if not self._top_left[i] < point[i] <= self._down_right[i]:
                return False
        return True

    def intersection(self, box):
        for i in range(self._dim):
            max_d = (box.down_right[i] - box.top_left[i]) / 2 + (self._down_right[i] - self._top_left[i]) / 2
            actual_d = abs((box.down_right[i] + box.top_left[i]) / 2 - (self._down_right[i] + self._top_left[i]) / 2)

            if actual_d > max_d:
                return False

        return True

    def split(self, value, axis: int):
        new_down_right = self._down_right.clone()
        new_down_right[axis] = value

        new_top_left = self._top_left.clone()
        new_top_left[axis] = value

        return AaBb(self._dim, self._top_left, new_down_right), AaBb(self._dim, new_top_left, self._down_right)


class KdTree:
    def __init__(self, box: AaBb, dim: int, split_threshold: int = 10, depth: int = 0, max_depth: int = 8):
        self._depth = depth
        self._max_depth = max_depth

        self.dim = dim

        self._values = []
        self._box = box

        self._l_child: KdTree = None
        self._r_child: KdTree = None

        self.split_threshold = split_threshold

    def walk(self, callback):
        callback(self._values, self._box)
        if self._l_child is not None:
            self._l_child.walk(callback)
        if self._r_child is not None:
            self._r_child.walk(callback)

    def is_leaf(self):
        return self._l_child is None

    def insert(self, box: AaBb):
        # 是否属于当前范围
        if not self._box.intersection(box):
            return
        if self.is_leaf():
            # 若是叶子节点
            self._values.append(box)
            if len(self._values) > self.split_threshold and self._depth < self._max_depth:
                # 检查是否需要分裂
                self._split()
        else:
            # 如果有子节点，尝试在左右两个子节点插入
            self._insert_to_child(box)

    def query(self, x, y):
        pass

    def _intersection(self, point: Vec, direct: Vec):
        t_min = 0
        t_max = 999999999.0
        for i in range(self.dim):
            if abs(direct[i]) < 1e-6 and (direct[i] < self._box.top_left[i] or direct[i] > self._box.down_right[i]):
                # 垂直或水平线在范围之外
                return False

            n = 1.0 / (direct[i] + 1e-5)
            t1 = (self._box.top_left[i] - point[i]) * n
            t2 = (self._box.down_right[i] - point[i]) * n

            if t1 > t2:
                t1, t2 = t2, t1
            if t1 > t_min:
                t_min = t1
            if t2 < t_max:
                t_max = t2
            if t_min > t_max:
                return False
        return True

    def ray_intersection(self, point: Vec, direct: Vec):
        if self._intersection(point, direct):
            if self.is_leaf():
                return [self._box]
            return self._l_child.ray_intersection(point, direct) + self._r_child.ray_intersection(point, direct)
        return []

    def possible_values(self, point: Vec, direct: Vec):
        if self._intersection(point, direct):
            if self.is_leaf():
                return self._values
            return self._l_child.possible_values(point, direct) + self._r_child.possible_values(point, direct)
        return []

    def _split(self):
        max_var = -1
        max_var_axis = -1
        axis_values = []

        for i in range(self.dim):
            # 按-中位数-（平均数似乎在某些场景更合理）选取划分点
            axis_value = list(map(lambda it: it.top_left[i], self._values))
            axis_values.append(axis_value)
            axis_var = np.var(axis_value)

            if axis_var > max_var:
                max_var = axis_var
                max_var_axis = i

        new_box1, new_box2 = self._box.split(int(np.mean(axis_values[max_var_axis])), max_var_axis)
        self._l_child = KdTree(new_box1, self.dim, self.split_threshold, self._depth + 1, self._max_depth)
        self._r_child = KdTree(new_box2, self.dim, self.split_threshold, self._depth + 1, self._max_depth)

        for item in self._values:
            self._insert_to_child(item)
        self._values = []

    def _insert_to_child(self, box: AaBb):
        # 尝试在两个子树上插入
        self._l_child.insert(box)
        self._r_child.insert(box)


if __name__ == '__main__':
    tree = KdTree(AaBb(2, Vec(2, 0, 0), Vec(2, 100, 100)), 2)

    tree.insert(AaBb(2, Vec(2, 10, 10), Vec(2, 15, 15)))
    tree.insert(AaBb(2, Vec(2, 20, 10), Vec(2, 25, 15)))
    tree.insert(AaBb(2, Vec(2, 60, 10), Vec(2, 65, 15)))
    tree.insert(AaBb(2, Vec(2, 15, 30), Vec(2, 20, 35)))
    tree.insert(AaBb(2, Vec(2, 55, 80), Vec(2, 60, 85)))
    tree.insert(AaBb(2, Vec(2, 35, 50), Vec(2, 40, 55)))
    tree.insert(AaBb(2, Vec(2, 50, 50), Vec(2, 55, 55)))
    tree.insert(AaBb(2, Vec(2, 20, 90), Vec(2, 25, 95)))
    tree.insert(AaBb(2, Vec(2, 20, 80), Vec(2, 25, 85)))
    tree.insert(AaBb(2, Vec(2, 30, 10), Vec(2, 35, 15)))

    box1 = AaBb(2, Vec(2, 20, 20), Vec(2, 50, 50))
    box2 = AaBb(2, Vec(2, 10, 10), Vec(2, 25, 25))
    box3 = AaBb(2, Vec(2, 30, 30), Vec(2, 40, 40))

    print(box1.intersection(box2))
    print(box2.intersection(box1))
    print(box1.intersection(box3))
    print(box3.intersection(box1))
    print(box2.intersection(box3))
    print(box3.intersection(box2))
