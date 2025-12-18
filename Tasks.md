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

---

# 🚧 UPCOMING PHASES

La siguiente hoja de ruta prioriza la **Arquitectura Multijugador** y la **Calidad de Código**, aplicando principios SOLID y preparando el código para Tests Unitarios.

---

## 15. Lobby y Configuración de Partida (PARTIALLY COMPLETE)
**Objetivo:** Permitir a los jugadores configurar la partida antes de comenzar.

### 15.1. Menú Principal ✅
- [x] Crear pantalla de menú con opciones:
    - [x] "Crear Partida" (Host)
    - [x] "Unirse a Partida" (Client)
    - [ ] "Configuración"
    - [x] "Salir"
- [x] Campos de entrada para IP y puerto.
- [x] Manejo de estados de conexión.

### 15.2. Lobby de Configuración
- [ ] Pantalla de lobby con parámetros configurables:
    - [ ] Número de Oleadas (3, 5, 7, 10)
    - [ ] Dificultad (Fácil, Normal, Difícil)
    - [ ] Velocidad de Juego (1x, 1.5x, 2x)
    - [ ] Tamaño del Mapa (15x15, 20x20, 25x25)
    - [ ] Dinero Inicial
- [ ] Indicador de "Listo" para cada jugador.
- [ ] Botón "Iniciar Partida" (solo Host, habilitado cuando ambos están listos).

### 15.3. Handshake de Configuración
- [ ] El servidor envía `MatchConfigCommand` al cliente al conectarse.
- [ ] El cliente valida y confirma la configuración.
- [ ] Sincronización de configuración antes de iniciar.

### 15.4. Unit Tests
- [x] Tests de MainMenu UI (parcialmente completados).
- [ ] Tests de validación de parámetros de configuración.
- [ ] Tests de handshake de red.

---

## 16. Motor de Pantalla Dividida y Input Contextual (PARTIALLY COMPLETE)
**Objetivo:** Renderizar dos mapas simultáneamente y gestionar input según el contexto.

### 16.1. Sistema de Doble Viewport ✅
- [x] Crear clase `DualView` (anteriormente `SplitScreenRenderer`):
    - [x] Viewport Izquierdo: Mapa propio (Defensa).
    - [x] Viewport Derecho: Mapa rival (Ofensa).
- [x] Conversión de coordenadas de pantalla a grid.
- [x] Dibujado de línea divisoria y etiquetas.

### 16.2. InputHandler Contextual
- [x] Detectar en qué viewport está el cursor/clic.
- [ ] Contexto de Input según la fase:
    - [ ] `OffensePlanning`: Solo se puede editar el mapa rival (viewport derecho).
    - [ ] `DefensePlanning`: Solo se puede colocar torres en el mapa propio (viewport izquierdo).
    - [ ] `Battle`: Solo observación (input deshabilitado excepto cámara).
- [ ] Validación de acciones según el estado del juego.

### 16.3. Indicadores Visuales
- [ ] Borde resaltado en el viewport activo según la fase.
- [ ] Cursor diferente según el modo (editar camino vs colocar torre).
- [ ] Overlay con instrucciones ("Edita el camino del rival" / "Coloca tus torres").

### 16.4. Unit Tests
- [x] Tests de DualView (viewport dimensions, coordinate conversion).
- [ ] Tests de validación de input contextual.

---

## 17. Lógica de Fases Estricta (State Pattern)
**Objetivo:** Implementar una máquina de estados robusta para el flujo de juego.

### 17.1. Diseño de Estados
- [ ] Interfaz `GamePhaseState` con métodos:
    - [ ] `enter(game_state)`: Al entrar en la fase.
    - [ ] `update(game_state, dt)`: Actualización por frame.
    - [ ] `handle_input(game_state, event)`: Manejo de input.
    - [ ] `exit(game_state)`: Al salir de la fase.
    - [ ] `can_transition_to(next_phase)`: Validación de transición.

### 17.2. Implementar Estados Concretos
- [ ] `LobbyState`: Configuración de partida.
- [ ] `OffensePlanningState`: Edición del camino rival.
- [ ] `DefensePlanningState`: Colocación de torres propias.
- [ ] `BattleState`: Ejecución de la oleada en tiempo real.
- [ ] `GameOverState`: Fin de partida.

### 17.3. Transiciones de Estado
- [ ] Diagrama de transiciones:
    ```
    Lobby → OffensePlanning → DefensePlanning → Battle → OffensePlanning (next wave) → ... → GameOver
    ```
- [ ] Validación de transiciones (no se puede saltar fases).
- [ ] Sincronización de transiciones entre cliente y servidor.

### 17.4. Lógica de Puntos Bloqueados (Inmutabilidad)
- [ ] Al finalizar `OffensePlanningState`, marcar puntos de control como `locked`.
- [ ] En la siguiente oleada, solo permitir añadir nuevos puntos o modificar los no bloqueados.
- [ ] Visualización de puntos bloqueados (color diferente, icono de candado).

### 17.5. Temporizador de Fase
- [ ] Cada fase tiene un tiempo límite opcional.
- [ ] Countdown visual en la UI.
- [ ] Auto-transición al expirar el tiempo.

