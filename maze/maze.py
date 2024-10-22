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

class Maze():
    FLOOR   = 0
    BLOCK   = 1
    CURRENT = 2
    NEW     = 3

    UP    = 0
    LEFT  = 1
    RIGHT = 2
    DOWN  = 3
    NONE  = 4

    def __init__(self, width : int, height : int):
        super().__init__()
        # 最低5以上の奇数
        if width % 2 == 0:
            width += 1
        if width < 5:
            width = 5
        if height % 2 == 0:
            height += 1
        if height < 5:
            height = 5
        self.width = width
        self.height = height
        self.map = [[0 for i in range(height)] for j in range(width)]
        self._step    = 0
        self._steps   = []
        self._substep = 0
        self.clear()

    def clear(self):
        for x, y in product(range(self.width), range(self.height)):
            if x == 0 or x == self.width-1 or y == 0 or y == self.height-1:
                self.map[x][y] = Maze.BLOCK
            #elif x % 2 == 0 and y % 2 == 0:
            #    self.map[x][y] = Maze.BLOCK
            else:
                self.map[x][y] = Maze.FLOOR

    def make_method1(self):
        self.prepare_method1()
        while self.next_method1():
            pass

    def prepare_method1(self):
        self.clear()
        self._step    = 0
        self._steps   = []
        self._substep = 0
        for y, x in product(range(self.height), range(self.width)):
            if x > 0 and x < self.width-1 and x % 2 == 0 \
               and y > 0 and y < self.height-1 and y % 2 == 0:
                self._steps.append((x, y))

    def next_method1(self) -> bool:
        if self._step < len(self._steps):
            x, y = self._steps[self._step]
            self._substep += 1
            if self._substep == 1:
                self.map[x][y] = Maze.BLOCK
            elif self._substep == 2:
                while True:
                    if y == 2:
                        dir = randint(Maze.UP, Maze.DOWN)
                        #dir = randint(Maze.UP, Maze.NONE)
                    else:
                        dir = randint(Maze.LEFT, Maze.DOWN)
                        #dir = randint(Maze.LEFT, Maze.NONE)
                    if dir == Maze.UP:
                        chk_x = x
                        chk_y = y-1
                    elif dir == Maze.DOWN:
                        chk_x = x
                        chk_y = y+1
                    elif dir == Maze.LEFT:
                        chk_x = x-1
                        chk_y = y
                    elif dir == Maze.RIGHT:
                        chk_x = x+1
                        chk_y = y
                    else:
                        break
                    if self.map[chk_x][chk_y] == Maze.FLOOR:
                        self.map[chk_x][chk_y] = Maze.BLOCK
                        break
            elif self._substep == 3:
                self.map[x][y] = Maze.BLOCK
                self._step += 1
                self._substep = 0
            return True
        else:
            return False

class MazeGroup(pygame.sprite.Group):

    def __init__(self, maze : Maze, size_x : int, size_y : int, width : int, height : int):
        super().__init__()
        self._maze = maze
        self._maze.prepare_method1()
        self._complate_flag = False
        #self._maze.make_method1()

        for x in range(size_x):
            for y in range(size_y):
                block_size_x = width  // size_x
                block_size_y = height // size_y
                block_pos_x  = block_size_x * x
                block_pos_y  = block_size_y * y
                rect = pygame.Rect(block_pos_x, block_pos_y, block_size_x, block_size_y)
                sprite = MazeSprite(self._maze, x, y, rect)
                self.add(sprite)

    def update(self):
        if not self._maze.next_method1():
            self._complate_flag = True
        super().update()
    
    def is_complate(self):
        return self._complate_flag


