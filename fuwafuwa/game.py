import sys
import pygame
from pygame.locals import QUIT, Rect, MOUSEBUTTONDOWN, MOUSEMOTION

class Game(object):
    """Gameクラス"""
    SCENE_INITIAL = 0

    def __init__(self, width=800, height=600):
        """初期化"""
        # 初期化
        pygame.init()
        # FPS Clock取得
        self.FPS   = 10
        self.clock = pygame.time.Clock()
        # フォント
        self.font = pygame.font.SysFont(None, 36)
        # サーフェース
        self.window_width  = width
        self.window_height = height
        self.surface = pygame.display.set_mode((self.window_width, self.window_height))

    def __del__(self):
        """終了"""
        pygame.quit()

    def run(self):
        """メイン処理"""
        # シーン設定
        scene = Game.SCENE_INITIAL
        # メインループ
        while True:
            # 終了判定
            if pygame.event.peek(QUIT):
                break
            # フレームごとの処理
            scene = self.on_frame(scene)
            # 画面更新
            pygame.display.update()
            # 処理待ち
            self.clock.tick(self.FPS)

    def on_frame(self, scene):
        """フレームごとの処理

        派生クラスで実装
        """
        pass

def main():
    """メイン"""
    pass

if __name__ == '__main__':
    main()
