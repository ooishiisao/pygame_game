import sys
from random import randint
from itertools import product
import pygame
from pygame.locals import QUIT, Rect, MOUSEBUTTONDOWN, MOUSEMOTION, KEYDOWN
from game import Game

class ConfigOld:
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


class CellOld(pygame.sprite.Sprite):
    TYPE_MINE = -1
    TYPE_NONE = 0
    STATE_CLOSED = 0
    STATE_OPEN   = 1
    MARK_OFF = 0
    MARK_ON  = 1

    def __init__(self, x, y):
        super().__init__()

        self.type       = CellOld.TYPE_NONE
        self.state_open = CellOld.STATE_CLOSED
        self.state_mark = CellOld.MARK_OFF

        # image open
        self.image_open = ConfigOld.image_open.copy()
        # image closed (normal)
        self.image_closed = ConfigOld.image_closed.copy()
        # image closed (mark)
        self.image_closed_mark = ConfigOld.image_closed.copy()
        fnt = pygame.font.SysFont(None, 24)
        qmark_image = fnt.render("?", True, (0, 0, 0))
        qmark_rect = qmark_image.get_rect()
        qmark_rect.center = self.image_closed_mark.get_rect().center
        self.image_closed_mark.blit(qmark_image, qmark_rect)

        self.image = self.image_closed
        self.rect = Rect(x * ConfigOld.cell_width, y * ConfigOld.cell_height, ConfigOld.cell_width, ConfigOld.cell_height)

    def setMine(self):
        if self.type == CellOld.TYPE_MINE:
            return False
        else:
            self.type = CellOld.TYPE_MINE
            mine_rect = ConfigOld.image_mine.get_rect()
            mine_rect.center = self.image_open.get_rect().center
            self.image_open.blit(ConfigOld.image_mine, mine_rect)
            return True

    def setCount(self, count):
        self.type = count
        fnt = pygame.font.SysFont(None, 24)
        number_image = fnt.render("{}".format(count), True, (0, 0, 0))
        number_rect = number_image.get_rect()
        number_rect.center = self.image_open.get_rect().center
        self.image_open.blit(number_image, number_rect)

    def open(self):
        self.state_open = CellOld.STATE_OPEN
        if self.type == CellOld.TYPE_MINE:
            return CellOld.TYPE_MINE
        else:
            return CellOld.TYPE_NONE

    def mark(self):
        if self.state_mark == CellOld.MARK_OFF:
            self.state_mark = CellOld.MARK_ON
        else:
            self.state_mark = CellOld.MARK_OFF

    def update(self):
        if self.state_open == CellOld.STATE_OPEN:
            self.image = self.image_open
        else:
            if self.state_mark == CellOld.MARK_OFF:
                self.image = self.image_closed
            else:
                self.image = self.image_closed_mark