class MazeSprite(pygame.sprite.Sprite):

    def __init__(self, maze : Maze, x : int, y : int, rect : pygame.Rect):
        super().__init__()
        self._maze = maze
        self._maze_x = x * 2 + 1
        self._maze_y = y * 2 + 1
        self.rect = rect
        self.image = pygame.Surface((rect.width, rect.height))

    def update(self):
        self.image.fill((255,255,255))
        x = self._maze_x
        y = self._maze_y
        width  = self.rect.width - 0
        height = self.rect.height - 0
        thick_x = width  // 8
        thick_y = height // 8
        self.image.fill((0,0,0), (0,             0,              thick_x, thick_y))
        self.image.fill((0,0,0), (width-thick_x, 0,              thick_x, thick_y))
        self.image.fill((0,0,0), (0,             height-thick_y, thick_x, thick_y))
        self.image.fill((0,0,0), (width-thick_x, height-thick_y, thick_x, thick_y))
        if self._maze.map[x][y-1] == Maze.BLOCK:
            self.image.fill((0,0,0), \
                (thick_x,       0,              width-thick_x*2, thick_y         ))
        if self._maze.map[x-1][y] == Maze.BLOCK:
            self.image.fill((0,0,0), \
                (0,             thick_y,        thick_x,         height-thick_y*2))
        if self._maze.map[x+1][y] == Maze.BLOCK:
            self.image.fill((0,0,0), \
                (width-thick_x, thick_y,        thick_x,         height-thick_y*2))
        if self._maze.map[x][y+1] == Maze.BLOCK:
            self.image.fill((0,0,0), \
                (thick_x,       height-thick_y, width-thick_x*2, thick_y         ))

class MazeGraph():

    def __init__(self, maze : Maze, size_x : int, size_y : int):
        self._maze = maze
        self._size_x = size_x
        self._size_y = size_y
        self.nodes = []
        self.links = []
        for x, y in product(range(size_x), range(size_y)):
            self.nodes.append(MazeNode(x, y))

        for node in self.nodes:
            maze_x = node.x * 2 + 1
            maze_y = node.y * 2 + 1
            # UP
            node_nextto = MazeNode(-1, -1) # dummy
            if self._maze.map[maze_x][maze_y-1] == Maze.FLOOR:
                node_nextto = self._find_node(node.x, node.y-1)
            if node_nextto.link[Maze.DOWN] is None:
                self.links.append(MazeLink(node_nextto, Maze.UP, node, Maze.DOWN))
            # LEFT
            node_nextto = MazeNode(-1, -1) # dummy
            if self._maze.map[maze_x-1][maze_y] == Maze.FLOOR:
                node_nextto = self._find_node(node.x-1, node.y)
            if node_nextto.link[Maze.RIGHT] is None:
                self.links.append(MazeLink(node_nextto, Maze.LEFT, node, Maze.RIGHT))
            # RIGHT
            node_nextto = MazeNode(-1, -1) # dummy
            if self._maze.map[maze_x+1][maze_y] == Maze.FLOOR:
                node_nextto = self._find_node(node.x+1, node.y)
            if node_nextto.link[Maze.LEFT] is None:
                self.links.append(MazeLink(node, Maze.LEFT, node_nextto, Maze.RIGHT))
            # DOWN
            node_nextto = MazeNode(-1, -1) # dummy
            if self._maze.map[maze_x][maze_y+1] == Maze.FLOOR:
                node_nextto = self._find_node(node.x, node.y+1)
            if node_nextto.link[Maze.UP] is None:
                self.links.append(MazeLink(node, Maze.UP, node_nextto, Maze.DOWN))

    def _find_node(self, x : int, y : int):
        ret = None
        for node in self.nodes:
            if node.x == x and node.y == y:
                ret = node
                break
        return ret

class MazeNode():
    UP    = 0
    LEFT  = 1
    RIGHT = 2
    DOWN  = 3
    UNDETERMINED = 0
    TENTATIVE    = 1
    DETERMINED   = 2

    def __init__(self, x : int, y : int):
        self.x        = x
        self.y        = y
        self.link     = [None for x in range(4)]
        self.distance = 0
        self.state    = MazeNode.UNDETERMINED


