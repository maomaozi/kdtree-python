import numpy as np


class Vec2:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def clone(self):
        return Vec2(self.x, self.y)

    def __getitem__(self, i: int):
        if i == 0:
            return self.x
        return self.y

    def __setitem__(self, i: int, value):
        if i == 0:
            self.x = value
        else:
            self.y = value


class AaBb:
    def __init__(self, top_left: Vec2, down_right: Vec2):
        self._top_left = top_left
        self._down_right = down_right

    @property
    def top_left(self):
        return self._top_left

    @property
    def down_right(self):
        return self._down_right

    def point_intersection(self, point: Vec2):
        return self._top_left.x < point.x <= self._down_right.x and self._top_left.y < point.y <= self._down_right.y

    def intersection(self, box):
        return self.point_intersection(box.top_left) \
               or self.point_intersection(box.down_right) \
               or box.point_intersection(self.top_left) \
               or box.point_intersection(self._down_right)

    def split(self, value, axis: int):
        new_down_right = self._down_right.clone()
        new_down_right[axis] = value

        new_top_left = self._top_left.clone()
        new_top_left[axis] = value

        return AaBb(self._top_left, new_down_right), AaBb(new_top_left, self._down_right)


class KdTree:
    def __init__(self, box: AaBb, split_threshold: int = 10, depth: int = 0, max_depth: int = 8):
        self._depth = depth
        self._max_depth = max_depth

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
            return False

        if self.is_leaf():
            # 若是叶子节点
            self._values.append(box)
            if len(self._values) > self.split_threshold and self._depth < self._max_depth:
                # 检查是否需要分裂
                self._split()
        else:
            # 如果有子节点，尝试在左右两个子节点插入
            self._insert_to_child(box)

        return True

    def query(self, x, y):
        pass

    def _intersection(self, point: Vec2, direct: Vec2):
        t_min = 0
        t_max = 999999999.0
        for i in range(2):
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

    def ray_intersection(self, point: Vec2, direct: Vec2):
        if self._intersection(point, direct):
            if self.is_leaf():
                return [self._box]
            return self._l_child.ray_intersection(point, direct) + self._r_child.ray_intersection(point, direct)
        return []

    def possible_values(self, point: Vec2, direct: Vec2):
        if self._intersection(point, direct):
            if self.is_leaf():
                return self._values
            return self._l_child.possible_values(point, direct) + self._r_child.possible_values(point, direct)
        return []

    def _split(self):
        x_pos = list(map(lambda it: it.top_left[0], self._values))
        y_pos = list(map(lambda it: it.top_left[1], self._values))

        # 按照方差大的维度划分
        if np.var(x_pos) > np.var(y_pos):
            # 按-中位数-（平均数似乎在某些场景更合理）选取划分点
            new_box1, new_box2 = self._box.split(int(np.mean(x_pos)), 0)
        else:
            new_box1, new_box2 = self._box.split(int(np.mean(y_pos)), 1)

        self._l_child = KdTree(new_box1, self.split_threshold, self._depth + 1, self._max_depth)
        self._r_child = KdTree(new_box2, self.split_threshold, self._depth + 1, self._max_depth)

        for item in self._values:
            self._insert_to_child(item)
        self._values = []

    def _insert_to_child(self, point):
        # 尝试在两个子树上插入
        self._l_child.insert(point)
        self._r_child.insert(point)


if __name__ == '__main__':
    tree = KdTree(AaBb(Vec2(0, 0), Vec2(100, 100)))

    tree.insert(AaBb(Vec2(10, 10), Vec2(15, 15)))
    tree.insert(AaBb(Vec2(20, 10), Vec2(25, 15)))
    tree.insert(AaBb(Vec2(60, 10), Vec2(65, 15)))
    tree.insert(AaBb(Vec2(15, 30), Vec2(20, 35)))
    tree.insert(AaBb(Vec2(55, 80), Vec2(60, 85)))
    tree.insert(AaBb(Vec2(35, 50), Vec2(40, 55)))
    tree.insert(AaBb(Vec2(50, 50), Vec2(55, 55)))
    tree.insert(AaBb(Vec2(20, 90), Vec2(25, 95)))
    tree.insert(AaBb(Vec2(20, 80), Vec2(25, 85)))
    tree.insert(AaBb(Vec2(30, 10), Vec2(35, 15)))

    box1 = AaBb(Vec2(20, 20), Vec2(50, 50))
    box2 = AaBb(Vec2(10, 10), Vec2(25, 25))
    box3 = AaBb(Vec2(30, 30), Vec2(40, 40))

    print(box1.intersection(box2))
    print(box2.intersection(box1))
    print(box1.intersection(box3))
    print(box3.intersection(box1))
    print(box2.intersection(box3))
    print(box3.intersection(box2))
