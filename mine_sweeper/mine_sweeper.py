import sys
from random import randint
from itertools import product
import pygame
from pygame.locals import QUIT, Rect, MOUSEBUTTONDOWN, MOUSEMOTION

class Config:
    path_image_bomb   = "mine_sweeper/block_bomb.png"
    path_image_open   = "mine_sweeper/block_open.png"
    path_image_closed = "mine_sweeper/block_closed.png"
    image_mine : pygame.Surface   = None
    image_open : pygame.Surface   = None
    image_closed : pygame.Surface = None

    board_size_x  = 0
    board_size_y  = 0
    cell_width    = 0
    cell_height   = 0
    screen_width  = 0
    screen_height = 0

    mine_count    = 0

    @classmethod
    def init(cls, x, y, count):
        cls.board_size_x = x
        cls.board_size_y = y
        cls.mine_count = count
    
        cls.image_mine    = pygame.image.load(cls.path_image_bomb)
        cls.image_open    = pygame.image.load(cls.path_image_open)
        cls.image_closed  = pygame.image.load(cls.path_image_closed)

        cls.cell_width    = cls.image_open.get_rect().width
        cls.cell_height   = cls.image_open.get_rect().height
        cls.screen_width  = cls.board_size_x * cls.cell_width
        cls.screen_height = cls.board_size_y * cls.cell_height


class Cell(pygame.sprite.Sprite):
    TYPE_MINE = -1
    TYPE_NONE = 0
    STATE_CLOSED = 0
    STATE_OPEN   = 1
    MARK_OFF = 0
    MARK_ON  = 1

    def __init__(self, x, y):
        super().__init__()

        self.type       = Cell.TYPE_NONE
        self.state_open = Cell.STATE_CLOSED
        self.state_mark = Cell.MARK_OFF

        # image open
        self.image_open = Config.image_open.copy()
        # image closed (normal)
        self.image_closed = Config.image_closed.copy()
        # image closed (mark)
        self.image_closed_mark = Config.image_closed.copy()
        fnt = pygame.font.SysFont(None, 24)
        qmark_image = fnt.render("?", True, (0, 0, 0))
        qmark_rect = qmark_image.get_rect()
        qmark_rect.center = self.image_closed_mark.get_rect().center
        self.image_closed_mark.blit(qmark_image, qmark_rect)

        self.image = self.image_closed
        self.rect = Rect(x * Config.cell_width, y * Config.cell_height, Config.cell_width, Config.cell_height)

    def setMine(self):
        if self.type == Cell.TYPE_MINE:
            return False
        else:
            self.type = Cell.TYPE_MINE
            mine_rect = Config.image_mine.get_rect()
            mine_rect.center = self.image_open.get_rect().center
            self.image_open.blit(Config.image_mine, mine_rect)
            return True

    def setCount(self, count):
        self.type = count
        fnt = pygame.font.SysFont(None, 24)
        number_image = fnt.render("{}".format(count), True, (0, 0, 0))
        number_rect = number_image.get_rect()
        number_rect.center = self.image_open.get_rect().center
        self.image_open.blit(number_image, number_rect)

    def open(self):
        self.state_open = Cell.STATE_OPEN
        if self.type == Cell.TYPE_MINE:
            return Cell.TYPE_MINE
        else:
            return Cell.TYPE_NONE

    def mark(self):
        if self.state_mark == Cell.MARK_OFF:
            self.state_mark = Cell.MARK_ON
        else:
            self.state_mark = Cell.MARK_OFF

    def update(self):
        if self.state_open == Cell.STATE_OPEN:
            self.image = self.image_open
        else:
            if self.state_mark == Cell.MARK_OFF:
                self.image = self.image_closed
            else:
                self.image = self.image_closed_mark


