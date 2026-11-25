# i2_packedscene.md — @export PackedScene 一覧

## 検索対象

- core/ data/ scenes/ の .gd ファイルの `@export.*PackedScene`
- 各変数の `.instantiate()` 呼び出し行
- .tscn での割り当てパス（取得できた場合のみ）

---

## 全件リスト

| ファイル:行 | 変数名 | instantiate の行 | .tscn 割り当てパス |
|---|---|---|---|
| scenes/databases/SpeciesDefinition.gd:102 | visual_scene | Enemy.gd:181 `spec_def.visual_scene.instantiate()` | ? (tscn未設定—DataResourceごとに異なる) |
| scenes/Characters/Player/Spell/SpellUI.gd:5 | spell_card_scene | SpellUI.gd:68 `spell_card_scene.instantiate()` | SpellUI.tscn:38 `SubResource("PackedScene_71ed6")` (インライン定義) |
| scenes/Utils/SwarmSpawner.gd:12 | fast_enemy_scene | SwarmSpawner.gd:50,98 `scene.instantiate()` (間接) | ? (tscn未割り当て確認済み) |
| scenes/Utils/SwarmSpawner.gd:13 | tank_enemy_scene | SwarmSpawner.gd:50,98 `scene.instantiate()` (間接) | ? (tscn未割り当て確認済み) |
| scenes/Utils/SwarmSpawner.gd:14 | balanced_enemy_scene | SwarmSpawner.gd:50,98 `scene.instantiate()` (間接) | ? (tscn未割り当て確認済み) |
| scenes/Utils/SwarmSpawner.gd:119 | boss_scene | SwarmSpawner.gd:129 `boss_scene.instantiate()` | ? (tscn未割り当て確認済み) |
| scenes/World/WorldRoot/WorldRoot.gd:12 | player_scene | WorldRoot.gd:84 `player_scene.instantiate()` | WorldRoot.tscn:11 `res://scenes/Characters/Player/Player.tscn` |
| scenes/World/WorldRoot/WorldRoot.gd:13 | enemy_scene | WorldRoot.gd:93 `scene.instantiate()` (間接) | ? (WorldRoot.tscn に enemy_scene の割り当てなし) |

## 注記

- `SwarmSpawner.gd` は fast/tank/balanced/boss を `scene` という中間変数に入れて `scene.instantiate()` を呼ぶ（直接変数名では instantiate しない）。
- `WorldRoot.gd:93` の `scene` は `enemy_scene` とは別の局所変数（`_map = scene.instantiate()` 文脈；map シーンをロードしたもの）。`enemy_scene` の instantiate はWorldRoot.gd内で直接は未使用（WorldManager経由でEnemySpawnerが担当）。
- `LogisticsNPC.gd:72–74` では `@export` なしで `load("res://scenes/Map/CargoCrate.tscn")` → `.instantiate()` を使用（本リストのスコープ外）。
- `IndicatorManager.gd:11,30,52,71` は `const INDICATOR_SCENE = preload(...)` を使用（`@export` ではない）。
- `ObjectGenerator.gd:69` / `WorldMap.gd:210,225` は動的 `load(path).instantiate()` を使用（`@export PackedScene` ではない）。
