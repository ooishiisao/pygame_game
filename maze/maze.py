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

    def __init__(self, x, y):
        super().__init__()
        # 最低5以上の奇数
        if x % 2 == 0:
            x += 1
        if x < 5:
            x = 5
        if y % 2 == 0:
            y += 1
        if y < 5:
            y = 5
        self.x = x
        self.y = y
        self.maze = [[0 for i in range(y)] for j in range(x)]
        self._step    = 0
        self._steps   = []
        self._substep = 0
        self.clear()

    def clear(self):
        for x, y in product(range(self.x), range(self.y)):
            if x == 0 or x == self.x-1 or y == 0 or y == self.y-1:
                self.maze[x][y] = Maze.BLOCK
            #elif x % 2 == 0 and y % 2 == 0:
            #    self.maze[x][y] = Maze.BLOCK
            else:
                self.maze[x][y] = Maze.FLOOR

    def make_by_lay_pole(self):
        self.prepare_by_lay_pole()
        while self.next_by_lay_pole():
            pass

    def prepare_by_lay_pole(self):
        self.clear()
        self._step    = 0
        self._steps   = []
        self._substep = 0
        for y, x in product(range(self.y), range(self.x)):
            if x > 0 and x < self.x-1 and x % 2 == 0 \
               and y > 0 and y < self.y-1 and y % 2 == 0:
                self._steps.append((x, y))

    def next_by_lay_pole(self):
        if self._step < len(self._steps):
            x, y = self._steps[self._step]
            self._substep += 1
            if self._substep == 1:
                self.maze[x][y] = Maze.BLOCK
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
                    if self.maze[chk_x][chk_y] == Maze.FLOOR:
                        self.maze[chk_x][chk_y] = Maze.BLOCK
                        break
            elif self._substep == 3:
                self.maze[x][y] = Maze.BLOCK
                self._step += 1
                self._substep = 0
            return True
        else:
            return False


class MazeSprite(pygame.sprite.Sprite):

    def __init__(self, maze, width, height):
        super().__init__()
        self._maze = maze
        self._maze_width  = width
        self._maze_height = height
        self.rect = (0, 0, width, height)
        self.image = pygame.Surface((width, height))
        self.image.fill((0,0,0))

    def updatex(self):
        for x, y in product(range(self._maze.x), range(self._maze.y)):
            if self._maze.maze[x][y] == Maze.BLOCK:
                color = (0,0,0)
            elif self._maze.maze[x][y] == Maze.CURRENT:
                color = (255,0,0)
            else:
                color = (255,255,255)
            self.image.fill(color, (x*self._cell_width, y*self._cell_height, self._cell_width, self._cell_height))

    def update(self):
        for x, y in product(range(self._maze.x), range(self._maze.y)):
            if self._maze.maze[x][y] == Maze.BLOCK:
                color = (0,0,0)
            elif self._maze.maze[x][y] == Maze.CURRENT:
                color = (255,0,0)
            else:
                color = (255,255,255)

            left   = self._maze_width  *  (x + x // 2) // (self._maze.x + self._maze.x // 2)
            width  = self._maze_width  + (self._maze.x + (self._maze.x // 2)-1) // (self._maze.x + (self._maze.x // 2))
            top    = self._maze_height *  (y + y // 2) // (self._maze.y + self._maze.y // 2)
            height = self._maze_height + (self._maze.y + (self._maze.y // 2)-1) // (self._maze.y + (self._maze.y // 2))
            self.image.fill(color, (left, top, width, height))

class MazeGame(Game):
    """MazeGameクラス"""

    SCENE_TITLE = 0
    SCENE_GAME  = 1
    SCENE_END   = 2

    def __init__(self, width=800, height=600):
        """初期化"""
        super().__init__(width, height)

        self.FPS    = 30
        self._scene = self.SCENE_TITLE
        self._maze   = Maze(21, 21)
        self._maze.prepare_by_lay_pole()
        #self._maze.make_by_lay_pole()
        
        self._sprite = MazeSprite(self._maze, width, height)
        self._group  = pygame.sprite.Group(self._sprite)

    def on_frame(self):
        """フレーム処理
        Args:
            scene (int) : 0 タイトル / 1 ゲーム / 2 終了
        """
        self._maze.next_by_lay_pole()    

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
