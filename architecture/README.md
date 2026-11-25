# Architecture Chart Workflow

python tools/architecture/generate_all_charts.py
python tools/architecture/flow_trace.py entries --top 60
python tools/architecture/generate_all_charts.py --trace 実際のクラス名.実際の関数名 --depth 8 --cap 100

Godotプロジェクトの実装構造・Runtime Path・Gameplay Eventを調査するためのツール群です。

## 1. 方針

既存スクリプトの解析ロジックは変更しません。追加するのは、複数のスクリプトをまとめて実行する `generate_all_charts.py` だけです。

| ツール | 役割 | 使用タイミング |
|---|---|---|
| `generate_charts_v2.py` | クラス・依存関係・Signal・Sceneなどの全体構造を抽出 | 基本的に毎回 |
| `flow_trace.py` | 指定した起点から関数・Signal・Handlerの経路を抽出 | 特定のRuntime Pathを調査 |
| `flow_chart.py` | 人が定義したGameplay Eventと実装上の根拠を照合 | Gameplay上の意味と実装の対応を調査 |
| `pack.py` | 特定クラスと関連情報をAI向けにまとめる | 実装変更をAIに依頼 |
| `generate_all_charts.py` | 上記3種類のチャート生成をまとめて実行 | 共通入口 |

**基本原則**

- 構造上の接続関係は静的解析で抽出します。
- LLMに存在しない関数・クラス・Signalや矢印を作らせません。
- LLMは必要に応じてラベル付け、意味的な分類、実装候補の選択を担当します。
- 全体構造と個別Runtime Pathを分けて保存します。
- ピンポイント調査のたびにGameplay Skeletonを作る必要はありません。

---

## 2. ディレクトリ構成

既存ファイルはそのまま残し、次のファイルを追加します。

```text
tools/
  architecture/
    apply_change.py
    flow_chart.py
    flow_trace.py
    generate_charts_fixed.py
    generate_charts_v2.py
    pack.py

    generate_all_charts.py   # 新規追加

    output/
      classes.json
      dependencies.json
      signals.json
      scenes.json
      unresolved.json
      domains.json
      domains.mmd
      ...
      
  flow_skeleton.txt          # 必要なGameplay調査時だけ作成
```

`output/` は生成先です。古い出力が残っている場合は、必要に応じて削除してから実行してください。

---

## 3. 統合スクリプト

...

---

## 4. 初回セットアップ

プロジェクトのルートディレクトリで実行します。

### Python環境

```powershell
python --version
```

### Graphviz

SVG出力にはGraphvizの `dot` が必要です。

```powershell
dot -V
```

未導入の場合は、GraphvizをインストールしてPATHを通してください。GraphvizがなくてもDOTファイルなどは生成できます。

### 初回全体生成

```powershell
python tools/architecture/generate_all_charts.py
```

テストコードも含めて解析したい場合：

```powershell
python tools/architecture/generate_all_charts.py --with-tests
```

通常はテストコードを除外した状態を基準にします。

### 生成物の確認

```powershell
Get-ChildItem tools/architecture/output
```

まず確認するファイル：

- `report.json`
- `domains.mmd`
- `llm_flow_input.md`
- `dependencies.json`
- `signals.json`
- `unresolved.json`

---

## 5. 使用例

### Case 1：プロジェクト全体の現状を把握する

**目的：** 現在の実装全体を調査し、Architecture Baselineを作成する。

```powershell
python tools/architecture/generate_all_charts.py
```

生成される主な情報：

- 全クラス
- クラス間依存
- 継承関係
- Signalの宣言・発行・受信
- Scene構造
- Domain分類
- 未解決の参照

これは実装の節目ごとに実行します。

全関数を個別にTraceする必要はありません。

---

### Case 2：古い実装・情報のない機能を調査する

**目的：** 既存資料や設計情報がなく、どこに実装されているか分からない機能を探す。

最初に全体構造を更新します。

