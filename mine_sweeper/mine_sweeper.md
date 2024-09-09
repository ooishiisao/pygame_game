
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

class BoardGroup
{
    + init(盤面, サイズ[pixel])
    + update()
    + draw()
}

class BoardSprite
{
    + 位置
    + イメージ
    + init(盤面, サイズ[pixel])
    + update()
}

class Board
{
    + width
    + height
    + cells[]
    + init(盤面サイズ)
    + open(マス目位置)
    + mark(マス目位置)
}

class CellGroup
{
    + init(セル[], サイズ[pixel])
    + update()
    + draw()
}

class CellSprite
{
    + 位置
    + イメージ
    + init(セル, サイズ[pixel])
    + update()
}
class Cell
{
    + neighbors[]
    + mine_type
    + open_state
    + mark_state
    + init()
    + set_neighbor(pos, cell)
    + set_mine()
    + open()
    + mark()
    + get_mine_count()
    
}

Game <|- MineSweeperGame
MineSweeperGame  "1" *-- "1" Board
MineSweeperGame  "1" *-- "1" BoardGroup   : upadte(クリック位置),draw()
MineSweeperGame  "1" *-- "1" CellGroup    : upadte(),draw()

Board            "1" *-   "*" Cell

Board                <--      BoardGroup  : 参照(初期化),各種操作
Board                <--      BoardSprite : 参照(描画)
BoardGroup       "1" *-  "1"  BoardSprite

Cell                 <---     CellGroup   : 参照(初期化)
Cell                 <---     CellSprite  : 参照(描画)
CellGroup        "1" *-   "*" CellSprite
BoardGroup           <--      CellGroup   : 参照(セルサイズ[pixel])


class Config
{
    + screen_width
    + screen_height
    + board_width
    + board_height
}

@enduml
```

---
- class Config
    - screen_width
        スクリーン幅 [ピクセル]
    - screen_height
        スクリーン高 [ピクセル]
    - board_width
        ボード幅 [セル]
    - board_height
        ボード高 [セル]

---
- class Board
    - size
        盤面サイズ
    - cells[][]
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
- class Cell
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

