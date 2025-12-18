# Tasks.md - Project Roadmap

This document tracks the progress and future phases of "PathWars: The Interpolation Duel".

---

# ✅ COMPLETED PHASES

## 1. Network Core System ✅
- [x] Basic TCP Sockets with Observer pattern in `src/network/manager.py`.
## 2. Game Entities Logic ✅
## 3. Game State & Grid System ✅
## 4. Visual Engine & Main Loop ✅
## 5. UI & Interaction Layer ✅
## 6. Curve Editor System ✅
## 7. Wave Manager & Spawner ✅
## 8. Combat System ✅
## 9. Wave Transition & Game Feedback ✅
## 10. Tower Special Effects ✅
## 11. Curve Editor Integration ✅
-   [x] Integrated in `main.py`
-   [x] Added smooth interpolation with chordal parameterization.
-   [x] Enforced X-sorting (Mathematical Function property).
-   [x] Restricted to Grid: Control points are now clamped to grid cells.
## 12. Wire Up Game Feedback Components ✅
## 13. Wire Up Tower Effects ✅

## 14. Arquitectura Cliente-Servidor y Refactorización (Core) ✅
**Objetivo:** Establecer una arquitectura sólida y escalable para el multijugador.

### 14.1. Implementar GameServer (Autoridad) ✅
- [x] Crear clase `GameServer` que gestione el estado autoritativo del juego.
- [x] Implementar validación de comandos del lado del servidor.
- [x] Gestionar conexiones de múltiples clientes (preparar para escalabilidad).

### 14.2. Implementar GameClient ✅
- [x] Crear clase `GameClient` que maneje la conexión con el servidor.
- [x] Implementar envío y recepción de comandos.
- [x] Separar lógica de renderizado (local) de lógica de juego (remota).

### 14.3. Patrón Command para Sincronización de Red ✅
- [x] Diseñar interfaz `GameCommand` (tipo, player_id, data, timestamp).
- [x] Implementar comandos específicos:
    - [x] `PlaceTowerCommand`
    - [x] `ModifyControlPointCommand`
    - [x] `SendMercenaryCommand`
    - [x] `ResearchCommand`
    - [x] `ReadyCommand` (para transición de fase)
- [x] Serialización y deserialización de comandos (JSON).
- [x] Queue de comandos con timestamp para sincronización.

### 14.4. Separación de GameState (Local vs Remoto) ✅
- [x] `GameState` (Remoto): HP, dinero, torres, puntos de control, fase actual.
- [x] `LocalGameState`: Posiciones de sprites, animaciones, efectos visuales.
- [x] Sincronización periódica del estado remoto.
- [x] Interpolación local para suavizado de movimientos.

### 14.5. Unit Tests ✅
- [x] Tests de serialización/deserialización de comandos.
- [x] Tests de validación de comandos en el servidor.
- [x] Tests de sincronización de estado.

### 14.6. Multiplayer Session Management ✅
- [x] `DuelSession` class for orchestrating multiplayer duels.
- [x] `SyncEngine` for real-time state synchronization.
- [x] `PlayerRole` enum for HOST/CLIENT distinction.
- [x] Asymmetric curve editing model implemented.

## 15. Strategy Pattern for Interpolation ✅
**Objetivo:** Implementar el patrón Strategy para los métodos de interpolación.

- [x] Interfaz `InterpolationStrategy` con método `interpolate()`.
- [x] Implementaciones concretas:
    - [x] `LinearStrategy` (siempre disponible)
    - [x] `LagrangeStrategy` (requiere investigación)
    - [x] `SplineStrategy` (requiere investigación)
- [x] `InterpolationRegistry` para gestionar estrategias disponibles.
- [x] Integración con `ResearchManager` para desbloqueo de métodos.
- [x] Tests unitarios de estrategias de interpolación.

## 16. Sistema de Investigación (I+D) ✅
**Objetivo:** Permitir a los jugadores desbloquear métodos avanzados de interpolación.

- [x] Clase `ResearchManager` con gestión de investigaciones desbloqueadas.
- [x] Enum `ResearchType` con investigaciones disponibles:
    - [x] `LAGRANGE_INTERPOLATION`
    - [x] `SPLINE_INTERPOLATION`
    - [x] `TANGENT_CONTROL`
- [x] Validación de prerequisitos y costos.
- [x] `ResearchCommand` para sincronización de red.
- [x] Tests unitarios del sistema de investigación.

## 17. Sistema de Mercenarios ✅
**Objetivo:** Permitir enviar enemigos extra al rival durante la fase ofensiva.

- [x] Clase base `BaseMercenary` extendiendo `Enemy`.
- [x] `MercenaryFactory` (Factory Pattern) para crear mercenarios.
- [x] Tipos de mercenarios implementados:
    - [x] `ReinforcedStudent` (+50% HP)
    - [x] `SpeedyVariableX` (+100% velocidad, -30% HP)
    - [x] `TankConstantPi` (+200% HP, -50% velocidad)