```powershell
python tools/architecture/generate_all_charts.py
```

次に、起点候補を調べます。

```powershell
python tools/architecture/flow_trace.py entries --top 60
```

これは到達可能な関数が多い起点候補を表示します。

候補から関連しそうなクラス・関数を見つけたら、その名前を使ってTraceします。

```powershell
python tools/architecture/flow_trace.py trace --from ClassName.function_name --depth 6
```

`ClassName.function_name` は実際に `entries` で確認した名前に置き換えてください。

複数の候補を同時に調べる場合：

```powershell
python tools/architecture/flow_trace.py trace --from ClassA.function_a ClassB.function_b --depth 6
```

調査したいクラスが分かったら、必要に応じてAI向けの実装情報をまとめます。

```powershell
python tools/architecture/pack.py --task "この機能の現在の実装経路と責務を調査し、既存設計を変更せずに説明してください" --target ClassName
```

**情報がない場合の注意**

静的解析が調べるのは現在のプロジェクトに存在するコードです。既に削除された古い実装やGit履歴の内容を自動復元するものではありません。

現在のコードに痕跡がない場合は、`unresolved.json`、既存資料、Git履歴などを別途確認します。根拠が見つからないものは「不明」として残します。

---

### Case 3：毒システムのRuntime Pathを調べる

**目的：** Poisonの処理がどこから入り、どのクラス・関数を経由して状態変化や死亡、生態系への影響に接続するか確認する。

まず全体構造を更新します。

```powershell
python tools/architecture/generate_all_charts.py
```

次に、毒システムの実装クラスを探します。

```powershell
python tools/architecture/flow_trace.py entries --top 100
```

該当するクラス名・関数名を確認したら、統合スクリプトからTraceします。

```powershell
python tools/architecture/generate_all_charts.py --trace ActualPoisonClass.actual_function --depth 8 --cap 100
```

上記の `ActualPoisonClass.actual_function` は、実際のコードに存在する起点に置き換えてください。

複数の起点を使う場合：

```powershell
python tools/architecture/generate_all_charts.py --trace ActualPoisonClass.apply_poison ActualPoisonClass.update_poison ActualPoisonClass.remove_poison --depth 8 --cap 120
```

確認対象：

- 毒の付与
- 毒状態の更新
- 毒の蓄積・減衰
- DamageやStatusとの接続
- Entityの状態変化
- 死亡処理との接続
- Ecologyへの接続

ここでは `flow_trace.py` だけで十分です。

**毒システム専用のSkeletonや専用チャート生成機能は追加しません。**

Runtime Pathだけで意味が読み取れない場合に限り、次のGameplay Skeleton方式を使います。

---

### Case 4：Gameplay Eventと実装経路を対応させる

**目的：** 複数のクラスにまたがる処理について、ゲーム上の出来事と実装上の根拠を照合する。

これは `flow_trace` だけではGameplay上の意味を十分に表せない場合に使います。

まずSkeletonを作ります。

**ファイル名：`tools/flow_skeleton.txt`**

```text
# id | Gameplay Event | 次のid

player_attack | Playerが対象を攻撃する | damage
damage | 対象にダメージが発生する | death
death | 対象が死亡する | ecology
ecology | 死亡が生態系に反映される |
```

Skeletonの内容は人が定義します。矢印はLLMに考えさせません。

次にEvidence Promptを作成します。

```powershell
python tools/architecture/generate_all_charts.py --skeleton tools/flow_skeleton.txt
```

出力：

```text
tools/architecture/output/evidence_prompt.md
```

このファイルをローカルLLMに渡します。

LLMには、候補一覧から各イベントに対応するクラス・Signalを選択させます。候補にない名前は作らせません。

返答を次のファイルに保存します。

**ファイル名：`tools/architecture/output/evidence.json`**

その後、検証します。

```powershell
python tools/architecture/generate_all_charts.py --skeleton tools/flow_skeleton.txt --evidence tools/architecture/output/evidence.json
```

