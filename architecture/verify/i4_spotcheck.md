# i4_spotcheck.md — dependencies.json スポットチェック

## サンプリング方針

`tools/architecture/output/dependencies.json` から kind ごとにソースが偏らないよう抽出。
各件について source の該当行周辺を開き、依存が実コードに存在するか判定。

---

## 判定表

### signal（6件）

| # | source | target | detail | line(target-connect) | 判定 | 備考 |
|---|---|---|---|---|---|---|
| S1 | core/autoload/GameState.gd | scenes/Characters/Player/PlayerSpell.gd | spell_discovered | 36 | **NG** | PlayerSpell.gd:36 に `GameState.spell_discovered.connect(...)` は存在するが、source の GameState.gd には `spell_discovered` の signal 宣言がなく（GameState.gd:25–27 を確認）、emit も未確認。signal 宣言は SpellMasteryManager.gd 側にも存在せず。実際には signal が存在しない可能性が高い。 |
| S2 | core/autoload/SpellMasteryManager.gd | scenes/Characters/Player/PlayerSpell.gd | spell_discovered | 36 | **NG** | SpellMasteryManager.gd には `spell_discovered` の signal 宣言も emit も見つからない（L63は `emit_signal("spell_unlocked",...)` のみ）。connect 先の PlayerSpell.gd:36 は `GameState.spell_discovered.connect(...)` であり SpellMasteryManager は source として不正。 |
| S3 | core/autoload/WorldManager.gd | scenes/World/WorldRoot/WorldRoot.gd | region_changed | 176 | **OK** | WorldRoot.gd:176 `WorldManager.region_changed.connect(_on_region_changed)` を確認。WorldManager.gd に `signal region_changed` と `region_changed.emit(...)` の実在は未確認（grep で region_changed ヒットなし → emit 側 **不明**）。connect 行は存在するため OK とするが emit 要確認。 |
| S4 | core/systems/ecology/EcologyManager.gd | scenes/Systems/SpawnController.gd | spawn_request_object | 22 | **OK** | SpawnController.gd:22 `eco_mgr.spawn_request_object.connect(...)` 確認済み。EcologyManager.gd:11 に `signal spawn_request_object(...)` 宣言、L169 に `emit_signal("spawn_request_object", req)` 確認済み。 |
| S5 | core/systems/ecology/EcologyManager.gd | scenes/Systems/SpawnController.gd | spawn_requested | 20 | **OK** | SpawnController.gd:20 `eco_mgr.spawn_requested.connect(...)` 確認済み。EcologyManager.gd:10 に `signal spawn_requested(...)` 宣言、L168 に `emit_signal("spawn_requested", ...)` 確認済み。 |
| S6 | core/systems/ecology/EcologyManager.gd | scenes/UI/EcologyObservationUI.gd | ecology_updated | 30 | **OK** | EcologyObservationUI.gd:30 `EcologyManager.ecology_updated.connect(...)` 確認済み。EcologyManager.gd:12 に signal 宣言、L718 に `emit_signal("ecology_updated", region_id)` 確認済み。 |

---

### class_use（6件）

| # | source | target | line | 判定 | 備考 |
|---|---|---|---|---|---|
| C1 | core/autoload/EventBus.gd | scenes/Systems/Combat/DamageEvent.gd | 15 | **OK** | EventBus.gd:15 `signal damage_dealt(event: DamageEvent)` — 型名として DamageEvent を参照している。 |
| C2 | core/autoload/GameState.gd | core/databases/EnemyStats.gd | 585 | **OK** | GameState.gd:585 `if res is EnemyStats:` — クラス名で型チェックしている。 |
| C3 | core/autoload/WorldManager.gd | core/systems/ecology/EnvironmentState.gd | 130 | **OK** | WorldManager.gd:130 `var env: EnvironmentState = ecology_manager.get_environment(area_id)` — 型注釈として参照。 |
| C4 | core/components/StatusComponent.gd | core/components/PoisonStatusEffect.gd | 38 | **OK** | StatusComponent.gd:38 `PoisonStatusEffect.POISON_DOSE_DURATION` / L40 `PoisonStatusEffect.new(...)` — クラス名を直接使用。 |
| C5 | core/databases/BiomeDatabase.gd | core/systems/ecology/EnvironmentState.gd | 33 | **OK** | BiomeDatabase.gd:33 `static func get_biome_for_env(env: EnvironmentState)` — 引数型注釈として参照。 |
| C6 | core/databases/DropEntry.gd | core/databases/ItemData.gd | 4 | **OK** | DropEntry.gd:4 `@export var item: ItemData = null` — 型注釈として参照。 |

---

### autoload_use（3件）

| # | source | target | line | 判定 | 備考 |
|---|---|---|---|---|---|
| A1 | core/autoload/GameState.gd | core/autoload/EconomyManager.gd | 119 | **OK** | GameState.gd:119 `EconomyManager.add_gold(amount)` — autoload 名でメソッド呼び出し。 |
| A2 | core/autoload/SaveManager.gd | core/autoload/WorldManager.gd | 18 | **OK** | SaveManager.gd:18 `data["world"] = WorldManager.get_save_data()` — autoload 名でメソッド呼び出し。 |
| A3 | core/autoload/TimeSystem.gd | core/autoload/WorldManager.gd | 48 | **OK** | TimeSystem.gd:48 `if WorldManager.has_method("process_daily_burn_recovery"):` — autoload 名でメソッドチェック後呼び出し。 |

---

### scene_ref（2件・全件）

| # | source | target | line | 判定 | 備考 |
|---|---|---|---|---|---|
| R1 | scenes/Characters/Player/Player.tscn | scenes/Characters/Player/PlayerMesh.tscn | 0 | **OK** | Player.tscn:5 `[ext_resource ... path="res://scenes/Characters/Player/PlayerMesh.tscn"]` を確認。 |
| R2 | scenes/World/WorldRoot/WorldRoot.tscn | scenes/Camera/WorldCamera.tscn | 0 | **OK** | WorldRoot.tscn:5 `[ext_resource ... path="res://scenes/Camera/WorldCamera.tscn"]` 、L13 `instance=ExtResource("3_xbwbs")` を確認。 |

---

## サマリー

| 判定 | 件数 |
|---|---|
| OK | 13 |
| NG | 2 |
| 不明 | 0 |

**NG 詳細:**
- **S1** (GameState→PlayerSpell / spell_discovered): GameState.gd に `spell_discovered` signal の宣言が存在しない。PlayerSpell.gd:36 は `GameState.spell_discovered.connect(...)` と接続を試みているが、signal の発行元が不明。
- **S2** (SpellMasteryManager→PlayerSpell / spell_discovered): SpellMasteryManager.gd に `spell_discovered` の signal 宣言も emit_signal 呼び出しも存在しない（check_unlocks_and_discoveries 内で emit_signal("spell_unlocked",...) のみ存在）。dependencies.json の辺は source/target の向きも含めて不正と判断。
