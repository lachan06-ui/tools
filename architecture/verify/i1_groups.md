# i1_groups.md — グループ使用一覧

## 検索対象

- `.gd` / `.tscn` の core/ data/ scenes/
- 検索語: `add_to_group`, `remove_from_group`, `is_in_group`,
  `call_group`, `get_nodes_in_group`, `get_first_node_in_group`, `notify_group`, `.tscn` の `groups=[...]`

---

## 全件リスト（40件以下のため全件掲載）

### add_to_group

| ファイル:行 | 関数名 | グループ名 |
|---|---|---|
| Targetable.gd:21 | add_to_group | "targetable" |
| Corpse.gd:58 | add_to_group | "Corpses" |
| Enemy.gd:60 | add_to_group | "enemies" |
| LogisticsNPC.gd:18 | add_to_group | "logistics_npcs" |
| Player.gd:68 | add_to_group | "player" |
| Cart.gd:9 | add_to_group | "carts" |
| FireAgent.gd:24 | add_to_group | "FireAgents" |
| PoisonArea.gd:17 | add_to_group | "poison_areas" |
| TreeWood.gd:22 | add_to_group | "trees" |
| TreeWood.gd:23 | add_to_group | "targetable" |
| TreeWood.gd:38 | add_to_group | "fallen_trees" |

### remove_from_group

| ファイル:行 | 関数名 | グループ名 |
|---|---|---|
| Corpse.gd:148 | remove_from_group | "Corpses" |
| TreeWood.gd:39 | remove_from_group | "trees" |
| TreeWood.gd:79 | remove_from_group | "fallen_trees" |

### is_in_group

| ファイル:行 | 関数名 | グループ名 |
|---|---|---|
| SpeciesRelation.gd:169 | is_in_group | "player" |
| DefaultEnemyBehavior.gd:275 | is_in_group | "player" |
| DamageSystem.gd:31 | is_in_group | "player" |
| DamageSystem.gd:33 | is_in_group | "enemies" |
| DebugEntityOverlay.gd:73 | is_in_group | "player" |

### call_group

0件

### get_nodes_in_group

| ファイル:行 | 関数名 | グループ名 |
|---|---|---|
| PoisonAvoidance.gd:16 | get_nodes_in_group | "poison_areas" |
| DefaultEnemyBehavior.gd:89 | get_nodes_in_group | "poison_areas" |
| EnemyAI.gd:291 | get_nodes_in_group | "Corpses" |
| LogisticsNPC.gd:62 | get_nodes_in_group | "allies" |
| Player.gd:156 | get_nodes_in_group | "carts" |
| PlayerCombat.gd:50 | get_nodes_in_group | "targetable" |
| PlayerCombat.gd:98 | get_nodes_in_group | "enemies" |
| PlayerCombat.gd:141 | get_nodes_in_group | "targetable" |
| PlayerCombat.gd:198 | get_nodes_in_group | "carts" |
| PlayerSpell.gd:248 | get_nodes_in_group | "enemies" |
| PlayerSpell.gd:313 | get_nodes_in_group | "FireAgents" |
| TargetSystem.gd:215 | get_nodes_in_group | "targetable" |
| TargetSystem.gd:437 | get_nodes_in_group | "targetable" |
| FireAgent.gd:61 | get_nodes_in_group | "FireAgents" |
| DebugEntityOverlay.gd:45 | get_nodes_in_group | "enemies" |
| DebugEntityOverlay.gd:48 | get_nodes_in_group | "Corpses" |
| DebugPanel.gd:794 | get_nodes_in_group | "poison_areas" |
| DebugPoisonActions.gd:179 | get_nodes_in_group | "poison_areas" |
| DebugPoisonActions.gd:192 | get_nodes_in_group | "poison_areas" |
| DebugPoisonActions.gd:241 | get_nodes_in_group | "enemies" |
| DebugPoisonActions.gd:250 | get_nodes_in_group | "enemies" |
| DebugPoisonActions.gd:262 | get_nodes_in_group | "Corpses" |
| DebugPoisonActions.gd:277 | get_nodes_in_group | "Corpses" |
| DebugPoisonActions.gd:284 | get_nodes_in_group | "Corpses" |
| DebugPoisonView.gd:153 | get_nodes_in_group | "enemies" |
| DebugPoisonView.gd:184 | get_nodes_in_group | "Corpses" |
| DebugPoisonView.gd:220 | get_nodes_in_group | "poison_areas" |
| PoisonArea.gd:51 | get_nodes_in_group | "player" |
| PoisonArea.gd:54 | get_nodes_in_group | "enemies" |
| PoisonArea.gd:57 | get_nodes_in_group | "Corpses" |

### get_first_node_in_group

| ファイル:行 | 関数名 | グループ名 |
|---|---|---|
| GameState.gd:340 | get_first_node_in_group | "player" |
| WorldManager.gd:230 | get_first_node_in_group | "player" |
| Enemy.gd:280 | get_first_node_in_group | "player" |
| EnemyAI.gd:132 | get_first_node_in_group | "player" |
| EnemyAI.gd:375 | get_first_node_in_group | "player" |
| SpellUI.gd:50 | get_first_node_in_group | "player" |
| SpellUI.gd:62 | get_first_node_in_group | "player" |
| Player.gd:28 | get_first_node_in_group | "spell_ui" |
| SwarmSpawner.gd:114 | get_first_node_in_group | "Player" ※大文字(不一致注意) |
| DebugEntityOverlay.gd:18 | get_first_node_in_group | "player" |
| DebugPanel.gd:218 | get_first_node_in_group | "player" |
| DebugPanel.gd:943 | get_first_node_in_group | "player" |
| DebugPanel.gd:1545 | get_first_node_in_group | ? (行に変数使用) |
| DebugPanel.gd:1569 | get_first_node_in_group | ? (行に変数使用) |
| DebugPoisonActions.gd:146 | get_first_node_in_group | "player" |
| DebugPoisonActions.gd:208 | get_first_node_in_group | "player" |
| DebugPoisonActions.gd:215 | get_first_node_in_group | "player" |
| DebugPoisonActions.gd:236 | get_first_node_in_group | "player" |
| DebugPoisonActions.gd:256 | get_first_node_in_group | "player" |
| DebugPoisonView.gd:16 | get_first_node_in_group | "player" |
| DebugSpawnView.gd:14 | get_first_node_in_group | "spawn_controller" |
| DebugSpawnView.gd:81 | get_first_node_in_group | "player" |
| DebugWorldView.gd:11 | get_first_node_in_group | "player" |
| WorldRoot.gd:132 | get_first_node_in_group | "player" |
| WorldRoot.gd:209 | get_first_node_in_group | "player" |

### notify_group

0件

### tscn groups=[...]

| ファイル:行 | 関数名 | グループ名 |
|---|---|---|
| SpellUI.tscn:36 | groups=[...] | "spell_ui" |

---

## 注記

- `SwarmSpawner.gd:114` は `"Player"` (大文字P) でルックアップ。`Player.gd` は `add_to_group("player")` (小文字) で登録しており、**大文字小文字不一致**の可能性あり。
- `LogisticsNPC.gd:62` は `"allies"` グループを参照しているが、`add_to_group("allies")` の登録元は未確認（スキャン0件）。
- `"spawn_controller"` グループ（DebugSpawnView.gd:14）の登録元は未確認。

---

## グループ名サマリー表

| グループ名 | 登録ファイル数 | 呼び出しファイル数 |
|---|---|---|
| "player" | 1 (Player.gd) | 14 (EnemyAI, Enemy, SpellUI, DebugPanel×3, DebugPoisonActions×5, DebugPoisonView, DebugSpawnView, DebugWorldView, GameState, WorldManager, WorldRoot, SpeciesRelation, DefaultEnemyBehavior, DamageSystem, DebugEntityOverlay, PoisonArea) |
| "enemies" | 1 (Enemy.gd) | 7 (DamageSystem, PlayerCombat, PlayerSpell, DebugEntityOverlay, DebugPoisonActions×2, DebugPoisonView, PoisonArea) |
| "targetable" | 2 (Targetable.gd, TreeWood.gd) | 3 (PlayerCombat×2, TargetSystem×2) |
| "Corpses" | 1 (Corpse.gd) | 5 (EnemyAI, DebugEntityOverlay, DebugPoisonActions×3, DebugPoisonView, PoisonArea) |
| "poison_areas" | 1 (PoisonArea.gd) | 4 (PoisonAvoidance, DefaultEnemyBehavior, DebugPanel, DebugPoisonActions×3, DebugPoisonView) |
| "FireAgents" | 1 (FireAgent.gd) | 2 (PlayerSpell, FireAgent) |
| "carts" | 1 (Cart.gd) | 2 (Player, PlayerCombat) |
| "trees" | 1 (TreeWood.gd) | 0 |
| "fallen_trees" | 1 (TreeWood.gd) | 0 |
| "spell_ui" | 1 (SpellUI.tscn) | 1 (Player.gd) |
| "logistics_npcs" | 1 (LogisticsNPC.gd) | 0 |
| "allies" | 0 (登録元未確認) | 1 (LogisticsNPC.gd) |
| "spawn_controller" | 0 (登録元未確認) | 1 (DebugSpawnView.gd) |
| "Player" (大文字) | 0 (登録元未確認) | 1 (SwarmSpawner.gd) |