class BoardOld(pygame.sprite.Group):
    OPE_NONE = 0
    OPE_OPEN = 1
    OPE_MARK = 2

    def __init__(self):
        super().__init__()

        #2次元リスト作成
        self.cells = [list() for x in range(ConfigOld.board_size_x)]

        #CellOldオブジェクト作成（座標設定、グループ追加）
        for x in range(ConfigOld.board_size_x):
            for y in range(ConfigOld.board_size_y):
                cell = CellOld(x, y)
                self.cells[x].append(cell)
                self.add(cell)

        #地雷設置
        count = 0
        while count < ConfigOld.mine_count:
            val = randint(0, ConfigOld.board_size_x * ConfigOld.board_size_y - 1)
            x = val % ConfigOld.board_size_x
            y = val // ConfigOld.board_size_x
            cell : CellOld = self.cells[x][y]
            if cell.setMine():
                print("SET:", x, y)
                count += 1

        #地雷カウンタ計算
        #各セルを巡回
        for x, y in product(range(ConfigOld.board_size_x), range(ConfigOld.board_size_y)):
            outer : CellOld = self.cells[x][y]
            if outer.type != CellOld.TYPE_MINE:
                #地雷なしは周りをカウント
                count = 0
                for ix, iy in product((x-1, x, x+1), (y-1, y, y+1)):
                    #print( "X:", x, "Y:", y, "IX:", ix, "IY:", iy)
                    #はみ出しなし
                    if ix >= 0 and ix < ConfigOld.board_size_x and iy >= 0 and iy < ConfigOld.board_size_y:
                        #地雷をカウント
                        inner : CellOld = self.cells[ix][iy]
                        if inner.type == CellOld.TYPE_MINE:
                            count += 1
                #カウンタをセット
                outer.setCount(count)

    def open(self, x, y):
        cell : CellOld = self.cells[x][y]
        if cell.state_open == CellOld.STATE_OPEN:
            #既に暴いている
            return CellOld.TYPE_NONE
        if cell.open() == CellOld.TYPE_MINE:
            #地雷を踏んだ
            return CellOld.TYPE_MINE
        if cell.type == CellOld.TYPE_NONE:
            #周りに地雷なし。周りをあけていく。
            for ix, iy in product((x-1, x, x+1), (y-1, y, y+1)):
                if ix == x and iy == y:
                    #自分自身はスキップ
                    continue
                if ix >= 0 and ix < ConfigOld.board_size_x and iy >= 0 and iy < ConfigOld.board_size_y:
                    #print( "X:", x, "Y:", y, "IX:", ix, "IY:", iy)
                    self.open(ix, iy)

        return CellOld.TYPE_NONE

    def update(self, ope, px, py):
        x = int(px // ConfigOld.cell_width)
        y = int(py // ConfigOld.cell_height)
        if ope == BoardOld.OPE_OPEN:
            result = self.open(x, y)
            if result == CellOld.TYPE_MINE:
                #地雷を踏んだ
                print("SSSSSSSSSSSSSSSSS")
        if ope == BoardOld.OPE_MARK:
            self.cells[x][y].mark()

        super().update()

class Controller:
    def __init__(self):
        self.tick = pygame.time.Clock()
        self.font = pygame.font.SysFont(None, 36)
        self.surface = pygame.display.set_mode((ConfigOld.screen_width, ConfigOld.screen_height))

    @staticmethod
    def clear_callback(surf, rect):
        surf.fill((0, 0, 0), rect)

    def mainloop(self, board : BoardOld):
        self.surface.fill((0, 0, 0))
        xpos = 0
        ypos = 0

        while True:
            ope  = BoardOld.OPE_NONE
            for event in pygame.event.get():
                if event.type == QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type == MOUSEMOTION:
                    xpos, ypos = event.pos
                elif event.type == MOUSEBUTTONDOWN:
                    if(event.button == 1):
                        #LBUTTON
                        ope = BoardOld.OPE_OPEN
                        xpos, ypos = event.pos
                        break
                    elif(event.button == 3):
                        #RBUTTON
                        ope = BoardOld.OPE_MARK
                        xpos, ypos = event.pos
                        break
                    
            board.clear(self.surface, Controller.clear_callback)

            board.update(ope, xpos, ypos)

            board.draw(self.surface)

            pygame.display.update()
            self.tick.tick(10)


def mainaa():
        pygame.init()
        ConfigOld.init(16, 16, 1)

        controller = Controller()
        board = BoardOld()

        controller.mainloop(board)


class Config:
    screen_width  = 0
    screen_height = 0
    board_width   = 0
    board_height  = 0
    mine_count    = 0

class Cell():
    TYPE_NONE = 0
    TYPE_MINE = 1

    def __init__(self):
        self.__type = self.TYPE_NONE
        pass

    @property
    def type(self):
        return self.__type

    @type.setter
    def type(self, value):
        if(value == self.TYPE_NONE or value == self.TYPE_MINE):
            self.__type = value



class BoardGroup(pygame.sprite.Group, pygame.sprite.Sprite):

    def __init__(self, board):
        super().__init__(self)

        left   = 0
        top    = 0
        right  = config.screen_width
        bottom = config.screen_height
        self.rect = Rect(left, top, right, bottom)
        self.image = pygame.Surface((config.screen_width, config.screen_height))
        self.image.fill((128,128,128))

class Board():

    def __init__(self, width, height, mine_count):
        super().__init__()

        self.width = width
        self.height = height
        self.mine_count = mine_count

        #2次元リスト作成
        self.cells = []

        #Cellオブジェクト作成
        for x in range(width):
            print(x)
            self.cells.append(list())
            for y in range(height):
                cell = Cell()
                self.cells[x].append(cell)

        #地雷設置
        count = 0
        while count < mine_count:
            val = randint(0, width * height - 1)
            x = val % width
            y = val // height
            if self.cells[x][y].type == Cell.TYPE_NONE:
                print("SET:", x, y)
                count += 1

class MineSweeperGame(Game):
    """MineSweeperGameクラス"""

    SCENE_TITLE = 0
    SCENE_GAME  = 1
    SCENE_END   = 2

    def __init__(self, width=800, height=600):
        """初期化"""

        super().__init__(width, height)

        # 盤面
        self.board = Board(config.board_width, config.board_height, config.mine_count)
        self.boardgroup = BoardGroup(self.board)


        self.clear_surf = pygame.Surface((self.window_width,self.window_height))
        self.clear_surf.fill((0,0,0))
        self.scene = self.SCENE_TITLE

    def on_frame(self):
        """フレーム処理

        Args:
            scene (int) : 0 タイトル / 1 ゲーム / 2 終了
        Returns:
            int : 0 タイトル / 1 ゲーム / 2 終了
        """
        if self.scene == MineSweeperGame.SCENE_TITLE:
            scene_next = self.on_frame_title()
        else:
            scene_next = self.on_frame_game()
        return scene_next

    def on_frame_title(self):
        """フレーム処理（タイトル）

        Returns:
            int : 0 タイトル / 1 ゲーム
        """
        # タイトル
        scene_next = MineSweeperGame.SCENE_TITLE
        textsurf = self.font.render("MineSweeperGame", True,  (255,255,255))
        self.surface.blit(textsurf, 
                          ((self.window_width - textsurf.get_width()) / 2,
                           (self.window_height - textsurf.get_height()) / 2))

        # イベント処理
        for event in pygame.event.get():
            if event.type == KEYDOWN:
                scene_next = MineSweeperGame.SCENE_GAME
                self.surface.fill((0,0,0))
                break
        return scene_next

    def on_frame_game(self):
        """フレーム処理（ゲーム）

        Returns:
            int : 1 ゲーム / 2 終了
        """
        # 次のシーン
        scene_next = MineSweeperGame.SCENE_GAME
        # イベント処理
        soar_flag = False
        for event in pygame.event.get():
            if event.type == MOUSEMOTION:
                self.mouse_x, self.mouse_y = event.pos
            elif event.type == KEYDOWN:
                if event.key == K_SPACE:
                    soar_flag = True

        if self.scene == MineSweeperGame.SCENE_GAME:
            print("aaa")
            pass
            # 通常
            # オブジェクト更新

            # 衝突判定

            # 前回描画分をサーフェイスからクリア

        # 今回描画分をサーフェイスに描画
        self.boardgroup.draw(self.surface)

        return scene_next


config = Config
config.screen_width = 600
config.screen_height = 600
config.board_width = 20 
config.board_height = 20
config.mine_count = 5

def main():
    """メイン"""

    # ゲームオブジェクトを作成
    g = MineSweeperGame(config.screen_width, config.screen_height)
    # メイン処理
    g.run()


if __name__ == '__main__':
    main()
