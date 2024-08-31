"""FuwaFuwaゲーム"""

import sys
import math
import random
import pygame
from pygame.locals import QUIT, Rect, MOUSEBUTTONDOWN, MOUSEMOTION, KEYDOWN, K_SPACE

import game

class Ship(pygame.sprite.Sprite):
    """自機スプライトクラス"""

    def __init__(self, group):
        """初期化

        スプライトのimage、rectを設定
        Args:
            group (Group) : 所属させるグループ
        """
        super().__init__(group)
        self.image = pygame.Surface((64, 64))
        self.image.fill((200,200,200))
        self.rect = self.image.get_rect()
        self.rect.move_ip(0, 200)
        self.velocity = 0
        self.acceleration = 3

    def update(self, soar_flag):
        """更新

        自機の位置を更新
        Args:
            soar_flag (bool) : True 上昇 / False 下降
        """
        if soar_flag:
            self.velocity -= self.acceleration
        else:
            self.velocity += self.acceleration
        self.rect.move_ip(0, self.velocity)


class ShipGroup(pygame.sprite.GroupSingle):
    """自機グループクラス

    特別な処理はない。
    """

    def __init__(self):
        """初期化"""
        super().__init__()


class Wall(pygame.sprite.Sprite):
    """壁スプライトクラス"""

    def __init__(self, group, left, top, width, height, color=(128,32,0)):
        """初期化

        スプライトのimage、rectを設定
        Args:
            group (Group) : 所属させるグループ
            left (int) : 壁の左
            top (int) :  壁の上
            width (int) : 壁の幅
            height (int) : 壁の高さ
        """
        super().__init__(group)
        self.rect = Rect(left, top, width, height)
        self.image = pygame.Surface((width, height))
        self.image.fill(color)

    def update(self):
        """更新
        
        壁の位置を左に更新（スクロール）
        """
        self.rect.move_ip(-self.rect.width, 0)


