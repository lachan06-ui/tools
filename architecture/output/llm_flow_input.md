# 依頼
下の【事実資料】だけを根拠に、このゲームの「プレイヤー視点のゲームプレイフロー」を、次のJSONだけで出力してください。
説明文・Markdown・コードフェンスは書かないでください。出力は { で始まり } で終わります。

## 出力スキーマ
{"nodes":[{"id":"n1","label":"出来事を日本語で15字程度","evidence":["資料に出てくるクラス名またはシグナル名"]}],
 "edges":[{"from":"n1","to":"n2","kind":"signal または direct または guess","evidence":"シグナル名（kind が signal のときだけ）"}],
 "unknown":["資料から読み取れなかった点"]}

## ルール
- ノードは最大15個。クラス名ではなく「出来事」を書く（例：敵が死ぬ／死体が残る／栄養が土に戻る）。
- evidence は、資料にある名前をそのまま写す。資料にない名前を書かない。作らない。
- 辺の kind:
  - signal: 資料の「ドメイン間のイベント（シグナル）」にある関係。evidence にそのシグナル名
  - direct: 資料の「ドメイン間の直接呼び出し」にある関係
  - guess: 資料に根拠がないが、流れとして必要なもの
- 迷ったら guess にする。根拠を捏造しない。
- 資料から読み取れなかった点は unknown に書く。


# 事実資料

## ドメインと所属クラス
### combat
- AttachSystem
- DamageEvent
- DamageSystem
- TargetSystem
- Targetable

### core
- CarryHelper
- Entity
- EventBus
- GameState
- WorldManager
- WorldState

### crafting
- CraftingSystem
- CraftingUI

### ecology
- AreaDefinition
- BioRegionDefinition
- BioRegionInstance
- BiomeDatabase
- EcologyManager
- EcologyObservationUI
- EcologySerializer
- EcologySimulation
- EcologyTraceFeedback
- EnvironmentState
- FireAgent
- ForestBioRegionDefinition
- GeneticDriftCalculator
- GenusDefinition
- GroupPoisonState
- GroupSkillState
- MountainForestBioRegionDefinition
- NutrientCycle
- PoisonAvoidance
- PopulationCalculator
- SpatialRegionResolver
- SpawnController
- SpawnGroundResolver
- SpawnLocationResolver
- SpawnRequest
- SpeciesDatabase
- SpeciesDefinition
- SpeciesRelation
- SpeciesState
- TerritoryState
- UtilityScoringEngine

### enemy
- BehaviorProfile
- BehaviorRegistry
- Boss
- Corpse
- DefaultEnemyBehavior
- Enemy
- EnemyAI
- EnemyBehavior
- EnemyDatabase
- EnemySkill
- EnemySkillSystem
- EnemySpawner
- EnemyStats
- SkillRegistry
- SwarmSpawner

### feedback
- Effects
- Indicator
- IndicatorFactory
- IndicatorManager

### item
- DropEntry
- DropTable
- EconomyManager
- ItemData
- ItemDatabase

### map
- GenerateMapFromDEM
- InteractionObject
- InteractionSystem
- MapDatabase
- MapKnowledgeManager
- MapProvider
- MapReadingModeUI
- ObjectDatabase
- ObjectGenerator
- PoisonArea
- SpatialArea3D
- SpatialBioRegion3D
- SpecialRoomGenerator
- TreeGenerator
- TreeWood
- WorldMap
- WorldRoot

### npc
- Cart
- LogisticsNPC

### player
- Player
- PlayerCombat
- PlayerDodge
- PlayerLook
- PlayerMovement
- PlayerMovementInput
- PlayerSpell
- PlayerStats
- WorldCamera

### quest
- QuestGenerator
- QuestManager

### save
- SaveManager
- SaveSystem

### spell
- SpellCard
- SpellMasteryManager
- SpellUI

### status
- PoisonStatusEffect
- StatusComponent
- StatusEffect

### time
- TimeSystem

