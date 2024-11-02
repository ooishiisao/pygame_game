import sys
from random import randint
from itertools import product
import pygame
from pygame.locals import QUIT, Rect, MOUSEBUTTONDOWN, MOUSEMOTION, KEYDOWN
from game import Game

class Config:
    screen_width  = 0
    screen_height = 0
    x             = 0
    y             = 0


class MazeMap():
    FLOOR = 0
    WALL  = 1

    UP    = 0
    LEFT  = 1
    RIGHT = 2
    DOWN  = 3

    NONE  = 4

    def __init__(self, size_x : int, size_y : int):
        super().__init__()
        # 最低5以上の奇数
        if size_x % 2 == 0:
            size_x += 1
        if size_x < 5:
            size_x = 5
        if size_y % 2 == 0:
            size_y += 1
        if size_y < 5:
            size_y = 5
        self.size_x = size_x
        self.size_y = size_y
        self.map = [[0 for i in range(size_y)] for j in range(size_x)]
        self._step    = 0
        self._steps   = []
        self._substep = 0
        self.clear()

    def clear(self):
        for x, y in product(range(self.size_x), range(self.size_y)):
            if x == 0 or x == self.size_x-1 or y == 0 or y == self.size_y-1:
                self.map[x][y] = MazeMap.WALL
            #elif x % 2 == 0 and y % 2 == 0:
            #    self.map[x][y] = MazeMap.WALL
            else:
                self.map[x][y] = MazeMap.FLOOR

    def get_type(self, pos_x : int, pos_y : int):
        size_x = self.size_x
        size_y = self.size_y
        if pos_x >= 0 and pos_x < size_x and pos_y >= 0 and pos_y < size_y:
            ret = self.map[pos_x][pos_y]
        else:
            ret = MazeMap.WALL
        return ret

    def make_method1(self):
        self.prepare_method1()
        while self.next_method1():
            pass

    def prepare_method1(self):
        self.clear()
        self._step    = 0
        self._steps   = []
        self._substep = 0
        for y, x in product(range(self.size_y), range(self.size_x)):
            if x > 0 and x < self.size_x-1 and x % 2 == 0 \
               and y > 0 and y < self.size_y-1 and y % 2 == 0:
                self._steps.append((x, y))

    def next_method1(self) -> bool:
        if self._step < len(self._steps):
            x, y = self._steps[self._step]
            self._substep += 1
            if self._substep == 1:
                self.map[x][y] = MazeMap.WALL
            elif self._substep == 2:
                while True:
                    if y == 2:
                        dir = randint(MazeMap.UP, MazeMap.DOWN)
                        #dir = randint(MazeMap.UP, MazeMap.NONE)
                    else:
                        dir = randint(MazeMap.LEFT, MazeMap.DOWN)
                        #dir = randint(MazeMap.LEFT, MazeMap.NONE)
                    if dir == MazeMap.UP:
                        chk_x = x
                        chk_y = y-1
                    elif dir == MazeMap.DOWN:
                        chk_x = x
                        chk_y = y+1
                    elif dir == MazeMap.LEFT:
                        chk_x = x-1
                        chk_y = y
                    elif dir == MazeMap.RIGHT:
                        chk_x = x+1
                        chk_y = y
                    else:
                        break
                    if self.map[chk_x][chk_y] == MazeMap.FLOOR:
                        self.map[chk_x][chk_y] = MazeMap.WALL
                        break
            elif self._substep == 3:
                self.map[x][y] = MazeMap.WALL
                self._step += 1
                self._substep = 0
            return True
        else:
            return False

    def is_complete(self) -> bool:
        if self._step < len(self._steps):
            return False
        else:
            return True

    def dump(self):
        for y in range(self.size_y):
            line = ""
            for x in range(self.size_x):
                line += f"{self.map[x][y]} "
            print(f"{y} :{line}")


class MazeGraph():
    UP    = 0
    LEFT  = 1
    RIGHT = 2
    DOWN  = 3

    def __init__(self, map : MazeMap):
        self._map = map
        self.elements = []

        size_x = map.size_x
        size_y = map.size_y

        for x, y in product(range(size_x), range(size_y)):
            if x % 2 == 0 or y % 2 == 0:
                self.elements.append(MazeElement(MazeElement.TYPE_LINK, x, y))
            else:
                self.elements.append(MazeElement(MazeElement.TYPE_NODE, x, y))

    def scan(self):
        for elem in self.elements:
            elem.clear()

        for e in self.elements:
            elem : MazeElement = e
            pos_x = elem.pos_x
            pos_y = elem.pos_y

            if pos_x % 2 == 1 and pos_y % 2 == 1:
                # UP
                elem.set_link(MazeGraph.UP,    self._find_elem(pos_x,   pos_y-1) )
                # LEFT
                elem.set_link(MazeGraph.LEFT,  self._find_elem(pos_x-1, pos_y  ) )
                # RIGHT
                elem.set_link(MazeGraph.RIGHT, self._find_elem(pos_x+1, pos_y  ) )
                # DOWN
                elem.set_link(MazeGraph.DOWN,  self._find_elem(pos_x,   pos_y+1) )

    def _find_elem(self, x : int, y : int):
        ret = None
        for elem in self.elements:
            if elem.pos_x == x and elem.pos_y == y:
                if self._map.map[x][y] == MazeMap.FLOOR:
                    ret = elem
                break
        return ret

    def dump(self):
        for elem in self.elements:
            print("---------------")
            if elem.type == MazeElement.TYPE_NODE:
                print(f"type : NODE")
            else:
                print(f"type : LINK")
            print(f"pos x:{elem.pos_x} y:{elem.pos_y}")
            if elem.link[MazeGraph.UP] is None:
                print(f"link[UP]: None")
            else:
                print(f"link[UP]:   pos {elem.link[MazeGraph.UP].pos_x} {elem.link[MazeGraph.UP].pos_y}")
            if elem.link[MazeGraph.LEFT] is None:
                print(f"link[LEFT]: None")
            else:
                print(f"link[LEFT]:  pos {elem.link[MazeGraph.LEFT].pos_x} {elem.link[MazeGraph.LEFT].pos_y}")
            if elem.link[MazeGraph.RIGHT] is None:
                print(f"link[RIGHT]: None")
            else:
                print(f"link[RIGHT]: pos {elem.link[MazeGraph.RIGHT].pos_x} {elem.link[MazeGraph.RIGHT].pos_y}")
            if elem.link[MazeGraph.DOWN] is None:
                print(f"link[DOWN]: None")
            else:
                print(f"link[DOWN]:  pos {elem.link[MazeGraph.DOWN].pos_x} {elem.link[MazeGraph.DOWN].pos_y}")
            print(f"link_flag : {elem.link_flag}")

class MazeElement():
    TYPE_NODE  = 1
    TYPE_LINK  = 2
    UNDETERMINED = 0
    TENTATIVE    = 1
    DETERMINED   = 2

    def __init__(self, type : int, pos_x : int, pos_y : int):
        self.type      = type
        self.pos_x     = pos_x
        self.pos_y     = pos_y
        self.link      = [None for x in range(4)]
        self.link_flag = False
        self.distance  = 0
        self.state     = MazeElement.UNDETERMINED
    
    def set_link(self, dir : int, elem):
        self.link[dir] = elem
        if elem is not None:
            self.link_flag = True
            if dir == MazeGraph.UP:
                elem.link[MazeGraph.DOWN] = self
            if dir == MazeGraph.LEFT:
                elem.link[MazeGraph.RIGHT] = self
            if dir == MazeGraph.RIGHT:
                elem.link[MazeGraph.LEFT] = self
            if dir == MazeGraph.DOWN:
                elem.link[MazeGraph.UP] = self
            elem.link_flag = True

    def clear(self):
        self.link[MazeGraph.UP]    = None
        self.link[MazeGraph.LEFT]  = None
        self.link[MazeGraph.RIGHT] = None
        self.link[MazeGraph.DOWN]  = None
        self.link_flag = False


