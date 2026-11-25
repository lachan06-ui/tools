# Layer 0: Primitives & Data Atoms (base classes, data structures, or interface definitions)

## EventBus
### Purpose
- Central signal bus for decoupled communication across the game engine.
### Related Files
- core/autoload/EventBus.gd
### Responsibilities
- Centralized signaling for entity, combat, ecosystem, world, quest, time, and UI events.
### Public API Methods
- Not Found
### Signals
- entity_died(entity: Node)
- entity_spawned(entity: Node)
- damage_dealt(event: DamageEvent)
- player_died()
- distress_signal_triggered(position: Vector3)
- species_population_changed(map_id: String, species_id: String, new_pop: int)
- map_changed(from_id: String, to_id: String)
- quest_completed(quest_id: String)
- quest_failed(quest_id: String)
- day_passed(day_number: int)
- hud_refresh_requested()
- map_reading_toggled(is_open: bool)
- recipe_discovered(recipe_id: String)
- crafting_started(recipe_id: String, duration: float)
- crafting_completed(recipe_id: String, success: bool, result_item: Dictionary)
- crafting_interrupted(recipe_id: String)
- settlement_upgraded(settlement_id: String, new_tier: int)
### Properties
- Not Found
### Owned Data
- Not Found
### Depends On
- Entity
- DamageEvent
### Used By
- CraftingSystem
- CraftingUI
- Enemy
- LogisticsNPC
- MapKnowledgeManager
- MapReadingModeUI
- PlayerCombat
- PlayerMovement
### Save Data
- None
### Notes
- None

## StatusComponent
### Purpose
- Manages the attachment and removal of status effects on an entity.
### Related Files
- core/components/StatusComponent.gd
### Responsibilities
- Handling addition, removal, and retrieval of active statuses.
### Public API Methods
- add_status(effect: StatusEffect) -> void
- remove_status(effect_id: String) -> void
- has_status(effect_id: String) -> bool
- set_status_stacks(effect_id: String, stacks: int, duration: float = 0.0) -> void
- add_poison_amount(amount: float, duration: float = PoisonStatusEffect.POISON_DOSE_DURATION) -> float
- get_poison_amount() -> float
- get_poison_stacks() -> int
- get_poison_effect() -> PoisonStatusEffect
- get_status_stacks(effect_id: String) -> int
- tick(delta: float) -> void
- apply(effect: StatusEffect) -> void
- remove(effect_id: String) -> void
- has_effect(effect_id: String) -> bool
- get_effect(effect_id: String) -> StatusEffect
- get_all_ids() -> Array
- clear() -> void
### Signals
- Not Found
### Properties
- Not Found
### Owned Data
- _effects: Dictionary
### Depends On
- StatusEffect
- Player
- Enemy
- Corpse
- PoisonStatusEffect
### Used By
- DamageSystem
- DebugPoisonActions
- DebugPoisonView
- Entity
- Player
- PlayerMovement
- StatusEffect
### Save Data
- None
### Notes
- None

## StatusEffect
### Purpose
- Base class for defining behavior of individual status effects.
### Related Files
- core/components/StatusEffect.gd
### Responsibilities
- Not Found
### Public API Methods
- on_apply(entity: Node) -> void
- tick(delta: float) -> void
- on_remove() -> void
- is_expired() -> bool
- refresh(new_duration: float) -> void
### Signals
- Not Found
### Properties
- Not Found
### Owned Data
- id: String
- duration: float
- elapsed: float
- owner: Node
### Depends On
- StatusComponent
### Used By
- Entity
- PoisonStatusEffect
- StatusComponent
### Save Data
- None
### Notes
- None

## Targetable
### Purpose
- Provides an interface for identifying entities that can be targeted in combat.
### Related Files
- core/components/Targetable.gd
### Responsibilities
- Determining targetability and retrieving target position.
### Public API Methods
- Not Found
### Signals
- Not Found
### Properties
- target_type: String
- weight: float
- alive: bool
- is_targetable: bool
- can_attach: unmarked
- can_throw: unmarked
- can_shield: unmarked
- attach_priority: unmarked
### Owned Data
- Not Found
### Depends On
- TargetSystem
### Used By
- Corpse
- Enemy
- InteractionObject
- PlayerCombat
- PlayerMovement
- TargetSystem
- TreeWood
### Save Data
- None
### Notes
- None

## DropEntry
### Purpose
- Data structure for a single loot entry in a drop table.
### Related Files
- core/databases/DropEntry.gd
### Responsibilities
- Storing item ID and weight metadata.
### Public API Methods
- Not Found
### Signals
- Not Found
### Properties
- item: ItemData
- weight: int
- min_quantity: int
- max_quantity: int
### Owned Data
- Not Found
### Depends On
- ItemData
### Used By
- DropTable
### Save Data
- None
### Notes
- None

## EnemySkill
### Purpose
- Data structure for skills used by enemy entities.
### Related Files
- core/databases/EnemySkill.gd
### Responsibilities
- Storing skill ID and damage multiplier data.
### Public API Methods
- Not Found
### Signals
- Not Found
### Properties
- id: String
- type: String
- weight: int
- animation: String
- cooldown: float
- range: float
- damage: int
- effect: String
### Owned Data
- Not Found
### Depends On
- Not Found
### Used By
- DefaultEnemyBehavior
- Enemy
- EnemyAI
- EnemyStats
- SkillRegistry
### Save Data
- None
### Notes
- None

## EnemyStats
### Purpose
- Data structure for base enemy attributes. aka. EnemyArchetype
### Related Files
- core/databases/EnemyStats.gd
### Responsibilities
- Layer 2 of the 3-layer hierarchy: Biological Template → Species → Individual
- Owns combat/runtime parameters for a specific enemy variant.
- Population and group_size are owned exclusively by SpeciesDefinition (Layer 1).
### Public API Methods
- Not Found
### Signals
- Not Found
### Properties
- id: String
- species_id: String
- name: String
- monster_type: String
- weight: float
- nutrition: int
- tier: int
- description: String
- ecology: Array[String]
- max_hp: float
- speed: float
- base_atk: float
- base_def: float
- behavior_script: Script
- skills: Array[EnemySkill]
- drop_table: DropTable
### Owned Data
- Not Found
### Depends On
- SpeciesDefinition
- EnemySkill
- Enemy
- DropTable
### Used By
- EcologySimulation
- Enemy
- EnemyDatabase
- GameState
- QuestGenerator
- SkillRegistry
- SpawnController
- SpeciesDefinition
- WorldManager
### Save Data
- None
### Notes
- None

## GenusDefinition
### Purpose
- PLACEHOLDER
### Related Files
- core/databases/GenusDefinition.gd
### Responsibilities
- PLACEHOLDER
### Public API Methods
- apply_to_species(def: SpeciesDefinition) -> void
### Signals
- Not Found
### Properties
- genus_id: String
- display_name: String
- preferred_biomes: Array[String]
- diet_type: String
- reproduction_rate: float
- migration_rate: float
- group_size_min: int
- group_size_max: int
- taxonomic_order: String
- default_skill_slots: Array[String]
### Owned Data
- Not Found
### Depends On
- SpeciesDefinition
### Used By
- SpeciesDefinition
### Save Data
- None
### Notes
- None

## ItemData
### Purpose
- Data structure for individual item attributes.
### Related Files
- core/databases/ItemData.gd
### Responsibilities
- Storing item ID, weight, and value metadata.
### Public API Methods
- Not Found
### Signals
- Not Found
### Properties
- id: String
- name: String
- description: String
- value: int
### Owned Data
- Not Found
### Depends On
- Not Found
### Used By
- DropEntry
- ItemDatabase
### Save Data
- None
### Notes
- None

## SpeciesDefinition
### Purpose
- Definition of biological parameters for species.
### Related Files
- core/databases/SpeciesDefinition.gd
### Responsibilities
- Layer 1 (Biological Template) of the 3-layer Enemy hierarchy
- Defining species identity and hierarchical tiering.
- Storing habitat constraints (altitude, humidity, temperature).
- Managing dietary ecology (predation, prey, diet type).
- Determining environmental compatibility based on habitat ranges.
### Public API Methods
- is_environment_compatible(env: EnvironmentState, bio_def: Resource = null) -> bool
- calculate_compatibility_score(env: EnvironmentState, bio_def: Resource = null) -> float
- get_approach_tendency(target_species: String) -> float
- get_attack_intent(target_species: String) -> float
- get_experience_sensitivity() -> float
- get_enemy_stats() -> EnemyStats
### Signals
- Not Found
### Properties
- genus_definition: GenusDefinition
- species_id: String
- display_name: String
- tier: int
- monster_type: String
- preferred_biomes: Array[String]
- altitude_range: Vector2
- humidity_range: Vector2
- temperature_range: Vector2
- preferred_habitat_tags: Array[String]
- max_spawn_slope_degrees: float
- poison_adaptation_scale: float
- diet_type: String
- reproduction_rate: float
- migration_rate: float
- default_population: int
- group_size_min: int
- group_size_max: int
- enemy_id: String
- taxonomic_order: String
- behavior_profile: BehaviorProfile
- visual_scene: PackedScene
### Owned Data
- Not Found
### Depends On
- Enemy
- EnemyStats
- GenusDefinition
- EnvironmentState
- BehaviorProfile
- EnemyDatabase
### Used By
- BehaviorRegistry
- DebugSpawnView
- DefaultEnemyBehavior
- EcologyManager
- EcologySimulation
- Enemy
- EnemyDatabase
- EnemySpawner
- EnemyStats
- GameState
- GenusDefinition
- GroupPoisonState
- PopulationCalculator
- QuestGenerator
- SpawnController
- SpawnLocationResolver
- SpawnRequest
- SpeciesDatabase
- SpeciesRelation
- WorldManager
### Save Data
- None
### Notes
- None

## AreaDefinition
### Purpose
- Resource describing a gameplay/world Area.
### Related Files
- core/systems/ecology/AreaDefinition.gd
### Responsibilities
- Storing spatial metadata for an area.
### Public API Methods
- Not Found
### Signals
- Not Found
### Properties
- area_id: String
- display_name: String
- description: String
### Owned Data
- Not Found
### Depends On
- Not Found
### Used By
- None
### Save Data
- None
### Notes
- None

## BioRegionDefinition
### Purpose
- Resource describing an ecological/environmental sub-region within an Area.
### Related Files
- core/systems/ecology/BioRegionDefinition.gd
### Responsibilities
- Storing base environmental characteristics (temperature, humidity, vegetation, fertility).
- Providing habitat metadata and tags.
- Initializing `EnvironmentState` with base values.
### Public API Methods
- get_humidity() -> float
- get_vegetation() -> float
- get_fertility() -> float
- create_environment_state() -> EnvironmentState
### Signals
- Not Found
### Properties
- bio_region_id: String
- area_id: String
- display_name: String
- base_temperature: float
- base_humidity: float
- base_vegetation: float
- base_fertility: float
- habitat_tags: Array[String]
### Owned Data
- Not Found
### Depends On
- BioRegionInstance
- EnvironmentState
### Used By
- BioRegionInstance
- EcologyManager
- EnvironmentState
- ForestBioRegionDefinition
### Save Data
- None
### Notes
- Implementation includes specialized biological templates for Forest and Mountain Forest types.

## BioRegionInstance
### Purpose
- Represents a placed BioRegion instance referencing a BioRegionDefinition type with optional environmental overrides.
### Related Files
- core/systems/ecology/BioRegionInstance.gd
### Responsibilities
- Resolving environmental values by prioritizing instance-level overrides over template defaults.
- Creating `EnvironmentState` instances using resolved properties.
### Public API Methods
- get_humidity() -> float
- get_vegetation() -> float
- get_fertility() -> float
- create_environment_state() -> EnvironmentState
### Signals
- Not Found
### Properties
- bio_region_id: String
- area_id: String
- definition: BioRegionDefinition
- humidity_override: float
- vegetation_override: float
- fertility_override: float
### Owned Data
- UNSET_OVERRIDE: float
### Depends On
- BioRegionDefinition
- EnvironmentState
### Used By
- BioRegionDefinition
- EcologyManager
- EnvironmentState
### Save Data
- None
### Notes
- Uses `UNSET_OVERRIDE` constant (-999.0) to detect if an override is present.

## ForestBioRegionDefinition
### Purpose
- PLACEHOLDER
### Related Files
- core/systems/ecology/ForestBioRegionDefinition.gd
### Responsibilities
- PLACEHOLDER
### Public API Methods
- Not Found
### Signals
- Not Found
### Properties
- canopy_density: float
- forest_floor_moisture: float
### Owned Data
- Not Found
### Depends On
- BioRegionDefinition
### Used By
- MountainForestBioRegionDefinition
### Save Data
- None
### Notes
- None

## GroupSkillState
### Purpose
- PLACEHOLDER
### Related Files
- core/systems/ecology/GroupSkillState.gd
### Responsibilities
- PLACEHOLDER
### Public API Methods
- get_weight(group_id: String, target_species_id: String, skill_id: String) -> float
- set_weight(group_id: String, target_species_id: String, skill_id: String, weight: float) -> void
- inherit_group(parent_group_id: String, child_group_id: String) -> void
- delete_group(group_id: String) -> void
- get_save_data() -> Dictionary
- load_save_data(data: Dictionary) -> void
- clear_all() -> void
### Signals
- Not Found
### Properties
- Not Found
### Owned Data
- Not Found
### Depends On
- Not Found
### Used By
- DefaultEnemyBehavior
- EcologyManager
- WorldManager
### Save Data
- Provides get_save_data
- Provides load_save_data
### Notes
- None

## MountainForestBioRegionDefinition
### Purpose
- PLACEHOLDER
### Related Files
- core/systems/ecology/MountainForestBioRegionDefinition.gd
### Responsibilities
- PLACEHOLDER
### Public API Methods
- Not Found
### Signals
- Not Found
### Properties
- altitude_min: float
- altitude_max: float
### Owned Data
- Not Found
### Depends On
- ForestBioRegionDefinition
### Used By
- None
### Save Data
- None
### Notes
- None

## BehaviorRegistry
### Purpose
- Maps behavior identifiers to their respective implementation classes.
### Related Files
- scenes/Characters/Enemies/BehaviorRegistry.gd
### Responsibilities
- Providing behavior lookup and registration interfaces.
### Public API Methods
- register(species_id: String, behavior: Object) -> void
- get_behavior(species_id: String) -> Object
### Signals
- Not Found
### Properties
- Not Found
### Owned Data
- skill_system: unmarked
- registry: Dictionary
- default_behavior: unmarked
### Depends On
- DefaultEnemyBehavior
- SpeciesDefinition
### Used By
- EnemyBehavior
### Save Data
- None
### Notes
- None

## Corpse
### Purpose
- Represents the physical remains of a dead entity for decomposition.
### Related Files
- scenes/Characters/Enemies/Corpse.gd
### Responsibilities
- Managing nutrient release and decomposition timers.
### Public API Methods
- initialize_poison_from_environment() -> void
- interact(interactor: Node) -> void
- apply_knockback(force: Vector3) -> void
- advance_game_minutes(minutes: float) -> void
- is_dusting() -> bool
- advance_state(nutrition_units: int, progress: float, current_poison_amount: float, minutes: float, decay_speed: float, poison_factor: float) -> Dictionary
- get_decay_poison_multiplier_for_region(region_id: String) -> float
- get_decay_speed_for_region(region_id: String) -> float
- step_serialized(data: Dictionary, game_minutes: float) -> bool
- consume(units: int = 1) -> Dictionary
- serialize() -> Dictionary
- restore(data: Dictionary) -> void
- add_poison_amount(amount: float) -> float
- get_poison_amount() -> float
- on_pickup(carrier: Node) -> void
- on_throw(direction: Vector3, force: float) -> void
### Signals
- Not Found
### Properties
- nutrition: int
- weight: float
### Owned Data
- DECAY_GAME_MINUTES_PER_NUTRITION: float
- DECAY_REFERENCE_TEMP: float
- DECAY_REFERENCE_HUM: float
- DECAY_HUMIDITY_DOUBLING: float
- POISON_AMOUNT_PER_GAME_MINUTE: float
- DUST_FADE_SECONDS: float
- ENV_REFRESH_SEC: float
- CORPSE_POISON_VARIATION_MIN: float
- CORPSE_POISON_VARIATION_MAX: float
- CORPSE_POISON_LOAD_SCALE: float
- POISON_COLOR_MAX: Color
- POISON_VISUAL_MAX_AMOUNT: float
- POISON_OVERLAY_MAX_ALPHA: float
- POISON_VISUAL_INTERVAL: float
- _poison_overlay: StandardMaterial3D
- _poison_visual_timer: float
- _poison_visual_ratio: float
- poison_amount: float
- poison_initialized: bool
- species_id: String
- tier: int
- region_id: String
- ecology_carcass_id: String
- _carrier: Node3D
- nutrition_notified: bool
- initial_nutrition: int
- decay_progress: float
- targetable: Targetable
- velocity: Vector3
- decay: float:
- _dusting: bool
- _decay_speed: float
- _poison_factor: float
- _env_timer: float
- _last_game_minutes: float
### Depends On
- Targetable
- WorldManager
- NutrientCycle
- TimeSystem
- EcologyManager
- EnvironmentState
### Used By
- DebugEntityOverlay
- DebugPoisonActions
- DebugPoisonView
- EcologyManager
- Enemy
- EnemyAI
- InteractionObject
- InteractionSystem
- PoisonArea
- StatusComponent
- WorldManager
### Save Data
- Provides serialize
### Notes
- None