class MazeLink():

    def __init__(self, node1, dir1 : int, node2, dir2 : int):
        if node1.x == -1 and node1.y == -1 or node2.x == -1 and node2.y == -1:
            self.weight = -1
        else:
            self.weight = 1

        self.link = [None for x in range(4)]
        if dir1 == Maze.UP:
            self.link[Maze.UP]     = node1
            node1.link[Maze.DOWN]  = self
        elif dir1 == Maze.LEFT:
            self.link[Maze.LEFT]   = node1
            node1.link[Maze.RIGHT] = self
        elif dir1 == Maze.RIGHT:
            self.link[Maze.RIGHT]  = node1
            node1.link[Maze.LEFT]  = self
        elif dir1 == Maze.DOWN:
            self.link[Maze.DOWN]   = node1
            node1.link[Maze.UP]    = self

        if dir2 == Maze.UP:
            self.link[Maze.UP]     = node2
            node2.link[Maze.DOWN]  = self
        elif dir2 == Maze.LEFT:
            self.link[Maze.LEFT]   = node2
            node2.link[Maze.RIGHT] = self
        elif dir2 == Maze.RIGHT:
            self.link[Maze.RIGHT]  = node2
            node2.link[Maze.LEFT]  = self
        elif dir2 == Maze.DOWN:
            self.link[Maze.DOWN]   = node2
            node2.link[Maze.UP]    = self

class GraphGroup(pygame.sprite.Group):

    def __init__(self, graph : MazeGraph, size_x : int, size_y : int, width : int, height : int):
        super().__init__()
        self._graph = graph

        for node in graph.nodes:
            x = node.x
            y = node.y
            block_size_x = width  // size_x 
            block_size_y = height // size_y
            block_pos_x  = block_size_x * x + block_size_x // 4
            block_pos_y  = block_size_y * y + block_size_y // 4
            rect = pygame.Rect(block_pos_x, block_pos_y, block_size_x//2, block_size_y//2)
            sprite = NodeSprite(node, rect)
            self.add(sprite)

        for node in graph.links:
            sprite = LinkSprite()
            self.add(sprite)

    def update(self):
        super().update()
    

class NodeSprite(pygame.sprite.Sprite):

    def __init__(self, node : MazeNode, rect : pygame.Rect):
        super().__init__()
        self._node = node
        self.rect = rect
        self.image = pygame.Surface((rect.width, rect.height))

    def update(self):
        self.image.fill((255,255,255))

        width  = self.rect.width
        height = self.rect.height
        self.image.fill((0,0,255), (width//8*3, height//8*3, width//8*2, height//8*2))
        if self._node.link[Maze.UP].weight >= 0:
            self.image.fill((255,0,0), (width//8*3, height//8*0, width//8*2, height//8*2))
        if self._node.link[Maze.LEFT].weight >= 0:
            self.image.fill((255,0,0), (width//8*0, height//8*3, width//8*2, height//8*2))
        if self._node.link[Maze.RIGHT].weight >= 0:
            self.image.fill((255,0,0), (width//8*6, height//8*3, width//8*2, height//8*2))
        if self._node.link[Maze.DOWN].weight >= 0:
            self.image.fill((255,0,0), (width//8*3, height//8*6, width//8*2, height//8*2))

class LinkSprite(pygame.sprite.Sprite):

    def __init__(self):
        super().__init__()
        self.rect = (0, 0, 0, 0)
        self.image = pygame.Surface((0, 0))

class MazeGame(Game):
    """MazeGameクラス"""

    SCENE_MAZE  = 0
    SCENE_GRAPH = 1
    SCENE_END   = 2

    def __init__(self, width=800, height=600):
        """初期化"""
        super().__init__(width, height)

        self.scene    = MazeGame.SCENE_MAZE
        self.FPS      = 30
        size_x        = 10
        size_y        = 10
        self._size_x  = size_x
        self._size_y  = size_y
        self._width   = width
        self._height  = height
        self._maze    = Maze(size_x*2+1, size_y*2+1)
        self._mazegrp = MazeGroup(self._maze, size_x, size_y, width, height)
        self._grphgrp = None

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
        #if action_flag == True:
        if self.scene == MazeGame.SCENE_MAZE:
            self._mazegrp.update()
            if self._mazegrp.is_complate() == True:
                scene = MazeGame.SCENE_GRAPH
                self._graph   = MazeGraph(self._maze, self._size_x, self._size_y)
                self._grphgrp = GraphGroup(self._graph, self._size_x, self._size_y, self._width, self._height)
                self._grphgrp.update()



        # 今回描画分をサーフェイスに描画
        self._mazegrp.draw(self.surface)
        if self.scene == MazeGame.SCENE_GRAPH:
            pass
            self._grphgrp.draw(self.surface)


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