class MazeGroup(pygame.sprite.Group):

    def __init__(self, map : MazeMap, graph : MazeGraph, size_x : int, size_y : int, size_px_x : int, size_px_y : int):
        super().__init__()
        self._map = map
        self._map.prepare_method1()
        #self._map.make_method1()

        self._graph = graph

        node_ratio = 70
        link_ratio = 100 - node_ratio
        node_size_px_x = (size_px_x * node_ratio // 100) // (size_x // 2)
        node_size_px_y = (size_px_y * node_ratio // 100) // (size_y // 2)
        link_size_px_x = (size_px_x * link_ratio // 100) // (size_x // 2 + 1)
        link_size_px_y = (size_px_y * link_ratio // 100) // (size_y // 2 + 1)
        unit_size_px_x = link_size_px_x + node_size_px_x
        unit_size_px_y = link_size_px_y + node_size_px_y
        for elem in graph.elements:
            x = elem.pos_x
            y = elem.pos_y
            if x % 2 == 0:
                offset_x    = 0
                area_size_x = link_size_px_x
            else:
                offset_x    = link_size_px_x
                area_size_x = node_size_px_x
            if y % 2 == 0:
                offset_y    = 0
                area_size_y = link_size_px_y
            else:
                offset_y    = link_size_px_y
                area_size_y = node_size_px_y
            area_pos_x = unit_size_px_x * (x // 2) + offset_x
            area_pos_y = unit_size_px_y * (y // 2) + offset_y
            rect = pygame.Rect(area_pos_x, area_pos_y, area_size_x, area_size_y)
            sprite = MazeSprite(elem, x, y, rect)
            self.add(sprite)

    def update(self):
        if not self._map.is_complete():
            self._map.next_method1()
        self._graph.scan()
        #self._map.dump()
        #self._graph.dump()
        super().update()


class MazeSprite(pygame.sprite.Sprite):

    def __init__(self, elem : MazeElement, x : int, y : int, rect : pygame.Rect):
        super().__init__()
        self._elem = elem
        self.rect = rect
        self.image = pygame.Surface((rect.width, rect.height))
        self._font = pygame.font.SysFont(None, rect.height//2)

    def update(self):
        self.image.fill((200,200,200))
        if self._elem.type == MazeElement.TYPE_LINK:
            if self._elem.link_flag == False:
                self.image.fill((0,0,0))
            else:
                if self._elem.link[MazeGraph.UP] is not None:
                    rect = self.rect.scale_by(0.25, 1)
                else:
                    rect = self.rect.scale_by(1, 0.25)
                rect.center = self.image.get_rect().center
                self.image.fill((0,0,0), rect)

        else:
            pygame.draw.circle(self.image, (0,0,0), self.image.get_rect().center, self.rect.height//2.5) 
            image = self._font.render(f"{0}", True, (255,255,255))
            rect  = image.get_rect()
            rect.center = self.image.get_rect().center
            self.image.blit(image, rect)


class MazeGame(Game):
    """MazeGameクラス"""

    SCENE_MAZE  = 0
    SCENE_GRAPH = 1
    SCENE_END   = 2

    def __init__(self, size_px_x=800, size_px_y=800):
        """初期化"""
        super().__init__(size_px_x, size_px_y)

        self.scene      = MazeGame.SCENE_MAZE
        self.FPS        = 30
        apparent_size_x = 10
        apparent_size_y = 10
        size_x          = apparent_size_x*2+1
        size_y          = apparent_size_y*2+1
        self._mazemap   = MazeMap(size_x, size_y)
        self._mazegraph = MazeGraph(self._mazemap)
        self._mazegrp   = MazeGroup(self._mazemap, self._mazegraph, size_x, size_y, size_px_x, size_px_y)

    def on_frame(self):
        """フレーム処理
        """
        scene = self.scene

        # イベント処理
        mouse_x = 0
        mouse_y = 0
        action_flag = False
        for event in pygame.event.get():
            if event.type == MOUSEBUTTONDOWN:
                mouse_x, mouse_y = event.pos
                mouse_button     = event.button
                action_flag      = True
                break

        # オブジェクト更新
        self._mazegrp.update()
        if self.scene == MazeGame.SCENE_MAZE:
            pass

        # 今回描画分をサーフェイスに描画
        self._mazegrp.draw(self.surface)


        return scene



config = Config
config.screen_width  = 600
config.screen_height = 600
config.x             = 11 
config.y             = 11

def main():
    """メイン"""
    # ゲームオブジェクトを作成
    g = MazeGame()
    # メイン処理
    g.run()


if __name__ == '__main__':
    main()
