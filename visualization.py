import random
import time

import pygame

from kd_tree import KdTree, Vec2, AaBb


class Renderer:
    def __init__(self, x: int, y: int, scale: int):
        self.bg_color = 0x111111

        self.border = 1
        self.scale = scale
        self.win_sz_x = x * scale + self.border * 2
        self.win_sz_y = y * scale + self.border * 2

        self.screen = pygame.display.set_mode([self.win_sz_x, self.win_sz_y])
        pygame.display.flip()

    def cls(self):
        pygame.draw.rect(self.screen, self.bg_color, (0, 0, self.win_sz_x, self.win_sz_y))

    def draw_line(self, x1, y1, x2, y2, color=0xffffff):
        pygame.draw.aaline(self.screen, color,
                           (x1 * self.scale + self.border, y1 * self.scale + self.border),
                           (x2 * self.scale + self.border, y2 * self.scale + self.border))

    def draw_pixel(self, x, y, color=0xffffff):
        pygame.draw.circle(self.screen, color,
                           (x * self.scale + self.border, y * self.scale + self.border), self.scale, 1)

    def draw_box(self, top_left, down_right, color=0xffffff):
        # pygame.draw.rect(self.screen, color, (
        #     top_left.x * self.scale + self.border, top_left.y * self.scale + self.border,
        #     down_right.x * self.scale + self.border, down_right.y * self.scale + self.border
        # ), 1)
        self.draw_line(top_left.x, top_left.y, down_right.x, top_left.y, color)
        self.draw_line(top_left.x, top_left.y, top_left.x, down_right.y, color)
        self.draw_line(down_right.x, down_right.y, down_right.x, top_left.y, color)
        self.draw_line(down_right.x, down_right.y, top_left.x, down_right.y, color)

    @staticmethod
    def render():
        pygame.display.flip()

    def handel_events(self, click_callback):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                exit()

            if event.type == pygame.MOUSEBUTTONDOWN:
                click_callback(event.pos[0] // self.scale, event.pos[1] // self.scale)


if __name__ == '__main__':
    renderer = Renderer(100, 100, 5)

    tree = KdTree(AaBb(Vec2(0, 0), Vec2(100, 100)))


    def draw_callback(values, box: AaBb):
        for item in values:
            renderer.draw_box(item.top_left, item.down_right, 0x0000ff)
        renderer.draw_box(box.top_left, box.down_right)


    while True:
        renderer.cls()
        ray_point = Vec2(random.randint(0, 50), random.randint(0, 100))
        ray_direct = Vec2(100 - ray_point.x, random.randint(0, 100) - ray_point.y)

        renderer.draw_line(ray_point.x, ray_point.y, ray_point.x + ray_direct.x, ray_point.y + ray_direct.y, 0xff0000)

        tree.walk(draw_callback)

        for box in tree.ray_intersection(ray_point, ray_direct):
            renderer.draw_box(box.top_left, box.down_right, 0xffff00)

        for box in tree.possible_values(ray_point, ray_direct):
            renderer.draw_box(box.top_left, box.down_right, 0x00ff00)

        renderer.render()
        r = random.randint(1, 4)
        renderer.handel_events(lambda x, y: tree.insert(AaBb(Vec2(x - r, y - r), Vec2(x + r, y + r))))
        time.sleep(0.1)