## DefaultEnemyBehavior
### Purpose
- Implementation of standard patrol and chase behaviors.
### Related Files
- scenes/Characters/Enemies/DefaultEnemyBehavior.gd
### Responsibilities
- Handling patrol and chase logic.
### Public API Methods
- get_debug_relation_observation(owner: Enemy, target: Entity) -> Dictionary
- decide_movement(owner: Enemy, target: Entity) -> Vector3
- get_debug_candidate_observations(owner: Enemy, candidates: Array) -> Array[Dictionary]
- decide_target(owner: Enemy, candidates: Array) -> Entity
- decide_skill(owner: Enemy, target: Entity) -> String
- get_debug_skill_observation(owner: Enemy, target: Entity) -> Array[Dictionary]
- should_retreat(owner: Enemy) -> bool
### Signals
- Not Found
### Properties
- Not Found
### Owned Data
- Enemy: unmarked
- skill_system: EnemySkillSystem
### Depends On
- Enemy
- EnemySkillSystem
- UtilityScoringEngine
- SpeciesDatabase
- Entity
- SpeciesDefinition
- SpeciesRelation
- PoisonArea
- PoisonAvoidance
- SpatialRegionResolver
- TerritoryState
- EnemySkill
- GroupSkillState
### Used By
- BehaviorRegistry
- Enemy
### Save Data
- None
### Notes
- None

## Enemy
### Purpose
- Base class for enemy entities handling health and basic lifecycle.
### Related Files
- scenes/Characters/Enemies/Enemy.gd
### Responsibilities
- Managing health, damage reception, and death signaling.
### Public API Methods
- get_effective_atk() -> float
- get_effective_def() -> float
- get_effective_spd() -> float
- apply_knockback(force: Vector3) -> void
- swing_melee_attack() -> void
- take_damage(amount: float) -> void
- die() -> void
- freeze(duration: float) -> void
- configure(new_speed: float, new_hp: float) -> void
### Signals
- Not Found
### Properties
- speed: float
- knockback_damping: float
- attack_range: float
- attack_cooldown: float
- is_dummy: bool
- is_boss: bool
- enemy_id: String
- territory_radius: float
- visual_container: Node3D
- _ai: EnemyAI
### Owned Data
- species_id: String
- area_id: String
- bio_region_id: String
- territory_id: String
- group_id: String
- base_atk: float
- base_def: float
- atk: float
- def: float
- _archetype_skills: Array[EnemySkill]
- freeze_timer: float
- discovered: bool
- knockback_velocity: Vector3
- is_swinging: bool
- targetable: Targetable
- genetic_scale_modifier: Vector3
- genetic_part_scales: Dictionary
### Depends On
- EnemyAI
- QuestManager
- GameState
- EcologyManager
- EnemyDatabase
- Entity
- EnemySkill
- EnemyStats
- DefaultEnemyBehavior
- Targetable
- SpeciesDefinition
- SpeciesDatabase
- EventBus
- Corpse
- TargetSystem
- WorldManager
### Used By
- DebugEntityOverlay
- DebugPoisonActions
- DebugPoisonView
- DefaultEnemyBehavior
- EnemyAI
- EnemyBehavior
- EnemySpawner
- EnemyStats
- Entity
- SpawnController
- SpeciesDefinition
- StatusComponent
- WorldManager
- WorldMap
- WorldRoot
### Save Data
- None
### Notes
- None

## EnemyBehavior
### Purpose
- Base class for defining abstract enemy behaviors.
### Related Files
- scenes/Characters/Enemies/EnemyBehavior.gd
### Responsibilities
- Providing an execution interface for agent behaviors.
### Public API Methods
- decide_movement(owner: Enemy, target: Entity) -> Vector3
- decide_target(owner: Enemy, candidates: Array) -> Entity
- decide_skill(owner: Enemy, target: Entity) -> String
- get_debug_relation_observation(owner: Enemy, target: Entity) -> Dictionary
- get_debug_skill_observation(owner: Enemy, target: Entity) -> Array[Dictionary]
- should_retreat(owner: Enemy) -> bool
### Signals
- Not Found
### Properties
- Not Found
### Owned Data
- Enemy: unmarked
- skill_system: unmarked
- registry_manager: unmarked
### Depends On
- Enemy
- BehaviorRegistry
- EnemySkillSystem
- Entity
### Used By
- EnemyAI
### Save Data
- None
### Notes
- None

## SkillRegistry
### Purpose
- Single registry loaded from .tres for enemy skill definitions
### Related Files
- scenes/Characters/Enemies/SkillRegistry.gd
### Responsibilities
- Providing skill retrieval and registration interfaces.
### Public API Methods
- get_skill(skill_id: String) -> Dictionary
- has_skill(skill_id: String) -> bool
- get_skill_resource(skill_id: String) -> EnemySkill
- get_all_ids() -> Array
### Signals
- Not Found
### Properties
- Not Found
### Owned Data
- RESOURCES_DIR: unmarked
- skills: Dictionary
### Depends On
- EnemySkill
- EnemyStats
### Used By
- EnemySkillSystem
### Save Data
- None
### Notes
- None

## PlayerStats
### Purpose
- A simple data container for the player's physical attributes, specifically providing strength values used by movement and interaction systems.
### Related Files
- scenes/Characters/Player/PlayerStats.gd
### Responsibilities
- Storing strength/STR redundancy and compatibility values.
### Public API Methods
- Not Found
### Signals
- Not Found
### Properties
- player: Node
- strength: float
- STR: float
### Owned Data
- Not Found
### Depends On
- Not Found
### Used By
- Player
- PlayerMovement
### Save Data
- None
### Notes
- None

## Entity
### Purpose
- Base class for all world entities providing fundamental properties and lifecycle signals.
### Related Files
- scenes/Core/Entity.gd
### Responsibilities
- Managing health, damage handling, and death signaling.
### Public API Methods
- take_damage(_amount: float) -> void
- freeze(_duration: float) -> void
- die() -> void
- is_alive() -> bool
- heal(amount: float) -> void
- apply_poison_stacks(stacks: int, duration: float = 0.0) -> void
- add_poison_amount(amount: float, duration: float = PoisonStatusEffect.POISON_DOSE_DURATION) -> float
- get_poison_amount() -> float
- get_poison_stacks() -> int
- get_poison_damage_multiplier() -> float
- get_poison_performance_multiplier() -> float
- get_poison_resistance() -> float
- get_hp_ratio() -> float
- get_poison_attack_multiplier() -> float
- get_poison_speed_multiplier() -> float
- get_poison_defense_multiplier() -> float
- get_poison_level() -> int
- is_poison_aggressive() -> bool
- has_poison_dependency() -> bool
### Signals
- poison_received(applied_amount: float)
- on_global_event_received(event_type: String, data: Dictionary)
### Properties
- max_hp: float
- _gravity_ray: RayCast3D
### Owned Data
- hp: float
- is_dead: bool
- POISON_COLOR_MAX: Color
- POISON_VISUAL_MAX_AMOUNT: float
- POISON_OVERLAY_MAX_ALPHA: float
- POISON_VISUAL_INTERVAL: float
- _poison_overlay: StandardMaterial3D
- _poison_visual_timer: float
- _poison_visual_ratio: float
- entity_id: String
- map_id: String
- status_component: StatusComponent
- GROUND_OFFSET: unmarked
### Depends On
- Enemy
- Player
- StatusComponent
- PoisonStatusEffect
- GroupPoisonState
- StatusEffect
### Used By
- DamageSystem
- DebugEntityOverlay
- DebugObservationView
- DebugPanel
- DebugPanelActions
- DebugPanelNavigation
- DebugPoisonActions
- DebugPoisonView
- DefaultEnemyBehavior
- Enemy
- EnemyAI
- EnemyBehavior
- EventBus
- InteractionObject
- Player
- PlayerCombat
- PoisonArea
- TreeWood
- WorldManager
### Save Data
- None
### Notes
- None

## DamageEvent
### Purpose
- PLACEHOLDER
### Related Files
- scenes/Systems/Combat/DamageEvent.gd
### Responsibilities
- PLACEHOLDER
### Public API Methods
- Not Found
### Signals
- Not Found
### Properties
- Not Found
### Owned Data
- amount: float
- type: int
- source: int
- attacker: Node
- victim: Node
- knockback: Vector3
- is_critical: bool
- skill_id: String
### Depends On
- DamageSystem
### Used By
- DamageSystem
- EnemySkillSystem
- EventBus
- InteractionObject
- PlayerCombat
- PlayerSpell
- SpeciesRelation
### Save Data
- None
### Notes
- None

## Indicator
### Purpose
- Provides visual 3D indicators (circles, lines, sectors) for gameplay feedback.
### Related Files
- scenes/Systems/Indicator/Indicator.gd
### Responsibilities
- Rendering meshes and materials on indicator nodes.
- Generating geometric primitives (circles, target circles, sectors, lines) using ImmediateMesh.
### Public API Methods
- set_mesh(mesh: Mesh) -> void
- set_material(material: Material) -> void
### Signals
- Not Found
### Properties
- mesh_instance: MeshInstance3D
### Owned Data
- Not Found
### Depends On
- Not Found
### Used By
- IndicatorManager
### Save Data
- None
### Notes
- None

## CarryHelper
### Purpose
- PLACEHOLDER
### Related Files
- scenes/Utils/CarryHelper.gd
### Responsibilities
- PLACEHOLDER
### Public API Methods
- can_be_carried(strength: float, weight: float) -> bool
### Signals
- Not Found
### Properties
- Not Found
### Owned Data
- Not Found
### Depends On
- Not Found
### Used By
- Player
### Save Data
- None
### Notes
- None

## Effects
### Purpose
- PLACEHOLDER
### Related Files
- scenes/Utils/Effects.gd
### Responsibilities
- PLACEHOLDER
### Public API Methods
- Not Found
### Signals
- Not Found
### Properties
- Not Found
### Owned Data
- Not Found
### Depends On
- Not Found
### Used By
- GameState
- PlayerCombat
### Save Data
- None
### Notes
- None

# Layer 1: Global Context & Registries (global managers, singletons, or databases)

## EconomyManager
### Purpose
- PLACEHOLDER
### Related Files
- core/autoload/EconomyManager.gd
### Responsibilities
- PLACEHOLDER
### Public API Methods
- add_gold(amount: int) -> void
- spend_gold(amount: int) -> bool
- add_reputation(amount: int) -> void
- get_gold() -> int
- get_reputation() -> int
- load_economy_data(data: Dictionary) -> void
- get_save_data() -> Dictionary
- load_save_data(data: Dictionary) -> void
### Signals
- Not Found
### Properties
- Not Found
### Owned Data
- gold: int
- reputation: int
### Depends On
- Not Found
### Used By
- GameState
- QuestManager
### Save Data
- Provides get_save_data
- Provides load_save_data
### Notes
- None

## GameState
### Purpose
- Acts as the central global authority for managing game progression, economy, status effects, environment, and data loading/unloading.
### Related Files
- core/autoload/GameState.gd
### Responsibilities
- Manage Economy (gold, reputation).
- Track Quest progress and World Events.
- Handle Status effect lifecycle (application, stacking, duration decay, and interactions like Burn/Freeze).
- Manage Temperature accumulation (heat/cold) and thresholds.
- Manage Environment modifiers and terrain damage reports.
- Orchestrate Weapon Evolution logic (tracking kills, checking requirements, performing evolution).
- Maintain the Monster Codex (discovery and kill count tracking).
- Manage Village Modifiers (timed resource yield debuffs).
### Public API Methods
- load_spells_data() -> void
- get_mastery(spell_id: String) -> float
- gain_mastery(spell_id: String, sim_score: float) -> void
- check_unlocks_and_discoveries() -> void
- get_mastery_damage_bonus(spell_id: String) -> float
- get_mastery_range_bonus(spell_id: String) -> float
- get_mastery_typo_bonus(spell_id: String) -> float
- add_gold(amount: int)
- spend_gold(amount: int) -> bool
- add_reputation(amount: int)
- get_gold() -> int
- get_reputation() -> int
- next_day() -> void
- debug_msg() -> void
- add_village_modifier(modifier: Dictionary) -> void
- remove_village_modifier(id: String) -> void
- get_village_modifier_total(stat_name: String) -> float
- add_world_event(id: String, days: int) -> void
- remove_world_event(id: String) -> void
- has_world_event(id: String) -> bool
- apply_environment_report(report: Dictionary) -> void
- load_status_data() -> void
- add_status(id: String, duration: float, stack_add: int = 1) -> void
- apply_status(id: String) -> void
- remove_status(id: String) -> void
- has_status(id: String) -> bool
- get_status_stack(id: String) -> int
- get_status_time(id: String) -> float
- get_modifier(stat_name: String) -> float
- add_heat(amount: float) -> void
- add_cold(amount: float) -> void
- set_environment(mods: Dictionary) -> void
- get_environment_modifier(id: String) -> int
- get_environment_value(id: String) -> int
- process_status_interactions(_delta: float) -> void
- load_weapon_data() -> void
- register_weapon_kill(enemy_type: String) -> void
- get_available_evolutions() -> Array
- can_evolve(target_id: String) -> bool
- evolve_weapon(target_id: String) -> void
- get_weapon_node(id: String) -> Dictionary
- get_weapon_children(id: String) -> Array
- get_weapon_parent(id: String) -> String
- get_weapon_tree() -> Dictionary
- get_weapon_roots() -> Array
- get_weapon_depth(id: String) -> int
- get_weapon_path_to_root(id: String) -> Array
- get_weapon_evolution_count(id: String) -> int
- load_monster_data() -> void
- discover_monster(id: String) -> void
- is_monster_discovered(id: String) -> bool
- register_monster_kill(id: String) -> void
- get_codex_entry(id: String) -> Dictionary
- get_codex_entries() -> Dictionary
- get_codex_completion_percent() -> float
- get_monster_kill_count(id: String) -> int
- evaluate_map_after_quest(map_id: String) -> void
- get_map_reward_modifier(map_id: String) -> float
- get_environment_save_data() -> Dictionary
- load_environment_save_data(data: Dictionary) -> void
- get_save_data() -> Dictionary
- load_save_data(data: Dictionary) -> void
### Signals
- spell_unlocked(spell_id: String)
- spell_discovered(spell_id: String)
- global_event_received(event_type: String, data: Dictionary)
### Properties
- Not Found
### Owned Data
- current_quest: Dictionary
- current_day: int
- status_data: Dictionary
- active_statuses: Dictionary
- heat_level: float
- cold_level: float
- TEMPERATURE_DECAY_RATE: float
- TEMPERATURE_THRESHOLD: float
- environment_modifiers: Dictionary
- current_weapon: String
- weapon_data: Dictionary
- weapon_kills: Dictionary
- weapon_history: Array
- monster_data: Dictionary
- discovered_monsters: Array
- monster_kill_counts: Dictionary
- monster_codex: Dictionary
- village_modifiers: Array
- world_events: Array
### Depends On
- SpellMasteryManager
- EconomyManager
- Effects
- WorldState
- EnemyStats
- SpeciesDefinition
- SpeciesDatabase
### Used By
- CraftingSystem
- Enemy
- PlayerCombat
- PlayerMovement
- PlayerSpell
- QuestManager
- SaveSystem
- SpellMasteryManager
- SpellUI
### Save Data
- Provides get_save_data
- Provides load_save_data
### Notes
- None

## SaveManager
### Purpose
- Slot-based JSON persistence for game saves.
### Related Files
- core/autoload/SaveManager.gd
### Responsibilities
- Handling saving and loading of game data to slots.
### Public API Methods
- serialize() -> Dictionary
- deserialize(data: Dictionary) -> void
- save_to_slot(slot: int) -> void
- load_from_slot(slot: int) -> void
- slot_exists(slot: int) -> bool
- delete_slot(slot: int) -> void
### Signals
- Not Found
### Properties
- Not Found
### Owned Data
- SAVE_DIR: unmarked
- SAVE_EXT: unmarked
- CURRENT_SAVE_VERSION: int
### Depends On
- WorldManager
- EcologyManager
- CraftingSystem
- MapKnowledgeManager
### Used By
- WorldManager
### Save Data
- Provides serialize
- Provides deserialize
### Notes
- None

## SpellMasteryManager
### Purpose
- PLACEHOLDER
### Related Files
- core/autoload/SpellMasteryManager.gd
### Responsibilities
- PLACEHOLDER
### Public API Methods
- load_spells_data() -> void
- test_spell() -> void
- get_mastery(spell_id: String) -> float
- gain_mastery(spell_id: String, sim_score: float) -> void
- check_unlocks_and_discoveries() -> void
- get_mastery_damage_bonus(spell_id: String) -> float
- get_mastery_range_bonus(spell_id: String) -> float
- get_mastery_typo_bonus(spell_id: String) -> float
- get_save_data() -> Dictionary
- load_save_data(data: Dictionary) -> void
### Signals
- Not Found
### Properties
- Not Found
### Owned Data
- spell_mastery: Dictionary
- unlocked_spells: Array[String]
- discovered_spells: Array[String]
- all_spells: Array
### Depends On
- GameState
### Used By
- GameState
### Save Data
- Provides get_save_data
- Provides load_save_data
### Notes
- None

## TimeSystem
### Purpose
- Day/Night cycle progression with time segments and calculates astronomical values like sun angle and moon phase.
### Related Files
- core/autoload/TimeSystem.gd
### Responsibilities
- Managing time accumulation and providing time of day interfaces.
- Calculating astronomical values like sun angle and moon phase.
### Public API Methods
- advance_time(minutes: float) -> void
- advance_real_delta(delta: float, scale: float) -> void
- get_total_minutes() -> float
- next_day() -> void
- force_next_day() -> void
- get_time_of_day() -> String
- is_morning() -> bool
- is_noon() -> bool
- is_evening() -> bool
- is_night() -> bool
- get_save_data() -> Dictionary
- load_save_data(data: Dictionary) -> void
- get_sun_angle() -> float
- get_moon_phase() -> float
### Signals
- time_changed(minutes: float)
- day_changed(new_day: int)
- morning_started()
- noon_started()
- evening_started()
- night_started()
### Properties
- Not Found
### Owned Data
- DAY_LENGTH_MINUTES: float
- MORNING_START: float
- NOON_START: float
- EVENING_START: float
- NIGHT_START: float
- current_day: int
- current_time_minutes: float
- time_scale_village: float
- time_scale_dungeon: float
### Depends On
- QuestGenerator
- MapDatabase
- EcologyManager
### Used By
- Corpse
- DebugEcologyView
- DebugPanel
- DebugPanelActions
- DebugTimeView
- EcologyManager
- QuestGenerator
- SaveSystem
- WorldRoot
### Save Data
- Provides get_save_data
- Provides load_save_data
### Notes
- None

## WorldState
### Purpose
- PLACEHOLDER
### Related Files
- core/autoload/WorldState.gd
### Responsibilities
- PLACEHOLDER
### Public API Methods
- get_map_state(map_id: String) -> Dictionary
- get_map_value(map_id: String, key: String, default_value = 0)
- set_map_value(map_id: String, key: String, value) -> void
- add_map_value(map_id: String, key: String, amount) -> void
- ensure_map_exists(map_id: String) -> void
- update_map_decay(map_id: String, current_day: int) -> void
- evaluate_environment_damage(map_id: String) -> Dictionary
- add_burn_damage(map_id: String, amount: float) -> void
- add_poison_damage(map_id: String, amount: float) -> void
- get_environment_damage_summary(map_id: String) -> Dictionary
- get_save_data() -> Dictionary
- load_save_data(data: Dictionary) -> void
- debug_map_state(map_id: String) -> void
### Signals
- Not Found
### Properties
- Not Found
### Owned Data
- map_states: Dictionary
### Depends On
- Not Found
### Used By
- GameState
- SaveSystem
- WorldManager
### Save Data
- Provides get_save_data
- Provides load_save_data
### Notes
- None

## BiomeDatabase
### Purpose
- Repository for biome-specific environmental data.
### Related Files
- core/databases/BiomeDatabase.gd
### Responsibilities
- Retrieving biome data and listing biomes in a region.
### Public API Methods
- get_biome_for_env(env: EnvironmentState) -> String
- get_entry(id: String) -> Dictionary
- get_value(id: String, key: String, default = null)
- has_entry(id: String) -> bool
- get_all_ids() -> Array
- get_all() -> Array
### Signals
- Not Found
### Properties
- Not Found
### Owned Data
- DATA_PATH: unmarked
### Depends On
- EnvironmentState
### Used By
- EcologyManager
### Save Data
- None
### Notes
- None

## EnemyDatabase
### Purpose
- Repository for enemy configurations, stats, and skill associations.
### Related Files
- core/databases/EnemyDatabase.gd
### Responsibilities
- Providing enemy data retrieval by species.
### Public API Methods
- get_resource(id: String) -> EnemyStats
- get_entry(id: String) -> Dictionary
- get_value(id: String, key: String, default = null)
- has_entry(id: String) -> bool
- get_all_ids() -> Array
- get_all() -> Array
- get_species_default_population(species_id: String) -> int
- get_default_population(species_id: String) -> int
- get_species_definition(enemy_id: String) -> SpeciesDefinition
- get_weight(enemy_id: String) -> float
- get_nutrition(enemy_id: String) -> int
- get_faction_id(id: String) -> String
- get_group_id(id: String) -> String
- get_species_ids() -> Array
- get_by_tier(tier: int) -> Array
- get_by_species(species_id: String) -> Array
- get_enemy(id: String) -> Dictionary
- get_monster(id: String) -> Dictionary
- has_monster(id: String) -> bool
- get_all_monster_ids() -> Array
- get_all_monsters() -> Array
- get_monsters_by_tier(tier: int) -> Array
- get_monsters_by_species(species_id: String) -> Array
### Signals
- Not Found
### Properties
- Not Found
### Owned Data
- RESOURCES_DIR: unmarked
- _enemies_resources: Dictionary
### Depends On
- EnemyStats
- SpeciesDatabase
- SpeciesDefinition
### Used By
- Enemy
- QuestGenerator
- SpawnController
- SpeciesDatabase
- SpeciesDefinition
- WorldMap
### Save Data
- None
### Notes
- None

## ItemDatabase
### Purpose
- Repository for all items in the game.
### Related Files
- core/databases/ItemDatabase.gd
### Responsibilities
- Providing item data and presence verification within the registry.
### Public API Methods
- get_resource(id: String) -> ItemData
- get_entry(id: String) -> Dictionary
- get_value(id: String, key: String, default = null)
- has_entry(id: String) -> bool
- get_all_ids() -> Array
- get_all() -> Array
### Signals
- Not Found
### Properties
- Not Found
### Owned Data
- RESOURCES_DIR: unmarked
- _items_resources: Dictionary
### Depends On
- ItemData
### Used By
- CraftingSystem
- WorldMap
### Save Data
- None
### Notes
- None

## MapDatabase
### Purpose
- Static registry for map metadata and species associations.
### Related Files
- core/databases/MapDatabase.gd
### Responsibilities
- Retrieving map entries and mapping species to maps.
### Public API Methods
- get_entry(map_id: String) -> Dictionary
- get_value(map_id: String, key: String, default = null)
- has_entry(map_id: String) -> bool
- get_all_ids() -> Array
- get_all() -> Array
- get_species_for_map(map_id: String) -> Array
- get_map_data(map_id: String) -> Dictionary
- get_map_ids() -> Array
- map_exists(map_id: String) -> bool
### Signals
- Not Found
### Properties
- Not Found
### Owned Data
- MAPS: Dictionary
### Depends On
- Not Found
### Used By
- EcologyManager
- EnemySpawner
- QuestGenerator
- TimeSystem
### Save Data
- None
### Notes
- None

## ObjectDatabase
### Purpose
- Registry for all interactable world objects.
### Related Files
- core/databases/ObjectDatabase.gd
### Responsibilities
- Registering and retrieving object data within the registry.
### Public API Methods
- get_entry(id: String) -> Dictionary
- get_value(id: String, key: String, default = null)
- has_entry(id: String) -> bool
- get_all_ids() -> Array
- get_all() -> Array
### Signals
- Not Found
### Properties
- Not Found
### Owned Data
- DATA_PATH: unmarked
- _objects: Dictionary
### Depends On
- Not Found
### Used By
- WorldMap
### Save Data
- None
### Notes
- None

## SpeciesDatabase
### Purpose
- Repository for species definitions and biological traits.
### Related Files
- core/databases/SpeciesDatabase.gd
### Responsibilities
- Providing species info and listing all registered species.
### Public API Methods
- get_species(id: String) -> SpeciesDefinition
- has_species(id: String) -> bool
- get_all_species() -> Array
- get_all_ids() -> Array
- get_by_biome(biome_id: String) -> Array
- get_suitable_species(biome_id: String, env_humidity: float, env_temperature: float) -> Array
- get_compatible_candidates(env: EnvironmentState, bio_def: Resource = null) -> Array[SpeciesDefinition]
### Signals
- Not Found
### Properties
- Not Found
### Owned Data
- RESOURCES_DIR: unmarked
- _species: Dictionary
### Depends On
- SpeciesDefinition
- EnemyDatabase
- EnvironmentState
### Used By
- DebugSpawnView
- DefaultEnemyBehavior
- EcologyManager
- Enemy
- EnemyDatabase
- EnemySpawner
- GameState
- GroupPoisonState
- QuestGenerator
- SpeciesRelation
- WorldManager
- WorldMap
### Save Data
- None
### Notes
- None

## EcologySerializer
### Purpose
- Handles serialization and deserialization of ecology states with versioning.
### Related Files
- core/systems/ecology/EcologySerializer.gd
### Responsibilities
- Serializing and deserializing ecology data with version support.
### Public API Methods
- serialize_ecology(environments: Dictionary, species_states: Dictionary, carcasses: Array = [], observable_consequences: Array = []) -> Dictionary
- deserialize_ecology(data: Dictionary, environments: Dictionary, species_states: Dictionary, carcasses: Array = [], observable_consequences: Array = []) -> void
### Signals
- Not Found
### Properties
- Not Found
### Owned Data
- CURRENT_VERSION: unmarked
### Depends On
- EnvironmentState
- SpeciesState
### Used By
- EcologyManager
### Save Data
- Serialized via EcologySerializer
### Notes
- None

## EnvironmentState
### Purpose
- Holds current environmental values (terrain, biotic, anthropogenic) for one region.
### Related Files
- core/systems/ecology/EnvironmentState.gd
### Responsibilities
- Managing environmental variables, handling day progression/recovery, and applying nutrients.
### Public API Methods
- from_bio_region(bio_region: Resource) -> EnvironmentState
- tick_day() -> void
- apply_nutrients(nutrition: int, positive: bool = true) -> void
- consume_vegetation(amount: float) -> void
- apply_fire_damage(amount: float) -> void
- apply_poison(amount: float) -> void
- get_poison_stack_count(max_stacks: int) -> int
- to_dict() -> Dictionary
- from_dict(d: Dictionary) -> void
### Signals
- Not Found
### Properties
- Not Found
### Owned Data
- altitude: float
- humidity: float
- temperature: float
- water_level: float
- vegetation: float
- fertility: float
- food_amount: float
- detritus_food: float
- human_activity: float
- burn_recovery: float
- poison_level: float
- burn_level: float
- pollution: float
### Depends On
- BioRegionDefinition
- BioRegionInstance
### Used By
- BioRegionDefinition
- BioRegionInstance
- BiomeDatabase
- Corpse
- DebugEcologyView
- DebugPanel
- DebugPanelActions
- DebugPoisonActions
- DebugPoisonView
- DebugSpawnView
- EcologyManager
- EcologyObservationUI
- EcologySerializer
- EcologySimulation
- FireAgent
- NutrientCycle
- PoisonArea
- PopulationCalculator
- SpawnController
- SpawnLocationResolver
- SpawnRequest
- SpeciesDatabase
- SpeciesDefinition
- WorldManager
- WorldRoot
### Save Data
- None
### Notes
- None

## SpeciesState
### Purpose
- Tracks the current ecological state (population, stress, genetics) of a single species within a specific region.
### Related Files
- core/systems/ecology/SpeciesState.gd
### Responsibilities
- Storing population, stress, metrics, evolutionary state, and genetic drift data; providing persistence support.
### Public API Methods
- get_death_mean_body_scale() -> float
- get_death_body_scale_variance() -> float
- get_death_mean_part_scale(part_name: String) -> float
- get_death_deviation_from_population_mean() -> float
- apply_natural_selection(selection_strength: float = 0.05, min_deaths: int = 5) -> void
- calculate_reproduction_births(repro_rate: float = 0.1) -> int
- update_danger(base_atk: float = 10.0, base_def: float = 0.0, base_spd: float = 3.0) -> float
- to_dict() -> Dictionary
- from_dict(d: Dictionary) -> void
### Signals
- Not Found
### Properties
- Not Found
### Owned Data
- species_id: String
- population: int
- target_population: int
- stress: float
- food_available: float
- average_condition: float
- environmental_adaptation: float
- evolution_preparation: float
- danger: float
- mean_body_scale: float
- mean_part_scales: Dictionary
- total_generations: int
- last_death_phenotype: Dictionary
- death_count: int
- death_body_scale_sum: float
- death_body_scale_sq_sum: float
- death_part_scale_sums: Dictionary
### Depends On
- Not Found
### Used By
- DebugEcologyView
- DebugPanelActions
- EcologyManager
- EcologyObservationUI
- EcologySerializer
- EcologySimulation
- GeneticDriftCalculator
- PopulationCalculator
- QuestGenerator
- SpawnController
- SpawnRequest
- WorldManager
### Save Data
- None
### Notes
- None

# Layer 2: Systems & Orchestrators (simulation rules, generators, or management systems)

## WorldManager
### Purpose
- Manages the physical lifecycle of entities in the game world through spatial hashing and proximity-based activation/deactivation.
### Related Files
- core/autoload/WorldManager.gd
### Responsibilities
- Handle map transitions (travel_to) and region changes.
- Spatial Hashing: Rebuild a grid to track enemies, objects, and corpses efficiently.
- Proximity Activation: Spawn/instantiate (deserialize) nodes for enemies, objects, and corpses when the player is within ACTIVATION_RANGE.
- Proximity Deactivation: Despawn/serialize nodes for enemies, objects, and corpses when the player exceeds DEACTIVATION_RANGE.
- Manage Corpse lifetime decay.
- Track Waypoints and Shortcuts state.
- Provide area-based terrain resolution (resolve_area_at_position).
### Public API Methods
- set_player(player: Node3D) -> void
- get_player_position() -> Vector3
- get_nearby_active_nodes(pos: Vector3, radius: float = 30.0) -> Array[Node]
- resolve_area_at_position(pos: Vector3) -> String
- update_group_spatial_state(map_id: String, species_id: String, group_id: String, anchor: Vector3, activity_center: Vector3, activity_radius: float, member_count: int) -> void
- update_group_territory_influence(map_id: String, species_id: String, group_id: String, influence_center: Vector3, influence_range: float) -> void
- get_group_territory_influence(map_id: String, species_id: String, group_id: String) -> Dictionary
- get_group_spatial_state(map_id: String, species_id: String, group_id: String) -> Dictionary
- create_child_group(map_id: String, species_id: String, parent_group_id: String, member_identifiers: Array) -> String
- update_group_split_candidate(map_id: String, species_id: String, parent_group_id: String, candidate_member_identifiers: Array, candidate_center: Vector3, delta_days: float, required_days: float, continuity_distance: float) -> String
- update_territory_ownership(map_id: String) -> void
- get_group_owned_cells(map_id: String, species_id: String, group_id: String) -> Array
- get_chunk_coord_at_position(pos: Vector3) -> Vector2i
- get_chunk_area_id_at_position(pos: Vector3) -> String
- get_chunk_poison_level_at_position(pos: Vector3) -> float
- get_or_create_group_id(map_id: String, species_id: String, position: Vector3) -> String
- unlock_waypoint(id: String) -> void
- complete_shortcut(id: String) -> void
- get_save_data() -> Dictionary
- load_save_data(data: Dictionary) -> void
- register_enemy(data: Dictionary) -> void
- register_object(data: Dictionary) -> void
- register_corpse(node: Node) -> void
- unregister_entity(node: Node) -> void
- travel_to(map_id: String) -> void
- get_nearest_path_point(p: Vector3) -> Vector3
- get_cell_stability(p: Vector3) -> float
- get_wilderness(p: Vector3) -> float
### Signals
- map_changed(from_id: String, to_id: String)
- region_changed(region_name: String)
### Properties
- Not Found
### Owned Data
- ACTIVATION_RANGE: unmarked
- DEACTIVATION_RANGE: unmarked
- MAX_ACTIVE_ENEMIES: unmarked
- VILLAGE_RADIUS: unmarked
- GRID_SIZE: float
- PROXIMITY_INTERVAL: float
- _proximity_accum: float
- _spatial_grid: Dictionary
- _spatial_grid_dirty: bool
- world_state: Dictionary
- CHUNK_TO_AREA: Dictionary
- current_map_id: String
- current_area_id: String
- player_node: Node3D
- registered_enemies: Array[Dictionary]
- registered_objects: Array[Dictionary]
- registered_corpses: Array[Dictionary]
- active_enemy_nodes: Array[Node]
- active_object_nodes: Array[Node]
- active_corpse_nodes: Array[Node]
- group_spatial_states: Dictionary
- TERRITORY_CELL_SIZE: float
- TERRITORY_BLOCK_SIZE: int
- _territory_blocks: Dictionary
- logistics_paths: Array[PackedVector3Array]
- debug_stability_draw: bool
- _debug_mesh_instance: MeshInstance3D
- lumber_camps_functional: Dictionary
### Depends On
- EnemySpawner
- ObjectGenerator
- Corpse
- WorldState
- SaveManager
- Entity
- EcologySimulation
- GroupSkillState
- SpeciesRelation
- SpeciesDefinition
- EnemyStats
- EcologyManager
- SpeciesState
- EnvironmentState
- SpeciesDatabase
- Enemy
### Used By
- Corpse
- DebugEcologyView
- DebugPanelActions
- DebugSpawnView
- DebugTerritoryOverlay
- EcologyManager
- EcologyObservationUI
- EcologySimulation
- Enemy
- EnemyAI
- EnemySpawner
- LogisticsNPC
- MapKnowledgeManager
- ObjectGenerator
- SaveManager
- SaveSystem
- SpatialRegionResolver
- SpawnController
- TerritoryState
- WorldMap
- WorldRoot
### Save Data
- Provides get_save_data
- Provides load_save_data
### Notes
- None

