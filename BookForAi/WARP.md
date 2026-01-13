# WARP.md

This file provides guidance to WARP (warp.dev) when working with code in this repository.

## Overview

This repository implements a small RPG-style game using a layered architecture:

- **Backend:** Python + Flask REST API exposing `/api/...` endpoints.
- **Domain logic:** Pure Python domain model (entities, rules, battle engine, repositories as interfaces).
- **Application layer:** Use-case services orchestrating domain rules and repositories.
- **Infrastructure:** MySQL-backed and config/in-memory repositories; DB connection helpers.
- **Frontend:** Vue 3 + Vite SPA in `interfaces/client` consuming the `/api` endpoints.
- **SQL:** Database schema and seed data under `sql/`.

The top-level `README.md` (Chinese) describes this as a six-layer structure: `domain`, `application`, `interfaces`, `infrastructure`, `configs`, and `tests`.

## Common commands

### Backend (Python / Flask)

Run these from the repo root unless noted otherwise.

- **Install backend dependencies**
  - `pip install -r requirements.txt`

- **Run the Flask API server** (serves JSON under `/api/...`)
  - Recommended (module form):
    - `python -m interfaces.web_api.app`
  - Alternative script form:
    - `python interfaces/web_api/app.py`

The main entrypoint is `interfaces/web_api/app.py`, which creates the Flask app and registers blueprints from `interfaces/routes`.

### Frontend (Vue 3 + Vite)

From `interfaces/client`:

- **Install frontend dependencies**
  - `cd interfaces/client`
  - `npm install`

- **Run dev server** (Vite, defaults to `http://localhost:5173`)
  - `npm run dev`

- **Build production bundle**
  - `npm run build`

- **Preview built bundle**
  - `npm run preview`

The frontend talks to the backend via Axios with `baseURL: '/api'` and `withCredentials: true` (see `interfaces/client/src/services/http.js`).

### Database setup (MySQL)

MySQL is required for persistent data; connection parameters (host, user, password, database) are defined in `infrastructure/db/connection.py` and must match your local setup.

Schema and seed scripts live under `sql/`:

- `001_create_database.sql`, `002_create_tables.sql`, `003_init_data.sql`, ... up to later feature tables.
- `sql/README.md` describes usage; in summary:
  - **Windows:** run the provided batch script (e.g. `run_all.bat`) from the `sql` directory and enter your MySQL root password when prompted.
  - **Linux/macOS:** pipe the numbered SQL files into `mysql` as described in `sql/README.md`.

### Tests

Tests and simulations are in `tests/`.

- **Run the "ancient battlefield" test suite with pytest**
  - `python -m pytest tests/test_battlefield.py -v`

- **Run the same suite directly as a script** (no pytest required)
  - `python tests/test_battlefield.py`

- **Run a single pytest test function** (requires `pytest` to be installed)
  - Example for the 31-player tournament case:
  - `python -m pytest tests/test_battlefield.py::test_tournament_31_players -vv`

- **Manual/demo battle script**
  - `python tests/test.py`

There is no dedicated lint/type-check command configured in this repo for either Python or the Vue client; if you add such tooling, also add the corresponding commands here.

## Backend architecture

### Domain layer (`domain/`)

The domain layer models the core game world and rules without any framework or I/O details.

- **Entities (`domain/entities/`)**
  - Core game concepts: users/players, monsters, maps, items, beasts, towers, battle records, etc.
  - Example: `domain/entities/user.py`, `domain/entities/monster.py`, `domain/entities/beast.py`, `domain/entities/tower.py`.

- **Rules (`domain/rules/`)**
  - Stateless business rules such as battle resolution, cultivation, sign-in, and battle power.
  - Example: `domain/rules/battle_rules.py` defines `calc_battle(user, monster)` returning a `BattleResult` describing win/lose, exp, gold, and energy cost.

- **Repository interfaces (`domain/repositories/`)**
  - Abstract interfaces like `IUserRepo`, `IMonsterRepo`, `IInventoryRepo`, etc., describing how the application layer can load and persist domain entities.
  - These are pure abstractions; concrete implementations live in `infrastructure/`.

- **Battle engine (`domain/services/battle_engine.py`)**
  - A richer combat engine built on top of beast stats (`BeastStats`) and a `BattlePowerCalculator`.
  - Used heavily by `tests/test_battlefield.py` to simulate multi-round tournaments.

Domain code must never import Flask, SQL, or other infrastructure details; it is designed to be testable in isolation.

### Application layer (`application/services/`)

The application layer orchestrates domain rules and repositories into concrete use cases. Each service typically corresponds to a gameplay feature.

Examples:

- `BattleService` combines `IUserRepo`, `IMonsterRepo`, and `calc_battle` to:
  - Load user/monster
  - Compute battle outcome
  - Update user exp/gold/energy
  - Optionally compute and apply drops via `DropService`
  - Return a `BattleOutcome` dataclass that bundles the domain `BattleRecord`, updated `User`, drops, and map id.

- Other services include:
  - `SigninService` (daily sign-in),
  - `MapService` (available maps and monsters per player),
  - `InventoryService` (bag contents, capacity, adding items),
  - `BeastService` (managing owned beasts and their templates),
  - `CaptureService` (capture attempts on maps),
  - `TowerBattleService` (tower challenges),
  - `ZhenyaoService` (镇妖玩法),
  - `AuthService` (login/registration based on players in the DB).

Application services depend only on domain abstractions and repository interfaces, not on Flask or specific DB drivers. They are where multi-step business flows live.

### Infrastructure layer (`infrastructure/`)

The infrastructure layer provides concrete implementations for the domain repositories and other technical concerns.

- **Config-backed repositories (`infrastructure/config/`)**
  - Map JSON configuration files under `configs/` into domain-facing repositories.
  - Examples:
    - `ConfigMapRepo` reads from `configs/maps.json` / `map_regions.json`.
    - `ConfigMonsterRepo` reads from `configs/monsters.json` / `map_beasts.json`.
    - `ConfigItemRepo` reads from `configs/items.json` and related drop/bag/shop configs.
    - `ConfigBeastTemplateRepo` reads from `configs/beast_templates.json`.
    - `ConfigTowerRepo` reads tower configs from `configs/tower_config.json`, `tower_guardians.json`, and `tower_rewards.json`.

- **MySQL-backed repositories (`infrastructure/db/`)**
  - Use `infrastructure/db/connection.py` for DB access (via `pymysql`).
  - Implement persistence for inventories, players, beasts on players, tower state, Zhenyao battles, etc.
  - Typical pattern: small classes like `MySQLInventoryRepo`, `MySQLPlayerBeastRepo`, `MySQLTowerStateRepo` that implement the corresponding domain interfaces using SQL from the `sql/` schema.

- **In-memory repositories (`infrastructure/memory/`)**
  - Simple in-memory implementations used for quick prototyping or for data that does not yet need persistence.
  - Example: `InMemoryUserRepo` seeds a default `User` (id=1, username "hero") for testing, while beasts can be held in `InMemoryBeastRepo`.

Infrastructure code is wired into the application layer via the service container in `interfaces/web_api/bootstrap.py`.

## Interface layer and service wiring

### Service container (`interfaces/web_api/bootstrap.py`)

`ServiceContainer` is a manual dependency injection container that wires domain repositories and application services together:

- Instantiates repositories from `infrastructure.config`, `infrastructure.db`, and `infrastructure.memory`.
- Creates service instances from `application.services.*` with the appropriate repositories injected.
- Exposes them as attributes on a global `services` object used by the Flask routes.

Any new application service or repository should be registered here so it is available to HTTP routes.

### Flask app and routes (`interfaces/web_api/` and `interfaces/routes/`)

- **`interfaces/web_api/app.py`**
  - Creates the `Flask` app, sets `secret_key` (for session-based auth), and registers blueprints:
    - `auth_bp`, `player_bp`, `tower_bp`, `arena_bp`, `king_bp`, `ranking_bp`, `map_bp`, `shop_bp`, `inventory_bp` from `interfaces/routes/*`.
  - Also keeps some legacy `/api/...` endpoints directly in this file for backwards compatibility (battle, sign-in, maps, inventory, beasts, capture, teleport count, etc.).

- **Blueprints in `interfaces/routes/`**
  - Each file groups HTTP endpoints for a specific feature and uses `services` from `bootstrap.py`.
  - Example: `auth_routes.py` defines `/api/auth/login`, `/api/auth/register`, `/api/auth/logout`, and `/api/auth/status` using `AuthService`, `PlayerRepo`, and `PlayerBeastRepo`.
  - Similar patterns apply for routes handling towers, arena, king challenge, rankings, map/teleport, shop, inventory, and player-facing endpoints.

Routes are thin adapters: they parse `request`, delegate to an application service, and convert results to JSON.

## Frontend architecture (`interfaces/client`)

The Vue 3 SPA mirrors backend features and talks to Flask over `/api`.

- **Routing (`src/router/index.js`)**
  - Defines the client-side route tree with `vue-router`, mapping URLs like `/tower`, `/beast`, `/arena`, `/battlefield`, `/pvp`, `/shop`, `/map`, `/player/...` to corresponding pages under `src/features/*`.
  - The default route `/` renders the main lobby page.

- **HTTP service (`src/services/http.js`)**
  - Configures a shared Axios instance:
    - `baseURL: '/api'` so paths like `/user/me` hit the Flask API.
    - `withCredentials: true` to send/receive session cookies.

- **Domain-specific services (`src/services/*.js`)**
  - Example: `userService.js` wraps `/api/user/me` as `fetchUser()`; additional services can be added here to encapsulate backend calls.

- **Feature organization (`src/features/*`)**
  - Pages and components are grouped by gameplay feature: `arena`, `battlefield`, `beast`, `inventory`, `king`, `lobby`, `main`, `map`, `player`, `pvp`, `ranking`, `shop`, `tower`, etc.
  - This roughly mirrors the backend route grouping and application services, making it straightforward to locate the frontend counterpart of a backend feature.

## Configs and data (`configs/` and `sql/`)

- **`configs/`**
  - JSON files describing game content and parameters:
    - Maps, regions, and monsters per map.
    - Items, drop tables, shop inventory.
    - Beast templates.
    - Tower floors, guardians, and rewards.
    - Bag/ inventory upgrade thresholds.
  - These are treated as data, not code; they are read by `infrastructure/config` repositories. Adjusting balance or adding content usually starts here.

- **`sql/`**
  - Ordered SQL migration/initialization scripts (`001_...`, `002_...`, etc.) and a helper to run them all.
  - Table designs cover tower state, player beasts, arena/king challenges, various counters, and supporting data referenced by the MySQL repositories.

## Tests and simulations (`tests/`)

- **`tests/test_battlefield.py`**
  - High-level simulation of the "ancient battlefield" tournament:
    - Generates test players with beasts derived from a target battle power.
    - Uses `BattlefieldSystem` and `BattleEngine` to run single-elimination tournaments with possible byes.
    - Validates reward tiers based on player counts, number of rounds, champion selection, and temporary champion titles with expiration.
  - Designed to be both readable output (prints to stdout) and executable as either a pytest suite or a standalone script.

- **`tests/test.py` and `tests/manual_battle_demo.py`**
  - Smaller demos of core battle mechanics used for quick experimentation.

When modifying battle formulas or tournament logic, update the corresponding domain code (`domain/rules/battle_rules.py`, `domain/services/battle_engine.py`) and adjust these tests to keep simulations consistent with the intended design.