class WallGroup(pygame.sprite.Group):
    """壁グループクラス"""

    def __init__(self, window_width, window_height):
        """初期化

        Args:
            window_width (int) : ウィンドウの幅
            window_height (int) : ウィンドウの高さ
        """
        super().__init__()
        self.wall_limit = 10
        self.wall_width = 5
        self.window_width = window_width
        self.window_height = window_height
        # 今の穴と次の穴の間(x)
        self.hole_gap   = 50
        # 次の穴の位置の変化量(y)
        self.hole_delta = 200
        # 次の穴の位置の変化量(y)の拡大量
        self.hole_delta_expand = 10
        # 穴の縮み量
        self.hole_shrink = 5
        self.hole0_x = self.window_width
        self.hole0_y = self.window_height / 2
        self.hole0_r = (self.window_height / 2) - self.wall_limit
        self.hole1_x = self.window_width * 2
        self.hole1_y = self.window_height / 2
        self.hole1_r = ((self.window_height / 2) - self.wall_limit) * 0.8

        # 初期壁
        upper = self.hole0_y - self.hole0_r
        lower = self.hole0_y + self.hole0_r
        for x in range(0, self.window_width, self.wall_width):
            Wall(self, x, 0,     self.wall_width, upper)
            Wall(self, x, lower, self.wall_width, window_height - lower)

    def update(self):
        """更新"""

        # 壁グループの更新
        # 画面右のすぐ外に壁を作成
        self.generate_wall_1()
        # 壁グループ内部オブジェクト(hole)をスクロール
        self.hole0_x = self.hole0_x - self.wall_width
        self.hole1_x = self.hole1_x - self.wall_width
        # 右のholeの中心が画面にタッチしたら更新
        if self.hole1_x <= self.window_width:
            # 旧hole1を新hole0に差し替え
            self.hole0_x = self.hole1_x
            self.hole0_y = self.hole1_y
            self.hole0_r = self.hole1_r
            # 新しいhole1の作成
            # 新しいholeは縮ませる
            self.hole1_r = self.hole0_r - self.hole_shrink
            # 新しいholeはgap分隙間をあける
            self.hole1_x = self.hole0_x + self.hole0_r + self.hole_gap + self.hole1_r
            # 新しいholeのy位置はランダム変化させる
            self.hole1_y = self.hole0_y + random.randint(-self.hole_delta, self.hole_delta)
            # はみ出た分は補正
            if self.hole1_y < self.hole1_r + self.wall_limit:
                self.hole1_y = self.hole1_r + self.wall_limit
            if self.hole1_y > self.window_height - self.hole1_r - self.wall_limit:
                self.hole1_y = self.window_height - self.hole1_r - self.wall_limit
            # はみ出て分は補正
            self.hole_delta = self.hole_delta + self.hole_delta_expand

        # 壁の更新
        # 壁をスクロール
        super().update()
        # 画面外に消えた壁は削除
        for sprite in self.sprites():
            if sprite.rect.left < 0:
                self.remove(sprite)
                del(sprite)

    def is_over(self):
        """穴が塞がったか確認

        Returns:
            integer : True 塞がった / False まだ塞がっていない
        """
        if self.hole0_radius <= 0:
            return True
        else:
            return False

    def generate_wall_0(self):
        """Windowの右外側に壁を生成"""

        upper = self.hole0_y - self.hole0_r
        if upper < self.wall_limit:
            upper = self.wall_limit
        lower = self.hole0_y + self.hole0_r
        if lower > self.window_height - self.wall_limit:
            lower = self.window_height - self.wall_limit
        Wall(self, self.window_width, 0,     self.wall_width, upper)
        Wall(self, self.window_width, lower, self.wall_width, self.window_height - lower)

    def generate_wall_1(self):
        """Windowの右外側に壁を生成"""

        (x1, y1, r1) = (self.hole0_x, self.hole0_y, self.hole0_r)
        (x2, y2, r2) = (self.hole1_x, self.hole1_y, self.hole1_r)

        if r1 <= 0 or r2 <= 0:
            Wall(self, self.window_width, 0,     self.wall_width, self.window_height)
            return

        if y1 == y2:
            # hole0とhole1の角度が0
            dx1 = 0
            dy1 = r1
            dx2 = 0
            dy2 = r2
        else:
            # hole0とhole1を結ぶ直線を基準として、
            # それぞれの円の中心からの垂線と円周の交点の位置を特定
            slope90       = -(x2 - x1) / (y2 - y1)
            slope90_angle = math.atan(slope90) 
            dx1 = r1 * math.cos(slope90_angle)
            dy1 = r1 * math.sin(slope90_angle)
            dx2 = r2 * math.cos(slope90_angle)
            dy2 = r2 * math.sin(slope90_angle) 
        if y1 < y2:
            # 下向きの場合
            # hole0側は上記の基準位置、hole1側は絶対的な垂線上の位置
            upper_x1 = x1 + dx1
            upper_y1 = y1 + dy1
            upper_x2 = x2
            upper_y2 = y2 - r2
            # hole0側は絶対的な垂線上の位置、hole1側は上記の基準位置
            lower_x1 = x1
            lower_y1 = y1 + r1
            lower_x2 = x2 - dx2
            lower_y2 = y2 - dy2
        else:
            # 上向きの場合
            # hole0側は絶対的な垂線上の位置、hole1側は上記の基準位置
            upper_x1 = x1
            upper_y1 = y1 - r1
            upper_x2 = x2 - dx2
            upper_y2 = y2 - dy2
            # hole0側は上記の基準位置、hole1側は絶対的な垂線上の位置
            lower_x1 = x1 + dx1
            lower_y1 = y1 + dy1
            lower_x2 = x2
            lower_y2 = y2 + r2

        # 上側の壁
        if x1 <= self.window_width and self.window_width <= upper_x1:
            upper = y1 - (r1 ** 2 - (self.window_width - x1) ** 2) ** 0.5
        elif upper_x1 <= self.window_width and self.window_width <= upper_x2:
            slope = (upper_y2 - upper_y1) / (upper_x2 - upper_x1)
            intercept = upper_y1 - slope * upper_x1 
            upper = slope * self.window_width + intercept
        else:
            upper = y2 - (r2 ** 2 - (self.window_width - x2) ** 2) ** 0.5
        Wall(self, self.window_width, 0,     self.wall_width, upper)

        # 下側の壁
        if x1 <= self.window_width and self.window_width <= lower_x1:
            lower = y1 + (r1 ** 2 - (self.window_width - x1) ** 2) ** 0.5
        elif lower_x1 <= self.window_width and self.window_width <= lower_x2:
            slope = (lower_y2 - lower_y1) / (lower_x2 - lower_x1)
            intercept = lower_y1 - slope * lower_x1
            lower = slope * self.window_width + intercept
        else:
            lower = y2 + (r2 ** 2 - (self.window_width - x2) ** 2) ** 0.5
        Wall(self, self.window_width, lower, self.wall_width, self.window_height - lower)


class FuwaFuwaGame(game.Game):
    """FuwaFuwaGameクラス"""

    SCENE_TITLE = 0
    SCENE_GAME  = 1
    SCENE_END   = 2

    def __init__(self):
        """初期化"""

        super().__init__()
        pygame.key.set_repeat(5,10)

        # 自機
        self.shipgroup = ShipGroup()
        self.ship = Ship(self.shipgroup)
        # 壁
        self.wallgroup = WallGroup(self.window_width, self.window_height)
        # スプライトクリア用サーフェース
        self.clear_surf = pygame.Surface((self.window_width,self.window_height))
        self.clear_surf.fill((0,0,0))

    def on_frame(self, scene):
        """フレーム処理

        Args:
            scene (int) : 0 タイトル / 1 ゲーム / 2 終了
        Returns:
            int : 0 タイトル / 1 ゲーム / 2 終了
        """
        if scene == FuwaFuwaGame.SCENE_TITLE:
            scene_new = self.on_frame_title()
        else:
            scene_new = self.on_frame_game(scene)
        return scene_new

    def on_frame_title(self):
        """フレーム処理（タイトル）

        Returns:
            int : 0 タイトル / 1 ゲーム
        """
        # タイトル
        scene = FuwaFuwaGame.SCENE_TITLE
        textsurf = self.font.render("Fuwafuwa", True,  (255,255,255))
        self.surface.blit(textsurf, 
                          ((self.window_width - textsurf.get_width()) / 2,
                           (self.window_height - textsurf.get_height()) / 2))

        # イベント処理
        for event in pygame.event.get():
            if event.type == KEYDOWN:
                scene = FuwaFuwaGame.SCENE_GAME
                self.surface.fill((0,0,0))
                break
        return scene

    def on_frame_game(self, scene):
        """フレーム処理（ゲーム）

        Returns:
            int : 1 ゲーム / 2 終了
        """
        # イベント処理
        soar_flag = False
        for event in pygame.event.get():
            if event.type == MOUSEMOTION:
                self.mouse_x, self.mouse_y = event.pos
            elif event.type == KEYDOWN:
                if event.key == K_SPACE:
                    soar_flag = True

        if scene == FuwaFuwaGame.SCENE_GAME:
            # 通常
            # オブジェクト更新
            self.shipgroup.update(soar_flag)
            self.wallgroup.update()

            # 衝突判定
            if pygame.sprite.spritecollide(self.ship, self.wallgroup, False):
                scene = FuwaFuwaGame.SCENE_END
                #pass

            # 前回描画分をサーフェイスからクリア
            self.shipgroup.clear(self.surface, self.clear_surf)
            self.wallgroup.clear(self.surface, self.clear_surf)

        # 今回描画分をサーフェイスに描画
        self.shipgroup.draw(self.surface)
        self.wallgroup.draw(self.surface)

        return scene


def main():
    """メイン"""

    # ゲームオブジェクトを作成
    g = FuwaFuwaGame()
    # メイン処理
    g.run()


if __name__ == '__main__':
    main()
