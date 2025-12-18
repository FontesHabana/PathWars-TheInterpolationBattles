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

---

# 🚧 UPCOMING PHASES

La siguiente hoja de ruta prioriza la **Arquitectura Multijugador** y la **Calidad de Código**, aplicando principios SOLID y preparando el código para Tests Unitarios.

---

## 14. Arquitectura Cliente-Servidor y Refactorización (Core) 🚀 MÁXIMA PRIORIDAD
**Objetivo:** Establecer una arquitectura sólida y escalable para el multijugador.

### 14.1. Implementar GameServer (Autoridad)
- [x] Crear clase `GameServer` que gestione el estado autoritativo del juego.
- [x] Implementar validación de comandos del lado del servidor.
- [x] Gestionar conexiones de múltiples clientes (preparar para escalabilidad).

### 14.2. Implementar GameClient
- [x] Crear clase `GameClient` que maneje la conexión con el servidor.
- [x] Implementar envío y recepción de comandos.
- [x] Separar lógica de renderizado (local) de lógica de juego (remota).

### 14.3. Patrón Command para Sincronización de Red
- [x] Diseñar interfaz `GameCommand` (tipo, player_id, data, timestamp).
- [x] Implementar comandos específicos:
    - [x] `PlaceTowerCommand`
    - [x] `ModifyControlPointCommand`
    - [x] `SendMercenaryCommand`
    - [x] `ResearchCommand`
    - [x] `ReadyCommand` (para transición de fase)
- [x] Serialización y deserialización de comandos (JSON).
- [x] Queue de comandos con timestamp para sincronización.

### 14.4. Separación de GameState (Local vs Remoto)
- [ ] `GameState` (Remoto): HP, dinero, torres, puntos de control, fase actual.
- [ ] `LocalGameState`: Posiciones de sprites, animaciones, efectos visuales.
- [ ] Sincronización periódica del estado remoto.
- [ ] Interpolación local para suavizado de movimientos.

### 14.5. Unit Tests
- [x] Tests de serialización/deserialización de comandos.
- [x] Tests de validación de comandos en el servidor.
- [x] Tests de sincronización de estado.

---

## 15. Lobby y Configuración de Partida
**Objetivo:** Permitir a los jugadores configurar la partida antes de comenzar.

### 15.1. Menú Principal
- [ ] Crear pantalla de menú con opciones:
    - [ ] "Crear Partida" (Host)
    - [ ] "Unirse a Partida" (Client)
    - [ ] "Configuración"
    - [ ] "Salir"

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
- [ ] Tests de validación de parámetros de configuración.
- [ ] Tests de handshake de red.

---

## 16. Motor de Pantalla Dividida y Input Contextual
**Objetivo:** Renderizar dos mapas simultáneamente y gestionar input según el contexto.

### 16.1. Sistema de Doble Viewport
- [ ] Crear clase `SplitScreenRenderer`:
    - [ ] Viewport Izquierdo: Mapa propio (Defensa).
    - [ ] Viewport Derecho: Mapa rival (Ofensa).
- [ ] Cada viewport tiene su propia cámara y transformación.
- [ ] Renderizado independiente de grilla, torres, enemigos, camino.

### 16.2. InputHandler Contextual
- [ ] Detectar en qué viewport está el cursor/clic.
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
- [ ] Tests de detección de viewport activo.
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
- **Fase 14: Arquitectura Cliente-Servidor** - Establecer las bases sólidas para el multijugador.
- **Aplicación de Principios SOLID** - Diseño modular y extensible.
- **Preparación para Tests Unitarios** - Código testeable desde el inicio.
