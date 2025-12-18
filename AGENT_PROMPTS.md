# Prompts para Agentes de Desarrollo - PathWars: The Interpolation Battles

Este documento contiene prompts detallados para múltiples agentes de desarrollo que pueden trabajar en paralelo sin conflictos. Cada prompt está diseñado para ser autocontenido y seguir buenas prácticas de desarrollo.

---

## 📋 Resumen de Tareas Paralelas

Las siguientes tareas han sido analizadas para poder ejecutarse simultáneamente sin conflictos de merge:

| Rama | Tarea | Archivos Principales | Dependencias |
|------|-------|---------------------|--------------|
| `feature/strategy-pattern-interpolation` | Refactorizar interpolación a Strategy Pattern | `src/math_engine/` | Ninguna |
| `feature/game-phase-state-machine` | Implementar State Pattern para fases | `src/core/game_phases/` (nuevo) | Ninguna |
| `feature/lobby-configuration` | Sistema de Lobby con configuración | `src/ui/lobby.py` (nuevo) | Ninguna |
| `feature/mercenary-system` | Sistema de Mercenarios (Factory Pattern) | `src/entities/mercenaries/` (nuevo) | Ninguna |
| `feature/research-system` | Sistema de I+D | `src/core/research/` (nuevo) | Ninguna |
| `feature/gameserver-command-execution` | Implementar ejecución de comandos en GameServer | `src/network/server.py` | Ninguna |

---

## 🔵 AGENTE 1: Strategy Pattern para Interpolación

**Rama:** `feature/strategy-pattern-interpolation`

**Archivos a modificar/crear:**
- `src/math_engine/interpolation_strategy.py` (nuevo)
- `src/math_engine/strategies/` (nuevo directorio)
- `src/math_engine/interpolator.py` (refactorizar)
- `tests/test_interpolation_strategies.py` (nuevo)

### Prompt Detallado:

```
Eres un desarrollador Python experto. Tu tarea es refactorizar el sistema de interpolación del juego PathWars para seguir el Strategy Pattern según el GDD del proyecto.

## Contexto del Proyecto
PathWars es un juego Tower Defense PvP donde los jugadores usan funciones matemáticas (interpolación) para definir el camino de los enemigos. El sistema actual usa métodos estáticos en una clase Interpolator, pero necesitamos refactorizarlo para permitir:
1. Selección dinámica de métodos de interpolación
2. Bloqueo/desbloqueo de métodos según investigaciones (I+D)
3. Fácil extensión con nuevos métodos

## Arquitectura Actual (a refactorizar)
El archivo `src/math_engine/interpolator.py` tiene métodos estáticos:
- `linear_interpolate()`
- `lagrange_interpolate()`
- `cubic_spline_interpolate()`

## Tarea
1. Crear la interfaz/protocolo `InterpolationStrategy` en `src/math_engine/interpolation_strategy.py`:
   ```python
   from abc import ABC, abstractmethod
   from typing import List, Tuple, Protocol
   
   class InterpolationStrategy(Protocol):
       """Protocol for interpolation strategies following Strategy Pattern."""
       
       @property
       def name(self) -> str:
           """Human-readable name of the interpolation method."""
           ...
       
       @property
       def requires_research(self) -> bool:
           """Whether this method requires research to unlock."""
           ...
       
       def interpolate(
           self, 
           control_points: List[Tuple[float, float]], 
           resolution: int = 100
       ) -> List[Tuple[float, float]]:
           """
           Interpolate between control points.
           
           Args:
               control_points: List of (x, y) tuples defining control points.
               resolution: Number of points to generate in the path.
               
           Returns:
               List of (x, y) tuples representing the interpolated path.
           """
           ...
   ```

2. Crear el directorio `src/math_engine/strategies/` con implementaciones:
   - `__init__.py` (exports)
   - `linear_strategy.py` - LinearInterpolation (siempre disponible)
   - `lagrange_strategy.py` - LagrangeInterpolation (requiere I+D, cost: 500$)
   - `spline_strategy.py` - SplineInterpolation (requiere I+D, cost: 1000$)

3. Cada estrategia debe:
   - Implementar el protocolo InterpolationStrategy
   - Tener docstrings completos
   - Manejar edge cases (menos de 2 puntos, puntos duplicados)
   - Usar numpy/scipy según corresponda (ya están en requirements.txt)

4. Crear `src/math_engine/interpolation_registry.py`:
   - Singleton que registra todas las estrategias disponibles
   - Método `get_strategy(name: str) -> InterpolationStrategy`
   - Método `get_available_strategies() -> List[str]`
   - Método `is_unlocked(name: str, unlocked_methods: Set[str]) -> bool`

5. Actualizar `src/math_engine/interpolator.py`:
   - Mantener compatibilidad hacia atrás con los métodos estáticos existentes
   - Añadir métodos que usen las estrategias internamente
   - Marcar métodos estáticos como @deprecated (usando warnings)

6. Crear tests comprehensivos en `tests/test_interpolation_strategies.py`:
   - Test de cada estrategia individual
   - Test de registro de estrategias
   - Test de interpolación con diferentes números de puntos
   - Test de edge cases
   - Mínimo 15 tests

## Principios a Seguir
- **Single Responsibility**: Cada estrategia solo interpola
- **Open/Closed**: Fácil añadir nuevas estrategias sin modificar existentes
- **Liskov Substitution**: Todas las estrategias son intercambiables
- **Interface Segregation**: Interfaz mínima y clara
- **Dependency Inversion**: CurveState depende de abstracción, no de implementaciones

## Comandos para Verificar
```bash
cd /home/runner/work/PathWars-TheInterpolationBattles/PathWars-TheInterpolationBattles
python -m pytest tests/test_interpolation_strategies.py -v
python -m pytest tests/test_math_engine.py -v  # Verificar que tests existentes siguen pasando
```

## NO Modificar
- `src/core/curve_state.py` (otra tarea lo actualizará para usar las estrategias)
- Tests existentes en otros archivos
```

---

## 🟢 AGENTE 2: State Pattern para Fases de Juego

**Rama:** `feature/game-phase-state-machine`

**Archivos a crear:**
- `src/core/game_phases/` (nuevo directorio)
- `src/core/game_phases/__init__.py`
- `src/core/game_phases/base_phase.py`
- `src/core/game_phases/lobby_state.py`
- `src/core/game_phases/offense_planning_state.py`
- `src/core/game_phases/defense_planning_state.py`
- `src/core/game_phases/battle_state.py`
- `src/core/game_phases/game_over_state.py`
- `src/core/game_phases/phase_manager.py`
- `tests/test_game_phases.py`

### Prompt Detallado:

```
Eres un desarrollador Python experto. Tu tarea es implementar una máquina de estados robusta para el flujo de juego de PathWars usando el State Pattern.

## Contexto del Proyecto
PathWars tiene las siguientes fases de juego según el GDD:
1. **Lobby**: Configuración de partida antes de comenzar
2. **OffensePlanning**: El jugador edita el camino que seguirán sus enemigos en el mapa rival
3. **DefensePlanning**: El jugador coloca torres en su propio mapa
4. **Battle**: Ejecución de la oleada en tiempo real
5. **GameOver**: Fin de partida (victoria o derrota)

Actualmente existe un enum simple `GamePhase` en `src/core/game_state.py` que no implementa el patrón State completo.

## Tarea

1. Crear el directorio `src/core/game_phases/`

2. Crear `base_phase.py` con la clase abstracta:
   ```python
   from abc import ABC, abstractmethod
   from typing import Optional, TYPE_CHECKING
   import pygame
   
   if TYPE_CHECKING:
       from .phase_manager import PhaseManager
   
   class GamePhaseState(ABC):
       """Abstract base class for game phase states (State Pattern)."""
       
       def __init__(self, phase_manager: 'PhaseManager') -> None:
           self._phase_manager = phase_manager
           self._time_limit: Optional[float] = None  # None = sin límite
           self._elapsed_time: float = 0.0
       
       @property
       @abstractmethod
       def name(self) -> str:
           """Return the name of this phase."""
           ...
       
       @property
       def time_remaining(self) -> Optional[float]:
           """Return remaining time, or None if no limit."""
           if self._time_limit is None:
               return None
           return max(0.0, self._time_limit - self._elapsed_time)
       
       @abstractmethod
       def enter(self) -> None:
           """Called when entering this phase."""
           ...
       
       @abstractmethod
       def exit(self) -> None:
           """Called when exiting this phase."""
           ...
       
       @abstractmethod
       def update(self, dt: float) -> None:
           """Update the phase each frame."""
           ...
       
       @abstractmethod
       def handle_input(self, event: pygame.event.Event) -> bool:
           """
           Handle input event.
           Returns True if event was consumed.
           """
           ...
       
       @abstractmethod
       def can_transition_to(self, next_phase: str) -> bool:
           """Check if transition to the specified phase is valid."""
           ...
       
       def request_transition(self, next_phase: str) -> bool:
           """Request a phase transition through the manager."""
           return self._phase_manager.transition_to(next_phase)
   ```

3. Implementar cada estado concreto:

   **lobby_state.py**:
   - Permite configurar parámetros de partida
   - Valida que ambos jugadores estén conectados
   - Solo puede transicionar a OffensePlanning

   **offense_planning_state.py**:
   - Tiempo límite configurable (default: 60 segundos)
   - Permite editar puntos de control en el mapa rival
   - Al salir, bloquea los puntos de control actuales (locked_points)
   - Solo puede transicionar a DefensePlanning

   **defense_planning_state.py**:
   - Tiempo límite configurable (default: 45 segundos)
   - Permite colocar torres en el mapa propio
   - Solo puede transicionar a Battle

   **battle_state.py**:
   - Sin límite de tiempo (termina cuando los enemigos cruzan o mueren)
   - Input deshabilitado excepto pausa/cámara
   - Puede transicionar a OffensePlanning (siguiente oleada) o GameOver

   **game_over_state.py**:
   - Muestra resultados
   - Solo puede transicionar a Lobby

4. Crear `phase_manager.py`:
   ```python
   class PhaseManager:
       """Manages game phase transitions following State Pattern."""
       
       def __init__(self) -> None:
           self._current_state: Optional[GamePhaseState] = None
           self._states: Dict[str, GamePhaseState] = {}
           
       def register_state(self, name: str, state: GamePhaseState) -> None:
           """Register a state with the manager."""
           ...
       
       def transition_to(self, phase_name: str) -> bool:
           """
           Transition to a new phase.
           Validates transition and calls enter/exit hooks.
           Returns True if transition succeeded.
           """
           ...
       
       def update(self, dt: float) -> None:
           """Update current phase."""
           ...
       
       def handle_input(self, event: pygame.event.Event) -> bool:
           """Route input to current phase."""
           ...
       
       @property
       def current_phase_name(self) -> Optional[str]:
           """Get name of current phase."""
           ...
   ```

5. Crear tests en `tests/test_game_phases.py`:
   - Test de transiciones válidas
   - Test de transiciones inválidas (deben fallar)
   - Test de enter/exit hooks
   - Test de time limits
   - Test de handle_input en cada fase
   - Mínimo 20 tests

## Diagrama de Transiciones
```
Lobby → OffensePlanning → DefensePlanning → Battle
                ↑                              ↓
                └──────── (next wave) ─────────┘
                                               ↓
                                          GameOver → Lobby
