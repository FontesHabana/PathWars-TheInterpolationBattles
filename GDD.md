# Game Design Document: MathWars - The Interpolation Duel

## 1. Resumen Ejecutivo
**Título:** MathWars: The Interpolation Duel
**Género:** Tower Defense PvP / Estrategia Matemática
**Plataforma:** PC (Windows/Linux/Mac) - Python
**Modo de Juego:** Multijugador LAN (WiFi) 1vs1
**Motor/Librerías:** Python (Pygame para renderizado, SciPy/NumPy para cálculos matemáticos, Sockets para red).
**Estilo Visual:** "Academic Neon Cyberpunk" (Isometric, Grid-based).

## 2. Mecánicas de Juego (Core Loop)

### 2.1. Objetivo
El objetivo es sobrevivir a 5 hordas (ondas) de enemigos enviados por el rival, mientras tus propios enemigos intentan cruzar el mapa del rival. Gana el jugador que tenga más vida en su base al final de la 5ta horda o el último en pie.

### 2.2. División de Pantalla
La interfaz se divide verticalmente:
*   **Izquierda (Tu Campo):** Donde construyes torres para defenderte de los enemigos del rival.
*   **Derecha (Campo Rival):** Una visualización en tiempo real de lo que ocurre en el campo del enemigo (tus enemigos atacándolo).

### 2.3. Sistema de Fases (Turnos)

El juego consta de 5 Hordas (configurables en el Lobby). Cada Horda tiene dos fases diferenciadas:

#### **Fase A: Fase Ofensiva (Editar Mapa Rival)**
En esta fase, el jugador modifica la **Ruta de Ataque** que seguirán sus enemigos en el campo del rival.
*   **Input:** El jugador tiene un conjunto de puntos de control (Nodos) en un plano cartesiano del mapa enemigo.
*   **Restricciones de Edición:**
    *   **Puntos Bloqueados:** Los puntos de control colocados en oleadas anteriores quedan inmutables. Solo se pueden añadir nuevos puntos o modificar los de la oleada actual.
    *   **Límite de Modificación por Turno:** El jugador puede añadir o mover un número limitado de puntos por oleada (definido en configuración).
*   **Herramientas de Interpolación (Mejoras):**
    1.  **Añadir Nodos:** Gastar recursos para agregar puntos intermedios ($P_x, P_y$) para esquivar zonas donde el rival puso torres.
    2.  **Cambiar Método (mediante I+D):**
        *   *Lineal:* Ruta por defecto, predecible. Siempre disponible.
        *   *Polinomio de Lagrange:* Suave pero con "fenómeno de Runge" (oscilaciones fuertes en los bordes). Debe desbloquearse mediante Investigación.
        *   *Spline Cúbico:* La ruta más suave y segura. Debe desbloquearse mediante Investigación.
    3.  **Ajuste de Derivadas (Tangentes):** Modificar la pendiente en un punto para "acelerar" la curva o hacer giros cerrados (inspirado en curvas de Hermite/Bézier).

#### **Fase B: Fase Defensiva (Colocar Torres Propias)**
Después de editar el camino del rival, el jugador planifica su defensa en su propio campo.
*   **Construcción de Torres:** El jugador coloca torres en su grilla usando los recursos acumulados.
*   **Estrategia:** Anticipar el camino que el rival diseñó para sus enemigos.

#### **Fase C: Batalla (Tiempo Real)**
*   Los enemigos (Estudiantes/Becarios) siguen la función matemática generada $f(x)$.
*   Las Torres (Profesores) disparan automáticamente.
*   **Economía:** Cada enemigo eliminado otorga dinero ($$).

### 2.4. Las Torres (Los Profesores)
Las torres se colocan en una grilla discreta. Se pueden mejorar (Grado de Maestría -> Doctorado).

1.  **El Decano (Tanque/Bloqueo):**
    *   *Descripción:* Mucha vida, bajo daño. Puede bloquear el camino (si la función matemática choca con él, los enemigos se detienen a "oír su discurso").
2.  **Prof. de Cálculo (Ataque a Distancia):**
    *   *Descripción:* Dispara tizas a alta velocidad. Cadencia rápida, daño medio.
    *   *Ataque:* "Proyectil de Límite".
3.  **Prof. de Física (Cañón/AoE):**
    *   *Descripción:* Lanza proyectiles parabólicos que hacen daño en área.
    *   *Ataque:* "Explosión Vectorial".
4.  **Prof. de Estadística (Support/Slow):**
    *   *Descripción:* No hace daño, pero aplica un debuff de "Confusión" (Ralentiza a los enemigos o añade ruido aleatorio a su trayectoria).

### 2.5. Mecánicas Económicas Avanzadas

#### **2.5.1. Sistema de Mercenarios**
Durante la Fase Ofensiva, además de editar el camino, el jugador puede invertir dinero para enviar **enemigos extra** al rival:
*   **Costo:** Variable según tipo de enemigo.
*   **Tipos de Mercenarios:**
    *   *Estudiante Reforzado:* Más HP que el estudiante básico.
    *   *Variable X Veloz:* Alta velocidad, baja vida.
    *   *Constante Pi:* Enemigo tanque, muy lento pero resistente.
*   **Objetivo:** Saturar las defensas rivales y causar daño a su base.

#### **2.5.2. Sistema de Investigación y Desarrollo (I+D)**
El jugador puede invertir dinero para desbloquear métodos de interpolación avanzados:
*   **Investigaciones Disponibles:**
    *   *Polinomio de Lagrange:* Costo: 500$. Desbloquea interpolación por Lagrange para el camino rival.
    *   *Spline Cúbico:* Costo: 1000$. Desbloquea interpolación por Spline para el camino rival.
    *   *Control de Tangentes:* Costo: 750$. Permite modificar derivadas en puntos de control.
*   **Mecánica:** Las investigaciones son permanentes durante la partida. Una vez desbloqueadas, el método está disponible para todas las oleadas siguientes.
*   **Estrategia:** Invertir temprano en I+D permite crear rutas más complejas y difíciles de defender.

### 2.6. Configuración de Partida (Lobby)

Antes de iniciar una partida multijugador, los jugadores pueden configurar los siguientes parámetros en el **Lobby**:
*   **Número de Oleadas:** 3, 5, 7 o 10 oleadas.
*   **Dificultad:** Fácil, Normal, Difícil (afecta HP de enemigos y dinero inicial).
*   **Velocidad de Juego:** Normal (1x), Rápido (1.5x), Muy Rápido (2x).
*   **Tamaño del Mapa:** Pequeño (15x15), Mediano (20x20), Grande (25x25).
*   **Dinero Inicial:** Cantidad de recursos al comenzar (por defecto: 500$).

Ambos jugadores deben estar de acuerdo con la configuración antes de iniciar la partida.

### 2.7. Sistema Visual

#### **2.7.1. Sprites y Animaciones**
El juego utiliza sprites isométricos pre-renderizados:
*   **Torres:** Sprites estáticos con animaciones de ataque (2-3 frames).
*   **Enemigos:** Sprites con animación de caminar (4 frames) y muerte (3 frames).
*   **Proyectiles:** Sprites pequeños con rotación dinámica según la dirección.

#### **2.7.2. Autotiling del Camino**
El camino generado por la curva matemática se visualiza mediante un sistema de **autotiling**:
*   **Lógica de Conexión:** Cada tile del camino analiza sus vecinos para determinar qué sprite usar (recto, curva, intersección).
*   **Tiles Disponibles:**
    *   *Recto Horizontal*
    *   *Recto Vertical*
    *   *Curva 90° (4 rotaciones)*
    *   *Intersección T (4 rotaciones)*
    *   *Intersección Cruz*
*   **Actualización Dinámica:** El camino se recalcula y re-dibuja cada vez que el jugador modifica los puntos de control durante la Fase Ofensiva.

## 3. Arquitectura Técnica (Para los Agentes de IA)

### 3.1. Stack Tecnológico
*   **Lenguaje:** Python 3.10+
*   **Gráficos:** `pygame` (Sprite handling, game loop).
*   **Matemáticas:** `numpy` (arrays), `scipy.interpolate` (Lagrange, CubicSpline).
*   **Red:** `socket` (librería estándar). Arquitectura Cliente-Servidor o P2P sincronizado.

### 3.2. Arquitectura de Red (Cliente-Servidor)
*   **Modelo:** Cliente-Servidor autorizado. Un jugador actúa como `GameServer` (autoridad del juego) y el otro como `GameClient`.
*   **Patrón Command:** Todas las acciones de juego (colocar torre, modificar punto, enviar mercenarios) se encapsulan como comandos serializables enviados al servidor.
*   **GameState:**
    *   *Local:* Estado local del cliente (posiciones de sprite, animaciones).
    *   *Remoto:* Estado sincronizado del servidor (HP, dinero, torres colocadas, puntos de control).
*   **Sincronización:**
    *   Al terminar la *Fase Ofensiva*, cada cliente envía sus puntos de control o coeficientes del polinomio al servidor.
    *   Al terminar la *Fase Defensiva*, cada cliente envía las torres colocadas.
    *   Durante la batalla, se sincronizan solo los estados críticos (HP de base, dinero, torres destruidas). Las posiciones de enemigos se calculan determinísticamente en ambos lados usando el mismo `seed` y función de tiempo.
*   **Handshake de Configuración:** Al conectarse, el servidor envía la configuración de partida (oleadas, velocidad, tamaño de mapa) al cliente. El cliente debe confirmar antes de comenzar.

### 3.3. Estructura de Datos

#### Ruta (Curve Path)
```python
# Ejemplo para el agente de código
class Route:
    def __init__(self, control_points, method='linear'):
        self.points = control_points # Lista de tuplas [(0,0), (5,5), ...]
        self.method = method # 'linear', 'lagrange', 'spline'
        self.locked_points = [] # Puntos de oleadas anteriores (inmutables)

    def generate_path(self, resolution=100):
        # Utilizar scipy.interpolate para generar los puntos intermedios
        pass

    def can_modify_point(self, index):
        # Verifica si el punto puede ser modificado (no está bloqueado)
        return index not in self.locked_points
```

#### Comando de Red (Command Pattern)
```python
class GameCommand:
    def __init__(self, command_type, player_id, data):
        self.type = command_type  # 'PLACE_TOWER', 'MODIFY_POINT', 'SEND_MERCENARY', 'RESEARCH'
        self.player_id = player_id
        self.data = data  # Diccionario con parámetros específicos
        self.timestamp = time.time()

    def serialize(self):
        # Convierte el comando a JSON para envío por red
        pass

    def execute(self, game_state):
        # Ejecuta el comando en el GameState
        pass
```

#### Estado de Juego (Game State)
```python
class GameState:
    def __init__(self):
        self.phase = 'LOBBY'  # 'LOBBY', 'OFFENSE_PLANNING', 'DEFENSE_PLANNING', 'BATTLE'
        self.current_wave = 0
        self.players = {
            'player1': PlayerState(),
            'player2': PlayerState()
        }
        self.config = MatchConfig()

class PlayerState:
    def __init__(self):
        self.base_hp = 100
        self.money = 500
        self.towers = []
        self.route = Route([], 'linear')
        self.researched_methods = ['linear']  # Métodos de interpolación desbloqueados
```

---

## 4. Dirección de Arte y Prompts (Nano Banana Pro)

**Estilo General:**
El estilo debe ser consistente. Buscamos un **"Isometric Mathematical Voxel"**. Una mezcla de estilo videojuego *low-poly* tierno, pero situado sobre un papel milimetrado brillante o una cuadrícula de neón tipo TRON pero académica.

> **Nota para el uso de Prompts:** Asegúrate de configurar Nano Banana Pro en un ratio cuadrado (1:1) o landscape (16:9) según necesites para sprites o fondos.

### 4.1. Escenario (El Campo de Batalla)
Necesitamos un fondo que parezca un cuaderno de matemáticas avanzado o una simulación por computadora.

*   **Prompt Escenario:**
    > isometric view of a tower defense game map, grid based floor looking like glowing blue graph paper, dark background, technological academic aesthetic, neon grid lines, digital math visualization style, 3d render, low poly, clean minimal design, unreal engine 5 style --ar 16:9

### 4.2. Las Torres (Los Profesores)
Deben verse como caricaturas estilizadas isométricas.

*   **Prompt Torre Tanque (El Decano):**
    > isometric game sprite of a sturdy university dean character, holding a heavy shield made of books, wearing a formal suit and thick glasses, standing on a hexagonal techno base, low poly 3d render, cute but serious, magical academic aura, blue and gold colors, white background --no shadow

*   **Prompt Torre Ranged (Prof. Cálculo):**
    > isometric game sprite of a skinny math professor, holding a gigantic chalk as a spear, messy white hair, wearing a lab coat filled with equations, standing on a hexagonal techno base, action pose, low poly 3d render, stylized graphics, neon green accents, white background --no shadow

*   **Prompt Torre Cañón (Prof. Física):**
    > isometric game sprite of a physics professor next to a large mechanical cannon made of telescopes and brass parts, steampunk academic vibe, wearing goggles, standing on a hexagonal techno base, low poly 3d render, orange and metallic colors, white background --no shadow

*   **Prompt Torre Support (Prof. Estadística):**
    > isometric game sprite of a mysterious professor holding a glowing crystal ball with data charts floating around, wearing purple robes, standing on a hexagonal techno base, magical aura, low poly 3d render, mystic academic vibe, white background --no shadow

### 4.3. Los Enemigos (La Horda)
Deben parecer estudiantes, becarios o "números" personificados.

*   **Prompt Enemigo Básico (El Estudiante):**
    > isometric game sprite of a generic university student carrying a heavy backpack, running animation pose, low poly 3d render, glowing red eyes indicating enemy status, stylized character, clean colors, white background --no shadow

*   **Prompt Enemigo Rápido (La Variable X):**
    > isometric game sprite of a glowing letter X with legs and arms, running very fast, mathematical abstract character, neon glitch aesthetic, low poly 3d render, aggressive pose, white background --no shadow

### 4.4. UI (Interfaz de Usuario)
Iconos para los botones de interpolación.

*   **Prompt Iconos de UI:**
    > set of game ui icons for a math game: 1) a linear graph icon, 2) a smooth curvy wave graph icon, 3) a chaotic oscillating graph icon, 4) a pencil adding a point to a line. Vector style, flat design, glowing neon blue lines on dark square background, minimalist user interface assets.

---

## 5. Hoja de Ruta para los Agentes de IA

Si estás utilizando un entorno de agentes (como AutoGPT, BabyAGI, o ChatDev), dales estas instrucciones secuenciales, siguiendo los principios **SOLID**:

### Principios de Desarrollo:
*   **Single Responsibility:** Cada clase debe tener una única responsabilidad clara.
*   **Open/Closed:** Las clases deben estar abiertas para extensión pero cerradas para modificación.
*   **Liskov Substitution:** Las subclases deben poder sustituir a sus clases base.
*   **Interface Segregation:** Preferir interfaces específicas a interfaces generales.
*   **Dependency Inversion:** Depender de abstracciones, no de implementaciones concretas.

### Secuencia de Implementación:
1.  **Agente de Arquitectura (Cliente-Servidor):** 
    *   "Implementa `GameServer` y `GameClient` usando sockets TCP."
    *   "Implementa el patrón Command para encapsular acciones de juego (GameCommand)."
    *   "Separa GameState en Local y Remoto para optimizar red."
    *   "Agrega Unit Tests para serialización de comandos."

2.  **Agente de Estado de Juego (State Pattern):**
    *   "Implementa una máquina de estados: `LobbyState`, `OffensePlanningState`, `DefensePlanningState`, `BattleState`."
    *   "Cada estado debe validar las transiciones y las acciones permitidas."
    *   "Agrega Unit Tests para transiciones de estado."

3.  **Agente Matemático (Strategy Pattern):**
    *   "Crea `InterpolationStrategy` como interfaz."
    *   "Implementa `LinearStrategy`, `LagrangeStrategy`, `SplineStrategy`."
    *   "El método de interpolación debe ser seleccionable dinámicamente según lo desbloqueado en I+D."
    *   "Agrega Unit Tests para cada estrategia de interpolación."

4.  **Agente de Economía (Factory Pattern):**
    *   "Implementa `EnemyFactory` para crear mercenarios dinámicamente."
    *   "Implementa `ResearchManager` para gestionar desbloqueos de I+D."
    *   "Agrega Unit Tests para creación de enemigos y validación de investigaciones."

5.  **Agente de UI/UX:**
    *   "Crea el Lobby con selección de configuración de partida."
    *   "Implementa el motor de pantalla dividida (dual viewport)."
    *   "Agrega `InputHandler` con contexto (¿toco mi mapa o el rival?)."
    *   "Implementa el sistema de Autotiling para el camino."

6.  **Agente Visual (Asset Management):**
    *   "Implementa `AssetManager` avanzado con carga asíncrona."
    *   "Crea sistema de Autotiling con lógica de conexión de tiles."
    *   "Integra sprites de torres, enemigos y proyectiles."

7.  **Agente de Integración:**
    *   "Une la red, el estado de juego y la UI."
    *   "Implementa el flujo completo: Lobby → Offense → Defense → Battle."
    *   "Agrega Integration Tests para el flujo completo de una partida."

### Testing:
*   **Unit Tests:** Cada módulo debe tener tests unitarios (pytest).
*   **Integration Tests:** Tests de flujo completo end-to-end.
*   **Coverage:** Mínimo 70% de cobertura de código.