# 依頼
次の関数それぞれが「何をするか」を、日本語20字以内で書いてください。
根拠は、関数名・シグネチャ・コメント・呼び先の名前だけです。コードの中身を想像で補わないでください。
読み取れない場合は「不明」と書いてください。

## 出力（JSONのみ。説明文・コードフェンスは書かない。出力は { で始まり } で終わる）
{"labels":{"Class.func":"20字以内の説明"}}

## ルール
- キーは、下の一覧にある関数ID（Class.func）をそのまま使う。一覧にないIDを書かない。
- 「〜する」の形で、動作を書く（例：種の個体数を日次で更新する）。

## 関数一覧

### EnemyAI.tick  (scenes/Characters/Enemies/EnemyAI.gd:48)
sig: func tick(delta: float) -> void:
calls: EnemyAI._acquire_food_source, EnemyAI._acquire_target, EnemyAI._apply_poison_steering, EnemyAI._is_attached, EnemyAI._is_frozen, EnemyAI._is_knockbacked, EnemyAI._stop_movement, EnemyAI._transition_state, EnemyAI._update_attack, EnemyAI._update_feed, EnemyAI._update_movement, EnemyAI._update_return, EnemyAI._validate_owner

### EnemyAI._acquire_food_source  (scenes/Characters/Enemies/EnemyAI.gd:286)
sig: func _acquire_food_source() -> Corpse:

### EnemyAI._acquire_target  (scenes/Characters/Enemies/EnemyAI.gd:124)
sig: func _acquire_target() -> Entity:

### EnemyAI._apply_poison_steering  (scenes/Characters/Enemies/EnemyAI.gd:230)
sig: func _apply_poison_steering() -> void:
calls: PoisonAvoidance.steer

### EnemyAI._is_attached  (scenes/Characters/Enemies/EnemyAI.gd:257)
sig: func _is_attached() -> bool:
calls: EnemyAI._get_autoload

### EnemyAI._is_frozen  (scenes/Characters/Enemies/EnemyAI.gd:263)
sig: func _is_frozen() -> bool:

### EnemyAI._is_knockbacked  (scenes/Characters/Enemies/EnemyAI.gd:266)
sig: func _is_knockbacked() -> bool:

### EnemyAI._stop_movement  (scenes/Characters/Enemies/EnemyAI.gd:213)
sig: func _stop_movement() -> void:

### EnemyAI._transition_state  (scenes/Characters/Enemies/EnemyAI.gd:98)
sig: func _transition_state(target: Entity, food_source: Corpse) -> void:
calls: EnemyAI._get_return_target, EnemyAI._get_territory_radius

### EnemyAI._update_attack  (scenes/Characters/Enemies/EnemyAI.gd:217)
sig: func _update_attack(delta: float, target: Entity) -> void:

### EnemyAI._update_feed  (scenes/Characters/Enemies/EnemyAI.gd:174)
sig: func _update_feed(food_source: Corpse) -> void:
calls: EnemyAI._consume_food, EnemyAI._stop_movement

### EnemyAI._update_movement  (scenes/Characters/Enemies/EnemyAI.gd:140)
sig: func _update_movement(target: Entity) -> void:
doc: --- Per-state behaviours ---

### EnemyAI._update_return  (scenes/Characters/Enemies/EnemyAI.gd:157)
sig: func _update_return() -> void:
calls: EnemyAI._get_return_target, EnemyAI._stop_movement

### EnemyAI._validate_owner  (scenes/Characters/Enemies/EnemyAI.gd:248)
sig: func _validate_owner() -> bool:

### PoisonAvoidance.steer  (core/systems/ecology/PoisonAvoidance.gd:47)
sig: static func steer(owner: Node3D, base_direction: Vector3) -> Vector3:
doc: base_direction に毒回避を混ぜた移動方向を返す。
calls: PoisonAvoidance.compute

### EnemyAI._get_autoload  (scenes/Characters/Enemies/EnemyAI.gd:251)
sig: func _get_autoload(autoload_name: String) -> Node:

### EnemyAI._get_return_target  (scenes/Characters/Enemies/EnemyAI.gd:86)
sig: func _get_return_target() -> Vector3:
calls: EnemyAI._get_territory_state

### EnemyAI._get_territory_radius  (scenes/Characters/Enemies/EnemyAI.gd:92)
sig: func _get_territory_radius() -> float:
calls: EnemyAI._get_territory_state

### EnemyAI._consume_food  (scenes/Characters/Enemies/EnemyAI.gd:192)
sig: func _consume_food(food_source: Corpse) -> void:
calls: EnemyAI._get_territory_radius, NutrientCycle.excrete

### PoisonAvoidance.compute  (core/systems/ecology/PoisonAvoidance.gd:9)
sig: static func compute(owner: Node3D) -> Dictionary:
calls: GroupPoisonState.get_avoidance_weight, GroupPoisonState.get_tolerance

### EnemyAI._get_territory_state  (scenes/Characters/Enemies/EnemyAI.gd:76)
sig: func _get_territory_state() -> TerritoryState:

### NutrientCycle.excrete  (core/systems/ecology/NutrientCycle.gd:14)
sig: static func excrete(region_id: String, _center: Vector3, _radius: float, units: float) -> void:
doc: 食べた栄養 -> フンとして活動範囲に平均配分。 / TODO: Chunkプールができたら radius 内のChunkへ配分する(今はRegion単位)。
calls: NutrientCycle._add_detritus

### GroupPoisonState.get_avoidance_weight  (core/systems/ecology/GroupPoisonState.gd:54)
sig: static func get_avoidance_weight(group_id: String, species_id: String) -> float:
doc: 正: 毒域を避ける強さ / 負: 毒域へ寄る強さ
calls: GroupPoisonState._get_species, GroupPoisonState.get_tolerance

### GroupPoisonState.get_tolerance  (core/systems/ecology/GroupPoisonState.gd:28)
sig: static func get_tolerance(group_id: String, species_id: String) -> float:
calls: GroupPoisonState._get_species, GroupPoisonState._key

### NutrientCycle._add_detritus  (core/systems/ecology/NutrientCycle.gd:17)
sig: static func _add_detritus(region_id: String, units: float) -> void:

### GroupPoisonState._get_species  (core/systems/ecology/GroupPoisonState.gd:67)
sig: static func _get_species(species_id: String) -> SpeciesDefinition:

### GroupPoisonState._key  (core/systems/ecology/GroupPoisonState.gd:64)
sig: static func _key(group_id: String, species_id: String) -> String:
