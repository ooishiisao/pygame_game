import sys
from random import randint
from itertools import product
import pygame
from pygame.locals import QUIT, Rect, MOUSEBUTTONDOWN, MOUSEMOTION, KEYDOWN
from game import Game

class Config:
    screen_width  = 0
    screen_height = 0
    rows          = 0
    columns       = 0
    mine_count    = 0

class District():
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
        self._x          = x
        self._y          = y
        self._mine_type  = District.TYPE_NONE
        self._open_state = District.STATE_CLOSED
        self._mark_state = District.STATE_NOMARK
        self._neighbors = [None, None, None, None, None, None, None, None]

    @property
    def x(self):
        return self._x

    @property
    def y(self):
        return self._y

    @property
    def mine_type(self):
        return self._mine_type

    @property
    def open_state(self):
        return self._open_state

    @property
    def mark_state(self):
        return self._mark_state

    def set_neighbor(self, pos, district):
        """隣のセルとのリンクを設定"""
        if pos >= District.POS_NW and pos <= District.POS_SE:
            self._neighbors[pos] = district

    def set_mine(self):
        """地雷をセット"""
        if self._mine_type == District.TYPE_NONE:
            self._mine_type = District.TYPE_MINE
            return True
        else:
            return False

    def open(self):
        """セルを暴く"""
        self._open_state = District.STATE_OPEN
        if self._mine_type == District.TYPE_NONE:
            print(f"open x:{self.x} y:{self.y}")
            if self.get_around_mines() == 0:
                #周りのセルを開く
                for district in self._neighbors:
                    if district is None:
                        continue
                    if district.mine_type == District.TYPE_MINE:
                        continue
                    if district.open_state == District.STATE_OPEN:
                        continue
                    district.open()
        return self._mine_type

    def mark(self):
        """セルをマーキングする"""
        print(f"mark x:{self.x} y:{self.y}")
        if self._mark_state == District.STATE_NOMARK:
            self._mark_state = District.STATE_MARKED
        else:
            self._mark_state = District.STATE_NOMARK

    def get_around_mines(self):
        """周りの地雷の数を返す"""
        count = 0
        for district in self._neighbors:
            if district is None:
                continue
            if district.mine_type == District.TYPE_MINE:
                count += 1
        return count

class Plain():

    def __init__(self, rows, columns, mine_count):
        super().__init__()
        self._districts = []
        self._rows    = rows
        self._columns = columns
        self._mine_count = mine_count

        #Districtオブジェクト作成
        for y, x in product(range(self._columns), range(self._rows)):
            district = District(x, y)
            self.districts.append(district)

        #周辺のDistrictとのリンク
        for y, x in product(range(self._columns), range(self._rows)):
            pos = 0
            district : District = self.districts[y*self._columns + x]
            for xx, yy in product((x-1, x, x+1), (y-1, y, y+1)):
                if  x == xx and y == yy:
                    continue
                if xx >= 0 and xx < self._columns and yy >= 0 and yy < self._rows:
                        neighbor = self.districts[yy*self._columns + xx]
                        district.set_neighbor(pos, neighbor)
                pos+=1

        #地雷設置
        count = 0
        while count < self._mine_count :
            val = randint(0, self._columns * self._rows - 1)
            x = val % self._columns
            y = val // self._rows
            if self.districts[y*self._columns + x].set_mine():
                count += 1

    @property
    def districts(self):
        return self._districts

    @property
    def columns(self):
        return self._columns

    @property
    def rows(self):
        return self._rows

    @property
    def mine_count(self):
        return self._mine_count

    def open(self, x, y):
        ret = self.districts[self._columns * y + x].open()
        return ret

    def mark(self, x, y):
        self.districts[self._columns * y + x].mark()


class DistrictSprite(pygame.sprite.Sprite):

    def __init__(self, district, area):
        super().__init__()
        self._district = district
        area.width  -= 5
        area.height -= 5
        self.rect = area
        #print(self.rect)
        self.image = pygame.Surface((area.width, area.height))
        self.image.fill((128,128,128))
        self._font = pygame.font.SysFont(None, 24)

    def update(self):
        if self._district.open_state == District.STATE_OPEN:
            count = self._district.get_around_mines()
            number_image = self._font.render(f"{count}", True, (255,255,255))
            number_rect = number_image.get_rect()
            number_rect.center = self.image.get_rect().center
            self.image.blit(number_image, number_rect)
        else:
            if self._district.mark_state == District.STATE_MARKED:
                number_image = self._font.render("?", True, (255,255,255))
                number_rect = number_image.get_rect()
                number_rect.center = self.image.get_rect().center
                self.image.blit(number_image, number_rect)
            else:
                self.image.fill((128,128,128))


class DistrictGroup(pygame.sprite.Group):

    def __init__(self, districts, rows, columns, area):
        super().__init__()
        width  = area.width  // columns
        height = area.height // rows
        for district in districts:
            self.add(DistrictSprite(district, Rect(width * district.x, height * district.y, width, height)))


class PlainSprite(pygame.sprite.Sprite):

    def __init__(self, plain, area):
        super().__init__()
        self._plain = plain
        self.rect = area
        self.image = pygame.Surface((area.width, area.height))
        self.image.fill((128,0,0))


class PlainGroup(pygame.sprite.Group):

    def __init__(self, plain : Plain, area):
        super().__init__(self)
        self._plain           = plain
        self._districts_area   = area
        self._district_width  = area.width  // self._plain.columns
        self._district_height = area.height // self._plain.rows

        self._plainsprite = PlainSprite(plain, area)
        self.add(self._plainsprite)

        self._districtgroup = DistrictGroup(plain.districts, plain.rows, plain.columns, area)

    def update(self, operation, mouse_x, mouse_y):
        x = (mouse_x - self._districts_area.left) // self._district_width
        y = (mouse_y - self._districts_area.top)  // self._district_height
        if operation == 1:
            self._plain.open(x, y)
        elif operation == 3:
            self._plain.mark(x, y)

        self._districtgroup.update()

    def draw(self, surf):
        super().draw(surf)
        self._districtgroup.draw(surf)

class MineSweeperGame(Game):
    """MineSweeperGameクラス"""

    SCENE_TITLE = 0
    SCENE_GAME  = 1
    SCENE_END   = 2

    def __init__(self, width=800, height=600):
        """初期化"""
        super().__init__(width, height)
        # 盤面（とセル）
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

                self._plain      = Plain(config.rows, config.columns, config.mine_count)
                area = Rect(0, 0, config.screen_width, config.screen_height)
                self._plaingroup = PlainGroup(self._plain, area)
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
                mouse_button     = event.button
                update_flag      = True

        if update_flag == True and self.scene == MineSweeperGame.SCENE_GAME:
            # オブジェクト更新
            self._plaingroup.update(mouse_button, mouse_x, mouse_y)

            # 前回描画分をサーフェイスからクリア

        # 今回描画分をサーフェイスに描画
        self._plaingroup.draw(self.surface)

        return scene_next


config = Config
config.screen_width  = 600
config.screen_height = 600
config.rows          = 20 
config.columns       = 20
config.mine_count    = 40

def main():
    """メイン"""
    # ゲームオブジェクトを作成
    g = MineSweeperGame(config.screen_width, config.screen_height)
    # メイン処理
    g.run()


if __name__ == '__main__':
    main()
