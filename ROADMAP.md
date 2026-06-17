# Burden of Survival -- Development Roadmap

> **Philosophy:** Build systems individually. Integrate in sequence. Ship the smallest complete thing first. Every phase produces something playable before the next begins.

---

## Release Targets Overview

| Release | Name | Target | Description |
|---------|------|--------|-------------|
| .5 | The Property | Month 8-10 | Real property, basic zombies, core survival loop |
| 1.0 | Rung 1 Early Access | Month 36-48 | Full hometown solo experience |
| 2.0 | The County | TBD | Co-op, expanded map, community formation |
| 3.0 | The State | TBD | Multiplayer, factions, geographic discovery |
| 4.0 | The Nation | TBD | MMO scale, civilizational endgame |
| 5.0 | The World | TBD | Global simulation, true win condition |

---

## PHASE 0: Foundation
**Duration:** Months 1-2  
**Goal:** Engine configured, tools installed, first real geography in engine

### Tasks
- [ ] UE5 installation and project configuration
- [ ] GitHub repository setup with Git LFS for binary assets
- [ ] Cesium for Unreal plugin installation and configuration
- [ ] OpenStreetMap data pipeline research and first test
- [ ] Display Ward/Cabot, Arkansas terrain in UE5 using Cesium
- [ ] Basic character controller (movement, camera, first/third person toggle)
- [ ] Basic project folder structure established
- [ ] UE5 learning: World Partition, Large World Coordinates, basic Blueprints

### Milestone
**Walk around a rough version of the Ward/Cabot area in UE5.**  
Terrain present. Character moves. Nothing else required. This proves the geographic premise works.

### Success Criteria
- Real GPS coordinates map to correct terrain in engine
- Character can walk, run, crouch without fighting the engine
- Frame rate acceptable at ground level

---

## PHASE 1: Release .5 -- "The Property"
**Duration:** Months 3-10  
**Goal:** Playable prototype on real property with functional zombie simulation

### What This Release Contains
- Shane's actual property in Ward/Cabot, AR (1.5 acres, real dimensions)
- The house -- procedurally generated from OSM footprint or hand-built
- 10-20 zombies on and around the property
- Day/night cycle (real sunrise/sunset times for the location)
- Basic interaction system (pick up, examine objects)
- Zero HUD -- committed from day one
- Basic character voice (10-15 lines communicating state)
- Basic survival loop -- character can die, session resets
- Basic audio -- footsteps, ambient environment, zombie audio