## DropTable
### Purpose
- Manages weighted random selection for item drops.
### Related Files
- core/databases/DropTable.gd
### Responsibilities
- Calculating weights and performing randomized selection of drops.
### Public API Methods
- Not Found
### Signals
- Not Found
### Properties
- drops: Array[DropEntry]
### Owned Data
- Not Found
### Depends On
- DropEntry
### Used By
- EnemyStats
### Save Data
- None
### Notes
- None

## EcologyManager
### Purpose
- Manages all regions, drives daily ecology updates, and issues spawn requests.
### Related Files
- core/systems/ecology/EcologyManager.gd
### Responsibilities
- Managing regions and bio-regions.
- Tracking species populations and stress levels.
- Simulating predation pressure and competition.
- Handling daily ecological updates and day transitions.
- Processing nutrient integration via corpse notifications.
- Orchestrating spawn requests through SpawnController
- Implementing swarm event triggers for population spikes.
### Public API Methods
- inject_spawn_controller(sc: Node) -> void
- set_population(map_id: String, species_id: String, value: int) -> void
- debug_ant_overpopulation() -> void
- debug_ant_extinction() -> void
- print_ecosystem_report(map_id: String) -> void
- get_species_database() -> Node
- get_spatial_resolver() -> Node
- get_world_manager() -> Node
- update_species_territory(region_id: String, species_id: String, pop: int, env: EnvironmentState, bio_def: Resource = null) -> void
- add_or_update_feeding_sign(region_id: String, species_id: String, position: Vector3, state: SpeciesState, env: EnvironmentState, bio_def: Resource = null) -> void
- begin_structured_spawn() -> void
- end_structured_spawn() -> void
- emit_spawn_request(region_id: String, def: SpeciesDefinition, count: int, env: EnvironmentState, req: SpawnRequest) -> void
- emit_swarm_event(region_id: String, species_id: String, count: int) -> void
- initialize_map_population(map_id: String) -> void
- register_species_birth(map_id: String, species_id: String, count: int = 1) -> void
- get_latest_carcass_id(region_id: String, species_id: String, death_position: Vector3) -> String
- set_carcass_nutrition(carcass_id: String, nutrition: float) -> void
- get_carcass_remaining_nutrition(carcass_id: String) -> float
- consume_carcass(carcass_id: String, units: float) -> float
- move_carcass_by_id(carcass_id: String, region_id: String, position: Vector3) -> void
- change_stress(map_id: String, species_id: String, delta: float) -> void
- register_region(region_id: String, env: EnvironmentState) -> void
- register_bio_region(bio_region: Resource) -> void
- register_fire_trace(region_id: String, position: Vector3, strength: float, radius: float, lifetime_days: int = 10) -> void
- on_day_passed() -> void
- calculate_effective_activity_radius(region_id: String, species_id: String, target_species_id: String) -> float
- notify_corpse(region_id: String, species_id: String, nutrition: int, source_region_id: String = "") -> void
- move_carcass_to_region(carcass: Dictionary, region_id: String, bio_region_id: String = "") -> void
- get_environment(region_id: String) -> EnvironmentState
- get_bio_region_def(bio_region_id: String) -> Resource
- get_species_in_region(region_id: String) -> Array
- get_species_state(region_id: String, species_id: String) -> SpeciesState
- get_population(region_id: String, species_id: String) -> int
- get_carcasses_in_region(region_id: String) -> Array
- get_observable_consequences_in_region(region_id: String) -> Array
- get_all_carcasses() -> Array
- get_save_data() -> Dictionary
- load_save_data(data: Dictionary) -> void
### Signals
- spawn_requested(region_id: String, species_def: SpeciesDefinition, count: int, env: EnvironmentState)
- spawn_request_object(request: RefCounted)
- ecology_updated(region_id: String)
- swarm_event_requested(region_id: String, species_id: String, count: int)
### Properties
- Not Found
### Owned Data
- DEBUG: int
- MINIMUM_POPULATION: int
- SWARM_SPIKE_THRESHOLD: float
- CARCASS_DECOMPOSITION_DAYS: float
- CARCASS_TRACE_DAYS: int
- CARCASS_DETRITUS_YIELD: float
- CARNIVORE_CARRION_YIELD: float
- DETRITUS_PROCESS_RATE: float
- DETRITUS_FERTILITY_YIELD: float
- ACTIVITY_APPROACH_WEIGHT: float
- ACTIVITY_FOOD_DEFICIT_WEIGHT: float
- ACTIVITY_MIN_FACTOR: float
- ACTIVITY_MAX_FACTOR: float
- CARNIVORE_BASE_DAILY_CAPACITY: float
- CARNIVORE_MIN_DAILY_DEMAND_FACTOR: float
- AVOIDANCE_PRESSURE_WEIGHT: float
- AVOIDANCE_PRESSURE_MAX: float
- INITIAL_ECOLOGY_MAX_DAYS: int
- INITIAL_ECOLOGY_STABILITY_WINDOW: int
- INITIAL_ECOLOGY_POPULATION_TOLERANCE: float
- INITIAL_ECOLOGY_VEGETATION_TOLERANCE: float
- TERRITORY_ACTIVITY_MARGIN: float
- TERRITORY_MIN_RADIUS: float
- TERRITORY_MAX_RADIUS: float
- _environments: Dictionary
- _bio_region_defs: Dictionary
- _species_states: Dictionary
- _carcasses: Array
- _carcass_serial: int
- _observable_consequences: Array
- TRIDAY_INTERVAL: int
- _day_counter: int
- is_processing_structured_spawn: bool
- _spawn_controller: SpawnController
- _simulation: EcologySimulation
- _day_counter_ref: Array[int]
- _last_initial_stabilization_days: int
- _last_initial_stabilization_stable: bool
- _last_initial_stabilization_aborted: bool
### Depends On
- SpeciesDatabase
- MapDatabase
- SpatialRegionResolver
- TimeSystem
- EnvironmentState
- SpeciesState
- PopulationCalculator
- SpawnController
- Corpse
- SpeciesDefinition
- BioRegionDefinition
- EcologyTraceFeedback
- EcologySimulation
- BioRegionInstance
- WorldManager
- SpawnRequest
- TerritoryState
- GroupPoisonState
- EcologySerializer
- SpeciesRelation
- GroupSkillState
- BiomeDatabase
### Used By
- Corpse
- DebugEcologyView
- DebugPanel
- DebugPanelActions
- DebugPoisonActions
- DebugPoisonView
- DebugSpawnView
- DebugTerritoryOverlay
- EcologyObservationUI
- EcologySimulation
- EcologyTraceFeedback
- Enemy
- EnemySpawner
- FireAgent
- NutrientCycle
- QuestGenerator
- SaveManager
- SaveSystem
- SpawnController
- SpawnLocationResolver
- TimeSystem
- WorldManager
- WorldMap
- WorldRoot
### Save Data
- Serialized via EcologySerializer
### Notes
- None

## GeneticDriftCalculator
### Purpose
- Stateless utility implementing Cumulative Moving Average (mu) drift and Atrophy models for evolutionary traits.
### Related Files
- core/systems/ecology/GeneticDriftCalculator.gd
### Responsibilities
- Applying genetic drift, applying atrophy, calculating trait tradeoffs, and calculating metabolic cost.
### Public API Methods
- apply_drift(state: SpeciesState, individual_scale: float, part_name: String = "") -> void
- apply_atrophy(state: SpeciesState, atrophy_factor: float = 0.05) -> void
- calculate_trait_tradeoffs(state: SpeciesState) -> Dictionary
- calculate_metabolic_cost(state: SpeciesState) -> float
### Signals
- Not Found
### Properties
- Not Found
### Owned Data
- Not Found
### Depends On
- SpeciesState
### Used By
- EcologySimulation
- PopulationCalculator
### Save Data
- None
### Notes
- None

## PopulationCalculator
### Purpose
- Stateless utility that computes target population, growth delta, and spawn needs based on environmental and biological factors.
### Related Files
- core/systems/ecology/PopulationCalculator.gd
### Responsibilities
- Calculating population dynamics, habitat suitability, carrying capacity, and mortality factor integration.
### Public API Methods
- calculate(env: EnvironmentState, def: SpeciesDefinition, state: SpeciesState, competition_factor: float = 0.0) -> Result
### Signals
- Not Found
### Properties
- Not Found
### Owned Data
- Not Found
### Depends On
- EnvironmentState
- SpeciesDefinition
- SpeciesState
- GeneticDriftCalculator
### Used By
- EcologyManager
- EcologySimulation
### Save Data
- None
### Notes
- None

## SpatialRegionResolver
### Purpose
- Centralized resolver mapping Vector3 positions to Area ID, Bio Region ID, and Territory ID.
### Related Files
- core/systems/ecology/SpatialRegionResolver.gd
### Responsibilities
- Resolving 3D positions to spatial identifiers.
- Managing registration of area nodes, bio-region nodes, and territories.
### Public API Methods
- get_instance() -> Node
- register_area_node(area: SpatialArea3D) -> void
- unregister_area_node(node: Node3D) -> void
- register_bio_region_node(node: Node3D) -> void
- unregister_bio_region_node(node: Node3D) -> void
- register_territory(territory: TerritoryState) -> void
- unregister_territory(territory: TerritoryState) -> void
- get_territory(territory_id: String) -> TerritoryState
- get_area_node(area_id: String) -> SpatialArea3D
- get_bio_region_node(bio_region_id: String) -> Node3D
- has_area_nodes() -> bool
- has_bio_region_nodes() -> bool
- resolve_area(position: Vector3) -> String
- resolve_bio_region(position: Vector3) -> String
- resolve_territory(position: Vector3, species_id: String) -> String
- get_group_territory_state(map_id: String, species_id: String, group_id: String) -> Dictionary
- is_spawn_blocked(position: Vector3) -> bool
### Signals
- Not Found
### Properties
- Not Found
### Owned Data
- _bio_region_nodes: Array
- _territories: Array[TerritoryState]
- area_nodes: Array[SpatialArea3D]
- spawn_blocker_nodes: Array[SpatialArea3D]
### Depends On
- TerritoryState
- SpatialArea3D
- SpatialBioRegion3D
- WorldManager
### Used By
- DebugEcologyView
- DebugPanel
- DefaultEnemyBehavior
- EcologyManager
- EcologyObservationUI
- EnemyAI
- SpatialArea3D
- SpatialBioRegion3D
- SpawnLocationResolver
- SpeciesRelation
- TerritoryState
- WorldMap
### Save Data
- None
### Notes
- None

## SpawnGroundResolver
### Purpose
- PLACEHOLDER
### Related Files
- core/systems/ecology/SpawnGroundResolver.gd
### Responsibilities
- PLACEHOLDER
### Public API Methods
- resolve_ground(world: World3D, xz_position: Vector3) -> Dictionary
- is_slope_valid(normal: Vector3, max_slope_degrees: float) -> bool
### Signals
- Not Found
### Properties
- Not Found
### Owned Data
- GROUND_RAY_HEIGHT: float
- GROUND_RAY_DEPTH: float
- GROUND_OFFSET: float
- DEFAULT_GROUND_COLLISION_MASK: int
- collision_mask: int
### Depends On
- Not Found
### Used By
- SpawnLocationResolver
### Save Data
- None
### Notes
- None

## SpawnRequest
### Purpose
- Lightweight data structure for passing spawn requests through the pipeline.
### Related Files
- core/systems/ecology/SpawnRequest.gd
### Responsibilities
- Carrying species, count, and environmental context for a spawn event.
### Public API Methods
- Not Found
### Signals
- Not Found
### Properties
- Not Found
### Owned Data
- area_id: StringName
- bio_region_id: StringName
- territory_id: StringName
- species_id: StringName
- count: int
- species_def: SpeciesDefinition
- env: EnvironmentState
- species_state: SpeciesState
### Depends On
- SpeciesDefinition
- EnvironmentState
- SpeciesState
### Used By
- EcologyManager
- EcologySimulation
- WorldMap
### Save Data
- None
### Notes
- None

## SpeciesRelation
### Purpose
- Maintains dynamic approach tendency and attack desire per area and species pair.
### Related Files
- core/systems/ecology/SpeciesRelation.gd
### Responsibilities
- Registry of species relation data.
- Management of approach tendency and attack desire values.
- Updating relations based on combat interaction deltas.
- Persistence of relation state via serialization.
### Public API Methods
- get_relation(scope_id: String, observer_species: String, target_species: String) -> Dictionary
- get_approach_tendency(scope_id: String, observer_species: String, target_species: String) -> float
- get_attack_desire(scope_id: String, observer_species: String, target_species: String) -> float
- set_relation(scope_id: String, observer_species: String, target_species: String, approach_tendency: float, attack_desire: float) -> void
- has_relation(scope_id: String, observer_species: String, target_species: String) -> bool
- record_interaction(group_id: String, observer_species: String, target_species: String, delta_approach: float, delta_attack: float) -> void
- on_combat_event(event: DamageEvent) -> void
- get_experience_sensitivity(species_id: String) -> float
- get_save_data() -> Dictionary
- load_save_data(data: Dictionary) -> void
- clear_all() -> void
- inherit_group(parent_group_id: String, child_group_id: String) -> void
- delete_group(group_id: String) -> void
### Signals
- Not Found
### Properties
- Not Found
### Owned Data
- BASE_DAMAGE_APPROACH_DELTA: float
- BASE_DAMAGE_ATTACK_DELTA: float
- BASE_KILL_APPROACH_DELTA: float
- BASE_KILL_ATTACK_DELTA: float
- BASE_DAMAGE_VICTIM_APPROACH_DELTA: float
- BASE_DAMAGE_VICTIM_ATTACK_DELTA: float
- BASE_KILL_VICTIM_APPROACH_DELTA: float
- BASE_KILL_VICTIM_ATTACK_DELTA: float
### Depends On
- SpatialRegionResolver
- DamageSystem
- SpeciesDatabase
- SpeciesDefinition
- DamageEvent
### Used By
- DamageSystem
- DefaultEnemyBehavior
- EcologyManager
- EcologySimulation
- UtilityScoringEngine
- WorldManager
- WorldMap
### Save Data
- Provides get_save_data
- Provides load_save_data
### Notes
- Resolves area using `SpatialRegionResolver.resolve_area` or `Spatial $\text{_}$ resolver.resolve_bio_region`, or via `map_id` property.
- Extracts species identity from `species_id` or `enemy_id` metadata/properties or the "player" group.
- Updates relation values by processing `DamageEvent` intensity (damage vs. kill).

## TerritoryState
### Purpose
- Runtime state container for species-specific biological territories.
### Related Files
- core/systems/ecology/TerritoryState.gd
### Responsibilities
- Storing spatial and identity data for a territory.
- Providing dictionary serialization support.
### Public API Methods
- contains_point(position: Vector3) -> bool
- contains_activity_point(position: Vector3) -> bool
- to_dict() -> Dictionary
- from_dict(d: Dictionary) -> void
### Signals
- Not Found
### Properties
- Not Found
### Owned Data
- territory_id: String
- species_id: String
- bio_region_id: String
- area_id: String
- center: Vector3
- radius: float
- activity_radius: float
### Depends On
- WorldManager
- SpatialRegionResolver
### Used By
- DebugEcologyView
- DebugTerritoryOverlay
- DefaultEnemyBehavior
- EcologyManager
- EcologyObservationUI
- EcologySimulation
- EnemyAI
- SpatialRegionResolver
- SpawnLocationResolver
- WorldMap
### Save Data
- None
### Notes
- None

## UtilityScoringEngine
### Purpose
- Stateless utility for computing AI decision-making scores (attack vs flee) based on biological and learned data.
### Related Files
- core/systems/ecology/UtilityScoringEngine.gd
### Responsibilities
- Calculating attack desire, flee desire, diet scaling, and threat penalty integration.
### Public API Methods
- calculate_flee_desire(group_id: String, observer_id: String, observer_power: float, target_id: String, target_power: float) -> float
### Signals
- Not Found
### Properties
- Not Found
### Owned Data
- Not Found
### Depends On
- SpeciesRelation
### Used By
- DefaultEnemyBehavior
- EnemyAI
### Save Data
- None
### Notes
- None

## EnemySkillSystem
### Purpose
- Manages the execution and cooldowns of skills for enemies.
### Related Files
- scenes/Characters/Enemies/EnemySkillSystem.gd
### Responsibilities
- Managing skill execution and cooldown tracking.
### Public API Methods
- execute(skill_id: String, owner: Node, target: Node) -> DamageEvent
### Signals
- Not Found
### Properties
- Not Found
### Owned Data
- registry: unmarked
### Depends On
- SkillRegistry
- DamageSystem
- DamageEvent
### Used By
- DefaultEnemyBehavior
- EnemyAI
- EnemyBehavior
### Save Data
- None
### Notes
- None

## EnemySpawner
### Purpose
- Automates the spawning of enemies at designated locations using a timer.
### Related Files
- scenes/Map/EnemySpawner.gd
### Responsibilities
- Registering spawn points and executing enemy spawning via timer.
### Public API Methods
- setup(container: Node) -> void
- register_spawn_points(map_id: String, positions: Array) -> void
- spawn_enemies_in_room(room: Node3D, map_id: String) -> void
- spawn_enemy_at(pos: Vector3, map_id: String) -> void
- register_spawn_point_with_species(species_id: String, map_id: String, pos: Vector3) -> Dictionary
- serialize_enemy(node: Node) -> Dictionary
- deserialize_enemy(data: Dictionary, container: Node) -> Node
- select_weighted_species(map_id: String) -> String
### Signals
- Not Found
### Properties
- Not Found
### Owned Data
- ENEMY_SCENE: unmarked
- _container: Node
### Depends On
- WorldManager
- Enemy
- EcologyManager
- SpeciesDefinition
- SpeciesDatabase
- EnemyAI
- MapDatabase
### Used By
- WorldManager
- WorldMap
- WorldRoot
### Save Data
- None
### Notes
- None

## GenerateMapFromDEM
### Purpose
- PLACEHOLDER
### Related Files
- scenes/Map/GenerateMapFromDEM.gd
### Responsibilities
- PLACEHOLDER
### Public API Methods
- build_terrain_mesh()
### Signals
- Not Found
### Properties
- dem_image_path: String
- grid_size: float
- height_scale: float
- generate_mesh_now: bool
### Owned Data
- height_map: unmarked
### Depends On
- Not Found
### Used By
- None
### Save Data
- None
### Notes
- None

## ObjectGenerator
### Purpose
- Instantiates interactable world objects at specific coordinates within a map.
### Related Files
- scenes/Map/ObjectGenerator.gd
### Responsibilities
- Handling object instantiation and spatial distribution.
### Public API Methods
- register_objects(map_id: String, config: Dictionary = {}) -> void
- generate_objects_in_room(room: Node3D, config: Dictionary = {}) -> void
- serialize_object(node: Node) -> Dictionary
- deserialize_object(data: Dictionary, container: Node) -> Node
### Signals
- Not Found
### Properties
- Not Found
### Owned Data
- INTERACTION_SCENE_BASE: unmarked
### Depends On
- InteractionObject
- WorldManager
### Used By
- WorldManager
- WorldRoot
### Save Data
- None
### Notes
- None

## SpecialRoomGenerator
### Purpose
- PLACEHOLDER
### Related Files
- scenes/Map/SpecialRoomGenerator.gd
### Responsibilities
- PLACEHOLDER
### Public API Methods
- process_special_room(_room: Node3D, _index: int) -> void
### Signals
- Not Found
### Properties
- Not Found
### Owned Data
- Not Found
### Depends On
- Not Found
### Used By
- None
### Save Data
- None
### Notes
- None

## QuestGenerator
### Purpose
- Procedurally generates new quests using templates or parameters.
### Related Files
- scenes/Quest/QuestGenerator.gd
### Responsibilities
- Procedural generation of quests using templates or parameters.
### Public API Methods
- evaluate_map(map_id: String) -> void
- generate_population_quests(map_id: String) -> Array
- generate_investigation_quests(map_id: String) -> Array
- generate_event_quests(_map_id: String) -> Array
- get_available_generated_quests() -> Array
- debug_generated_quests() -> void
- get_save_data() -> Dictionary
- load_save_data(data: Dictionary) -> void
- debug_generate()
### Signals
- Not Found
### Properties
- Not Found
### Owned Data
- OVERPOP_RATIO: float
- UNDERPOP_RATIO: float
- DANGER_EXTERMINATION_THRESHOLD: float
- DANGER_ELITE_THRESHOLD: float
- REWARD_GOLD_BASE: int
- REWARD_REP_BASE: int
- TARGET_KILL_COUNT: int
- _pending_quests: Array
### Depends On
- EcologyManager
- MapDatabase
- QuestManager
- EnemyDatabase
- SpeciesState
- SpeciesDefinition
- SpeciesDatabase
- EnemyStats
- TimeSystem
### Used By
- EcologySimulation
- SaveSystem
- TimeSystem
- WorldRoot
### Save Data
- Provides get_save_data
- Provides load_save_data
### Notes
- None

## QuestManager
### Purpose
- PLACEHOLDER
### Related Files
- scenes/Quest/QuestManager.gd
### Responsibilities
- PLACEHOLDER
### Public API Methods
- get_available_quests() -> Array[Dictionary]
- get_quest_definition(id: String) -> Dictionary
- accept_quest(id: String) -> bool
- abandon_quest(id: String) -> void
- register_kill(enemy_id: String) -> void
- is_completed(id: String) -> bool
- claim_reward(id: String) -> bool
- get_active_quest(id: String) -> Dictionary
- get_all_active_quests() -> Dictionary
- get_save_data() -> Dictionary
- load_save_data(data: Dictionary) -> void
### Signals
- Not Found
### Properties
- Not Found
### Owned Data
- available_quests: Array[Dictionary]
- active_quests: Dictionary
- completed_quests: Array[String]
- claimed_quests: Dictionary
### Depends On
- GameState
- EconomyManager
### Used By
- Enemy
- QuestGenerator
- SaveSystem
### Save Data
- Provides get_save_data
- Provides load_save_data
### Notes
- None

## AttachSystem
### Purpose
- PLACEHOLDER
### Related Files
- scenes/Systems/Combat/AttachSystem.gd
### Responsibilities
- PLACEHOLDER
### Public API Methods
- attach(target: Node) -> void
- detach() -> void
- has_attached_target() -> bool
- get_attached_target() -> Node
- set_carried(obj: Node) -> void
- get_carried() -> Node
- drop_carried() -> void
### Signals
- Not Found
### Properties
- Not Found
### Owned Data
- attached_target: Node
- _carried_object: Node
### Depends On
- InteractionSystem
### Used By
- EnemyAI
- InteractionSystem
- PlayerCombat
- PlayerMovement
### Save Data
- None
### Notes
- None

## DamageSystem
### Purpose
- Central damage pipeline for applying and resolving damage between entities.
### Related Files
- scenes/Systems/Combat/DamageSystem.gd
### Responsibilities
- Manages the damage lifecycle from attacker to target.
- Resolves and tags the damage source (PLAYER, ENEMY, or ENVIRONMENT) based on attacker group.
- Delivers damage to valid targets via `take_damage`.
- Emits damage events via signal.
- Notifies the `SpeciesRelation` system of combat events.
### Public API Methods
- apply_damage(attacker: Entity, target: Entity, amount: float, type: int = DamageEvent.Type.PHYSICAL, skill_id: String = "") -> DamageEvent
### Signals
- damage_applied(event: DamageEvent)
### Properties
- Not Found
### Owned Data
- Not Found
### Depends On
- DamageEvent
- StatusComponent
- Entity
- SpeciesRelation
### Used By
- DamageEvent
- EnemySkillSystem
- InteractionObject
- PlayerCombat
- PlayerSpell
- SpeciesRelation
### Save Data
- None
### Notes
- Resolves `DamageEvent.Source` based on whether the attacker is in the "player" or "enemies" group, or is null.
- Implementation relies on the `take_damage` method existing on the target `Entity`.

## FireAgent
### Purpose
- PLACEHOLDER
### Related Files
- scenes/Systems/FireAgent.gd
### Responsibilities
- PLACEHOLDER
### Public API Methods
- ignite() -> void
- extinguish() -> void
- try_ignite(applied_heat: float) -> bool
### Signals
- ignited()
- extinguished()
### Properties
- ignition_temperature_threshold: float
- burn_duration: float
- heat_radius: float
- heat_emission: float
### Owned Data
- is_burning: bool
- current_temperature: float
- _burn_timer: float
- region_id: String
### Depends On
- EnvironmentState
- EcologyManager
### Used By
- PlayerSpell
### Save Data
- None
### Notes
- None

## IndicatorFactory
### Purpose
- PLACEHOLDER
### Related Files
- scenes/Systems/Indicator/IndicatorFactory.gd
### Responsibilities
- PLACEHOLDER
### Public API Methods
- create_circle(radius: float, color: Color) -> Mesh
- create_target_circle(radius: float, color: Color) -> Mesh
- create_sector(radius: float, angle_deg: float, color: Color) -> Mesh
- create_line(length: float, color: Color) -> Mesh
### Signals
- Not Found
### Properties
- Not Found
### Owned Data
- SEGMENTS: unmarked
### Depends On
- Not Found
### Used By
- IndicatorManager
### Save Data
- None
### Notes
- None

## IndicatorManager
### Purpose
- PLACEHOLDER
### Related Files
- scenes/Systems/Indicator/IndicatorManager.gd
### Responsibilities
- PLACEHOLDER
### Public API Methods
- create_circle(pos: Vector3, radius: float, color: Color) -> int
- create_target_circle(pos: Vector3, radius: float, color: Color) -> int
- create_sector(pos, radius, angle, color) -> int
- create_line_between(from: Vector3, to: Vector3, color: Color) -> int
- face_camera(id: int, camera: Camera3D) -> void
- remove(id: int)
- set_position(id: int, pos: Vector3)
- exists(id: int) -> bool
### Signals
- Not Found
### Properties
- Not Found
### Owned Data
- INDICATOR_SCENE: unmarked
- IndicatorFactory: unmarked
- indicators: unmarked
- next_id: unmarked
### Depends On
- Indicator
- IndicatorFactory
### Used By
- TargetSystem
### Save Data
- None
### Notes
- None

## InteractionSystem
### Purpose
- PLACEHOLDER
### Related Files
- scenes/Systems/Interaction/InteractionSystem.gd
### Responsibilities
- PLACEHOLDER
### Public API Methods
- try_interact(interactor: Node, object: Node) -> bool
- try_pickup(carrier: Node, object: Node) -> bool
- drop(carrier: Node) -> void
- try_throw(carrier: Node, direction: Vector3, force: float) -> bool
- attach(target: Node) -> void
- detach() -> void
### Signals
- Not Found
### Properties
- Not Found
### Owned Data
- Not Found
### Depends On
- AttachSystem
- InteractionObject
- Corpse
### Used By
- AttachSystem
- InteractionObject
- Player
### Save Data
- None
### Notes
- None

## SaveSystem
### Purpose
- Handles the serialization and deserialization of the game's global state and the state of various interconnected subsystems.
### Related Files
- scenes/Systems/SaveSystem.gd
### Responsibilities
- Persisting game state to a JSON file at `user://savegame.json`.
- Loading and parsing existing save data from storage.
- Aggregating state from `WorldState`, `QuestManager`, `EcologyManager`, `TimeSystem`, and `QuestGenerator`.
- Synchronizing `GameState` properties (e.g., gold, reputation, spells, weapons) from the save file.
### Public API Methods
- save_game() -> void
- load_game() -> bool
### Signals
- Not Found
### Properties
- Not Found
### Owned Data
- SAVE_PATH: String
### Depends On
- GameState
- WorldState
- QuestManager
- TimeSystem
- QuestGenerator
- WorldManager
- EcologyManager
### Used By
- None
### Save Data
- None
### Notes
- Uses JSON format with tab indentation.
- Data extraction for `GameState` includes `gold`, `reputation`, `current_day`, `spell_mastery`, `unlocked_spells`, `discovered_spells`, `weapon_history`, `weapon_kills`, `current_weapon`, `monster_codex`, `monster_kill_counts`, and `environment`.
- During loading, handles the clearing and repopulation of arrays and dictionaries (e.g., `unlocked_spells`, `monster_codex`).

## SpawnController
### Purpose
- PLACEHOLDER
### Related Files
- scenes/Systems/SpawnController.gd
### Responsibilities
- PLACEHOLDER
### Public API Methods
- debug_spawn_at_position(region_id: String, def: SpeciesDefinition, position: Vector3, env: EnvironmentState) -> bool
### Signals
- Not Found
### Properties
- Not Found
### Owned Data
- ENEMY_SCENE: unmarked
- MAX_PER_REQUEST: int
- GROUP_SCATTER: float
- resolver: RefCounted
### Depends On
- EcologyManager
- EnvironmentState
- SpeciesDefinition
- WorldManager
- SpawnLocationResolver
- Enemy
- SpeciesState
- EnemyDatabase
- EnemyStats
### Used By
- DebugSpawnView
- EcologyManager
- WorldRoot
### Save Data
- None
### Notes
- None

## SpawnLocationResolver
### Purpose
- PLACEHOLDER
### Related Files
- scenes/Systems/SpawnLocationResolver.gd
### Responsibilities
- PLACEHOLDER
### Public API Methods
- resolve_spawn_request(req: RefCounted) -> Vector3
- is_spatial_request_valid(area_id: String, bio_region_id: String, territory_id: String) -> bool
- is_environment_suitable(def: SpeciesDefinition, env: EnvironmentState) -> bool
### Signals
- Not Found
### Properties
- Not Found
### Owned Data
- DEFAULT_MAX_SLOPE_DEGREES: float
- SPAWN_ATTEMPTS: int
- SPAWN_BOUNDS_MIN: unmarked
- SPAWN_BOUNDS_MAX: unmarked
- ground_resolver: SpawnGroundResolver
### Depends On
- SpatialRegionResolver
- EnvironmentState
- SpeciesDefinition
- SpawnGroundResolver
- TerritoryState
- EcologyManager
### Used By
- SpawnController
- WorldMap
### Save Data
- None
### Notes
- None

## TargetSystem
### Purpose
- PLACEHOLDER
### Related Files
- scenes/Systems/Targeting/TargetSystem.gd
### Responsibilities
- PLACEHOLDER
### Public API Methods
- toggle_screen_center_target() -> void
- is_attached_target_locked() -> bool
- set_target_volume(radius: float, length: float) -> void
- set_target(target: Node) -> void
- clear_target() -> void
- has_target() -> bool
- get_target() -> Node
- get_target_volume() -> Dictionary
- get_preferred_attach_target() -> Node3D
- is_target_volume_debug_visible() -> bool
- set_target_volume_debug_visible(enabled: bool) -> void
### Signals
- Not Found
### Properties
- max_target_distance: float
- target_screen_radius: float
- target_ray_radius: float
- target_indicator_camera_offset: float
- target_indicator_fallback_height: float
- target_ray_length: float
- debug_target_ray_duration: float
### Owned Data
- _debug_ray_handle: int
- player: Node
- current_target: Node
- attached_target: Node
- _attach_range_handle: int
- _target_handle: int
- _debug_target_volume: MeshInstance3D
- _target_volume_debug_visible: bool
### Depends On
- IndicatorManager
- Targetable
- PlayerCombat
### Used By
- DebugPanel
- DebugPanelActions
- DebugPoisonActions
- DebugPoisonView
- DebugUtilityView
- Enemy
- Player
- PlayerCombat
- PlayerLook
- Targetable
- WorldCamera
### Save Data
- None
### Notes
- None

## CraftingSystem
### Purpose
- Not Found
### Related Files
- scenes/Utils/CraftingSystem.gd
### Responsibilities
- Manages crafting workflows including recipe loading from JSON, tracking discovered recipes, executing crafting sessions (field vs settlement), and applying durability/quality penalties for field usage.
### Public API Methods
- is_recipe_known(recipe_id: String) -> bool
- discover_recipe(recipe_id: String) -> void
- get_crafting_modifier(recipe_id: String, is_field: bool) -> Dictionary
- is_crafting_active() -> bool
- execute_craft(recipe_id: String, is_field: bool) -> bool
- get_save_data() -> Dictionary
- load_save_data(data: Dictionary) -> void
### Signals
- Not Found
### Properties
- Not Found
### Owned Data
- _recipes: Dictionary
- _discovered: Dictionary
- _active_recipe_id: String
- _active_timer: float
- _active_is_field: bool
### Depends On
- EventBus
- ItemDatabase
- GameState
### Used By
- CraftingUI
- SaveManager
### Save Data
- Provides get_save_data
- Provides load_save_data
### Notes
- None

## MapKnowledgeManager
### Purpose
- Not Found
### Related Files
- scenes/Utils/MapKnowledgeManager.gd
### Responsibilities
- Manages Fog of War state using compressed bitmasks for sectors and manages both manual and knowledge-based map markers.
### Public API Methods
- is_sector_explored(sector: Vector2i) -> bool
- mark_sector_explored(sector: Vector2i) -> void
- mark_world_position_explored(world_pos: Vector3) -> void
- world_to_sector(world_pos: Vector3) -> Vector2i
- get_known_landmarks() -> Array[Dictionary]
- add_manual_marker(marker_dict: Dictionary) -> bool
- add_knowledge_marker(marker_dict: Dictionary) -> bool
- remove_marker(marker_id: String) -> bool
- get_all_markers() -> Array[Dictionary]
- get_save_data() -> Dictionary
- load_save_data(data: Dictionary) -> void
### Signals
- Not Found
### Properties
- Not Found
### Owned Data
- SECTOR_WORLD_SIZE: float
- CHUNK_SECTORS_PER_AXIS: int
- MAX_MANUAL_MARKERS: int
- MAX_KNOWLEDGE_MARKERS: int
- _explored_chunks: Dictionary
- _manual_markers: Array[Dictionary]
- _knowledge_markers: Array[Dictionary]
### Depends On
- EventBus
- WorldManager
### Used By
- MapReadingModeUI
- SaveManager
### Save Data
- Provides get_save_data
- Provides load_save_data
### Notes
- None

## SwarmSpawner
### Purpose
- Controls spawning of ant‑style swarm enemies and the hornet boss.
### Related Files
- scenes/Utils/SwarmSpawner.gd
### Responsibilities
- Spawning different enemy types (fast, tank, balanced) via timer or explicit command.
- Managing a collection of active swarm enemies up to a maximum size.
- Spawning a boss when the swarm reaches a specific size threshold.
- Configuring spawned enemies with speed, health, target references, and attraction strength if methods are available.
### Public API Methods
- spawn_swarm(boss_type: String, spawn_center: Vector3, count: int, enemy_type: String = "balanced") -> void
### Signals
- Not Found
### Properties
- fast_enemy_scene: PackedScene    # Fast, low hp enemy prefab
- tank_enemy_scene: PackedScene    # High hp, slow enemy prefab
- balanced_enemy_scene: PackedScene    # Balanced enemy prefab
- max_swarm_size: int
- spawn_interval: float
- spawn_radius: float
- pheromone_attraction_strength: float
- boss_scene: PackedScene
- boss_trigger_size: int
### Owned Data
- _spawn_timer: Timer
- _current_swarm: Array[Node]
### Depends On
- Player
- Boss
### Used By
- Boss
- WorldMap
- WorldRoot
### Save Data
- None
### Notes
- Periodically spawns random enemy types via an internal Timer.

## MapProvider
### Purpose
- PLACEHOLDER
### Related Files
- scenes/World/MapProvider.gd
### Responsibilities
- PLACEHOLDER
### Public API Methods
- setup(owner: Node) -> void
- generate() -> void
- regenerate() -> void
- clear() -> void
- spawn_enemy(_enemy_id: String, _pos: Vector3) -> Node
- spawn_object(_object_id: String, _pos: Vector3) -> Node
- spawn_item(_item_id: String, _pos: Vector3) -> Node
### Signals
- Not Found
### Properties
- Not Found
### Owned Data
- dungeon: Node
### Depends On
- Not Found
### Used By
- WorldMap
- WorldRoot
### Save Data
- None
### Notes
- None

## SpatialArea3D
### Purpose
- Represents an Area boundary in the Godot editor for spatial lookup without continuous physics monitoring.
### Related Files
- scenes/World/SpatialArea3D.gd
### Responsibilities
- Registering and unregistering with the SpatialRegionResolver autoload.
- Providing point containment checks within defined collision shapes (Box, Sphere, Cylinder).
### Public API Methods
- contains_point(position: Vector3) -> bool
### Signals
- Not Found
### Properties
- area_id: StringName
- area_priority: int
- definition: Resource
- altitude_override_enabled: bool
- altitude_override: float
- spawn_allowed: bool
- spawn_blocked: bool
### Owned Data
- Not Found
### Depends On
- SpatialRegionResolver
### Used By
- SpatialBioRegion3D
- SpatialRegionResolver
- WorldMap
### Save Data
- None
### Notes
- Explicitly disables monitoring and monitorable for performance.

## SpatialBioRegion3D
### Purpose
- Represents an ecological Bio Region boundary in the Godot editor for spatial lookup without continuous physics monitoring.
### Related Files
- scenes/World/SpatialBioRegion3D.gd
### Responsibilities
- Registering and unregistering with the SpatialRegionResolver autoload.
- Providing point containment checks within defined collision shapes (Box, Sphere, Cylinder).
### Public API Methods
- contains_point(pos: Vector3) -> bool
### Signals
- Not Found
### Properties
- bio_region_id: String
- area_id: String
- definition: Resource
### Owned Data
- Not Found
### Depends On
- SpatialArea3D
- SpatialRegionResolver
### Used By
- SpatialRegionResolver
### Save Data
- None
### Notes
- Explicitly disables monitoring and monitorable for performance.

## TreeGenerator
### Purpose
- PLACEHOLDER
### Related Files
- scenes/World/WorldMap/TreeGenerator.gd
### Responsibilities
- PLACEHOLDER
### Public API Methods
- Not Found
### Signals
- Not Found
### Properties
- terrain: Node3D
- min_distance_between_trees: float
- lod_begin: float
- lod_end: float
- forest_range_A: 
- forest_range_B: 
### Owned Data
- placed_positions: Array[Vector3]
### Depends On
- Not Found
### Used By
- None
### Save Data
- None
### Notes
- None

## WorldMap
### Purpose
- PLACEHOLDER
### Related Files
- scenes/World/WorldMap/WorldMap.gd
### Responsibilities
- PLACEHOLDER
### Public API Methods
- setup(owner: Node) -> void
- generate() -> void
- clear() -> void
- regenerate() -> void
- spawn_enemy(enemy_id: String, pos: Vector3) -> Node
- spawn_object(object_id: String, pos: Vector3) -> Node
- spawn_item(item_id: String, pos: Vector3) -> Node
- clear_spawned() -> void
### Signals
- Not Found
### Properties
- Not Found
### Owned Data
- ENEMY_SCENE: unmarked
- _swarm_spawner: Node
- _spawned: Array
- _spawned_dicts: Array
### Depends On
- SwarmSpawner
- SpawnRequest
- EnemySpawner
- EnemyDatabase
- ItemDatabase
- ObjectDatabase
- MapProvider
- Enemy
- EcologyManager
- SpatialRegionResolver
- TerritoryState
- SpatialArea3D
- SpawnLocationResolver
- SpeciesDatabase
- WorldManager
- InteractionObject
- SpeciesRelation
### Used By
- WorldRoot
### Save Data
- None
### Notes
- None

## WorldRoot
### Purpose
- PLACEHOLDER
### Related Files
- scenes/World/WorldRoot/WorldRoot.gd
### Responsibilities
- PLACEHOLDER
### Public API Methods
- regenerate_dungeon() -> void
### Signals
- Not Found
### Properties
- player_scene: PackedScene
- enemy_scene: PackedScene
- player_position_label: Label
- map_node: unmarked
### Owned Data
- DEBUG: int
- _map: MapProvider
- _village_ui: Control
- _village_layer: CanvasLayer
- _enemy_spawner: RefCounted
- _spawn_controller: Node
- _object_generator: RefCounted
- _feedback_node: Node3D
- _spawn_point: unmarked
- _poison_area: PoisonArea
- scenes_list: unmarked
- target_scene: unmarked
### Depends On
- SpawnController
- EnemySpawner
- ObjectGenerator
- WorldManager
- EcologyManager
- TimeSystem
- QuestGenerator
- MapProvider
- PoisonArea
- WorldMap
- DebugPanel
- EcologyObservationUI
- EcologyTraceFeedback
- WorldCamera
- Enemy
- EnvironmentState
- Player
- SwarmSpawner
### Used By
- None
### Save Data
- None
### Notes
- None

# Layer 3: Entities & Actors (player classes, NPC types, or unit behaviors)

## Boss
### Purpose
- Extends enemy functionality with specialized boss mechanics and phases.
### Related Files
- scenes/Characters/Enemies/Boss.gd
### Responsibilities
- Managing combat phases and boss abilities.
### Public API Methods
- apply_damage(amount: int) -> void
### Signals
- Not Found
### Properties
- max_health: int
- phase_durations: Array[float]
- swarm_spawner_path: NodePath
### Owned Data
- _current_health: int
- _current_phase: int
- _phase_timer: Timer
### Depends On
- SwarmSpawner
- Player
### Used By
- SwarmSpawner
### Save Data
- None
### Notes
- None

## EnemyAI
### Purpose
- Handles decision-making logic for enemy entities based on surroundings.
### Related Files
- scenes/Characters/Enemies/EnemyAI.gd
### Responsibilities
- Managing state, detection, and behavior loops.
### Public API Methods
- init(owner_node: Enemy) -> void
- tick(delta: float) -> void
- get_state_name() -> String
- is_idle() -> bool
- is_chasing() -> bool
- is_attacking() -> bool
- is_returning() -> bool
- get_debug_summary() -> String
- get_debug_observation() -> Dictionary
- get_debug_target_observation(target: Node) -> Dictionary
### Signals
- Not Found
### Properties
- Not Found
### Owned Data
- Enemy: unmarked
- behavior: unmarked
- _owner: Enemy
- attack_timer: float
- state: int
- spawn_position: Vector3
- _last_target: Entity
- _last_move_direction: Vector3
- _last_skill_id: String
- _last_approach_tendency: float
- _last_attack_desire: float
- _last_static_approach: float
- _last_static_attack: float
- _last_dynamic_approach: float
- _last_dynamic_attack: float
- _last_skill_weight: float
- RETURN_THRESHOLD: unmarked
- FEED_RANGE: float
- FEED_COOLDOWN: float
- FEED_POISON_TRANSFER_RATIO: float
- feed_timer: float
- _last_food_source: Corpse
### Depends On
- Enemy
- EnemyBehavior
- EnemySkillSystem
- AttachSystem
- Entity
- Corpse
- TerritoryState
- SpatialRegionResolver
- WorldManager
- UtilityScoringEngine
- NutrientCycle
- EnemySkill
- PoisonAvoidance
### Used By
- Enemy
- EnemySpawner
### Save Data
- None
### Notes
- None

## LogisticsNPC
### Purpose
- A CharacterBody3D representing a logistics NPC that travels along predefined paths and reacts to low health by fleeing and dropping resources.
### Related Files
- scenes/Characters/NPC/LogisticsNPC.gd
### Responsibilities
- Path navigation, health-based fleeing, resource dropping, combat alerting, damage reception, and distress signaling.
### Public API Methods
- take_damage(amount: float) -> void
- alert_escorts() -> void
- drop_resources_and_flee() -> void
### Signals
- Not Found
### Properties
- max_hp: float
- hp: float
- speed: float
- nav_agent: NavigationAgent3D
### Owned Data
- current_path_idx: int
- current_pt_idx: int
- is_fleeing: bool
- has_dropped_resources: bool
### Depends On
- WorldManager
- EventBus
### Used By
- None
### Save Data
- None
### Notes
- None

## Player
### Purpose
- The main controller for the player character entity, managing movement, combat, spells, status effects, and cart interactions.
### Related Files
- scenes/Characters/Player/Player.gd
### Responsibilities
- Vitality management, movement/combat/spell delegation, status effect management, cart attachment logic, target acquisition, weapon loading, and position history tracking.
### Public API Methods
- toggle_typing_mode(enabled_bool: bool)
- has_status(id: String) -> bool
- show_shout_effect(text_shout: String)
- take_damage(amount: float)
- submit_spell(text: String)
- die() -> void
### Signals
- mode_changed(is_typing_mode: bool)
### Properties
- movement_handler: unmarked
- combat_handler: unmarked
- spell_handler: unmarked
- look_handler: unmarked
- max_mp: unmarked
- spell_ui: unmarked
### Owned Data
- mp: unmarked
- statuses: unmarked
- is_invincible: bool
- weapons_data: unmarked
- has_left_weapon: bool
- has_right_weapon: bool
- HISTORY_MAX_SIZE: unmarked
- position_history: Array[Vector3]
- attached_cart: CharacterBody3D
- is_typing_mode: bool
- ui_layer: CanvasLayer
- hp_label: Label
- mp_label: Label
- total_damage_taken: float
- total_damage_dealt: float
- total_steps_taken: float
- equipped_spells: unmarked
### Depends On
- Entity
- PlayerMovement
- PlayerCombat
- PlayerSpell
- PlayerLook
- Cart
- TargetSystem
- PlayerStats
- StatusComponent
- CarryHelper
- InteractionSystem
### Used By
- Boss
- DebugPanelActions
- DebugPoisonActions
- DebugPoisonView
- DebugWorldView
- Entity
- PlayerCombat
- PlayerSpell
- StatusComponent
- SwarmSpawner
- WorldRoot
### Save Data
- None
### Notes
- None

## PlayerCombat
### Purpose
- Manages player offensive and defensive combat actions including auto-attacks, weapon throwing, and blocking.
### Related Files
- scenes/Characters/Player/PlayerCombat.gd
### Responsibilities
- Handling auto-attack timers and execution.
- Detecting nearby enemies for melee attacks.
- Managing weapon throwing logic (left/right).
- Processing player blocking state.
- Executing target attachment/detachment during combat.
- Processing damage reception including damage reduction via blocking and effects triggering.
### Public API Methods
- process_manual_attack() -> void
- manual_attack() -> void
- process_auto_attack(delta)
- auto_attack()
- process_weapon_throw()
- throw_weapon()
- process_block()
- find_attach_candidate() -> Node
- try_attach_target() -> int
- process_attach()
- process_attach_throw()
- process_attach_block()
- update_attached_target() -> void
- take_damage(amount: float)
- update_timers(delta)
### Signals
- Not Found
### Properties
- player: Node
- melee_damage: float
- knockback_force: float
- throw_force: float
- auto_attack_interval: float
### Owned Data
- is_blocking: bool
- auto_attack_timer: float
- e_was_pressed: bool
- lmb_was_pressed: bool
- ATTACH_RANGE: unmarked
### Depends On
- AttachSystem
- TargetSystem
- GameState
- DamageSystem
- Entity
- DamageEvent
- Targetable
- Player
- EventBus
- Effects
### Used By
- Player
- TargetSystem
### Save Data
- None
### Notes
- None

## PlayerDodge
### Purpose
- Handles the player's dodge mechanics including direction, duration, and cooldown management.
### Related Files
- scenes/Characters/Player/PlayerDodge.gd
### Responsibilities
- Executing dodge starts based on input direction.
- Managing active dodge duration and velocity adjustments.
- Handling dodge cooldown timers.
- Calculating movement vectors relative to the camera viewport.
### Public API Methods
- process_dodge(delta: float) -> bool
- update_timers(delta: float) -> void
### Signals
- Not Found
### Properties
- player: CharacterBody3D
- dodge_speed_multiplier: float
- dodge_duration: float
- dodge_cooldown: float
- dodge_jump_velocity: float
### Owned Data
- dodge_direction: Vector3
- is_dodging: bool
- dodge_timer: float
- dodge_cooldown_timer: float
### Depends On
- Not Found
### Used By
- PlayerMovement
### Save Data
- None
### Notes
- None

## PlayerLook
### Purpose
- Manages procedural rotation of the player's head and body towards targets or movement direction.
### Related Files
- scenes/Characters/Player/PlayerLook.gd
### Responsibilities
- Rotating the body node toward target positions.
- Rotating the head node toward camera view or TargetSystem targets.
- Clamping head rotation within defined yaw and pitch limits.
### Public API Methods
- process_look(delta: float) -> bool
- update_head_look(delta: float) -> bool
### Signals
- Not Found
### Properties
- player: CharacterBody3D
- body_node: Node3D
- head_node: Node3D
- body_rotation_speed: float
- head_rotation_speed: float
- head_max_yaw: float
- head_max_pitch: float
### Owned Data
- Not Found
### Depends On
- TargetSystem
### Used By
- Player
- WorldCamera
### Save Data
- None
### Notes
- None

## PlayerMovement
### Purpose
- Handles player locomotion including walking, running, dashing, and rolling, while managing movement constraints (slopes, weight-based speed debuffs). Enforces a movement lock during the crafting state.
### Related Files
- scenes/Characters/Player/PlayerMovement.gd
### Responsibilities
- Managing click-to-move navigation, speed modes, dash/roll mechanics, slope restrictions, and weight-based speed penalties.
### Public API Methods
- process_movement() -> void
- update_run_mode() -> void
- get_current_speed() -> float
- apply_gravity() -> void
- process_dodge(delta: float) -> bool
- process_step_detection(input_dir: Vector3) -> void
- update_timers(delta: float) -> void
### Signals
- Not Found
### Properties
- player: CharacterBody3D
- input_handler: unmarked
- dodge_handler: unmarked
- walk_speed: float
- run_speed: float
### Owned Data
- is_run_mode: bool
- posture_state: PostureState
- is_running: bool
- is_dodgeing: bool
- dodge_timer: float
- dodge_cooldown_timer: float
### Depends On
- PlayerMovementInput
- PlayerDodge
- EventBus
- GameState
- Cart
- PlayerStats
- StatusComponent
- AttachSystem
- Targetable
### Used By
- Player
### Save Data
- None
### Notes
- None

