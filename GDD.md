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

El juego consta de 5 Hordas. Cada Horda tiene dos fases:

#### **Fase A: Planificación Matemática (Interpolación)**
Antes de que los enemigos salgan, el jugador diseña la **Ruta de Ataque** que seguirán sus "minions" en el campo rival.
*   **Input:** El jugador tiene un conjunto de puntos de control (Nodos) en un plano cartesiano.
*   **Herramientas de Interpolación (Mejoras):**
    1.  **Añadir Nodos:** Gastar recursos para agregar puntos intermedios ($P_x, P_y$) para esquivar zonas donde el rival puso torres.
    2.  **Cambiar Método:**
        *   *Lineal:* Ruta por defecto, predecible.
        *   *Polinomio de Lagrange:* Suave pero con "fenómeno de Runge" (oscilaciones fuertes en los bordes). Puede ser rápido pero arriesgado.
        *   *Spline Cúbico:* La ruta más suave y segura.
    3.  **Ajuste de Derivadas (Tangentes):** Modificar la pendiente en un punto para "acelerar" la curva o hacer giros cerrados (inspirado en curvas de Hermite/Bézier).

#### **Fase B: Batalla (Tiempo Real)**
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

## 3. Arquitectura Técnica (Para los Agentes de IA)

### 3.1. Stack Tecnológico
*   **Lenguaje:** Python 3.10+
*   **Gráficos:** `pygame` (Sprite handling, game loop).
*   **Matemáticas:** `numpy` (arrays), `scipy.interpolate` (Lagrange, CubicSpline).
*   **Red:** `socket` (librería estándar). Arquitectura Cliente-Servidor o P2P sincronizado.

### 3.2. Lógica de Red (WiFi)
*   **Handshake:** Un jugador actúa como `Host` (Servidor) y el otro como `Client`.
*   **Sincronización:**
    *   Al terminar la *Fase de Planificación*, el Cliente envía un array de coordenadas o los coeficientes del polinomio al Host.
    *   Durante la batalla, se sincronizan solo los estados críticos (HP de base, dinero, creación de torres). No enviar posiciones cada frame, sino calcular determinísticamente en ambos lados usando el mismo `seed` y función de tiempo.

### 3.3. Estructura de Datos de la Ruta
```python
# Ejemplo para el agente de código
class Route:
    def __init__(self, control_points, method='linear'):
        self.points = control_points # Lista de tuplas [(0,0), (5,5), ...]
        self.method = method # 'linear', 'lagrange', 'spline'

    def generate_path(self, resolution=100):
        # Utilizar scipy.interpolate para generar los puntos intermedios
        pass
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

Si estás utilizando un entorno de agentes (como AutoGPT, BabyAGI, o ChatDev), dales estas instrucciones secuenciales:

1.  **Agente de Infraestructura:** "Crea un script en Python `server.py` y `client.py` que establezca una conexión socket TCP y permita enviar objetos serializados (Pickle o JSON) entre dos terminales."
2.  **Agente Matemático:** "Crea un módulo `math_engine.py`. Debe tener funciones que reciban una lista de coordenadas `(x, y)` y devuelvan una lista de 100 puntos interpolados usando `scipy.interpolate.lagrange` y `CubicSpline`."
3.  **Agente de Juego (Core):** "Crea el bucle principal en Pygame. Dibuja una grilla. Implementa la clase `Tower` y la clase `Enemy`. Los enemigos deben moverse actualizando su posición (x,y) basada en la lista generada por el Agente Matemático."
4.  **Agente de Integración:** "Une la red y el juego. Cuando el Jugador 1 termina de editar su curva, envía los datos al Jugador 2. El Jugador 2 recibe los datos y spawnea los enemigos en su pantalla usando esa curva."