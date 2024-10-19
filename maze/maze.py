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

    def __init__(self, maze : Maze):
        super().__init__()
        self._maze = maze

    def update(self):
        self._maze.next_method1()
        super().update()

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
        thick_x = width  // 16
        thick_y = height // 16
        self.image.fill((0,0,0), (0,             0,              thick_x, thick_y))
        self.image.fill((0,0,0), (width-thick_x, 0,              thick_x, thick_y))
        self.image.fill((0,0,0), (0,             height-thick_y, thick_x, thick_y))
        self.image.fill((0,0,0), (width-thick_x, height-thick_y, thick_x, thick_y))
        if self._maze.map[x][y-1] == Maze.BLOCK:
            self.image.fill((0,0,0), (0, 0, width, thick_y))
        if self._maze.map[x-1][y] == Maze.BLOCK:
            self.image.fill((0,0,0), (0, 0, thick_x, height))
        if self._maze.map[x+1][y] == Maze.BLOCK:
            self.image.fill((0,0,0), (width-thick_x, 0, thick_x, height))
        if self._maze.map[x][y+1] == Maze.BLOCK:
            self.image.fill((0,0,0), (0, height-thick_y, width, thick_y))

class MazeNode():
    UNDETERMINED = 0
    DETERMINED   = 1

    def __init__(self, x : int, y : int):
        self.x             = x
        self.y             = y
        self.link_to_up    = None
        self.link_to_left  = None
        self.link_to_right = None
        self.link_to_down  = None
        self.distance      = 0xFFFFFFFF
        self.state         = MazeNode.UNDETERMINED

class MazeLink():
    UNDETERMINED = 0
    DETERMINED   = 1

    def __init__(self, x : int, y : int):
        self.x : int = x
        self.y : int = y
        self.weight : int = 1
        self.end1 : MazeNode = None
        self.end2 : MazeNode = None

class MazeSearch():

    def __init__(self, maze : Maze):
        self._maze : Maze = maze
        self._nodes : list[MazeNode] = []
        for x, y in product(range(maze.x), range(maze.y)):
            if x % 2 == 1 and y % 2 == 1:
                self._nodes.append(MazeNode(x, y))

        for node in self._nodes:
            x = node.x
            y = node.y
            # UP
            if self._maze.map[x][y-1] == Maze.FLOOR:
                self.link_to_up = self.find_node(x, y-2)
            # LEFT
            if self._maze.map[x-1][y] == Maze.FLOOR:
                self.link_to_up = self.find_node(x-2, y)
            # RIGHT
            if self._maze.map[x+1][y] == Maze.FLOOR:
                self.link_to_up = self.find_node(x+2, y)
            # DOWN
            if self._maze.map[x][y+1] == Maze.FLOOR:
                self.link_to_up = self.find_node(x, y+2)

    def find_node(self, x : int, y : int):
        ret = None
        for node in self._nodes:
            if node.x == x and node.y == y:
                ret = node
                break
        return ret



class MazeGame(Game):
    """MazeGameクラス"""

    SCENE_TITLE = 0
    SCENE_GAME  = 1
    SCENE_END   = 2

    def __init__(self, width=800, height=600):
        """初期化"""
        super().__init__(width, height)

        self.FPS    = 30
        size_x      = 20
        size_y      = 20
        self._maze  = Maze(size_x*2+1, size_y*2+1)
        self._maze.prepare_method1()
        #self._maze.make_method1()
        
        self._group = MazeGroup(self._maze)
        for x in range(size_x):
            for y in range(size_y):
                block_size_x = width  // size_x
                block_size_y = height // size_y
                block_pos_x  = block_size_x * x
                block_pos_y  = block_size_y * y
                rect = pygame.Rect(block_pos_x, block_pos_y, block_size_x, block_size_y)
                sprite = MazeSprite(self._maze, x, y, rect)
                self._group.add(sprite)

    def on_frame(self):
        """フレーム処理
        Args:
            scene (int) : 0 タイトル / 1 ゲーム / 2 終了
        """
        self._maze.next_method1()    

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
        self._group.update()

        # 今回描画分をサーフェイスに描画
        self._group.draw(self.surface)



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