- [x] `SendMercenaryCommand` para sincronización de red.
- [x] Tests unitarios del sistema de mercenarios.

## 18. Lobby y Configuración de Partida ✅
**Objetivo:** Permitir a los jugadores configurar la partida antes de comenzar.

- [x] Menú principal con opciones para crear/unirse a partida.
- [x] Clase `MatchConfig` con parámetros configurables.
- [x] Sistema de configuración del lobby implementado.
- [x] Tests de configuración de partida.

## 19. GameServer Command Execution ✅
**Objetivo:** Implementar ejecución de comandos en el servidor.

- [x] GameServer puede recibir y procesar comandos.
- [x] Validación básica de comandos implementada.
- [x] Queue de comandos con timestamp para sincronización.
- [x] Tests de ejecución de comandos en servidor.

## 20. Game Loop & Phase System ✅
**Objetivo:** Implementar el sistema de fases del juego usando el patrón State.

### 20.1. Phase State Pattern ✅
- [x] Interfaz `GamePhaseState` con métodos del patrón State:
    - [x] `enter()` y `exit()` para transiciones
    - [x] Métodos de validación de acciones por fase
    - [x] `get_allowed_transitions()` para validar transiciones
- [x] Estados concretos implementados:
    - [x] `PreparationPhaseState` - Colocación de 2 puntos iniciales
    - [x] `PathModificationPhaseState` - Modificación de camino (1 punto max)
    - [x] `BuildingPhaseState` - Colocación de torres
    - [x] `CombatPhaseState` - Ejecución de oleada
    - [x] `RoundEndPhaseState` - Transición entre rondas

### 20.2. Phase Manager ✅
- [x] Clase `PhaseManager` para orquestar el loop de juego.
- [x] Gestión de transiciones de fase con validación.
- [x] Tracking de número de ronda (1-N, configurable).
- [x] Enforcement de reglas de puntos de control:
    - [x] 2 puntos iniciales en fase de preparación
    - [x] Max 1 punto de modificación por ronda después
    - [x] Puntos de rondas anteriores bloqueados (no movibles)
    - [x] Validación de bordes para puntos iniciales

### 20.3. Unit Tests ✅
- [x] Tests de estados de fase (permissions y transiciones).
- [x] Tests de PhaseManager (transiciones, constraints).
- [x] Tests de límite de puntos en preparación (2 puntos).
- [x] Tests de límite de modificación por ronda (1 punto).
- [x] Tests de validación de bordes para puntos iniciales.
- [x] Tests de tracking de rondas y finalización de partida.

---

# 🚧 UPCOMING PHASES

La siguiente hoja de ruta prioriza la **Arquitectura Multijugador** y la **Calidad de Código**, aplicando principios SOLID y preparando el código para Tests Unitarios.

---

## 21. Lobby UI Enhancement (FUTURE)
**Objetivo:** Mejorar la interfaz de lobby con más opciones de configuración.

### 21.1. Pantalla de lobby con parámetros configurables
- [ ] Número de Oleadas (3, 5, 7, 10)
- [ ] Dificultad (Fácil, Normal, Difícil)
- [ ] Velocidad de Juego (1x, 1.5x, 2x)
- [ ] Tamaño del Mapa (15x15, 20x20, 25x25)
- [ ] Dinero Inicial

### 21.2. Handshake de Configuración
- [ ] El servidor envía `MatchConfigCommand` al cliente al conectarse.
- [ ] El cliente valida y confirma la configuración.
- [ ] Sincronización de configuración antes de iniciar.

---

## 22. Motor de Pantalla Dividida y Input Contextual (FUTURE)
**Objetivo:** Renderizar dos mapas simultáneamente y gestionar input según el contexto.

### 22.1. Sistema de Doble Viewport ✅
- [x] Crear clase `DualView` (anteriormente `SplitScreenRenderer`):
    - [x] Viewport Izquierdo: Mapa propio (Defensa).
    - [x] Viewport Derecho: Mapa rival (Ofensa).
- [x] Conversión de coordenadas de pantalla a grid.
- [x] Dibujado de línea divisoria y etiquetas.

### 22.2. InputHandler Contextual
- [x] Detectar en qué viewport está el cursor/clic.
- [ ] Contexto de Input según la fase:
    - [ ] `OffensePlanning`: Solo se puede editar el mapa rival (viewport derecho).
    - [ ] `DefensePlanning`: Solo se puede colocar torres en el mapa propio (viewport izquierdo).
    - [ ] `Battle`: Solo observación (input deshabilitado excepto cámara).
- [ ] Validación de acciones según el estado del juego.

### 22.3. Indicadores Visuales
- [ ] Borde resaltado en el viewport activo según la fase.
- [ ] Cursor diferente según el modo (editar camino vs colocar torre).
- [ ] Overlay con instrucciones ("Edita el camino del rival" / "Coloca tus torres").

