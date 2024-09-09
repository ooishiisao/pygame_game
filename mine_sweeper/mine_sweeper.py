import sys
from random import randint
from itertools import product
import pygame
from pygame.locals import QUIT, Rect, MOUSEBUTTONDOWN, MOUSEMOTION, KEYDOWN
from game import Game

class Config:
    screen_width  = 0
    screen_height = 0
    plain_width   = 0
    plain_height  = 0
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

    def set_neighbor(self, pos, district):
        """隣のセルとのリンクを設定"""
        if( pos >= District.POS_NW and pos <= District.POS_SE):
            self.__neighbors[pos] = district

    def set_mine(self):
        """地雷をセット"""
        if(self.__mine_type == District.TYPE_NONE):
            self.__type = District.TYPE_MINE
            return True
        else:
            return False

    def open(self):
        """セルを暴く"""
        self.__open_state = District.STATE_OPEN
        if( self.__mine_type == District.TYPE_NONE ):
            #周りのセルを開く
            #TODO
            pass
        return self.__mine_type

    def mark(self):
        """セルをマーキングする"""
        if( self.__mark_state == District.STATE_NOMARK ):
            self.__mark_state == District.STATE_MARKED
        else:
            self.__mark_state == District.STATE_NOMARK

    def get_mine_count(self):
        """周りの地雷の数を返す"""
        count = 0
        for district in self.__neighbors:
            if district is not None and district.mine_type == District.TYPE_MINE:
                count += 1
        return count

class DistrictSprite(pygame.sprite.Sprite):

    def __init__(self, district, image_width, image_height):
        super().__init__()
        self.__district = district
        left   = image_width  * district.x
        top    = image_height * district.y
        right  = image_width - 5
        bottom = image_height - 5
        self.rect = Rect(left, top, right, bottom)
        print(self.rect)
        self.image = pygame.Surface((image_width - 5, image_height - 5))
        self.image.fill((128,128,128))

    def update(self):
        if self.__district.open_state == District.STATE_OPEN:
            self.image.fill((128,0,128))
        else:
            self.image.fill((128,128,0))

class DistrictGroup(pygame.sprite.Group):

    def __init__(self, districts, image_width, image_height):
        super().__init__()
        self.__image_width  = image_width
        self.__image_height = image_height
        for district in districts:
            self.add(DistrictSprite(district, image_width, image_height))

class Plain():

    def __init__(self, width, height, mine_count):
        super().__init__()
        self.districts = []
        self.__width      = width
        self.__height     = height 
        self.__mine_count = mine_count

        #Districtオブジェクト作成
        for y, x in product(range(self.__width), range(self.__height)):
            district = District(x, y)
            self.districts.append(district)

        #周辺のDistrictとのリンク
        for y, x in product(range(self.__width), range(self.__height)):
            pos = 0
            district : District = self.districts[y*self.__width + x]
            for xx, yy in product((x-1, x, x+1), (y-1, y, y+1)):
                if(xx >= 0 and xx < self.__width and yy >= 0 and yy < self.__height):
                    neighbor = self.districts[yy*self.__width + xx]
                    district.set_neighbor(pos, neighbor)
                pos+=1

        #地雷設置
        count = 0
        while count < self.__mine_count :
            val = randint(0, self.__width * self.__height - 1)
            x = val % self.__width
            y = val // self.__height
            if self.districts[y*self.__width + x].mine_type == District.TYPE_NONE:
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
        ret = self.districts[self.__width * y + x].open()
        return ret

    def mark(self, x, y):
        self.districts[self.__width * y + y].mark()

class PlainSprite(pygame.sprite.Sprite):

    def __init__(self, plain, pixel_width, pixel_height):
        super().__init__()
        self.rect = Rect(0, 0, pixel_width, pixel_height)
        self.image = pygame.Surface((pixel_width, pixel_height))
        self.image.fill((128,0,0))

class PlainGroup(pygame.sprite.Group):

    def __init__(self, plain : Plain, pixel_width, pixel_height):
        super().__init__(self)
        self.__plain       = plain
        self.__plainsprite = PlainSprite(plain, pixel_width, pixel_height)
        self.add(self.__plainsprite)
        self.__plain_width  = pixel_width
        self.__plain_height = pixel_height
        self.__district_width   = pixel_width  // self.__plain.width
        self.__district_height  = pixel_height // self.__plain.height

    @property
    def district_width(self):
        return self.__district_width

    @property
    def district_height(self):
        return self.__district_height

    def update(self, operation, mouse_x, mouse_y):
        x = mouse_x // self.__district_width
        y = mouse_y // self.__district_height
        print( "PlainGroup", x, y)
        district = self.__plain.open(x, y)


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

                self.plain      = Plain(config.plain_width, config.plain_height, config.mine_count)
                self.plaingroup = PlainGroup(self.plain, config.screen_width, config.screen_height)
                self.districtgroup  = DistrictGroup(self.plain.districts, self.plaingroup.district_width, self.plaingroup.district_height)


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
            self.plaingroup.update(1, mouse_x, mouse_y)
            self.districtgroup.update()

            # 前回描画分をサーフェイスからクリア

        # 今回描画分をサーフェイスに描画
        self.plaingroup.draw(self.surface)
        self.districtgroup.draw(self.surface)

        return scene_next


config = Config
config.screen_width = 600
config.screen_height = 600
config.plain_width = 10 
config.plain_height = 10
config.mine_count = 2

def main():
    """メイン"""
    # ゲームオブジェクトを作成
    g = MineSweeperGame(config.screen_width, config.screen_height)
    # メイン処理
    g.run()


if __name__ == '__main__':
    main()