```

## Principios a Seguir
- **Single Responsibility**: Cada estado maneja solo su lógica
- **Open/Closed**: Fácil añadir nuevas fases sin modificar PhaseManager
- **State Pattern**: Comportamiento diferente según el estado actual

## Comandos para Verificar
```bash
cd /home/runner/work/PathWars-TheInterpolationBattles/PathWars-TheInterpolationBattles
python -m pytest tests/test_game_phases.py -v
```

## NO Modificar
- `src/core/game_state.py` (mantener enum existente por compatibilidad)
- `src/multiplayer/duel_session.py`
- Archivos de UI existentes
```

---

## 🟡 AGENTE 3: Sistema de Lobby con Configuración

**Rama:** `feature/lobby-configuration`

**Archivos a crear:**
- `src/ui/lobby.py`
- `src/core/match_config.py`
- `tests/test_lobby.py`
- `tests/test_match_config.py`

### Prompt Detallado:

```
Eres un desarrollador Python experto. Tu tarea es implementar el sistema de Lobby con configuración de partida para PathWars.

## Contexto del Proyecto
Según el GDD, antes de iniciar una partida multijugador, los jugadores deben poder configurar:
- Número de Oleadas: 3, 5, 7 o 10
- Dificultad: Fácil, Normal, Difícil
- Velocidad de Juego: 1x, 1.5x, 2x
- Tamaño del Mapa: 15x15, 20x20, 25x25
- Dinero Inicial: Cantidad configurable

El MainMenu ya existe en `src/ui/main_menu.py` pero NO tiene lobby de configuración.

## Tarea

1. Crear `src/core/match_config.py`:
   ```python
   from dataclasses import dataclass, field
   from enum import Enum, auto
   from typing import Dict, Any
   
   class Difficulty(Enum):
       EASY = auto()
       NORMAL = auto()
       HARD = auto()
       
       def enemy_hp_multiplier(self) -> float:
           """Return HP multiplier for enemies based on difficulty."""
           return {self.EASY: 0.75, self.NORMAL: 1.0, self.HARD: 1.5}[self]
       
       def starting_money_bonus(self) -> int:
           """Return bonus starting money."""
           return {self.EASY: 200, self.NORMAL: 0, self.HARD: -100}[self]
   
   class GameSpeed(Enum):
       NORMAL = 1.0
       FAST = 1.5
       VERY_FAST = 2.0
   
   class MapSize(Enum):
       SMALL = (15, 15)
       MEDIUM = (20, 20)
       LARGE = (25, 25)
       
       @property
       def width(self) -> int:
           return self.value[0]
       
       @property
       def height(self) -> int:
           return self.value[1]
   
   @dataclass
   class MatchConfig:
       """Configuration for a match."""
       wave_count: int = 5
       difficulty: Difficulty = Difficulty.NORMAL
       game_speed: GameSpeed = GameSpeed.NORMAL
       map_size: MapSize = MapSize.MEDIUM
       starting_money: int = 500
       
       # Phase time limits
       offense_phase_time: float = 60.0  # seconds
       defense_phase_time: float = 45.0  # seconds
       
       def validate(self) -> bool:
           """Validate configuration values."""
           if self.wave_count not in (3, 5, 7, 10):
               return False
           if self.starting_money < 100 or self.starting_money > 5000:
               return False
           return True
       
       def to_dict(self) -> Dict[str, Any]:
           """Serialize to dictionary for network transmission."""
           ...
       
       @classmethod
       def from_dict(cls, data: Dict[str, Any]) -> 'MatchConfig':
           """Deserialize from dictionary."""
           ...
   ```

2. Crear `src/ui/lobby.py`:
   ```python
   class LobbyScreen:
       """
       Lobby screen for multiplayer match configuration.
       
       Shows configurable parameters and ready status for both players.
       Only the host can modify settings.
       """
       
       def __init__(self, screen_width: int, screen_height: int) -> None:
           ...
       
       def set_host_mode(self, is_host: bool) -> None:
           """Set whether local player is host (can edit settings)."""
           ...
       
       def set_config(self, config: MatchConfig) -> None:
           """Set the current match configuration."""
           ...
       
       def get_config(self) -> MatchConfig:
           """Get the current match configuration."""
           ...
       
       def set_local_ready(self, ready: bool) -> None:
           """Set local player ready status."""
           ...
       
       def set_remote_ready(self, ready: bool) -> None:
           """Set remote player ready status."""
           ...
       
       def handle_event(self, event: pygame.event.Event) -> Optional[str]:
           """
           Handle pygame events.
           Returns 'start' when both players ready and host clicks start.
           Returns 'back' when back button pressed.
           """
           ...
       
       def draw(self, surface: pygame.Surface) -> None:
           """Draw the lobby screen."""
           ...
   ```

3. UI del Lobby debe incluir:
   - Título "Match Configuration"
   - Dropdowns/selectores para cada parámetro (usando pygame.Rect y clicks)
   - Indicadores de "Ready" para cada jugador (checkmarks)
   - Botón "Ready" para el jugador local
   - Botón "Start Game" (solo visible para host, solo habilitado si ambos ready)
   - Botón "Back" para volver al menú principal
   - Status text mostrando "Waiting for opponent..." si no está conectado

4. Crear tests:
   - `tests/test_match_config.py`: Tests de serialización, validación, enums
   - `tests/test_lobby.py`: Tests de UI del lobby (usando pygame headless con fixtures existentes)

## Estilo Visual
El proyecto usa estilo "Academic Neon Cyberpunk". Mantener consistencia con MainMenu:
- Fondo oscuro semi-transparente (20, 20, 40)
- Botones con hover effects
- Colores: Azul (60, 60, 120), Verde para "Ready" (60, 120, 60)
- Fuentes: pygame.font.Font(None, 72/48/36/32)

## Principios
- Separation of Concerns: MatchConfig es solo datos, LobbyScreen solo UI
- Usar fixtures de conftest.py para tests de pygame

## Comandos para Verificar
```bash
cd /home/runner/work/PathWars-TheInterpolationBattles/PathWars-TheInterpolationBattles
python -m pytest tests/test_match_config.py tests/test_lobby.py -v
```

## NO Modificar
- `src/ui/main_menu.py`
- Otros archivos de UI
- `src/network/`
```

---

## 🟠 AGENTE 4: Sistema de Mercenarios (Factory Pattern)

**Rama:** `feature/mercenary-system`

**Archivos a crear:**
- `src/entities/mercenaries/` (nuevo directorio)
- `src/entities/mercenaries/__init__.py`
- `src/entities/mercenaries/base_mercenary.py`
- `src/entities/mercenaries/mercenary_factory.py`
- `src/entities/mercenaries/mercenary_types.py`
- `tests/test_mercenaries.py`

### Prompt Detallado:

```
Eres un desarrollador Python experto. Tu tarea es implementar el Sistema de Mercenarios usando el Factory Pattern para PathWars.

## Contexto del Proyecto
Según el GDD, durante la Fase Ofensiva los jugadores pueden invertir dinero para enviar enemigos extra al rival. Los mercenarios son:

| Tipo | Nombre | Costo | HP Modifier | Speed Modifier |
|------|--------|-------|-------------|----------------|
| REINFORCED_STUDENT | Estudiante Reforzado | 100$ | +50% HP | Normal |
| SPEEDY_VARIABLE_X | Variable X Veloz | 75$ | -30% HP | +100% velocidad |
| TANK_CONSTANT_PI | Constante Pi | 200$ | +200% HP | -50% velocidad |

## Tarea

1. Crear directorio `src/entities/mercenaries/`

2. Crear `base_mercenary.py`:
   ```python
   from abc import ABC, abstractmethod
   from dataclasses import dataclass
   from typing import Tuple
   
   @dataclass
   class MercenaryStats:
       """Stats for a mercenary unit."""
       base_hp: int
       base_speed: float
       cost: int
       display_name: str
       
       def get_modified_hp(self, hp_modifier: float = 1.0) -> int:
           """Calculate HP with modifier."""
           return int(self.base_hp * hp_modifier)
       
       def get_modified_speed(self, speed_modifier: float = 1.0) -> float:
           """Calculate speed with modifier."""
           return self.base_speed * speed_modifier
   
   class BaseMercenary(ABC):
       """Abstract base class for mercenary units."""
       
       def __init__(self, owner_player_id: str, target_player_id: str) -> None:
           self._owner_id = owner_player_id
           self._target_id = target_player_id
           self._position: Tuple[float, float] = (0.0, 0.0)
           self._hp: int = self.stats.get_modified_hp(self.hp_modifier)
           self._speed: float = self.stats.get_modified_speed(self.speed_modifier)
           self._is_alive: bool = True
       
       @property
       @abstractmethod
       def stats(self) -> MercenaryStats:
           """Return base stats for this mercenary type."""
           ...
       
       @property
       @abstractmethod
       def hp_modifier(self) -> float:
           """Return HP modifier for this mercenary type."""
           ...
       
       @property
       @abstractmethod
       def speed_modifier(self) -> float:
           """Return speed modifier for this mercenary type."""
           ...
       
       @property
       def owner_player_id(self) -> str:
           return self._owner_id
       
       @property
       def target_player_id(self) -> str:
           return self._target_id
       
       @property
       def hp(self) -> int:
           return self._hp
       
       @property
       def speed(self) -> float:
           return self._speed
       
       @property
       def is_alive(self) -> bool:
           return self._is_alive
       
       @property
       def position(self) -> Tuple[float, float]:
           return self._position
       
       def take_damage(self, amount: int) -> None:
           """Receive damage."""
           self._hp = max(0, self._hp - amount)
           if self._hp <= 0:
               self._is_alive = False
       
       def move(self, dx: float, dy: float) -> None:
           """Move by delta."""
           x, y = self._position
           self._position = (x + dx, y + dy)
       
       def set_position(self, x: float, y: float) -> None:
           """Set absolute position."""
           self._position = (x, y)
   ```

3. Crear `mercenary_types.py` con implementaciones concretas:
   ```python
   from enum import Enum, auto
   
   class MercenaryType(Enum):
       REINFORCED_STUDENT = auto()
       SPEEDY_VARIABLE_X = auto()
       TANK_CONSTANT_PI = auto()
   
   class ReinforcedStudent(BaseMercenary):
       """Reinforced Student: +50% HP, normal speed, cost 100$."""
       
       @property
       def stats(self) -> MercenaryStats:
           return MercenaryStats(
               base_hp=100,
               base_speed=1.0,
               cost=100,
               display_name="Reinforced Student"
           )
       
       @property
       def hp_modifier(self) -> float:
           return 1.5
       
       @property
       def speed_modifier(self) -> float:
           return 1.0
   
   # Implementar SpeedyVariableX y TankConstantPi de forma similar
   ```

4. Crear `mercenary_factory.py`:
   ```python
   class MercenaryFactory:
       """Factory for creating mercenary instances (Factory Pattern)."""
       
       @staticmethod
       def create_mercenary(
           mercenary_type: MercenaryType,
           owner_player_id: str,
           target_player_id: str
       ) -> BaseMercenary:
           """
           Create a mercenary of the specified type.
           
           Args:
               mercenary_type: Type of mercenary to create.
               owner_player_id: ID of player who owns/sent this mercenary.
               target_player_id: ID of player this mercenary attacks.
               
           Returns:
               New mercenary instance.
               
           Raises:
               ValueError: If mercenary type is unknown.
           """
           ...
       
       @staticmethod
       def get_cost(mercenary_type: MercenaryType) -> int:
           """Get the cost of a mercenary type."""
           ...
       
       @staticmethod
       def get_available_types() -> list[MercenaryType]:
           """Get list of all available mercenary types."""
           ...
       
       @staticmethod
       def validate_purchase(
           mercenary_type: MercenaryType,
           quantity: int,
           available_money: int
       ) -> bool:
           """Check if player can afford to purchase mercenaries."""
           ...
   ```

5. Crear tests en `tests/test_mercenaries.py`:
   - Tests de creación de cada tipo de mercenario
   - Tests de stats (HP, speed, cost)
   - Tests de factory
   - Tests de damage y death
   - Tests de movement
   - Tests de validación de compra
   - Mínimo 15 tests

## Principios
- **Factory Pattern**: Centralizar creación de mercenarios
- **Single Responsibility**: Cada clase tiene una responsabilidad
- **Open/Closed**: Fácil añadir nuevos tipos de mercenarios

## Comandos para Verificar
```bash
cd /home/runner/work/PathWars-TheInterpolationBattles/PathWars-TheInterpolationBattles
python -m pytest tests/test_mercenaries.py -v
```

## NO Modificar
- `src/entities/` archivos existentes (si los hay)
- `src/network/commands.py` (otra tarea añadirá SendMercenaryCommand)
```