### 22.4. Unit Tests
- [x] Tests de DualView (viewport dimensions, coordinate conversion).
- [ ] Tests de validación de input contextual.

---

# 📋 CURRENT FOCUS
- **Phase 20: Game Loop & Phase System** - ✅ COMPLETED
- **Next: Integration with GameState and UI** - Connect phase system with game loop.

---

# 🔍 PROJECT REVIEW FINDINGS (Diciembre 2024)

Esta sección documenta los hallazgos de la revisión del proyecto después de la fusión de cambios.

## Problemas Corregidos

### Tests Corregidos ✅
1. **`test_grid.py::TestGameState::test_initial_values`**: Test actualizado para reflejar el valor correcto de dinero inicial (1000 en lugar de 100).
2. **Tests de pygame**: Corregido problema de inicialización de pygame.font en tests:
   - `test_result_screen.py::TestResultScreenDraw`
   - `test_wave_banner.py::TestWaveBannerDraw`
   - Solución: Añadido fixture `pygame_init` en `conftest.py` con scope de sesión.
3. **Tests de multiplayer**: Removidas llamadas innecesarias a `pygame.init()/quit()` en:
   - `test_dual_view.py`
   - `test_main_menu.py`

## Estado de Tests
- **461 tests pasando** ✅
- **0 tests fallando** ✅

## Oportunidades de Mejora Identificadas

### Alta Prioridad

#### 1. Falta de Validación Real de Comandos en GameServer
- **Ubicación**: `src/network/server.py`
- **Problema**: `_execute_command()` solo hace logging, no valida ni aplica comandos al estado del juego.
- **Acción Requerida**: Implementar validación y ejecución real de comandos.

#### 2. GameServer No Ejecuta Comandos en GameState
- **Ubicación**: `src/network/server.py`
- **Problema**: Los comandos se procesan pero no modifican el estado del juego.
- **Acción Requerida**: Conectar `GameServer._execute_command()` con `GameState`.

#### 3. Interpolation Strategies no siguen Strategy Pattern
- **Ubicación**: `src/math_engine/interpolator.py`
- **Problema**: Las funciones de interpolación son métodos estáticos, no clases que implementen una interfaz.
- **Acción Requerida**: Refactorizar a Strategy Pattern como indica el GDD.

### Media Prioridad

#### 4. CurveState.initialize_default_points Ignora Estado Bloqueado Original
- **Ubicación**: `src/core/curve_state.py` líneas 252-262
- **Problema**: La función desbloquea la curva temporalmente pero ignora `was_locked` al final.
- **Acción Requerida**: Restaurar estado `_locked` original si era necesario.

#### 5. Falta de AssetManager para Sprites/Animaciones
- **Ubicación**: `src/graphics/assets.py`
- **Problema**: `AssetManager` actual solo maneja fuentes, no sprites/animaciones.
- **Acción Requerida**: Extender para manejo completo de assets como indica Fase 19.

#### 6. GamePhase Enum Incompleto
- **Ubicación**: `src/core/game_state.py`
- **Problema**: Falta `LOBBY` phase que existe en `DuelPhase` (src/multiplayer/duel_session.py).
- **Acción Requerida**: Unificar phases o agregar LOBBY a GamePhase.

### Baja Prioridad

#### 7. Docstrings Faltantes en Algunos Métodos del Interpolator
- **Ubicación**: `src/math_engine/interpolator.py`
- **Problema**: Docstrings mínimos sin descripción de parámetros y retornos.
- **Acción Requerida**: Completar documentación.

#### 8. Uso de Type Comments en Lugar de Type Hints
- **Ubicación**: Varios archivos
- **Problema**: Algunos archivos usan `# type: ignore` o comentarios de tipo.
- **Acción Requerida**: Migrar a type hints nativos de Python 3.10+.

## Buenas Prácticas Observadas ✅

1. **Patrón Observer** bien implementado en NetworkManager y WaveManager.
2. **Patrón Command** bien implementado para comandos de red.
3. **Patrón Singleton** usado correctamente en GameState y NetworkManager.
4. **Separación de Responsabilidades** clara entre modules.
5. **Tests comprehensivos** con buena cobertura (461 tests).
6. **Documentación de código** con docstrings detallados.
7. **Manejo de errores** con excepciones personalizadas (InsufficientFundsError, CurveLockedError, etc.).
8. **Logging** implementado correctamente en todos los módulos.

## Próximos Pasos Recomendados

1. **Completar validación de comandos en GameServer** - Crítico para multijugador funcional.
2. **Implementar Lobby con configuración** - Permitir personalizar partidas.
3. **Unificar GamePhase y DuelPhase** - Evitar confusión en fases de juego.
4. **Implementar Strategy Pattern para interpolación** - Seguir diseño del GDD.
5. **Completar InputHandler contextual** - Crucial para experiencia de usuario en multijugador.
