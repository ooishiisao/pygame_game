
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
    # on_frame()
}

class MineSweeperGame
{
    - _scene
    - _plain
    - _plaingroup
    - _districtgroup

    # on_frame()
    # on_frame_title()
    # on_frame_game()
}

class PlainGroup
{
    + init(Plainオブジェクト, 表示エリア)
    - _plain
    - _plainsprite
    - _districtgroup
    - _districts_area
    - _district_width
    - _district_height

    + update()
    + draw()
}

class PlainSprite
{
    + area
    + image
    - _plain
    + init(Plainオブジェクト, 表示エリア)
    + update()
}

class Plain
{
    + rows
    + columns
    + mine_count
    + districts[]
    + init(行数, 列数, 地雷数)
    + open(マス目位置)
    + mark(マス目位置)
}

class DistrictGroup
{
    + init(Districtオブジェクト[], 行数, 列数, 表示エリア)
    + update()
    + draw()
}

class DistrictSprite
{
    + area
    + image
    - _district
    - _font
    + init(Districtオブジェクト, 表示エリア)
    + update()
}
class District
{
    + x
    + y
    + mine_type
    + open_state
    + mark_state
    + neighbors[]

    + init(x位置, y位置)
    + set_neighbor(位置定数, Districtオブジェクト)
    + set_mine()
    + open()
    + mark()
    + get_around_mines()
    
}

Game <|- MineSweeperGame
MineSweeperGame  "1" *-- "1" Plain
MineSweeperGame  "1" *-- "1" PlainGroup   : upadte(クリック位置),draw()

Plain            "1" *-   "*" District

Plain                <--      PlainGroup  : 参照(初期化),各種操作
Plain                <--      PlainSprite : 参照(描画)
PlainGroup       "1" *-  "1"  PlainSprite
PlainGroup       "1" *-  "1"  DistrictGroup : update(), draw()

District             <---     DistrictGroup   : 参照(初期化)
District             <---     DistrictSprite  : 参照(描画)
DistrictGroup    "1" *-   "*" DistrictSprite


class Config
{
    + screen_width
    + screen_height
    + plain_width
    + plain_height
}

@enduml
```

---
- class Config
    - screen_width
        スクリーン幅 [ピクセル]
    - screen_height
        スクリーン高 [ピクセル]
    - plain_width
        ボード幅 [セル]
    - plain_height
        ボード高 [セル]

---
- class Plain
    - size
        盤面サイズ
    - districts[][]
        セルを保持する2次元配列（2行2列余分に確保）
    - init(盤面サイズ, 地雷数)
        以下を実施。
        - セルの生成
        - セル同士のリンクを張る。
        - 地雷の設置
    - open(マス目位置)
        盤面操作（地面を開ける）
    - mark(マス目位置)
        盤面操作（マーキングする）

---
- class District
    - type
        地雷を設置、確認
        - TYPE_MINE : 地雷
        - TYPE_NONE : 非地雷。周りの地雷数。
    - open_flag
        - FLAG_OPEN   : 開封済
        - FLAG_CLOSED : 未開封
    - mark_flag
        - FLAG_NOMARK : マークあり
        - FLAG_MARKED : マークなし
    - init()
        オブジェクト生成
    - set_neighbors(隣セルの位置, セル)
        隣のセルとリンクを張る。
    - open()
        地面を開封する
        周りの地雷がない場合、周りを開いていく。
    - mark()
        マーキングする。
    - get_bomb_count()
        周りの地雷数を返す。