### 17.6. Unit Tests
- [ ] Tests de transiciones válidas e inválidas.
- [ ] Tests de lógica de bloqueo de puntos.
- [ ] Tests de temporizador de fase.

---

## 18. Expansión Económica (Mercenarios e I+D)
**Objetivo:** Implementar las mecánicas económicas avanzadas del GDD.

### 18.1. Sistema de Mercenarios
- [ ] Crear `MercenaryFactory` (Factory Pattern):
    - [ ] `create_mercenary(type, player_id)`: Devuelve instancia de enemigo.
- [ ] Tipos de Mercenarios:
    - [ ] `ReinforcedStudent`: +50% HP.
    - [ ] `SpeedyVariableX`: +100% velocidad, -30% HP.
    - [ ] `TankConstantPi`: +200% HP, -50% velocidad.
- [ ] UI: Panel de mercenarios con botones de compra.
- [ ] Comando de red: `SendMercenaryCommand(type, quantity, target_player)`.
- [ ] Validación de dinero suficiente.

### 18.2. Sistema de Investigación (I+D)
- [ ] Crear `ResearchManager`:
    - [ ] `unlock_research(player_id, research_type)`: Desbloquea método.
    - [ ] `is_unlocked(player_id, research_type)`: Consulta si está desbloqueado.
- [ ] Investigaciones disponibles:
    - [ ] `LAGRANGE_INTERPOLATION`: 500$.
    - [ ] `SPLINE_INTERPOLATION`: 1000$.
    - [ ] `TANGENT_CONTROL`: 750$.
- [ ] UI: Panel de I+D con árbol de tecnologías.
- [ ] Comando de red: `ResearchCommand(research_type)`.
- [ ] Persistencia durante la partida (una vez desbloqueado, siempre disponible).

### 18.3. Strategy Pattern para Interpolación
- [ ] Interfaz `InterpolationStrategy`:
    - [ ] `interpolate(control_points, resolution)`: Devuelve lista de puntos.
- [ ] Implementaciones:
    - [ ] `LinearInterpolation` (siempre disponible).
    - [ ] `LagrangeInterpolation` (requiere investigación).
    - [ ] `SplineInterpolation` (requiere investigación).
- [ ] Selector dinámico en `Route`:
    - [ ] `set_interpolation_method(method)`: Solo si está desbloqueado.
    - [ ] Validación con `ResearchManager`.

### 18.4. Unit Tests
- [ ] Tests de creación de mercenarios.
- [ ] Tests de validación de costos.
- [ ] Tests de desbloqueo de investigaciones.
- [ ] Tests de estrategias de interpolación.

---

## 19. Sistema Visual (Sprites y Autotiling)
**Objetivo:** Mejorar la presentación visual del juego con assets profesionales.

### 19.1. AssetManager Avanzado
- [ ] Crear `AssetManager` singleton:
    - [ ] Carga asíncrona de sprites.
    - [ ] Cache de assets en memoria.
    - [ ] Gestión de spritesheets.
- [ ] Organización de assets:
    ```
    assets/
      sprites/
        towers/
          dean_idle.png
          dean_attack.png
          calculus_idle.png
          ...
        enemies/
          student_walk.png
          variable_x_walk.png
          ...
        projectiles/
          chalk.png
          explosion.png
        tiles/
          path_straight_h.png
          path_straight_v.png
          path_curve_tl.png
          ...
    ```

### 19.2. Sistema de Autotiling para el Camino
- [ ] Crear `PathTileSelector`:
    - [ ] `select_tile(grid_pos, neighbors)`: Devuelve sprite correcto según vecinos.
- [ ] Lógica de conexión de tiles:
    - [ ] Analizar 8 vecinos (N, S, E, W, NE, NW, SE, SW).
    - [ ] Determinar tipo de tile (recto, curva, intersección).
- [ ] Tiles disponibles:
    - [ ] Recto Horizontal / Vertical.
    - [ ] Curva 90° (4 rotaciones).
    - [ ] Intersección T (4 rotaciones).
    - [ ] Intersección Cruz.
- [ ] Actualización dinámica al modificar puntos de control.

### 19.3. Animaciones de Sprites
- [ ] Crear `SpriteAnimator`:
    - [ ] Gestión de frames de animación.
    - [ ] Control de velocidad de animación (FPS).
- [ ] Aplicar a:
    - [ ] Enemigos: Caminar, morir.
    - [ ] Torres: Idle, atacar.
    - [ ] Proyectiles: Rotación según dirección.

### 19.4. Partículas y Efectos
- [ ] Sistema básico de partículas para:
    - [ ] Explosiones (Prof. Física).
    - [ ] Impactos de proyectiles.
    - [ ] Muerte de enemigos (símbolos matemáticos flotantes).

### 19.5. Unit Tests
- [ ] Tests de carga de assets.
- [ ] Tests de selección de tiles.
- [ ] Tests de animaciones.

---

# 📋 CURRENT FOCUS
- **Fase 15: Lobby y Configuración de Partida** - Completar funcionalidad de lobby.
- **Fase 16: Input Contextual** - Finalizar manejo de input según fase de juego.
- **Fase 17: State Pattern** - Implementar máquina de estados completa.

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
