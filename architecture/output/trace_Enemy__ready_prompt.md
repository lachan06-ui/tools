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

### Enemy._ready  (scenes/Characters/Enemies/Enemy.gd:52)
sig: func _ready():
calls: Enemy._assemble_dynamic_visuals, Enemy._setup_stats_from_database, Enemy._setup_targetable

### Enemy._assemble_dynamic_visuals  (scenes/Characters/Enemies/Enemy.gd:162)
sig: func _assemble_dynamic_visuals():
doc: 💡 SpeciesDefinition.visual_scene からモデルをインスタンス化する。 / visual_scene が null の場合はプリミティブフォールバックを使用。
calls: Enemy._get_autoload

### Enemy._setup_stats_from_database  (scenes/Characters/Enemies/Enemy.gd:81)
sig: func _setup_stats_from_database():
calls: Enemy._get_enemy_db

### Enemy._setup_targetable  (scenes/Characters/Enemies/Enemy.gd:72)
sig: func _setup_targetable():
calls: Enemy._get_enemy_db

### Enemy._get_autoload  (scenes/Characters/Enemies/Enemy.gd:208)
sig: func _get_autoload(autoload_name: String) -> Node:

### Enemy._get_enemy_db  (scenes/Characters/Enemies/Enemy.gd:66)
sig: func _get_enemy_db() -> Node:
