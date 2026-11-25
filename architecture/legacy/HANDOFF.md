# 構造チャート ツール引き継ぎ

置き場所: `tools/architecture/HANDOFF.md`
AI IDE が使えなくなった後も、無料のChatGPT/Claude とローカルLLMで同じ規約・同じ検証で作業を続けるための手引き。

## 1. 方針（変えない）

- 構造（依存・シグナル・グループ・シーン）はスクリプトで抽出する。LLMは意味付けの「提案」だけ。
- 関係の記述（AがBを呼ぶ、など）はAIに書かせない。`output/dependencies.json` を正本にする。
- AIの出力は、テストとチャートの差分で検証する。そのまま信用しない。
- クラウドAIへの依頼は1回1目的。大きな依頼は往復とやり直しが増える。
- ドメイン（機能タグ）は人が確定する。ローカルLLMの結果は提案扱いで、自動上書きしない。

## 2. 構成

```
tools/architecture/
  generate_charts_v2.py     抽出本体（正規表現ベース、クラス単位）
  tests/test_generate_charts.py   フィクスチャテスト（pytest）
  output/                   生成物（コミット前に再生成）
  verify/                   IDEや手作業の調査報告
  HANDOFF.md                このファイル
tools/feature_tags.json     クラス名 -> タグ（先頭タグが主ドメイン）
```

## 3. コマンド

```
# 全体生成（ルートで）
python tools/architecture/generate_charts_v2.py --inventory tr_1_inventory.md --brief tools/project_brief.md

# 1クラスの周辺だけ
python tools/architecture/generate_charts_v2.py --focus <クラス名> --depth 1

# テスト
python -m pytest tools/architecture/tests -q
```

抽出ロジックを変えたら、先にテストを足してから直す。チャートが静かに間違うのが最大のリスク。

## 4. 出力の読み方

- `domains.svg` / `domains.mmd`: ドメイン間の粗い図。実線=直接参照（数字はクラス対の数）、青い点線=シグナル（ラベルがシグナル名）、矢印は依存する側→される側。
- `report.json`: 件数の要約。`unresolved_kinds` の内訳を見る。
- `dependencies.json`: 全エッジ（source, target, kind, line, detail）。signal 辺の line は受信側の connect 行。
- `signals.json`: シグナルごとの発行元・受信側。`note` に「発行元が検出されない」等。多くは「定義だけで未実装」。
- `unresolved.json`: 解決できなかったもの。`dynamic_*`（動的呼び出し）、`group_no_member`（登録元のないグループ。`similar` に大文字小文字違いの候補）、`ambiguous_*` / `foreign_bare_*`（シグナルの帰属不明）、`export_scene_*`、`preload_missing`。
- `llm_flow_input.md`: ローカルLLMにゲームプレイのフロー図を書かせるための事実資料。

## 5. 抽出の限界（知っておく）

- 正規表現ベースで、関数単位の呼び出し関係は取れない（クラス単位）。
- 取れない/取りにくい: `.tres` 内のシーン割り当て、変数経由の `call` / `get_node` / `load` / `emit_signal`（`unresolved.json` に件数のみ）、`has_method` ガード、インナークラスの帰属、`is_in_group` 以外の条件分岐。
- `class_use` は型注釈も数えるので、実際の呼び出しより多めに出る。
- 名前だけで解決したシグナルは `signals.json` の `resolved_by_name_only` で分かる。
- グループ名は大文字小文字を区別する。`group_no_member` の `similar` に出たら綴り違いを疑う。

## 6. ドメイン語彙（暫定。人が確定する）

正本は feature_tags.json の tag_descriptions
図から除外: debug
解消対象: untagged（役割が決まったクラスから `feature_tags.json` に追加）

未確定の判断:
- `item`（実体は `core/databases/` のDB群）を `data` に改名するか
- `spawn`・`crafting` を独立ドメインにするか、`ecology`・`item` に含めるか

ルール:
- Role/タグは「何をするか」で付ける。ファイル名や実装手段（util, helper）で付けない。
- 語彙は固定リストから選ぶ。自由記述にしない（表記揺れでグループ化が壊れる）。

## 7. クラウドAI（無料ChatGPT/Claude）への依頼テンプレート

```
# 依頼（1回1目的）
目的: <1文で>
対象: <クラス名 / ファイル>
制約: <守ること。例: 既存シグナル名は変えない>

## 材料
- 要項: <貼る>
- ドメイン図: <domains.mmd の該当部分、または focus の dot>
- 関連クラスのシグネチャ: <貼る>
- 変更対象の本文: <貼る>

## 出力形式（厳守）
1. 変更は unified diff、または関数単位の丸ごと置換のどちらかで出す
2. テストは tests/ に追加する（形式は既存に合わせる: <使っているテスト方式を記入>）
3. 変更したクラスの feature_tags.json の差分も出す
4. 足りないファイルがあれば、推測で書かず、ファイル名だけ挙げる

## 最後に
<やってほしいことを1行>
```

適用後の手順: diff適用 -> テスト実行 -> チャート再生成 -> 差分確認（新しい `unresolved`、消えたエッジ）。
I/Fを持つクラスの変更は、他の実装と別の依頼にする。

## 8. 調査の依頼テンプレート（AI IDE / ローカルLLM / 手作業）

共通ヘッダ:
```
【読み取り専用。既存ファイルは変更しない。保存先は tools/architecture/verify/ のみ】
- grep -n で行番号を取り、該当行の前後だけ開く。ファイル全文は読まない
- 確認できないものは「未確認」と書く。推測で埋めない
- 対象は core/ data/ scenes/ の .gd と .tscn
- 件数0は「0件」とだけ書く。多い場合は件数と代表例だけ
```

- グループ棚卸し: `add_to_group` / `is_in_group` / `call_group` / `get_nodes_in_group` / `get_first_node_in_group` と、.tscn の `groups=[...]`。形式「ファイル:行 | 関数 | グループ名」と、グループ別の登録/呼び出しファイル数。
- PackedScene: `@export` の PackedScene 変数と `.instantiate()`、.tscn / .tres での割り当て。
- 動的呼び出し: `call(` / `callv(` / `call_deferred(` / `get_node(` / `emit_signal(` / `connect(` / `load(` の第1引数がリテラルでないもの。パターン別に件数と代表例5件。
- 抜き取り照合: `dependencies.json` から signal 6 / class_use 6 / autoload_use 3 / scene_ref 2 を偏らず選び、実コードで OK / NG / 不明 を判定。NGは原因1行。

ローカル14B（段階2、ゴールデンセットを作ってから）:
- 入力はシグネチャ・docstring・呼び出し先の名前のみ（4〜8kトークン以内）。temperature 0。
- 出力は固定スキーマ: `{"class": str, "role": <語彙リストの1語>, "summary": <60字以内>, "evidence": ["file:line"]}`
- AST/`classes.json` に存在しない名前、語彙外の role を出したら自動で棄却する。
- キャッシュのキーは「ソースハッシュ + モデル名 + プロンプトのバージョン」。結果は提案で、確定は人。

## 9. 検証ルール

- 出力は機械で検証できる形にする（名前の実在、行番号の一致）。落ちたものは棄却し、人が読むのは通ったものだけ。
- 調査報告は、人が各2件ほど実コードと見比べてから使う。
- 失敗ログはローカルLLMで要約して返す（全文は貼らない）。

## 10. 段階計画

1. 今〜5千行: 抽出スクリプト + テスト + ドメイン語彙の固定 + チャートを読む習慣
2. 5千〜1万行: ローカルLLMでラベル提案（ゴールデンセット20〜30関数で一致率を測る）、pack（要項・チャート・シグネチャを1つにまとめる）、出力サイズの上限
3. 2万行〜: slice（条件・方向での絞り込み）、パッケージ境界（公開I/Fファイル）、内部importの禁止をスクリプトで検査

チャートやインデックスの生成はコミット前に自動実行し、手動更新にしない。