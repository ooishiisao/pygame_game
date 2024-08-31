# fuwafuwa

## シーケンス図
```puml
@startuml
activate python
create Game
python -> Game : init()
activate Game
create FuwaFuwaGame
Game -> FuwaFuwaGame : init()
activate FuwaFuwaGame
FuwaFuwaGame -> FuwaFuwaGame : 初期化
return
Game -> Game : pygame初期化
Game -> Game : Clock取得
Game -> Game : サーフェース取得
return

python -> Game : run()
activate Game
loop True
Game -> Game : 終了判定
Game -> FuwaFuwaGame : フレームごとの処理
activate FuwaFuwaGame
FuwaFuwaGame -> FuwaFuwaGame : イベント処理
FuwaFuwaGame -> FuwaFuwaGame : スプライト更新
FuwaFuwaGame -> FuwaFuwaGame : スプライトクリア
FuwaFuwaGame -> FuwaFuwaGame : スプライト描画
return

Game -> Game : 画面更新
Game -> Game : 次のフレームまで待つ
end
return

python -> Game : del
activate Game
Game -> Game : pygame終了
return

@enduml
```

```puml
@startuml
activate python

create Sprite
python -> Sprite : init()
return

python -> Group : add(Sprite)
activate Group
return

python -> Group : update()
activate Group

loop すべてのSprite
Group -> Sprite : update()
activate Sprite
return
end

return
@enduml
```

## クラス図
```puml
@startuml

class Game
{
    + FPS
    + clock
    + font
    + window_width
    + window_height
    + surface

    + run()
    # on_frame(シーン)
}

class FuwaFuwaGame
{
    # on_frame(シーン)
    - shipgroup
    - wallgroup
    - mouse_x
    - mouse_y
    - clear_surf
}

class Ship
{
    + rect
    + image
    + update()
    ..
    + velocity
    + acceleration
}

class ShipGroup
{
    + update()
    + clear()
    + draw()
    ..
}

class Wall
{
    + rect
    + image
    + update()
    ..
}

class WallGroup
{
    + update()
    + clear()
    + draw()
    ..
    wall_limit
    wall_width
    window_width
    window_height
    hole0_x
    hole0_y
    hole0_radius
    counter
}

Game <|- FuwaFuwaGame
FuwaFuwaGame "1" *-- "1" ShipGroup : スプライト更新と描画
FuwaFuwaGame "1" *-- "1" WallGroup : スプライト更新と描画
ShipGroup "1" *-- "*" Ship : スプライト更新と描画データ参照
WallGroup "1" *-- "*" Wall : スプライト更新と描画データ参照

@enduml
```

## 説明
### class Game
- コンストラクタ
    pygameの初期化、サーフェースの準備
- デストラクタ
    pygameの終了など
- run
    メインループ
    ｘボタンなどの終了だけ処理
    画面の更新とフレーム待ちは行う。
    それ以外のゲーム内のオブジェクトの更新は、その派生クラスのupdate()で処理されることを期待
- on_frame
    ゲーム内のオブジェクトを更新する。
    マウス、キーボードのイベント処理はここでやる。

### class Ship
自機
- update
    速度の計算（ボタンON：上昇方向／ボタンOFF：下降方向）
    位置を更新

### class ShipGroup
自機グループ

### class Wall
壁
- update()
    位置を更新（１ブロック、左に移動）

### class WallGroup
壁グループ
- update()
    画面右外に壁を作成
    画面左外に消えたら削除