出力：

- `flow_final.dot`
- `flow_final.svg`
- `flow_final_report.md`

`flow_final_report.md` では、実装上の接続が確認できた辺、未接続の辺、根拠がないイベントなどを確認します。

---

### Case 5：特定クラスを変更するためのAI向け資料を作る

**目的：** 既存の実装構造を把握したうえで、クラウドLLMに修正を依頼する。

まずチャートを更新します。

```powershell
python tools/architecture/generate_all_charts.py
```

次に、対象クラスと追加で本文を含めたいクラスを指定します。

```powershell
python tools/architecture/pack.py --task "毒の状態更新処理を確認し、既存APIを維持したまま必要な修正を提案してください" --target ActualPoisonClass --extra Entity DamageSystem
```

出力：

```text
tools/architecture/output/pack_ActualPoisonClass.md
```

このMarkdownをそのままAIに渡します。

`--target` は修正対象クラスです。`--extra` は本文も含めたい追加クラスです。

関連クラスを大量に追加するより、実際に関係するクラスだけを指定してください。

---

## 6. どのツールを使うべきか

| 調査したいこと | 使用するもの |
|---|---|
| 現在の実装全体を知りたい | `generate_charts_v2.py` |
| 古い機能の起点を探したい | `flow_trace.py entries` |
| 特定関数から何が起こるか知りたい | `flow_trace.py trace` |
| Gameplay Eventと実装の対応を確認したい | `flow_chart.py` |
| AIに実装変更を依頼したい | `pack.py` |
| 全体と指定Traceを一度に更新したい | `generate_all_charts.py` |

### ピンポイント機能に毎回専用機能を作らない

以下は新しい機能を追加しません。

- Poison専用チャート
- Fire専用チャート
- Territory専用チャート
- Predator/Prey専用チャート
- Spawn専用チャート

これらは既存の `flow_trace.py` に実際の起点を指定すれば調査できます。

Gameplay上のイベント順序とコードの対応を明示する必要がある場合だけ、共通の `flow_chart.py` を使います。

---

## 7. 運用ルール

### 全体構造の更新

実装を大きく変更した後は：

```powershell
python tools/architecture/generate_all_charts.py
```

### 特定機能の調査

```powershell
python tools/architecture/generate_all_charts.py --trace ActualClass.actual_function --depth 8 --cap 100
```

### Gameplay Eventの検証

SkeletonとEvidenceが必要な場合だけ実行します。

### 出力の保存

重要な実装区切りでは、`output/` を別のBaselineフォルダにコピーして保存します。

例：

```powershell
Copy-Item tools/architecture/output tools/architecture/baseline_poison_closed -Recurse
```

次回生成時には `output/` が更新されます。過去のBaselineは比較用に残します。

### チャートの読み方

- チャートに辺がある：静的解析上、その接続を示す根拠がある。
- チャートに辺がない：必ずしも実行時に接続されないとは限らない。
- `flow_trace.py` は型が推定できない動的なインスタンス呼び出しなどを追跡できない場合がある。
- `flow_chart.py` の「未接続」は、実装上の不具合と即断せず、根拠の選び間違いや静的解析の限界も確認する。

したがって、チャートはRuntime Testの代替ではなく、実装経路を調査するための補助資料です。

---

## 8. 今後の拡張方針

現時点では、新しい統合チャート生成エンジンは作りません。

まずは以下の3層を別々に生成します。

1. Architecture：クラス・依存関係・Signal・Scene
2. Runtime Trace：関数・Signal・Handlerの経路
3. Gameplay/Event：人が定義した出来事と実装根拠

これらを共通のクラス名・関数ID・Signal名で参照します。

その後、実際に複数のチャートを横断して調査する必要が出た段階で、LLMによる意味的な統合を検討します。

**当面の目標は、LLMに新しい矢印を発見させることではなく、機械的に確認できた実装経路を、Gameplay上の意味と結びつけて読みやすくすることです。**