## ドメイン間のイベント（シグナル）
- core → player: spell_discovered  [GameState → PlayerSpell]
- spell → player: spell_discovered  [SpellMasteryManager → PlayerSpell]
- core → map: region_changed  [WorldManager → WorldRoot]
- ecology → map: swarm_event_requested  [EcologyManager → WorldMap]
- player → crafting: crafting_interrupted  [PlayerCombat → CraftingUI]
- crafting → player: crafting_completed  [CraftingSystem → PlayerMovement]
- crafting → player: crafting_started  [CraftingSystem → PlayerMovement]
- map → ecology: spawn_requested  [WorldMap → SpawnController]

## ドメイン間の直接呼び出し（クラス対の数が多い順）
- enemy → ecology (21): EnemyDatabase->SpeciesDatabase, EnemyDatabase->SpeciesDefinition, Corpse->EcologyManager, Corpse->EnvironmentState
- map → ecology (15): PoisonArea->EnvironmentState, SpatialArea3D->SpatialRegionResolver, SpatialBioRegion3D->SpatialRegionResolver, WorldMap->SpeciesDatabase
- core → ecology (9): GameState->SpeciesDatabase, GameState->SpeciesDefinition, WorldManager->SpeciesDatabase, WorldManager->SpeciesDefinition
- player → combat (9): Player->TargetSystem, PlayerCombat->Targetable, PlayerCombat->AttachSystem, PlayerCombat->DamageEvent
- enemy → core (7): Corpse->WorldManager, DefaultEnemyBehavior->Entity, Enemy->WorldManager, EnemyAI->WorldManager
- ecology → enemy (6): SpeciesDefinition->BehaviorProfile, SpeciesDefinition->EnemyDatabase, SpeciesDefinition->EnemyStats, EcologySimulation->EnemyStats
- map → combat (5): InteractionObject->Targetable, InteractionObject->DamageEvent, InteractionObject->DamageSystem, InteractionSystem->AttachSystem
- map → core (5): InteractionObject->Entity, ObjectGenerator->WorldManager, PoisonArea->Entity, WorldMap->WorldManager
- map → enemy (5): InteractionSystem->Corpse, PoisonArea->Corpse, PoisonArea->Enemy, WorldMap->EnemySpawner
- player → core (5): Player->CarryHelper, PlayerCombat->GameState, PlayerCombat->Entity, PlayerMovement->GameState
- ecology → core (4): EcologyManager->WorldManager, SpatialRegionResolver->WorldManager, SpawnController->WorldManager, EcologyObservationUI->WorldManager
- enemy → combat (4): Corpse->Targetable, Enemy->Targetable, EnemySkillSystem->DamageEvent, EnemySkillSystem->DamageSystem
- quest → ecology (4): QuestGenerator->SpeciesDatabase, QuestGenerator->SpeciesDefinition, QuestGenerator->EcologyManager, QuestGenerator->SpeciesState
- save → core (4): SaveManager->WorldManager, SaveSystem->GameState, SaveSystem->WorldManager, SaveSystem->WorldState
- core → enemy (3): GameState->EnemyStats, WorldManager->Corpse, WorldManager->EnemySpawner
- core → status (3): Entity->PoisonStatusEffect, Entity->StatusComponent, Entity->StatusEffect
- ecology → map (3): EcologyManager->MapDatabase, PoisonAvoidance->PoisonArea, SpatialRegionResolver->SpatialArea3D
- map → player (3): PoisonArea->Player, WorldRoot->WorldCamera, WorldRoot->Player
- core → player (2): GameState->Player, WorldManager->Player
- enemy → map (2): DefaultEnemyBehavior->PoisonArea, EnemySpawner->MapDatabase
- enemy → player (2): Enemy->Player, EnemyAI->Player
- player → enemy (2): PlayerCombat->Enemy, PlayerSpell->Enemy
- player → map (2): Player->InteractionSystem, PlayerCombat->TreeWood
- player → npc (2): Player->Cart, PlayerCombat->Cart
- quest → enemy (2): QuestGenerator->EnemyDatabase, QuestGenerator->EnemyStats
- save → ecology (2): SaveManager->EcologyManager, SaveSystem->EcologyManager
- save → quest (2): SaveSystem->QuestGenerator, SaveSystem->QuestManager
- spell → core (2): SpellMasteryManager->GameState, SpellUI->GameState