## PlayerMovementInput
### Purpose
- PLACEHOLDER
### Related Files
- scenes/Characters/Player/PlayerMovementInput.gd
### Responsibilities
- PLACEHOLDER
### Public API Methods
- get_direction() -> Vector3
### Signals
- Not Found
### Properties
- player: CharacterBody3D
### Owned Data
- Not Found
### Depends On
- Not Found
### Used By
- PlayerMovement
### Save Data
- None
### Notes
- None

## PlayerSpell
### Purpose
- A sophisticated spell-casting system that processes text input (typed/spoken simulation) to execute spells with mechanics involving linguistic similarity, fatigue, and "Tongue Bite" risk.
### Related Files
- scenes/Characters/Player/PlayerSpell.gd
### Responsibilities
- Text-to-spell parsing, managing linguistic boosts, handling tongue fatigue/bite risk, executing dynamic spell effects, providing visual feedback (shouts), and loading spells data.
### Public API Methods
- load_spells()
- process_spell_mode()
- process_spell_input()
- parse_repeats_and_clean(input_text: String, target_word: String) -> Dictionary
- parse_and_cast_spell(input_text: String)
- trigger_tongue_bite()
- resolve_tongue_bite_event()
- cast_spell_fail(input_text: String)
- cast_spell_effect(spell_id: String, sim_score: float, power_boost: float = 1.0, range_boost: float = 1.0)
- show_shout_effect(text_shout: String, sim_score: float = 1.0)
### Signals
- Not Found
### Properties
- player: Node
### Owned Data
- spells_by_id: unmarked
- recent_spell_id: String
- repeat_count: int
- tongue_fatigue: float
- tongue_bite_risk: float
### Depends On
- GameState
- Player
- SpellUI
- DamageSystem
- DamageEvent
- FireAgent
### Used By
- Player
### Save Data
- None
### Notes
- None

## Cart
### Purpose
- Manages the movement and destination of a cart entity.
### Related Files
- scenes/Map/Cart.gd
### Responsibilities
- Handling cart movement and setting destinations.
### Public API Methods
- Not Found
### Signals
- Not Found
### Properties
- Not Found
### Owned Data
- attached_player: CharacterBody3D
### Depends On
- InteractionObject
### Used By
- Player
- PlayerMovement
### Save Data
- None
### Notes
- None

## EcologyObservationUI
### Purpose
- PLACEHOLDER
### Related Files
- scenes/UI/EcologyObservationUI.gd
### Responsibilities
- PLACEHOLDER
### Public API Methods
- refresh_display() -> void
- get_current_region_id() -> String
- get_observation_summary() -> Dictionary
### Signals
- Not Found
### Properties
- Not Found
### Owned Data
- _panel: PanelContainer
- _title_label: Label
- _context_label: Label
- _env_label: Label
- _species_container: VBoxContainer
- _territory_container: VBoxContainer
- _refresh_timer: Timer
- _current_region_id: String
- _debug_console_mode: bool
- _debug_console_rect: Rect2
- _debug_console_visible: unmarked
### Depends On
- EcologyManager
- SpatialRegionResolver
- WorldManager
- EnvironmentState
- SpeciesState
- TerritoryState
### Used By
- DebugObservationView
- DebugPanel
- DebugPanelActions
- DebugSpawnView
- WorldRoot
### Save Data
- None
### Notes
- None

## DebugPanel
### Purpose
- PLACEHOLDER
### Related Files
- scenes/World/Debug/DebugPanel.gd
### Responsibilities
- PLACEHOLDER
### Public API Methods
- request_right_view_refresh() -> void
- set_observation_ui(observation_ui: Control) -> void
### Signals
- Not Found
### Properties
- Not Found
### Owned Data
- DebugPanelNavigation: unmarked
- DebugRightViewRefresh: unmarked
- DebugPanelActions: unmarked
- DebugTerritoryOverlay: unmarked
- DebugEntityOverlay: unmarked
- _right_refresh_pending: bool
- DEBUG_KEY: Key
- DEBUG_REFRESH_INTERVAL: float
- POISON_REFRESH_INTERVAL: float
- PARENT_BUTTON_COLOR: Color
- PARENT_BUTTON_OPEN_COLOR: Color
- CHILD_BUTTON_COLOR: Color
- _navigation_helper: RefCounted
- _territory_overlay: RefCounted
- _entity_overlay: Node3D
- _actions: RefCounted
- _subtab_buttons: Dictionary
- _debug_refresh_timer: float
- _panel: PanelContainer
- _tab_container: TabContainer
- _navigation: VBoxContainer
- _status_label: Label
- _right_panel: PanelContainer
- _right_diagnostic_host: VBoxContainer
- _observation_ui: Control
- _world_camera: Node
- _selected_group: String
- _selected_item: String
- _console_visible: bool
- _previous_mouse_mode: Input.MouseMode
- _right_views: Dictionary
- _active_right_view: Control
- _right_selected_group: String
- _right_selected_item: String
- _right_ecology_species_tab_index: int
- _locked_target_observation_enabled: bool
- _locked_target_observation_elapsed: float
- _target_volume_radius_spin: SpinBox
- _target_volume_distance_spin: SpinBox
- _target_volume_visible_button: Button
- DEBUG_OVERLAY_REFRESH_INTERVAL: float
- _debug_overlay_timer: float
- _subtab_contents: Dictionary
- _expanded_subtab: String
- _entity_debug_overlay_enabled: bool
- _territory_debug_overlay_enabled: bool
### Depends On
- DebugPanelNavigation
- DebugRightViewRefresh
- DebugPanelActions
- DebugTerritoryOverlay
- DebugEntityOverlay
- WorldCamera
- DebugEcologyView
- DebugPoisonView
- DebugUIHelpers
- EnvironmentState
- EcologyManager
- TimeSystem
- TargetSystem
- DebugObservationView
- Entity
- SpatialRegionResolver
- EcologyObservationUI
### Used By
- WorldRoot
### Save Data
- None
### Notes
- None

## EcologyTraceFeedback
### Purpose
- PLACEHOLDER
### Related Files
- scenes/World/EcologyTraceFeedback.gd
### Responsibilities
- PLACEHOLDER
### Public API Methods
- set_active_region(region_id: String) -> void
### Signals
- Not Found
### Properties
- Not Found
### Owned Data
- _active_region_id: String
- ecology_manager: Node
### Depends On
- EcologyManager
### Used By
- EcologyManager
- WorldRoot
### Save Data
- None
### Notes
- None

# Layer 4: Interface & Interaction (UI overlays, HUD elements, or camera systems)

## WorldCamera
### Purpose
- A 3D camera system providing orbit, follow, and zoom capabilities, including a specialized mode for typing-related viewpoints.
### Related Files
- scenes/Camera/WorldCamera.gd
### Responsibilities
- Execute orbit rotation based on mouse input.
- Implement spring-arm/zoom functionality via wheel input.
- Follow a target node at controlled heights and speeds.
- Handle camera transition into "typing mode" with localized constraints.
- Provide raycasting for viewporting (get_aim_ray).
### Public API Methods
- get_aim_ray() -> Dictionary
- set_typing_camera_mode(enabled_bool: bool) -> void
- set_debug_console_mode(enabled_bool: bool) -> void
### Signals
- Not Found
### Properties
- pivot: Node3D
- spring_arm: SpringArm3D
- cam: Camera3D
- target: Node3D
- follow_speed: float
- follow_height: float
- mouse_sensitivity: float
- rotation_smoothing: float
- min_pitch: float
- max_pitch: float
- zoom_speed: float
- min_spring_length: float
- max_spring_length: float
- zoom_smoothing: float
- target_zoom_length: float
- target_focus_weight: float
- target_camera_smoothing: float
### Owned Data
- _target_rotation_x: float
- _target_rotation_y: float
- _target_spring_length: float
- _is_target_mode: bool
- _current_target: Node3D
- _is_typing_camera_mode: bool
- _typing_anchor_y: float
- _typing_anchor_x: float
- _debug_console_mode: bool
### Depends On
- PlayerLook
- TargetSystem
### Used By
- DebugPanel
- WorldRoot
### Save Data
- None
### Notes
- None

## SpellCard
### Purpose
- A lightweight data-binding component that populates a UI card with spell information (name, description, verbal keyword, and mana cost).
### Related Files
- scenes/Characters/Player/Spell/SpellCard.gd
### Responsibilities
- Populating UI elements from dictionary input.
### Public API Methods
- setup(spell_data: Dictionary)
### Signals
- Not Found
### Properties
- Not Found
### Owned Data
- Not Found
### Depends On
- Not Found
### Used By
- None
### Save Data
- None
### Notes
- None

## SpellUI
### Purpose
- Manages the UI overlay for the spell-casting mode, including the text input field and a grid of visual spell cards.
### Related Files
- scenes/Characters/Player/Spell/SpellUI.gd
### Responsibilities
- Generating the dynamic grid, instantiating spell cards, managing text input integration, layout management, and mastery visualization.
### Public API Methods
- focus_input()
- refresh_spell_cards(spells_data: Dictionary)
### Signals
- Not Found
### Properties
- spell_input: unmarked
- spell_cards: unmarked
- spell_card_scene: PackedScene
### Owned Data
- grid: GridContainer
### Depends On
- GameState
### Used By
- PlayerSpell
### Save Data
- None
### Notes
- None

## InteractionObject
### Purpose
- Detects player proximity and executes interaction logic when triggered.
### Related Files
- scenes/Map/InteractionObject.gd
### Responsibilities
- Proximity detection and interaction execution.
### Public API Methods
- interact(_interactor: Node) -> void
- apply_damage(attacker: Entity, amount: float) -> DamageEvent
- take_damage(amount: float) -> void
- destroy() -> void
- on_destroy() -> void
- on_pickup(_carrier: Node) -> void
- on_throw(_direction: Vector3, _force: float) -> void
### Signals
- Not Found
### Properties
- object_id: String
- object_type: String
- weight: float
- interactable: bool
- movable: bool
- breakable: bool
- is_pickable: bool
- is_throwable: bool
### Owned Data
- targetable: Targetable
### Depends On
- Corpse
- Entity
- InteractionSystem
- Targetable
- DamageSystem
- DamageEvent
### Used By
- Cart
- InteractionSystem
- ObjectGenerator
- WorldMap
### Save Data
- None
### Notes
- None

## CraftingUI
### Purpose
- Not Found
### Related Files
- scenes/UI/Crafting/CraftingUI.gd
### Responsibilities
- User interface for selecting recipes and managing crafting buttons in both settlement and field modes.
### Public API Methods
- open_crafting(field_mode: bool = true) -> void
- close_crafting() -> void
### Signals
- Not Found
### Properties
- recipe_container: VBoxContainer
- craft_button: Button
### Owned Data
- selected_recipe_id: String
- is_field_mode: bool
### Depends On
- CraftingSystem
- EventBus
### Used By
- None
### Save Data
- None
### Notes
- None

## MapReadingModeUI
### Purpose
- Not Found
### Related Files
- scenes/UI/Map/MapReadingModeUI.gd
### Responsibilities
- Diegetic UI overlay for viewing the physical map, fog of war, and markers.
### Public API Methods
- toggle_map() -> void
### Signals
- Not Found
### Properties
- map_panel: Control
- fog_container: Control
- marker_container: Control
### Owned Data
- is_open: bool
### Depends On
- MapKnowledgeManager
- EventBus
### Used By
- None
### Save Data
- None
### Notes
- None

# Layer 5: Classification Pending

## PoisonStatusEffect
### Purpose
- PLACEHOLDER
### Related Files
- core/components/PoisonStatusEffect.gd
### Responsibilities
- PLACEHOLDER
### Public API Methods
- add_poison_amount(amount: float, duration: float = POISON_DOSE_DURATION) -> float
- set_poison_amount(value: float, duration: float = POISON_DOSE_DURATION) -> void
- get_poison_amount() -> float
- get_stacks() -> int
- set_stacks(value: int) -> void
- get_poison_level() -> int
- get_attack_multiplier() -> float
- get_speed_multiplier() -> float
- get_defense_multiplier() -> float
- get_performance_multiplier() -> float
- get_threshold_level() -> int
- is_aggressive() -> bool
- has_dependency() -> bool
- refresh_stacks(value: int, new_duration: float) -> void
- tick(delta: float) -> void
- is_expired() -> bool
- get_dose_snapshot() -> Array[Dictionary]
### Signals
- Not Found
### Properties
- Not Found
### Owned Data
- POISON_STACK_UNIT: float
- POISON_DOSE_DURATION: float
- THRESHOLD_1: float
- THRESHOLD_2: float
- THRESHOLD_3: float
- ATTACK_1: float
- ATTACK_2: float
- ATTACK_3: float
- SPEED_1: float
- SPEED_2: float
- SPEED_3: float
- DEFENSE_1: float
- DEFENSE_2: float
- DEFENSE_3: float
- poison_amount: float
- threshold_level: int
- attack_multiplier: float
- speed_multiplier: float
- defense_multiplier: float
- damage_multiplier: float
- aggressive: bool
- dependent: bool
### Depends On
- StatusEffect
### Used By
- DebugPoisonView
- Entity
- StatusComponent
### Save Data
- None
### Notes
- None

## BehaviorProfile
### Purpose
- PLACEHOLDER
### Related Files
- core/databases/BehaviorProfile.gd
### Responsibilities
- PLACEHOLDER
### Public API Methods
- apply_personality_modifiers_once() -> void
- set_territorial_expansion(value: float) -> void
- set_group_combat_tendency(value: float) -> void
- set_approach_tendency(target_species: String, value: float) -> void
- set_attack_intent(target_species: String, value: float) -> void
- get_approach_tendency(target_species: String) -> float
- get_attack_intent(target_species: String) -> float
- get_experience_sensitivity() -> float
- get_territorial_expansion() -> float
- get_group_combat_tendency() -> float
### Signals
- Not Found
### Properties
- personality_tags: Array[String]
- approach_tendency_by_species: Dictionary[String, float]
- attack_intent_by_species: Dictionary[String, float]
### Owned Data
- _personality_modifiers_applied: bool
### Depends On
- Not Found
### Used By
- SpeciesDefinition
### Save Data
- None
### Notes
- None

## EcologySimulation
### Purpose
- PLACEHOLDER
### Related Files
- core/systems/ecology/EcologySimulation.gd
### Responsibilities
- PLACEHOLDER
### Public API Methods
- initialize(manager: Node, environments: Dictionary, bio_region_defs: Dictionary, species_states: Dictionary, carcasses: Array, observable_consequences: Array, day_counter_ref: Array[int]) -> void
- update_region_day(region_id: String, allow_materialization: bool = true) -> void
- calculate_effective_activity_radius(region_id: String, species_id: String, target_species_id: String) -> float
- on_triday_settlement() -> void
### Signals
- Not Found
### Properties
- Not Found
### Owned Data
- DEBUG: int
- CARCASS_DECOMPOSITION_DAYS: float
- CARCASS_DETRITUS_YIELD: float
- CARNIVORE_CARRION_YIELD: float
- DETRITUS_PROCESS_RATE: float
- DETRITUS_FERTILITY_YIELD: float
- ACTIVITY_APPROACH_WEIGHT: float
- ACTIVITY_FOOD_DEFICIT_WEIGHT: float
- ACTIVITY_MIN_FACTOR: float
- ACTIVITY_MAX_FACTOR: float
- POISON_ACTIVITY_MIN_FACTOR: float
- POISON_ACTIVITY_MAX_FACTOR: float
- POISON_ACTIVITY_WEIGHT: float
- POISON_STRESS_WEIGHT: float
- POISON_FOOD_PENALTY_WEIGHT: float
- CARNIVORE_BASE_DAILY_CAPACITY: float
- CARNIVORE_MIN_DAILY_DEMAND_FACTOR: float
- AVOIDANCE_PRESSURE_MAX: float
- AVOIDANCE_BASE_DISTANCE: float
- AVOIDANCE_MIN_DISTANCE_FACTOR: float
- AVOIDANCE_MAX_DISTANCE_FACTOR: float
- HERBIVORE_BASE_DAILY_CONSUMPTION: float
- HERBIVORE_MAX_DAILY_CONSUMPTION: float
- SWARM_SPIKE_THRESHOLD: float
- GROUP_SPLIT_SEPARATION_DISTANCE: float
- GROUP_SPLIT_DELAY_DAYS: float
- GROUP_SPLIT_MIN_CLUSTER_SIZE: int
- _manager: Node
- _environments: Dictionary
- _bio_region_defs: Dictionary
- _species_states: Dictionary
- _carcasses: Array
- _observable_consequences: Array
- _day_counter_ref: Array[int]
### Depends On
- EcologyManager
- EnvironmentState
- SpeciesState
- SpeciesDefinition
- PopulationCalculator
- GeneticDriftCalculator
- SpeciesRelation
- EnemyStats
- QuestGenerator
- WorldManager
- TerritoryState
- GroupPoisonState
- SpawnRequest
### Used By
- EcologyManager
- WorldManager
### Save Data
- None
### Notes
- None

## GroupPoisonState
### Purpose
- PLACEHOLDER
### Related Files
- core/systems/ecology/GroupPoisonState.gd
### Responsibilities
- PLACEHOLDER
### Public API Methods
- add_exposure(group_id: String, species_id: String, applied_amount: float) -> void
- set_exposure(group_id: String, species_id: String, value: float) -> void
- get_exposure(group_id: String, species_id: String) -> float
- get_resistance(group_id: String, species_id: String) -> float
- get_tolerance(group_id: String, species_id: String) -> float
- commit_daily_adaptation() -> void
- get_avoidance_weight(group_id: String, species_id: String) -> float
- reset() -> void
### Signals
- Not Found
### Properties
- Not Found
### Owned Data
- DEFAULT_ADAPTATION_SCALE: float
- DAILY_ADAPTATION_RETENTION: float
### Depends On
- SpeciesDefinition
- SpeciesDatabase
### Used By
- DebugEntityOverlay
- DebugPoisonActions
- DebugPoisonView
- EcologyManager
- EcologySimulation
- Entity
- PoisonAvoidance
### Save Data
- None
### Notes
- None

## NutrientCycle
### Purpose
- PLACEHOLDER
### Related Files
- core/systems/ecology/NutrientCycle.gd
### Responsibilities
- PLACEHOLDER
### Public API Methods
- return_to_soil(region_id: String, units: float) -> void
- excrete(region_id: String, _center: Vector3, _radius: float, units: float) -> void
### Signals
- Not Found
### Properties
- Not Found
### Owned Data
- NUTRITION_TO_DETRITUS: float
### Depends On
- EcologyManager
- EnvironmentState
### Used By
- Corpse
- EnemyAI
### Save Data
- None
### Notes
- None

## PoisonAvoidance
### Purpose
- PLACEHOLDER
### Related Files
- core/systems/ecology/PoisonAvoidance.gd
### Responsibilities
- PLACEHOLDER
### Public API Methods
- compute(owner: Node3D) -> Dictionary
- steer(owner: Node3D, base_direction: Vector3) -> Vector3
### Signals
- Not Found
### Properties
- Not Found
### Owned Data
- MARGIN: float
- IDLE_ESCAPE_WEIGHT: float
### Depends On
- PoisonArea
- GroupPoisonState
### Used By
- DebugPoisonView
- DefaultEnemyBehavior
- EnemyAI
### Save Data
- None
### Notes
- None

## DebugEcologyView
### Purpose
- PLACEHOLDER
### Related Files
- scenes/World/Debug/DebugEcologyView.gd
### Responsibilities
- PLACEHOLDER
### Public API Methods
- refresh(content: VBoxContainer, selected_item: String, region_id: String) -> void
- set_refresh_callback(callback: Callable) -> void
- get_runtime_species_count(tree: SceneTree, species_id: String) -> int
### Signals
- Not Found
### Properties
- Not Found
### Owned Data
- Not Found
### Depends On
- DebugUIHelpers
- WorldManager
- EnvironmentState
- EcologyManager
- SpeciesState
- TimeSystem
- TerritoryState
- SpatialRegionResolver
### Used By
- DebugPanel
- DebugPanelActions
- DebugRightViewRefresh
### Save Data
- None
### Notes
- None

## DebugEntityOverlay
### Purpose
- PLACEHOLDER
### Related Files
- scenes/World/Debug/DebugEntityOverlay.gd
### Responsibilities
- PLACEHOLDER
### Public API Methods
- Not Found
### Signals
- Not Found
### Properties
- Not Found
### Owned Data
- MAX_LABELS: int
- TEXT_INTERVAL: float
- LABEL_HEIGHT: float
- FONT_PIXEL_SIZE: float
- radius: float
- show_enemies: bool
- show_corpses: bool
- show_player: bool
- _labels: Array[Label3D]
- _text_timer: float
### Depends On
- Corpse
- Entity
- Enemy
- GroupPoisonState
### Used By
- DebugPanel
- DebugPoisonActions
### Save Data
- None
### Notes
- None

## DebugObservationView
### Purpose
- PLACEHOLDER
### Related Files
- scenes/World/Debug/DebugObservationView.gd
### Responsibilities
- PLACEHOLDER
### Public API Methods
- set_locked_observation(observation: Dictionary) -> void
- clear_locked_observation() -> void
- refresh(content: VBoxContainer, selected_item: String, observation_ui: Control) -> void
### Signals
- Not Found
### Properties
- Not Found
### Owned Data
- Not Found
### Depends On
- DebugUIHelpers
- EcologyObservationUI
- Entity
### Used By
- DebugPanel
- DebugRightViewRefresh
### Save Data
- None
### Notes
- None

## DebugPanelActions
### Purpose
- PLACEHOLDER
### Related Files
- scenes/World/Debug/DebugPanelActions.gd
### Responsibilities
- PLACEHOLDER
### Public API Methods
- build_subtab_actions(parent: VBoxContainer, group_name: String, item_name: String) -> void
### Signals
- Not Found
### Properties
- Not Found
### Owned Data
- _panel: Node
- _debug_species_option: OptionButton
- _debug_consequence_option: OptionButton
- _debug_consequence_selected_type: String
- ecology_manger: Node
- world_manager: Node
- observation_ui: Node
- target_system: Node
### Depends On
- EcologyManager
- WorldManager
- EcologyObservationUI
- TargetSystem
- Player
- Entity
- TimeSystem
- DebugPoisonActions
- EnvironmentState
- SpeciesState
- DebugEcologyView
- PoisonArea
- DebugSpawnView
### Used By
- DebugPanel
### Save Data
- None
### Notes
- None

## DebugPanelNavigation
### Purpose
- PLACEHOLDER
### Related Files
- scenes/World/Debug/DebugPanelNavigation.gd
### Responsibilities
- PLACEHOLDER
### Public API Methods
- build_navigation() -> void
- refresh_navigation_selection() -> void
- build_tabs() -> void
- resolve_diagnostic_selection(group_name: String, item_name: String) -> Dictionary
- create_expandable_subtab(parent: VBoxContainer, group_name: String, item_name: String) -> void
- refresh_subtab_buttons() -> void
- collapse_all_subtabs() -> void
- rebuild_expanded_subtab() -> void
- on_group_tab_changed(tab_index: int) -> void
### Signals
- Not Found
### Properties
- Not Found
### Owned Data
- NAVIGATION_SELECTED_COLOR: Color
- PARENT_BUTTON_COLOR: Color
- _panel: Node
### Depends On
- Entity
- DebugPoisonView
### Used By
- DebugPanel
### Save Data
- None
### Notes
- None

## DebugPoisonActions
### Purpose
- PLACEHOLDER
### Related Files
- scenes/World/Debug/DebugPoisonActions.gd
### Responsibilities
- PLACEHOLDER
### Public API Methods
- build_controls(parent: VBoxContainer, item_name: String, tree: SceneTree, get_region: Callable, spawn_position: Callable, refresh: Callable) -> void
- is_debug_area(node: Node) -> bool
- get_locked_target(tree: SceneTree) -> Node
- set_last_action(text: String) -> void
- set_env_poison(get_region: Callable, value: float, refresh: Callable) -> void
- create_area(tree: SceneTree, get_region: Callable, linked: bool, at_feet: bool, spawn_position: Callable, refresh: Callable) -> void
- apply_settings_to_debug_areas(tree: SceneTree, refresh: Callable) -> void
- remove_debug_areas(tree: SceneTree, refresh: Callable) -> void
- dose_player(tree: SceneTree, refresh: Callable) -> void
- clear_player(tree: SceneTree, refresh: Callable) -> void
- dose_target(tree: SceneTree, refresh: Callable) -> void
- clear_target(tree: SceneTree, refresh: Callable) -> void
- dose_enemies(tree: SceneTree, refresh: Callable) -> void
- clear_enemies(tree: SceneTree, refresh: Callable) -> void
- poison_nearest_corpse(tree: SceneTree, refresh: Callable) -> void
- dose_corpses(tree: SceneTree, refresh: Callable) -> void
- clear_corpses(tree: SceneTree, refresh: Callable) -> void
- add_tolerance_exposure(tree: SceneTree, refresh: Callable) -> void
- commit_tolerance_adaptation(refresh: Callable) -> void
- reset_tolerance(refresh: Callable) -> void
- set_overlay_enabled(tree: SceneTree, enabled: bool, refresh: Callable) -> void
### Signals
- Not Found
### Properties
- Not Found
### Owned Data
- DEBUG_META: StringName
- LINKED_PREFIX: String
- MANUAL_PREFIX: String
- ENV_PRESETS: Array[float]
### Depends On
- DebugEntityOverlay
- DebugUIHelpers
- TargetSystem
- EnvironmentState
- EcologyManager
- PoisonArea
- Player
- Enemy
- Corpse
- StatusComponent
- Entity
- GroupPoisonState
### Used By
- DebugPanelActions
- DebugPoisonView
### Save Data
- None
### Notes
- None

## DebugPoisonView
### Purpose
- PLACEHOLDER
### Related Files
- scenes/World/Debug/DebugPoisonView.gd
### Responsibilities
- PLACEHOLDER
### Public API Methods
- refresh(content: VBoxContainer, tree: SceneTree, region_id: String) -> void
- set_refresh_callback(callback: Callable) -> void
- set_selected_dataset(dataset: String) -> void
### Signals
- Not Found
### Properties
- Not Found
### Owned Data
- LIST_LIMIT: int
- DOSE_LIST_LIMIT: int
- EPSILON: float
- RATE_MIN_INTERVAL_SEC: float
- RATE_MAX_INTERVAL_SEC: float
### Depends On
- PoisonArea
- DebugUIHelpers
- Entity
- Corpse
- DebugPoisonActions
- Player
- Enemy
- GroupPoisonState
- EnvironmentState
- EcologyManager
- StatusComponent
- TargetSystem
- PoisonAvoidance
- PoisonStatusEffect
### Used By
- DebugPanel
- DebugPanelNavigation
- DebugRightViewRefresh
### Save Data
- None
### Notes
- None

## DebugRightViewRefresh
### Purpose
- PLACEHOLDER
### Related Files
- scenes/World/Debug/DebugRightViewRefresh.gd
### Responsibilities
- PLACEHOLDER
### Public API Methods
- refresh(panel: Node) -> void
### Signals
- Not Found
### Properties
- Not Found
### Owned Data
- Not Found
### Depends On
- DebugWorldView
- DebugObservationView
- DebugTimeView
- DebugEcologyView
- DebugPoisonView
- DebugSpawnView
- DebugUtilityView
- DebugUIHelpers
### Used By
- DebugPanel
### Save Data
- None
### Notes
- None

## DebugSpawnView
### Purpose
- PLACEHOLDER
### Related Files
- scenes/World/Debug/DebugSpawnView.gd
### Responsibilities
- PLACEHOLDER
### Public API Methods
- refresh(content: VBoxContainer, selected_item: String, tree: SceneTree, region_id: String = "") -> void
- spawn_one(panel: Node, tree: SceneTree, region_id: String, species_id: String) -> void
- kill_one(panel: Node, tree: SceneTree, region_id: String, species_id: String) -> void
- create_carcass(player_position: Vector3, species_id: String, region_id: String) -> void
### Signals
- Not Found
### Properties
- Not Found
### Owned Data
- Not Found
### Depends On
- DebugUIHelpers
- EcologyManager
- SpawnController
- EcologyObservationUI
- EnvironmentState
- SpeciesDatabase
- SpeciesDefinition
- WorldManager
### Used By
- DebugPanelActions
- DebugRightViewRefresh
### Save Data
- None
### Notes
- None

## DebugTerritoryOverlay
### Purpose
- PLACEHOLDER
### Related Files
- scenes/World/Debug/DebugTerritoryOverlay.gd
### Responsibilities
- PLACEHOLDER
### Public API Methods
- refresh(panel: Node) -> void
- clear() -> void
### Signals
- Not Found
### Properties
- Not Found
### Owned Data
- TERRITORY_DEBUG_SEGMENTS: int
- TERRITORY_DEBUG_Y_OFFSET: float
- TERRITORY_DEBUG_GROUP_SEGMENTS: int
- TERRITORY_DEBUG_GROUP_MARGIN: float
- TERRITORY_DEBUG_GROUP_MIN_RADIUS: float
- TERRITORY_DEBUG_GROUP_Y_OFFSET: float
- TERRITORY_DEBUG_DASH_INTERVAL: int
- TERRITORY_DEBUG_ACTIVITY_Y_OFFSET: float
- TERRITORY_DEBUG_INDIVIDUAL_SIZE: float
- TERRITORY_DEBUG_INFLUENCE_Y_OFFSET: float
- TERRITORY_DEBUG_CELL_Y_OFFSET: float
- _mesh_instance: MeshInstance3D
- _group_labels: Dictionary
### Depends On
- WorldManager
- EcologyManager
- TerritoryState
### Used By
- DebugPanel
### Save Data
- None
### Notes
- None

## DebugTimeView
### Purpose
- PLACEHOLDER
### Related Files
- scenes/World/Debug/DebugTimeView.gd
### Responsibilities
- PLACEHOLDER
### Public API Methods
- refresh(content: VBoxContainer, selected_item: String) -> void
### Signals
- Not Found
### Properties
- Not Found
### Owned Data
- Not Found
### Depends On
- DebugUIHelpers
- TimeSystem
### Used By
- DebugRightViewRefresh
### Save Data
- None
### Notes
- None

## DebugUIHelpers
### Purpose
- PLACEHOLDER
### Related Files
- scenes/World/Debug/DebugUIHelpers.gd
### Responsibilities
- PLACEHOLDER
### Public API Methods
- add_section_title(parent: Control, text: String) -> void
- add_value_row(parent: Control, label_text: String, value_text: String) -> void
- add_action_button(parent: Control, text: String, callback: Callable) -> void
- add_message(parent: Control, text: String) -> void
- add_separator(parent: Control) -> void
- clear_control_children(parent: Control) -> void
### Signals
- Not Found
### Properties
- Not Found
### Owned Data
- SECTION_TITLE_SCENE: PackedScene
- VALUE_ROW_SCENE: PackedScene
- ACTION_BUTTON_SCENE: PackedScene
- MESSAGE_SCENE: PackedScene
### Depends On
- Not Found
### Used By
- DebugEcologyView
- DebugObservationView
- DebugPanel
- DebugPoisonActions
- DebugPoisonView
- DebugRightViewRefresh
- DebugSpawnView
- DebugTimeView
- DebugUtilityView
- DebugWorldView
### Save Data
- None
### Notes
- None

## DebugUtilityView
### Purpose
- PLACEHOLDER
### Related Files
- scenes/World/Debug/DebugUtilityView.gd
### Responsibilities
- PLACEHOLDER
### Public API Methods
- refresh(content: VBoxContainer, selected_item: String) -> void
### Signals
- Not Found
### Properties
- Not Found
### Owned Data
- Not Found
### Depends On
- DebugUIHelpers
- TargetSystem
### Used By
- DebugRightViewRefresh
### Save Data
- None
### Notes
- None

## DebugWorldView
### Purpose
- PLACEHOLDER
### Related Files
- scenes/World/Debug/DebugWorldView.gd
### Responsibilities
- PLACEHOLDER
### Public API Methods
- refresh(content: VBoxContainer, selected_item: String, tree: SceneTree, region_id: String) -> void
### Signals
- Not Found
### Properties
- Not Found
### Owned Data
- Not Found
### Depends On
- DebugUIHelpers
- Player
### Used By
- DebugRightViewRefresh
### Save Data
- None
### Notes
- None

## PoisonArea
### Purpose
- PLACEHOLDER
### Related Files
- scenes/World/PoisonArea.gd
### Responsibilities
- PLACEHOLDER
### Public API Methods
- setup_from_environment(env: EnvironmentState) -> void
- contains_position(position: Vector3) -> bool
- get_poison_exposure_amount(delta: float) -> float
- refresh_visual() -> void
### Signals
- Not Found
### Properties
- region_id: String
- exposure_amount_per_second: float
- exposure_distance: float
- materialize_threshold: float
### Owned Data
- DEFAULT_MATERIALIZE_THRESHOLD: float
- environment_state: EnvironmentState
- _visual_mesh: MeshInstance3D
### Depends On
- EnvironmentState
- Entity
- Corpse
### Used By
- DebugPanelActions
- DebugPoisonActions
- DebugPoisonView
- DefaultEnemyBehavior
- PoisonAvoidance
- WorldRoot
### Save Data
- None
### Notes
- None

## TreeWood
### Purpose
- PLACEHOLDER
### Related Files
- scenes/World/TreeWood.gd
### Responsibilities
- PLACEHOLDER
### Public API Methods
- take_damage(amount: float) -> void
- fall() -> void
- collect_wood() -> int
- can_attach() -> bool
- begin_attach_tracking() -> void
- update_attached_motion(player: Node3D) -> void
### Signals
- Not Found
### Properties
- tree_max_hp: float
- wood_amount: int
- roll_distance_scale: float
### Owned Data
- state: State
- _last_attached_position: Vector3
- _has_attached_position: bool
- _tree_visual: MeshInstance3D
### Depends On
- Entity
- Targetable
### Used By
- None
### Save Data
- None
### Notes
- None
