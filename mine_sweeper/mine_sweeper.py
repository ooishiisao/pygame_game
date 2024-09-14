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
        self.__x          = x
        self.__y          = y
        self.__mine_type  = District.TYPE_NONE
        self.__open_state = District.STATE_CLOSED
        self.__mark_state = District.STATE_NOMARK
        self.__neighbors = [None, None, None, None, None, None, None, None]

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

    def set_neighbor(self, pos, district):
        """隣のセルとのリンクを設定"""
        if pos >= District.POS_NW and pos <= District.POS_SE:
            self.__neighbors[pos] = district

    def set_mine(self):
        """地雷をセット"""
        if self.__mine_type == District.TYPE_NONE:
            self.__mine_type = District.TYPE_MINE
            return True
        else:
            return False

    def open(self):
        """セルを暴く"""
        self.__open_state = District.STATE_OPEN
        if self.__mine_type == District.TYPE_NONE:
            print(f"open x:{self.x} y:{self.y}")
            if self.get_around_mines() == 0:
                #周りのセルを開く
                for district in self.__neighbors:
                    if district is None:
                        continue
                    if district.mine_type == District.TYPE_MINE:
                        continue
                    if district.open_state == District.STATE_OPEN:
                        continue
                    district.open()
        return self.__mine_type

    def mark(self):
        """セルをマーキングする"""
        print(f"mark x:{self.x} y:{self.y}")
        if self.__mark_state == District.STATE_NOMARK:
            self.__mark_state = District.STATE_MARKED
        else:
            self.__mark_state = District.STATE_NOMARK

    def get_around_mines(self):
        """周りの地雷の数を返す"""
        count = 0
        for district in self.__neighbors:
            if district is None:
                continue
            if district.mine_type == District.TYPE_MINE:
                count += 1
        return count

class Plain():

    def __init__(self, rows, columns, mine_count):
        super().__init__()
        self.districts = []
        self.__rows    = rows
        self.__columns = columns
        self.__mine_count = mine_count

        #Districtオブジェクト作成
        for y, x in product(range(self.__columns), range(self.__rows)):
            district = District(x, y)
            self.districts.append(district)

        #周辺のDistrictとのリンク
        for y, x in product(range(self.__columns), range(self.__rows)):
            pos = 0
            district : District = self.districts[y*self.__columns + x]
            for xx, yy in product((x-1, x, x+1), (y-1, y, y+1)):
                if  x == xx and y == yy:
                    continue
                if xx >= 0 and xx < self.__columns and yy >= 0 and yy < self.__rows:
                        neighbor = self.districts[yy*self.__columns + xx]
                        district.set_neighbor(pos, neighbor)
                pos+=1

        #地雷設置
        count = 0
        while count < self.__mine_count :
            val = randint(0, self.__columns * self.__rows - 1)
            x = val % self.__columns
            y = val // self.__rows
            if self.districts[y*self.__columns + x].set_mine():
                count += 1

    @property
    def columns(self):
        return self.__columns

    @property
    def rows(self):
        return self.__rows

    @property
    def mine_count(self):
        return self.__mine_count

    def open(self, x, y):
        ret = self.districts[self.__columns * y + x].open()
        return ret

    def mark(self, x, y):
        self.districts[self.__columns * y + x].mark()


class DistrictSprite(pygame.sprite.Sprite):

    def __init__(self, district, area):
        super().__init__()
        self.__district = district
        area.width  -= 5
        area.height -= 5
        self.rect = area
        #print(self.rect)
        self.image = pygame.Surface((area.width, area.height))
        self.image.fill((128,128,128))
        self.__font = pygame.font.SysFont(None, 24)

    def update(self):
        if self.__district.open_state == District.STATE_OPEN:
            count = self.__district.get_around_mines()
            number_image = self.__font.render(f"{count}", True, (255,255,255))
            number_rect = number_image.get_rect()
            number_rect.center = self.image.get_rect().center
            self.image.blit(number_image, number_rect)
        else:
            if self.__district.mark_state == District.STATE_MARKED:
                number_image = self.__font.render("?", True, (255,255,255))
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

    def __init__(self, plain, pixel_width, pixel_height):
        super().__init__()
        self.__plain = plain
        self.rect = Rect(0, 0, pixel_width, pixel_height)
        self.image = pygame.Surface((pixel_width, pixel_height))
        self.image.fill((128,0,0))
        self.__plain_area = Rect(0, 0, pixel_width, pixel_height)

    @property
    def plain_area(self):
        return self.__plain_area


class PlainGroup(pygame.sprite.Group):

    def __init__(self, plain : Plain, pixel_width, pixel_height):
        super().__init__(self)
        self.__plain       = plain
        self.__plainsprite = PlainSprite(plain, pixel_width, pixel_height)
        self.add(self.__plainsprite)
        self.__plain_area = self.__plainsprite.plain_area        
        self.__district_width  = self.__plain_area.width  // self.__plain.columns
        self.__district_height = self.__plain_area.height // self.__plain.rows

    @property
    def plain_area(self):
        return self.__plain_area

    def update(self, operation, mouse_x, mouse_y):
        x = (mouse_x - self.__plain_area.left) // self.__district_width
        y = (mouse_y - self.__plain_area.top)  // self.__district_height
        if operation == 1:
            self.__plain.open(x, y)
        elif operation == 3:
            self.__plain.mark(x, y)

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

                self.plain      = Plain(config.rows, config.columns, config.mine_count)
                self.plaingroup = PlainGroup(self.plain, config.screen_width, config.screen_height)
                self.districtgroup = DistrictGroup(self.plain.districts, self.plain.rows, self.plain.columns, self.plaingroup.plain_area)
                self.districtgroup.update()
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
                update_flag = True

        if update_flag == True and self.scene == MineSweeperGame.SCENE_GAME:
            # オブジェクト更新
            self.plaingroup.update(mouse_button, mouse_x, mouse_y)
            self.districtgroup.update()

            # 前回描画分をサーフェイスからクリア

        # 今回描画分をサーフェイスに描画
        self.plaingroup.draw(self.surface)
        self.districtgroup.draw(self.surface)

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
