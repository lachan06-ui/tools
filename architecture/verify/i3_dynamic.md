# i3_dynamic.md — 動的呼び出し調査

## 検索対象

core/ data/ scenes/ の .gd ファイル

## 定義

「文字列リテラルでない」引数を持つ次の呼び出しを検索:
- `call(` / `callv(` / `call_deferred(` — 第1引数が変数や式
- `get_node(` / `get_node_or_null(` — 引数が変数や式
- `emit_signal(` — 第1引数が変数や式（文字列でない）
- `connect(` — 第1引数が変数や式（文字列でない）
- `load(` — 引数が変数や式
- `has_method(` — 件数のみ

---

## パターン別結果

### `call(var)` — 5件

代表例:

| ファイル:行 | 該当行（先頭80字） |
|---|---|
| scenes/World/Debug/DebugPoisonActions.gd:62 | `var region_id: String = str(get_region.call())` |
| scenes/World/Debug/DebugPoisonActions.gd:126 | `var region_id: String = str(get_region.call())` |
| scenes/World/Debug/DebugPoisonActions.gd:144 | `var region_id: String = str(get_region.call())` |
| scenes/World/Debug/DebugPoisonActions.gd:161 | `var raw_position: Variant = spawn_position.call()` |
| scenes/World/Debug/DebugPoisonActions.gd:405 | `refresh.call()` |

> 全5件はデバッグツール内で Callable 型変数を `.call()` する用法。

---

### `callv(var)` — 0

---

### `call_deferred(var)` — 1件

| ファイル:行 | 該当行（先頭80字） |
|---|---|
| scenes/World/Debug/DebugPanel.gd:148 | `_restore_right_scroll.call_deferred(scroll, saved_scroll)` |

> `_restore_right_scroll` は Callable 型変数。

---

### `get_node(var)` — 2件

| ファイル:行 | 該当行（先頭80字） |
|---|---|
| scenes/Characters/Enemies/Enemy.gd:215 | `return main_loop.root.get_node(autoload_name)` |
| scenes/Characters/Enemies/EnemyAI.gd:254 | `return main_loop.root.get_node(autoload_name)` |

> `autoload_name` は文字列変数。autoload を動的ルックアップするユーティリティ関数。

---

### `get_node_or_null(var)` — 5件

| ファイル:行 | 該当行（先頭80字） |
|---|---|
| scenes/Characters/Enemies/Boss.gd:40 | `var spawner = get_node_or_null(swarm_spawner_path) as Node` |
| scenes/World/Debug/DebugPanel.gd:1417 | `var view: Control = _right_panel.get_node_or_null(_selected_group) as Control` |
| scenes/World/Debug/DebugPanel.gd:1435 | `var has_matching_view: bool = _right_panel != null and _right_panel.get_node_or_...` |
| scenes/World/Debug/DebugPanel.gd:1459 | `var first_button: Button = folder.get_node_or_null(folder.name.replace("Fold...` |
| scenes/World/Debug/DebugPanel.gd:1472 | `var view: Control = _right_panel.get_node_or_null(_right_selected_group) as Con` |

> `swarm_spawner_path` は NodePath型のエクスポート変数。DebugPanel の4件はUI内部パス操作。

---

### `emit_signal(var)` — 0

> 全 `emit_signal(` 呼び出しは第1引数が文字列リテラル（例: `emit_signal("spawn_requested", ...)`）。

---

### `connect(var)` — 36件

GDScript4 の新記法 `signal_obj.connect(callable)` が全36件。第1引数は Callable（メソッド参照やラムダ）であり文字列ではない。

代表例:

| ファイル:行 | 該当行（先頭80字） |
|---|---|
| scenes/Characters/Enemies/Boss.gd:27 | `_phase_timer.timeout.connect(_on_phase_timeout)` |
| scenes/Characters/Enemies/Corpse.gd:70 | `tree_exiting.connect(func():` |
| scenes/Characters/Enemies/Corpse.gd:180 | `get_tree().create_timer(particles.lifetime + 0.5).timeout.connect(particles.que` |
| scenes/Characters/Enemies/Enemy.gd:61 | `poison_received.connect(_on_poison_received)` |
| scenes/Characters/Enemies/Enemy.gd:276 | `t.timeout.connect(func(): Engine.time_scale = 1.0)` |

> 旧記法 `connect("signal_name", callable)` の使用はプロジェクト内で0件（全て新記法）。

---

### `load(var)` — 13件

| ファイル:行 | 該当行（先頭80字） |
|---|---|
| core/autoload/GameState.gd:584 | `var res = load(path)` |
| core/databases/EnemyDatabase.gd:27 | `var res = load(path)` |
| core/databases/ItemDatabase.gd:25 | `var res = load(path)` |
| core/databases/SpeciesDatabase.gd:27 | `var res : Resource = load(path)` |
| core/systems/ecology/EcologyManager.gd:104 | `var res = load(full_path)` |

> 残り8件は scenes/ 配下（ObjectGenerator, WorldMap, LogisticsNPC等）。
> いずれも `path` 変数にファイルパス文字列を組み立てて渡すパターン。

---

### `has_method(any)` — 133件（件数のみ）

---

## 注記

- `call(var)` の全5件はデバッグコード内（DebugPoisonActions.gd）。プロダクションの core/ には0件。
- `get_node(var)` の2件（Enemy.gd, EnemyAI.gd）は autoload を名前でルックアップするヘルパー関数内で意図的な動的アクセス。
- `emit_signal("string",...)` の旧記法は EcologyManager.gd 等に残存しているが第1引数は文字列リテラルのため本調査のスコープ外。
- `has_method(` の133件はランタイム型チェックのガード用途が大半（デバッグUI内を含む）。
