"""
Lore and descriptions for PathWars entities.

Contains the narrative and thematic descriptions for all towers and enemies
in the game, following the academic/university theme.
"""

from typing import Dict
from entities.tower import TowerType
from entities.enemy import EnemyType


# Display names for towers
TOWER_NAMES: Dict[TowerType, str] = {
    TowerType.DEAN: "El Decano",
    TowerType.CALCULUS: "Prof. de Clase Práctica (Numérica)",
    TowerType.PHYSICS: "Prof. de Discreta",
    TowerType.STATISTICS: "Prof. de Conferencia (Numérica)",
}

# Lore text for towers
TOWER_LORE: Dict[TowerType, str] = {
    TowerType.DEAN: (
        "Guardián del conocimiento y la disciplina. Sus años de experiencia "
        "le otorgan una resistencia inquebrantable. Ningún estudiante rebelde "
        "pasa sin ser amonestado."
    ),
    TowerType.CALCULUS: (
        "Maestro de las derivadas e integrales. Sus ataques rápidos y precisos "
        "como el método de Newton-Raphson convergen hacia la destrucción del enemigo."
    ),
    TowerType.PHYSICS: (
        "Experto en combinatoria y teoría de grafos. Sus explosivos contraejemplos "
        "afectan a múltiples enemigos simultáneamente. La fuerza bruta tiene su encanto."
    ),
    TowerType.STATISTICS: (
        "Domina la interpolación y los mínimos cuadrados. No causa daño directo, "
        "pero sus extensas conferencias ralentizan a cualquier estudiante que ose distraerse."
    ),
}

# Display names for enemies
ENEMY_NAMES: Dict[EnemyType, str] = {
    EnemyType.STUDENT: "Estudiante de Primer Año",
    EnemyType.VARIABLE_X: "Variable X",
}

# Lore text for enemies
ENEMY_LORE: Dict[EnemyType, str] = {
    EnemyType.STUDENT: (
        "Recién llegado a la facultad, avanza con determinación pero sin experiencia. "
        "Fácil de detener, pero nunca subestimes su número."
    ),
    EnemyType.VARIABLE_X: (
        "Una incógnita que se mueve con velocidad impredecible. Ligera pero escurridiza, "
        "representa todo lo que no entiendes en un examen."
    ),
}


def get_tower_display_name(tower_type: TowerType) -> str:
    """
    Get the display name for a tower type.
    
    Args:
        tower_type: The tower type.
        
    Returns:
        The display name string.
    """
    return TOWER_NAMES.get(tower_type, tower_type.name)


def get_tower_lore(tower_type: TowerType) -> str:
    """
    Get the lore text for a tower type.
    
    Args:
        tower_type: The tower type.
        
    Returns:
        The lore text string.
    """
    return TOWER_LORE.get(tower_type, "")


def get_enemy_display_name(enemy_type: EnemyType) -> str:
    """
    Get the display name for an enemy type.
    
    Args:
        enemy_type: The enemy type.
        
    Returns:
        The display name string.
    """
    return ENEMY_NAMES.get(enemy_type, enemy_type.name)


def get_enemy_lore(enemy_type: EnemyType) -> str:
    """
    Get the lore text for an enemy type.
    
    Args:
        enemy_type: The enemy type.
        
    Returns:
        The lore text string.
    """
    return ENEMY_LORE.get(enemy_type, "")
