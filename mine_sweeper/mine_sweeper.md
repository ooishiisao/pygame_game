
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

class MineSweeperGame
{
    # on_frame(シーン)
    - mouse_x
    - mouse_y
    - clear_surf
}

class PlainGroup
{
    + init(盤面, サイズ[pixel])
    + update()
    + draw()
}

class PlainSprite
{
    + 位置
    + イメージ
    + init(盤面, サイズ[pixel])
    + update()
}

class Plain
{
    + rows
    + columns
    + districts[]
    + init(盤面サイズ)
    + open(マス目位置)
    + mark(マス目位置)
}

class DistrictGroup
{
    + init(セル[], サイズ[pixel])
    + update()
    + draw()
}

class DistrictSprite
{
    + 位置
    + イメージ
    + init(セル, サイズ[pixel])
    + update()
}
class District
{
    + neighbors[]
    + mine_type
    + open_state
    + mark_state
    + init()
    + set_neighbor(pos, district)
    + set_mine()
    + open()
    + mark()
    + get_mine_count()
    
}

Game <|- MineSweeperGame
MineSweeperGame  "1" *-- "1" Plain
MineSweeperGame  "1" *-- "1" PlainGroup   : upadte(クリック位置),draw()
MineSweeperGame  "1" *-- "1" DistrictGroup    : upadte(),draw()

Plain            "1" *-   "*" District

Plain                <--      PlainGroup  : 参照(初期化),各種操作
Plain                <--      PlainSprite : 参照(描画)
PlainGroup       "1" *-  "1"  PlainSprite

District                 <---     DistrictGroup   : 参照(初期化)
District                 <---     DistrictSprite  : 参照(描画)
DistrictGroup        "1" *-   "*" DistrictSprite
PlainGroup           <--      DistrictGroup   : 参照(セルサイズ[pixel])


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
    - init(盤面サイズ)
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