class Board(pygame.sprite.Group):
    OPE_NONE = 0
    OPE_OPEN = 1
    OPE_MARK = 2

    def __init__(self):
        super().__init__()

        #2次元リスト作成
        self.cells = [list() for x in range(Config.board_size_x)]

        #Cellオブジェクト作成（座標設定、グループ追加）
        for x in range(Config.board_size_x):
            for y in range(Config.board_size_y):
                cell = Cell(x, y)
                self.cells[x].append(cell)
                self.add(cell)

        #地雷設置
        count = 0
        while count < Config.mine_count:
            val = randint(0, Config.board_size_x * Config.board_size_y - 1)
            x = val % Config.board_size_x
            y = val // Config.board_size_x
            cell : Cell = self.cells[x][y]
            if cell.setMine():
                print("SET:", x, y)
                count += 1

        #地雷カウンタ計算
        #各セルを巡回
        for x, y in product(range(Config.board_size_x), range(Config.board_size_y)):
            outer : Cell = self.cells[x][y]
            if outer.type != Cell.TYPE_MINE:
                #地雷なしは周りをカウント
                count = 0
                for ix, iy in product((x-1, x, x+1), (y-1, y, y+1)):
                    #print( "X:", x, "Y:", y, "IX:", ix, "IY:", iy)
                    #はみ出しなし
                    if ix >= 0 and ix < Config.board_size_x and iy >= 0 and iy < Config.board_size_y:
                        #地雷をカウント
                        inner : Cell = self.cells[ix][iy]
                        if inner.type == Cell.TYPE_MINE:
                            count += 1
                #カウンタをセット
                outer.setCount(count)

    def open(self, x, y):
        cell : Cell = self.cells[x][y]
        if cell.state_open == Cell.STATE_OPEN:
            #既に暴いている
            return Cell.TYPE_NONE
        if cell.open() == Cell.TYPE_MINE:
            #地雷を踏んだ
            return Cell.TYPE_MINE
        if cell.type == Cell.TYPE_NONE:
            #周りに地雷なし。周りをあけていく。
            for ix, iy in product((x-1, x, x+1), (y-1, y, y+1)):
                if ix == x and iy == y:
                    #自分自身はスキップ
                    continue
                if ix >= 0 and ix < Config.board_size_x and iy >= 0 and iy < Config.board_size_y:
                    #print( "X:", x, "Y:", y, "IX:", ix, "IY:", iy)
                    self.open(ix, iy)

        return Cell.TYPE_NONE

    def update(self, ope, px, py):
        x = int(px // Config.cell_width)
        y = int(py // Config.cell_height)
        if ope == Board.OPE_OPEN:
            result = self.open(x, y)
            if result == Cell.TYPE_MINE:
                #地雷を踏んだ
                print("SSSSSSSSSSSSSSSSS")
        if ope == Board.OPE_MARK:
            self.cells[x][y].mark()

        super().update()

class Controller:
    def __init__(self):
        self.tick = pygame.time.Clock()
        self.font = pygame.font.SysFont(None, 36)
        self.surface = pygame.display.set_mode((Config.screen_width, Config.screen_height))

    @staticmethod
    def clear_callback(surf, rect):
        surf.fill((0, 0, 0), rect)

    def mainloop(self, board : Board):
        self.surface.fill((0, 0, 0))
        xpos = 0
        ypos = 0

        while True:
            ope  = Board.OPE_NONE
            for event in pygame.event.get():
                if event.type == QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type == MOUSEMOTION:
                    xpos, ypos = event.pos
                elif event.type == MOUSEBUTTONDOWN:
                    if(event.button == 1):
                        #LBUTTON
                        ope = Board.OPE_OPEN
                        xpos, ypos = event.pos
                        break
                    elif(event.button == 3):
                        #RBUTTON
                        ope = Board.OPE_MARK
                        xpos, ypos = event.pos
                        break
                    
            board.clear(self.surface, Controller.clear_callback)

            board.update(ope, xpos, ypos)

            board.draw(self.surface)

            pygame.display.update()
            self.tick.tick(10)


def main():
        pygame.init()
        Config.init(16, 16, 48)

        controller = Controller()
        board = Board()

        controller.mainloop(board)

if __name__ == '__main__':
    main()
