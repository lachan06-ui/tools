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

### Entity.add_poison_amount  (scenes/Core/Entity.gd:102)
sig: func add_poison_amount(amount: float, duration: float = PoisonStatusEffect.POISON_DOSE_DURATION) -> float:
calls: Entity.get_poison_resistance, GroupPoisonState.add_exposure, シグナル Entity.poison_received

### Entity.get_poison_resistance  (scenes/Core/Entity.gd:144)
sig: func get_poison_resistance() -> float:
calls: GroupPoisonState.get_tolerance

### GroupPoisonState.add_exposure  (core/systems/ecology/GroupPoisonState.gd:13)
sig: static func add_exposure(group_id: String, species_id: String, applied_amount: float) -> void:
calls: GroupPoisonState._key

### GroupPoisonState.get_tolerance  (core/systems/ecology/GroupPoisonState.gd:28)
sig: static func get_tolerance(group_id: String, species_id: String) -> float:
calls: GroupPoisonState._get_species, GroupPoisonState._key

### GroupPoisonState._key  (core/systems/ecology/GroupPoisonState.gd:64)
sig: static func _key(group_id: String, species_id: String) -> String:

### Enemy._on_poison_received  (scenes/Characters/Enemies/Enemy.gd:161)
sig: func _on_poison_received(applied_amount: float) -> void:
calls: GroupPoisonState.add_exposure

### GroupPoisonState._get_species  (core/systems/ecology/GroupPoisonState.gd:67)
sig: static func _get_species(species_id: String) -> SpeciesDefinition:
