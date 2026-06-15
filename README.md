# Burden of Survival

**A hyper-realistic open-world zombie survival simulation built in Unreal Engine 5.**

> *"Survive in YOUR city. Your street. Your home."*

---

## What This Game Is

Burden of Survival is not another zombie game. It is a simulation of what surviving an outbreak would actually feel like -- physically, psychologically, and socially -- set in the real world using real geography.

You do not select a fictional map. You drop a pin. You survive where you live, where you grew up, or where you've always wanted to go. The streets are real. The population density is real. The zombie count is derived from the actual pre-outbreak population of the area you chose.

There are no health bars. No stamina meters. No XP counters. Your character tells you how they feel. You listen. You survive.

---

## Core Design Philosophy

**Diegetic Everything.** Every piece of information about your character's physical and psychological state is communicated through the character -- voice, animation, behavior. The screen is clean. The world communicates.

**The Body Keeps Score.** Physical fatigue accumulates realistically. You cannot chop wood all day and wake up fine. Muscle soreness is modeled. Sleep quality matters. Adrenaline carries a debt. Military training raises the ceiling. The ceiling still exists.

**Psychological Weight is Real.** The cost of hard decisions does not reset. Killing someone -- even when necessary -- leaves a mark. Losing a companion leaves a mark. Witnessing something terrible and not acting leaves a mark. These accumulate and express through behavior, voice, and what the character can and cannot do.

**The World Before Mattered.** Your character had a life. A profession. A family or not. A reputation. A Tuesday morning routine. The game begins in that Tuesday morning and the loss of it is real because the game let you inhabit it first.

**Humans Are More Dangerous Than Zombies -- But Zombies Are The Game.** The social simulation is deep and honest. Pre-existing biases, community dynamics, reputation, information as a weapon -- all of it is modeled. But the zombie survival experience is the foundation. Everything else is built on top of it.

**The World Is Finite.** The zombie population is derived from the real population of the selected area. Every zombie killed is permanently gone. The world can actually be won -- slowly, collectively, over time.

---

## The Scale System

The game scales in five rungs, each a complete experience that builds into the next:

| Rung | Scope | Players | Zombie Count |
|------|-------|---------|--------------|
| 1 | Hometown | Solo | Real local population |
| 2 | County | Co-op 2-4 | Real county population |
| 3 | State | Multiplayer | Real state population |
| 4 | United States | MMO Scale | ~335 million |
| 5 | World | Global | ~8 billion |

---

## Current Development Status

**Phase:** Pre-production / Foundation  
**Engine:** Unreal Engine 5  
**Developer:** TheRealApollyon  
**Target for Release .5:** Playable prototype on real property with zombie simulation  
**Target for Release 1.0:** Full Rung 1 Early Access

See [ROADMAP.md](ROADMAP.md) for detailed development timeline.  
See [Docs/GDD/](Docs/GDD/) for full design documentation.

---

## Key Systems

- **Real-World Geography Pipeline** -- OpenStreetMap + Cesium for Unreal generates any location on Earth
- **Acoustic Herd Simulation** -- Zombie hordes form organically through sound propagation, not scripted triggers
- **Physical Simulation** -- Fatigue, soreness, injury, adrenaline, and recovery modeled honestly
- **Psychological Weight System** -- Trauma, grief, and resilience tracked and expressed diegetically
- **Fight/Flight/Freeze Response** -- First encounters produce realistic neurological responses, not instant action
- **Social Simulation** -- NPC trust, reputation, cultural background, and pre-existing relationships all modeled
- **The Notebook** -- Player-driven memory system replacing all traditional quest/log UI
- **Pass the Torch** -- Persistent world timeline continues after death; find your previous character's base

---

## Design Documents

| Document | Description |
|----------|-------------|
| [Core Philosophy](Docs/GDD/00_Core_Philosophy.md) | Design principles and emotional targets |
| [World and Setting](Docs/GDD/01_World_Setting.md) | Geography, scale, lore |
| [Player Character](Docs/GDD/02_Player_Character.md) | Identity discovery, backgrounds, daily life simulation |
| [Survival Systems](Docs/GDD/03_Survival_Systems.md) | Physical simulation, fatigue, medical, needs |
| [Zombie Systems](Docs/GDD/04_Zombie_Systems.md) | AI, acoustic behavior, finite population |
| [NPC and Social Systems](Docs/GDD/05_NPC_Social_Systems.md) | Trust, reputation, community dynamics, bias |
| [Psychological Systems](Docs/GDD/06_Psychological_Systems.md) | Weight, trauma, the notebook, internal voice |
| [Geographic Pipeline](Docs/GDD/07_Geographic_Pipeline.md) | OSM, Cesium, procedural generation |
| [Progression and Scale](Docs/GDD/08_Progression_Scale.md) | The five rungs, endgame, Pass the Torch |

---

## Development Philosophy

This game is being built system by system, with each system tested and stable before integration. The first playable milestone is a single property in Ward/Cabot, Arkansas -- real geography, real scale, a handful of zombies, and the core survival loop. Everything else is built on that foundation.

Scope is the enemy. Depth is the goal.

---

## Contact

GitHub: [@TheRealApollyon](https://github.com/TheRealApollyon)

---

*Built in Unreal Engine 5. Real world. Real weight.*
