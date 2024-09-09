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
    TYPE_NONE   = 0
    TYPE_MINE   = 1
    STATE_CLOSED = 0
    STATE_OPEN   = 1
    STATE_NOMARK = 0
    STATE_MARKED = 1
    POS_NW = 0
    POS_N  = 1
    POS_NE = 2
    POS_W  = 3
    POS_E  = 4
    POS_SW = 5
    POS_S  = 6
    POS_SE = 7

    def __init__(self, x ,y):
        """初期化"""
        self.__x          = x
        self.__y          = y
        self.__mine_type  = Cell.TYPE_NONE
        self.__open_state = Cell.STATE_CLOSED
        self.__mark_state = Cell.STATE_NOMARK
        self.__neighbors = [None, None, None, None, None, None, None, None]
        self.debug = 0

    @property
    def x(self):
        return self.__x

    @property
    def y(self):
        return self.__y

    @property
    def mine_type(self):
        return self.__mine_type

    @property
    def open_state(self):
        return self.__open_state

    @property
    def mark_state(self):
        return self.__mark_state

    def set_neighbor(self, pos, cell):
        """隣のセルとのリンクを設定"""
        if( pos >= Cell.POS_NW and pos <= Cell.POS_SE):
            self.__neighbors[pos] = cell

    def set_mine(self):
        """地雷をセット"""
        if(self.__mine_type == Cell.TYPE_NONE):
            self.__type = Cell.TYPE_MINE
            return True
        else:
            return False

    def open(self):
        """セルを暴く"""
        self.__open_state = Cell.STATE_OPEN
        if( self.__mine_type == Cell.TYPE_NONE ):
            #周りのセルを開く
            #TODO
            pass
        return self.__mine_type

    def mark(self):
        """セルをマーキングする"""
        if( self.__mark_state == Cell.STATE_NOMARK ):
            self.__mark_state == Cell.STATE_MARKED
        else:
            self.__mark_state == Cell.STATE_NOMARK

    def get_mine_count(self):
        """周りの地雷の数を返す"""
        count = 0
        for cell in self.__neighbors:
            if cell is not None and cell.mine_type == Cell.TYPE_MINE:
                count += 1
        return count

class CellSprite(pygame.sprite.Sprite):

    def __init__(self, cell, image_width, image_height):
        super().__init__()
        self.__cell = cell
        left   = image_width  * cell.x
        top    = image_height * cell.y
        right  = image_width - 5
        bottom = image_height - 5
        self.rect = Rect(left, top, right, bottom)
        print(self.rect)
        self.image = pygame.Surface((image_width - 5, image_height - 5))
        self.image.fill((128,128,128))

    def update(self):
        if self.__cell.open_state == Cell.STATE_OPEN:
            self.image.fill((128,0,128))
        else:
            self.image.fill((128,128,0))

class CellGroup(pygame.sprite.Group):

    def __init__(self, cells, image_width, image_height):
        super().__init__()
        self.__image_width  = image_width
        self.__image_height = image_height
        for cell in cells:
            self.add(CellSprite(cell, image_width, image_height))

class Board():

    def __init__(self, width, height, mine_count):
        super().__init__()
        self.cells = []
        self.__width      = width
        self.__height     = height 
        self.__mine_count = mine_count

        #Cellオブジェクト作成
        for y, x in product(range(self.__width), range(self.__height)):
            cell = Cell(x, y)
            self.cells.append(cell)

        #周辺のCellとのリンク
        for y, x in product(range(self.__width), range(self.__height)):
            pos = 0
            cell : Cell = self.cells[y*self.__width + x]
            for xx, yy in product((x-1, x, x+1), (y-1, y, y+1)):
                if(xx >= 0 and xx < self.__width and yy >= 0 and yy < self.__height):
                    neighbor = self.cells[yy*self.__width + xx]
                    cell.set_neighbor(pos, neighbor)
                pos+=1

        #地雷設置
        count = 0
        while count < self.__mine_count :
            val = randint(0, self.__width * self.__height - 1)
            x = val % self.__width
            y = val // self.__height
            if self.cells[y*self.__width + x].mine_type == Cell.TYPE_NONE:
                print("[DEBUG]MINE_SET:", x, y)
                count += 1

    @property
    def width(self):
        return self.__width

    @property
    def height(self):
        return self.__height

    @property
    def mine_count(self):
        return self.__mine_count

    def open(self, x, y):
        ret = self.cells[self.__width * y + x].open()
        return ret

    def mark(self, x, y):
        self.cells[self.__width * y + y].mark()

class BoardSprite(pygame.sprite.Sprite):

    def __init__(self, board, pixel_width, pixel_height):
        super().__init__()
        self.rect = Rect(0, 0, pixel_width, pixel_height)
        self.image = pygame.Surface((pixel_width, pixel_height))
        self.image.fill((128,0,0))

class BoardGroup(pygame.sprite.Group):

    def __init__(self, board : Board, pixel_width, pixel_height):
        super().__init__(self)
        self.__board       = board
        self.__boardsprite = BoardSprite(board, pixel_width, pixel_height)
        self.add(self.__boardsprite)
        self.__board_width  = pixel_width
        self.__board_height = pixel_height
        self.__cell_width   = pixel_width  // self.__board.width
        self.__cell_height  = pixel_height // self.__board.height

    @property
    def cell_width(self):
        return self.__cell_width

    @property
    def cell_height(self):
        return self.__cell_height

    def update(self, operation, mouse_x, mouse_y):
        x = mouse_x // self.__cell_width
        y = mouse_y // self.__cell_height
        print( "BoardGroup", x, y)
        cell = self.__board.open(x, y)


class MineSweeperGame(Game):
    """MineSweeperGameクラス"""

    SCENE_TITLE = 0
    SCENE_GAME  = 1
    SCENE_END   = 2

    def __init__(self, width=800, height=600):
        """初期化"""
        super().__init__(width, height)
        # 盤面（とセル）
        self.clear_surf = pygame.Surface((width, height))
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
            if event.type == KEYDOWN or event.type == MOUSEBUTTONDOWN:
                scene_next = MineSweeperGame.SCENE_GAME
                self.surface.fill((0,0,0))

                self.board      = Board(config.board_width, config.board_height, config.mine_count)
                self.boardgroup = BoardGroup(self.board, config.screen_width, config.screen_height)
                self.cellgroup  = CellGroup(self.board.cells, self.boardgroup.cell_width, self.boardgroup.cell_height)


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
        mouse_x = 0
        mouse_y = 0
        update_flag = False
        for event in pygame.event.get():
            if event.type == MOUSEBUTTONDOWN:
                mouse_x, mouse_y = event.pos
                update_flag = True

        if update_flag == True and self.scene == MineSweeperGame.SCENE_GAME:
            # オブジェクト更新
            print("aaa", mouse_x, mouse_y)
            self.boardgroup.update(1, mouse_x, mouse_y)
            self.cellgroup.update()

            # 前回描画分をサーフェイスからクリア

        # 今回描画分をサーフェイスに描画
        self.boardgroup.draw(self.surface)
        self.cellgroup.draw(self.surface)

        return scene_next


config = Config
config.screen_width = 600
config.screen_height = 600
config.board_width = 10 
config.board_height = 10
config.mine_count = 2

def main():
    """メイン"""
    # ゲームオブジェクトを作成
    g = MineSweeperGame(config.screen_width, config.screen_height)
    # メイン処理
    g.run()


if __name__ == '__main__':
    main()