---

## 🟣 AGENTE 5: Sistema de Investigación (I+D)

**Rama:** `feature/research-system`

**Archivos a crear:**
- `src/core/research/` (nuevo directorio)
- `src/core/research/__init__.py`
- `src/core/research/research_type.py`
- `src/core/research/research_manager.py`
- `tests/test_research.py`

### Prompt Detallado:

```
Eres un desarrollador Python experto. Tu tarea es implementar el Sistema de Investigación y Desarrollo (I+D) para PathWars.

## Contexto del Proyecto
Según el GDD, los jugadores pueden invertir dinero para desbloquear métodos de interpolación avanzados:

| Investigación | Costo | Descripción |
|--------------|-------|-------------|
| LAGRANGE_INTERPOLATION | 500$ | Desbloquea Polinomio de Lagrange |
| SPLINE_INTERPOLATION | 1000$ | Desbloquea Spline Cúbico |
| TANGENT_CONTROL | 750$ | Permite modificar tangentes en puntos |

Las investigaciones son permanentes durante la partida.

## Tarea

1. Crear directorio `src/core/research/`

2. Crear `research_type.py`:
   ```python
   from enum import Enum, auto
   from dataclasses import dataclass
   from typing import List, Optional
   
   class ResearchType(Enum):
       """Types of research available in the game."""
       LAGRANGE_INTERPOLATION = auto()
       SPLINE_INTERPOLATION = auto()
       TANGENT_CONTROL = auto()
   
   @dataclass(frozen=True)
   class ResearchInfo:
       """Information about a research type."""
       research_type: ResearchType
       cost: int
       display_name: str
       description: str
       prerequisites: List[ResearchType]  # Research required before this one
       
   # Define research info for each type
   RESEARCH_INFO: dict[ResearchType, ResearchInfo] = {
       ResearchType.LAGRANGE_INTERPOLATION: ResearchInfo(
           research_type=ResearchType.LAGRANGE_INTERPOLATION,
           cost=500,
           display_name="Lagrange Polynomial",
           description="Unlock Lagrange interpolation for smoother curves (warning: Runge's phenomenon at edges)",
           prerequisites=[]
       ),
       ResearchType.SPLINE_INTERPOLATION: ResearchInfo(
           research_type=ResearchType.SPLINE_INTERPOLATION,
           cost=1000,
           display_name="Cubic Spline",
           description="Unlock Cubic Spline interpolation for the smoothest curves",
           prerequisites=[ResearchType.LAGRANGE_INTERPOLATION]  # Requires Lagrange first
       ),
       ResearchType.TANGENT_CONTROL: ResearchInfo(
           research_type=ResearchType.TANGENT_CONTROL,
           cost=750,
           display_name="Tangent Control",
           description="Modify curve derivatives at control points for precise path control",
           prerequisites=[]
       ),
   }
   ```

3. Crear `research_manager.py`:
   ```python
   from typing import Set, Optional
   import logging
   
   logger = logging.getLogger(__name__)
   
   class InsufficientFundsError(Exception):
       """Raised when player cannot afford research."""
       pass
   
   class PrerequisiteNotMetError(Exception):
       """Raised when research prerequisites are not met."""
       pass
   
   class AlreadyResearchedError(Exception):
       """Raised when trying to research something already unlocked."""
       pass
   
   class ResearchManager:
       """
       Manages research unlocks for a player.
       
       Tracks which research has been unlocked and validates new research purchases.
       """
       
       def __init__(self, player_id: str) -> None:
           self._player_id = player_id
           self._unlocked: Set[ResearchType] = set()
           
       @property
       def player_id(self) -> str:
           return self._player_id
       
       @property
       def unlocked_research(self) -> Set[ResearchType]:
           """Return copy of unlocked research set."""
           return set(self._unlocked)
       
       def is_unlocked(self, research_type: ResearchType) -> bool:
           """Check if research is unlocked."""
           return research_type in self._unlocked
       
       def can_unlock(self, research_type: ResearchType) -> bool:
           """
           Check if research can be unlocked (prerequisites met).
           Does not check cost.
           """
           if research_type in self._unlocked:
               return False
           
           info = RESEARCH_INFO.get(research_type)
           if info is None:
               return False
           
           # Check prerequisites
           for prereq in info.prerequisites:
               if prereq not in self._unlocked:
                   return False
           
           return True
       
       def get_cost(self, research_type: ResearchType) -> int:
           """Get cost of research."""
           info = RESEARCH_INFO.get(research_type)
           return info.cost if info else 0
       
       def unlock(self, research_type: ResearchType, available_money: int) -> int:
           """
           Attempt to unlock research.
           
           Args:
               research_type: Research to unlock.
               available_money: Player's current money.
               
           Returns:
               Cost of the research (to be deducted from player's money).
               
           Raises:
               AlreadyResearchedError: If already unlocked.
               PrerequisiteNotMetError: If prerequisites not met.
               InsufficientFundsError: If cannot afford.
           """
           if research_type in self._unlocked:
               raise AlreadyResearchedError(f"{research_type.name} is already researched")
           
           info = RESEARCH_INFO.get(research_type)
           if info is None:
               raise ValueError(f"Unknown research type: {research_type}")
           
           # Check prerequisites
           for prereq in info.prerequisites:
               if prereq not in self._unlocked:
                   prereq_info = RESEARCH_INFO.get(prereq)
                   prereq_name = prereq_info.display_name if prereq_info else prereq.name
                   raise PrerequisiteNotMetError(
                       f"Must unlock '{prereq_name}' before '{info.display_name}'"
                   )
           
           # Check cost
           if available_money < info.cost:
               raise InsufficientFundsError(
                   f"Need {info.cost}$, have {available_money}$"
               )
           
           self._unlocked.add(research_type)
           logger.info(f"Player {self._player_id} unlocked {research_type.name}")
           return info.cost
       
       def get_available_research(self) -> List[ResearchType]:
           """Get list of research that can be unlocked (prerequisites met)."""
           available = []
           for rt in ResearchType:
               if self.can_unlock(rt):
                   available.append(rt)
           return available
       
       def get_interpolation_methods(self) -> Set[str]:
           """
           Get set of interpolation method names unlocked.
           Always includes 'linear'.
           """
           methods = {'linear'}
           
           if ResearchType.LAGRANGE_INTERPOLATION in self._unlocked:
               methods.add('lagrange')
           
           if ResearchType.SPLINE_INTERPOLATION in self._unlocked:
               methods.add('spline')
           
           return methods
       
       def reset(self) -> None:
           """Reset all research (for new game)."""
           self._unlocked.clear()
       
       def to_dict(self) -> dict:
           """Serialize for network sync."""
           return {
               'player_id': self._player_id,
               'unlocked': [rt.name for rt in self._unlocked]
           }
       
       @classmethod
       def from_dict(cls, data: dict) -> 'ResearchManager':
           """Deserialize from network sync."""
           manager = cls(data['player_id'])
           for rt_name in data.get('unlocked', []):
               try:
                   rt = ResearchType[rt_name]
                   manager._unlocked.add(rt)
               except KeyError:
                   pass
           return manager
   ```

4. Crear tests en `tests/test_research.py`:
   - Tests de unlock básico
   - Tests de prerequisites
   - Tests de cost validation
   - Tests de already researched
   - Tests de serialization/deserialization
   - Tests de get_interpolation_methods
   - Tests de get_available_research
   - Mínimo 15 tests

## Principios
- **Single Responsibility**: ResearchManager solo maneja investigaciones
- Usar logging para debugging
- Usar excepciones específicas para errores

## Comandos para Verificar
```bash
cd /home/runner/work/PathWars-TheInterpolationBattles/PathWars-TheInterpolationBattles
python -m pytest tests/test_research.py -v
```

## NO Modificar
- `src/network/commands.py` (ResearchCommand ya existe)
- Otros archivos existentes
```

---

## 🔴 AGENTE 6: Implementar Ejecución de Comandos en GameServer

**Rama:** `feature/gameserver-command-execution`

**Archivos a modificar:**
- `src/network/server.py`
- `tests/network/test_server_command_execution.py` (nuevo)

### Prompt Detallado:

```
Eres un desarrollador Python experto. Tu tarea es implementar la ejecución real de comandos en GameServer para PathWars.

## Contexto del Proyecto
El GameServer actual en `src/network/server.py` tiene un placeholder que solo hace logging. Según el Tasks.md, esto es un problema de ALTA PRIORIDAD:

> "Falta de Validación Real de Comandos en GameServer"
> `_execute_command()` solo hace logging, no valida ni aplica comandos al estado del juego.

Los comandos están definidos en `src/network/commands.py`:
- PlaceTowerCommand
- ModifyControlPointCommand
- SendMercenaryCommand
- ResearchCommand
- ReadyCommand

## Tarea

1. Refactorizar `src/network/server.py`:

   ```python
   class GameServer:
       """
       Authoritative game server managing multiplayer game state.
       """
       
       def __init__(self) -> None:
           """Initialize the GameServer."""
           self.network_manager = NetworkManager()
           self.command_queue: Queue[GameCommand] = Queue()
           self.is_running = False
           
           # NEW: Authoritative game state
           self._game_state: Optional[GameState] = None
           
           # NEW: Command handlers registry
           self._command_handlers: Dict[str, Callable[[GameCommand], bool]] = {
               'PLACE_TOWER': self._handle_place_tower,
               'MODIFY_CONTROL_POINT': self._handle_modify_control_point,
               'SEND_MERCENARY': self._handle_send_mercenary,
               'RESEARCH': self._handle_research,
               'READY': self._handle_ready,
           }
           
           # Subscribe to network messages
           self.network_manager.subscribe(
               MessageType.PLAYER_ACTION,
               self._on_player_action
           )
       
       def set_game_state(self, game_state: GameState) -> None:
           """Set the authoritative game state to manage."""
           self._game_state = game_state
       
       def _execute_command(self, command: GameCommand) -> bool:
           """
           Execute a game command.
           
           Validates the command against game rules and updates state.
           
           Args:
               command: The command to execute.
               
           Returns:
               True if command was executed successfully, False otherwise.
           """
           command_type = command.command_type
           handler = self._command_handlers.get(command_type)
           
           if handler is None:
               logger.warning(f"Unknown command type: {command_type}")
               return False
           
           try:
               success = handler(command)
               if success:
                   logger.info(f"Executed {command_type} from player {command.player_id}")
                   # Broadcast state update to clients
                   self._broadcast_state_update()
               else:
                   logger.warning(f"Failed to execute {command_type}")
               return success
           except Exception as e:
               logger.error(f"Error executing {command_type}: {e}")
               return False
       
       def _handle_place_tower(self, command: GameCommand) -> bool:
           """
           Handle tower placement command.
           
           Validates:
           - Game is in DEFENSE_PLANNING phase (or PLANNING for single player)
           - Player has enough money
           - Position is valid (on grid, not occupied)
           """
           if self._game_state is None:
               return False
           
           # Extract data from command
           data = command.data
           tower_type = data.get('tower_type')
           position = data.get('position')  # {'x': int, 'y': int}
           
           if tower_type is None or position is None:
               logger.warning("Invalid PLACE_TOWER command data")
               return False
           
           # TODO: Validate phase, money, position
           # TODO: Create tower and add to game state
           # For now, just validate the structure
           
           logger.debug(f"Would place {tower_type} at {position}")
           return True
       
       def _handle_modify_control_point(self, command: GameCommand) -> bool:
           """Handle control point modification command."""
           if self._game_state is None:
               return False
           
           data = command.data
           action = data.get('action')  # 'add', 'move', 'remove'
           
           if action not in ('add', 'move', 'remove'):
               logger.warning(f"Invalid action: {action}")
               return False
           
           # TODO: Validate phase is OFFENSE_PLANNING
           # TODO: Apply modification to curve state
           
           logger.debug(f"Would {action} control point")
           return True
       
       def _handle_send_mercenary(self, command: GameCommand) -> bool:
           """Handle mercenary send command."""
           if self._game_state is None:
               return False
           
           data = command.data
           mercenary_type = data.get('mercenary_type')
           quantity = data.get('quantity', 1)
           target_player = data.get('target_player')
           
           if mercenary_type is None or target_player is None:
               logger.warning("Invalid SEND_MERCENARY command data")
               return False
           
           # TODO: Validate cost, create mercenaries
           
           logger.debug(f"Would send {quantity}x {mercenary_type} to {target_player}")
           return True
       
       def _handle_research(self, command: GameCommand) -> bool:
           """Handle research command."""
           if self._game_state is None:
               return False
           
           data = command.data
           research_type = data.get('research_type')
           
           if research_type is None:
               logger.warning("Invalid RESEARCH command data")
               return False
           
           # TODO: Validate cost, prerequisites, apply research
           
           logger.debug(f"Would research {research_type}")
           return True
       
       def _handle_ready(self, command: GameCommand) -> bool:
           """Handle ready state command."""
           if self._game_state is None:
               return False
           
           data = command.data
           ready = data.get('ready', False)
           
           # TODO: Track ready state per player
           # TODO: Check if both players ready, then transition phase
           
           logger.debug(f"Player {command.player_id} ready: {ready}")
           return True
       
       def _broadcast_state_update(self) -> None:
           """Broadcast current state to all connected clients."""
           if self._game_state is None:
               return
           
           state_dict = self._game_state.to_dict()
           message = Message(
               message_type=MessageType.STATE_UPDATE,
               payload=state_dict
           )
           self.network_manager.broadcast(message)
   ```

2. Asegurar que `process_commands()` retorna información sobre éxitos/fallos:
   ```python
   def process_commands(self) -> Tuple[int, int]:
       """
       Process all pending commands in the queue.
       
       Returns:
           Tuple of (successful_count, failed_count).
       """
       success_count = 0
       fail_count = 0
       
       while not self.command_queue.empty():
           command = self.command_queue.get()
           if self._execute_command(command):
               success_count += 1
           else:
               fail_count += 1
       
       return (success_count, fail_count)
   ```

3. Crear tests en `tests/network/test_server_command_execution.py`:
   - Test de cada tipo de comando (happy path)
   - Test de comandos con datos inválidos
   - Test de comando desconocido
   - Test de broadcast after execution
   - Test de process_commands return values
   - Mínimo 15 tests

## Principios
- **Command Pattern**: Ya implementado, solo añadir ejecución
- **Single Responsibility**: Cada handler maneja un tipo de comando
- Mantener compatibilidad hacia atrás

## Comandos para Verificar
```bash
cd /home/runner/work/PathWars-TheInterpolationBattles/PathWars-TheInterpolationBattles
python -m pytest tests/network/test_server_command_execution.py -v
python -m pytest tests/network/ -v  # Verificar que tests existentes siguen pasando
```

## NO Modificar
- `src/network/commands.py`
- `src/network/client.py`
- `src/network/manager.py`
- `src/network/protocol.py`
```

---

## 📝 Notas de Integración

### Orden de Merge Recomendado
Todas las tareas pueden ejecutarse en paralelo sin conflictos. El orden de merge sugerido es:

1. **Primero** (sin dependencias):
   - `feature/strategy-pattern-interpolation`
   - `feature/research-system`
   - `feature/mercenary-system`
   - `feature/lobby-configuration`
   - `feature/gameserver-command-execution`

2. **Segundo** (puede usar los anteriores):
   - `feature/game-phase-state-machine`

### Archivos Compartidos (EVITAR CONFLICTOS)
Los prompts han sido diseñados para NO modificar los mismos archivos:

| Archivo | Agente Responsable |
|---------|-------------------|
| `src/math_engine/interpolator.py` | Agente 1 (solo deprecar métodos) |
| `src/math_engine/` nuevo contenido | Agente 1 |
| `src/core/game_phases/` | Agente 2 |
| `src/ui/lobby.py` | Agente 3 |
| `src/core/match_config.py` | Agente 3 |
| `src/entities/mercenaries/` | Agente 4 |
| `src/core/research/` | Agente 5 |
| `src/network/server.py` | Agente 6 |

### Tests Coverage Target
Cada agente debe crear tests con:
- Mínimo 15 tests por módulo
- Coverage mínimo 70%
- Usar fixtures existentes de `tests/conftest.py`

### Comandos Globales para Verificar
```bash
# Ejecutar todos los tests
python -m pytest tests/ -v

# Verificar que no hay imports rotos
python -c "from src import *"

# Verificar style (si hay linter configurado)
# python -m flake8 src/ tests/
```