### What This Release Does NOT Contain
- Pre-outbreak window
- Psychological weight system (stubbed only)
- Notebook (stubbed -- can open, can't write yet)
- Full acoustic herd system (basic detection only)
- NPC companions
- Full fatigue/soreness system (basic energy only)
- Multiple locations
- Story or progression

### System Build Order for Phase 1

**Weeks 1-4: The Property**
- [ ] OSM building footprint data for the specific property
- [ ] Rough house geometry generated or hand-built
- [ ] Property boundaries and terrain accurate to real dimensions
- [ ] Basic interior -- navigable rooms, doors that open

**Weeks 5-8: The Zombies**
- [ ] Basic zombie AI state machine: Idle / Alerted / Chasing
- [ ] Basic sight detection (cone, distance-based)
- [ ] Basic sound detection (radius-based, placeholder for full acoustic system)
- [ ] Zombie movement and navigation on the property
- [ ] Basic zombie attack -- character can be downed

**Weeks 9-12: The Day**
- [ ] Day/night cycle tied to real sunrise/sunset for Ward, AR
- [ ] Basic dynamic lighting (sun position, shadows)
- [ ] Basic weather placeholder (clear/overcast toggle)
- [ ] Time of day affects zombie behavior (slightly more active at dusk)

**Weeks 13-16: The Feel**
- [ ] Zero HUD confirmed -- all meters removed
- [ ] Basic character voice lines (tired, hungry, scared, hurt)
- [ ] Basic interaction system (approach, prompt, pick up)
- [ ] Basic inventory (items carried, simple list)
- [ ] Basic survival needs (hunger/thirst timers that produce voice feedback)
- [ ] Basic audio pass (footsteps on different surfaces, ambient, zombie sounds)

**Weeks 17-20: Polish and Testing**
- [ ] Performance optimization for the property scale
- [ ] Bug fixing
- [ ] Playtesting with people who don't know what the game is
- [ ] Document what works and what doesn't
- [ ] Adjust based on feedback

### Milestone
**Show someone who doesn't know what the game is, hand them a controller, and watch them figure it out without being told anything.**  
If they understand how to read their character's state without UI, the design is working.

### Success Criteria
- Player can survive for 10+ minutes without being told how
- Character voice lines communicate state clearly enough to play without HUD
- Zombies behave in ways that feel logical and readable
- The property feels like A real place, not a game level
- Frame rate stable

---

## PHASE 2: Core Physical Systems
**Duration:** Months 10-18  
**Goal:** The physical simulation working at the depth the design requires

### Systems to Build

**Physical Fatigue System**
- [ ] Acute fatigue (stamina within a session)
- [ ] Accumulated fatigue (soreness that carries between sessions)
- [ ] Recovery modeling (sleep quality, nutrition, rest)
- [ ] Injury system (twisted ankle, cuts, infection progression)
- [ ] Adrenaline state (triggers, effects, crash, debt)
- [ ] Willpower resource (expressed through animation and voice, not UI)
- [ ] The couch mechanic (character seeks rest when depleted)
- [ ] Background/training modifier (military, laborer, sedentary profiles)

**Survival Needs (Full)**
- [ ] Hunger with nutritional modeling (calories, protein, variety)
- [ ] Thirst (water quality matters -- clean vs. contaminated)
- [ ] Temperature system (clothing, shelter, weather interaction)
- [ ] Sleep system (quality, location safety, recovery rate)
- [ ] Medical needs (illness, infection, chronic conditions)

**Physical Inventory**
- [ ] Real-time bag interaction animation
- [ ] Item weight affecting movement
- [ ] Access time based on item position in pack
- [ ] Clothing system (layers, warmth, protection, encumbrance)

### Milestone
**Surviving for an in-game week on the property should feel like work.**  
The player should be managing their character's physical state as a primary challenge, not just avoiding zombies.

---

## PHASE 3: The Acoustic Zombie Simulation
**Duration:** Months 12-24 (overlaps Phase 2)  
**Goal:** Zombie behavior driven entirely by acoustic simulation

### Systems to Build

**MetaSounds Acoustic Framework**
- [ ] Sound event system (every action produces a sound with radius and frequency)
- [ ] Sound propagation through walls and distance (attenuation modeling)
- [ ] Material-based sound modification (grass vs. concrete vs. wood)
- [ ] Weather effects on sound propagation (rain masking, wind distortion)

**Zombie Acoustic AI**
- [ ] Individual zombie hearing radius and sensitivity
- [ ] Zombie attention state triggered by sound events
- [ ] Alerted zombie producing its own sound (groaning)
- [ ] Sound cascade: alerted zombie draws nearby zombies
- [ ] Herd formation through cascade reaching critical mass
- [ ] Herd self-sustaining: collective noise of herd becomes permanent stimulus
- [ ] Migration behavior: herd moves toward stimulus, continues until blocked

**Zombie State Machine (Full)**
- [ ] Idle (wandering, low-frequency wheeze)
- [ ] Curious (heard something, investigating)
- [ ] Alerted (confirmed stimulus, aggressive hiss)
- [ ] Chasing (active pursuit)
- [ ] Herd member (part of migrating group, different behavior)
- [ ] Blocked (obstacle encountered, spreads along obstacle)

**Environmental Interaction**
- [ ] Zombies interact with doors (pressure, eventually breach)
- [ ] Zombies navigate around obstacles realistically
- [ ] Zombies drawn to light sources at night
- [ ] Weather effects on zombie behavior (cold slows, heat doesn't)

### Milestone
**A player who makes noise in one part of the map should be able to watch a herd form and migrate organically without any scripted triggers.**

---

## PHASE 4: The Diegetic Experience
**Duration:** Months 18-30  
**Goal:** Full no-HUD diegetic design working -- player reads all game state through character

### Systems to Build

**Internal Voice System**
- [ ] Voice line database organized by trigger category
- [ ] Psychological state modifier affecting delivery
- [ ] Physical state modifier affecting delivery
- [ ] Context system (what voice lines fire when)
- [ ] Internal vs. external voice audio treatment
- [ ] "I don't want to forget this" notebook prompt system
- [ ] Voice lines for every survival state combination

**Fight / Flight / Freeze System**
- [ ] Threat detection triggering freeze response
- [ ] Freeze duration based on character background and prior exposure
- [ ] Flight response breaking freeze (poorly directed, adrenaline-driven)
- [ ] Fight response threshold (blocked flight, protecting someone, prior training)
- [ ] Post-adrenaline crash system
- [ ] Habituation over time (shorter freeze, more directed flight)
- [ ] Human violence triggering same system (not just zombies)

**Psychological Weight System**
- [ ] Event tracking (what happened, when, who was involved)
- [ ] Weight accumulation by event category
- [ ] Deterioration expression (animation changes, voice changes, behavior changes)
- [ ] Recovery pathways (social connection, rest, small victories, beauty)
- [ ] Dissociation state (lights on, nobody home)
- [ ] Resilience building over time with adequate support

**The Notebook**
- [ ] Physical notebook object (found, not given)
- [ ] Writing animation (takes real time)
- [ ] Text input system
- [ ] Notebook damage system (water, fire)
- [ ] Kill counter (each entry is a person)
- [ ] People you've known list
- [ ] Map annotation functionality
- [ ] Notebook persistence through death (world contains it)

### Milestone
**Play for one hour with eyes closed during UI moments. If the character's voice communicates everything needed to survive, the system works.**

---

## PHASE 5: The Geographic Pipeline
**Duration:** Months 24-36  
**Goal:** Any location on Earth selectable and playable

### Systems to Build

**Location Selection**
- [ ] Map interface for pin drop
- [ ] City/address search
- [ ] Name entry screen (diegetic -- intake form)
- [ ] Location data caching system

**OSM Data Pipeline**
- [ ] OSM API integration
- [ ] Building footprint extraction and classification
- [ ] Road network extraction
- [ ] Land use data (residential, commercial, industrial, parks, water)
- [ ] Point of interest extraction (hospitals, schools, gas stations)

**Procedural Building Generation (PCG)**
- [ ] Residential building generator (single family, multi-family, apartment)
- [ ] Commercial building generator (store, office, restaurant)
- [ ] Industrial building generator
- [ ] Interior generation from footprint (navigable, survivable)
- [ ] Building state system (intact, damaged, burned, collapsed)

**Population Data Integration**
- [ ] Census API or dataset integration
- [ ] Zombie count calculation from real population
- [ ] Population density driving zombie distribution
- [ ] Zombie density variation (dense urban vs. sparse rural)

**World State System**
- [ ] Persistent world changes (cleared buildings stay cleared)
- [ ] Resource depletion tracking
- [ ] Environmental degradation over time

### Milestone
**Select St. Louis, Missouri. Walk through a recognizable version of downtown St. Louis with correct zombie density for a city of 2.8 million.**

---

## PHASE 6: The Pre-Outbreak Window
**Duration:** Months 30-42  
**Goal:** The full emotional arc from calm through chaos to planning

### Systems to Build

**Daily Life Simulation**
- [ ] Character background generation (profession + hobby + social position)
- [ ] Daily routine system (time slots, obligations, locations)
- [ ] Time compression for mundane periods
- [ ] Real-time moments for significant decisions
- [ ] Obligation consequence system (miss work = lose pay, relationship damage)

**Discovered Identity System**
- [ ] Personal item generation based on background
- [ ] Character name from player input, discovered on ID
- [ ] Memory fragment system (internal voice triggered by environment)
- [ ] NPC who knows you encounter

**Family and Social Dynamics**
- [ ] Family composition generation (spectrum from nuclear to recluse)
- [ ] Pre-outbreak relationship quality
- [ ] Family response to outbreak information (believing, skeptical, denial)
- [ ] Relationship consequence system

**News and Information Escalation**
- [ ] Information landscape simulation (Day 0 through window close)
- [ ] Platform-appropriate information (radio, TV, phone)
- [ ] Information reliability variation (some true, some false, some exaggerated)
- [ ] Geographic information gradient (urban knows sooner)

**The First Encounter Scenarios**
- [ ] Dawn of the Dead scenario (immediate urban)
- [ ] #Alive scenario (contained building)
- [ ] Highway gridlock scenario
- [ ] Workplace lockdown scenario
- [ ] Domestic routine interrupted scenario
- [ ] Rural delayed scenario

**Organic Outbreak Spread**
- [ ] Seed event placement (based on population density and transit)
- [ ] Spread simulation through geographic logic
- [ ] Neighborhood-level timing variation

### Milestone
**A player who picks their actual hometown and experiences the pre-outbreak window should feel the specific emotional weight of watching their real neighborhood change.**

---

## PHASE 7: NPC and Social Systems
**Duration:** Months 36-48  
**Goal:** NPCs that behave like people, not game characters

### Systems to Build

**NPC Generation**
- [ ] Profession + Hobby background system
- [ ] Social position generation (family, recluse, spectrum)
- [ ] Pre-existing reputation system
- [ ] Psychological state generation and tracking
- [ ] Cultural background (urban/rural, economic class)

**Trust System**
- [ ] Trust accumulation through consistent behavior
- [ ] Trust destruction through betrayal
- [ ] Reputation propagation through information network
- [ ] Pre-outbreak reputation carrying forward

**NPC Behavior**
- [ ] Stress response profiles (externalizer, internalizer, rationalizer, etc.)
- [ ] Voluntary departure system
- [ ] Non-zombie death system (illness, injury, accident)
- [ ] Bystander effect modeling (85% non-intervention)
- [ ] Shared inaction social dynamics
- [ ] The Trojan Horse scenario (false victim)

**Community Dynamics**
- [ ] Group formation and role assignment
- [ ] Leadership credibility accumulation and decay
- [ ] Faction formation within groups
- [ ] Cultural bias probability system
- [ ] Information network (survivor grapevine)
- [ ] Parallel information networks (community-specific)

**The Bite Scenario**
- [ ] Virus progression timeline (extremity vs. core)
- [ ] NPC concealment behavior
- [ ] Amputation option and consequence
- [ ] Psychological aftermath for group

### Milestone
**An NPC who was accepted into the group based on a sympathetic story is later revealed -- through a chance encounter with another group -- to have been ejected from their last group for specific reasons. The player runs back. What they find is determined by the simulation.**

---

## PHASE 8: Rung 1 Integration and Polish
**Duration:** Months 44-56  
**Goal:** All systems working together, polished to Early Access quality

### Tasks
- [ ] All systems integration testing
- [ ] Performance profiling and optimization
- [ ] Full audio design pass (all voice lines recorded, acoustic system tuned)
- [ ] Full animation pass (fatigue expression, fight/flight/freeze, skill progression)
- [ ] Pass the Torch system implementation
- [ ] Steam page, description, and screenshots
- [ ] Wishlist campaign (target: 6 months pre-launch)
- [ ] Community building (Discord, dev logs, design posts)
- [ ] Press and content creator outreach
- [ ] Pricing strategy
- [ ] Early Access launch

---

## Parallel Track: Content Production (Ongoing)

The following content can be developed alongside any phase using AI collaboration:

- [ ] Internal voice line database (thousands of contextual lines)
- [ ] NPC dialogue system and line database
- [ ] Lore documents (world history, outbreak origin, community histories)
- [ ] Design philosophy posts for community building
- [ ] Steam page copy and marketing materials
- [ ] Technical specification documents for each system
- [ ] Collaborator recruitment materials

---

## Resource Requirements by Phase

| Phase | Can Solo | Strongly Needs Collaborator |
|-------|----------|-----------------------------|
| 0 | Yes | No |
| 1 | Yes | No |
| 2 | Mostly | Audio designer for voice system |
| 3 | Mostly | Audio engineer for MetaSounds |
| 4 | Challenging | Voice actor/director for internal voice |
| 5 | No | Technical artist for OSM/PCG pipeline |
| 6 | Mostly | No |
| 7 | No | AI/systems programmer |
| 8 | No | Full small team |

---

## Timeline Summary

| Phase | Duration | Cumulative | Target Date |
|-------|----------|------------|-------------|
| 0: Foundation | 2 months | 2 months | Month 2 |
| 1: Release .5 | 8 months | 10 months | Month 10 |
| 2: Physical Systems | 8 months | 18 months | Month 18 |
| 3: Acoustic Simulation | 12 months | 24 months | Month 24 |
| 4: Diegetic Experience | 12 months | 30 months | Month 30 |
| 5: Geographic Pipeline | 12 months | 36 months | Month 36 |
| 6: Pre-Outbreak Window | 12 months | 42 months | Month 42 |
| 7: NPC and Social | 12 months | 48 months | Month 48 |
| 8: Integration and Polish | 8 months | 56 months | Month 56 |

**Realistic Release 1.0 Early Access: Month 48-56 from serious development start**  
**With strong collaborators: Month 36-44**  
**With AI collaboration for non-engine tasks: Compress by 6-12 months**

---

## The North Star

Every decision, every feature addition, every timeline tradeoff gets checked against one question:

**Does this produce the weight of being human?**

If yes, build it.  
If not, cut it.

---

*Last updated: Initial document*  
*Next review: After Phase 0 milestone achieved*
