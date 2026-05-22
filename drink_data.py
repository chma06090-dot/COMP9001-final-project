"""Shared data and visual constants for Sip Time Cafe."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Tuple


DEFAULT_ROOM_TEMP = 22.0
DEFAULT_DRINK = "Black coffee"
DEFAULT_CUP = "Ceramic mug"
DEFAULT_HOT_LIMIT = 65.0
DEFAULT_GOOD_HIGH = 60.0
DEFAULT_GOOD_LOW = 50.0
DEFAULT_COLD_LIMIT = 40.0
SIMULATION_MINUTES = 180
FONT_FAMILY = "Segoe UI"


@dataclass(frozen=True)
class CupProfile:
    """Cooling properties for a cup type."""

    cooling_rate: float
    note: str


@dataclass(frozen=True)
class DrinkProfile:
    """Default serving information for a hot drink type."""

    suggested_temp: float
    note: str


CUP_PROFILES: Dict[str, CupProfile] = {
    "Ceramic mug": CupProfile(
        0.033,
        "Balanced heat retention for everyday drinks.",
    ),
    "Glass cup": CupProfile(
        0.041,
        "Cools faster because glass transfers heat well.",
    ),
    "Paper cup": CupProfile(
        0.047,
        "Thin walls lose heat quickly.",
    ),
    "Lidded takeaway cup": CupProfile(
        0.026,
        "The lid slows cooling by reducing air flow.",
    ),
    "Insulated tumbler": CupProfile(
        0.012,
        "Strong insulation keeps drinks hot much longer.",
    ),
}


DRINK_PROFILES: Dict[str, DrinkProfile] = {
    "Black coffee": DrinkProfile(
        88,
        "Freshly brewed coffee is usually served very hot.",
    ),
    "Americano": DrinkProfile(
        86,
        "Hot water keeps it close to brewed coffee temperature.",
    ),
    "Latte / Cappuccino": DrinkProfile(
        72,
        "Steamed milk makes it cooler than black coffee.",
    ),
    "Milk tea": DrinkProfile(
        82,
        "A common takeaway drink, hot but softened by milk.",
    ),
    "Black tea": DrinkProfile(
        90,
        "Often brewed with near-boiling water.",
    ),
    "Green tea": DrinkProfile(
        80,
        "Usually brewed below boiling to avoid bitterness.",
    ),
    "Herbal tea": DrinkProfile(
        88,
        "Usually steeped hot, similar to black tea.",
    ),
    "Hot chocolate": DrinkProfile(
        78,
        "Milk and cocoa make it warm and creamy.",
    ),
    "Matcha latte": DrinkProfile(
        75,
        "Milk-based and often served at cafe temperature.",
    ),
    "Chai latte": DrinkProfile(
        78,
        "A spiced milk tea that is hot but not boiling.",
    ),
    "Hot water / lemon water": DrinkProfile(
        90,
        "Usually starts close to kettle temperature.",
    ),
    "Custom hot drink": DrinkProfile(
        85,
        "Use this for any other drink and adjust manually.",
    ),
}


POPULAR_DRINKS: Tuple[Tuple[str, str, str], ...] = (
    ("Black coffee", "Coffee", "#8f6bff"),
    ("Milk tea", "Milk tea", "#ffbd6e"),
    ("Hot chocolate", "Chocolate", "#d9826b"),
    ("Green tea", "Green tea", "#79d3a7"),
)


COLORS = {
    "background": "#f3f0ff",
    "panel": "#fffef8",
    "panel_alt": "#edf8ff",
    "ink": "#3a2f44",
    "muted": "#7d7288",
    "line": "#ddd7f3",
    "slate": "#9b8cff",
    "accent": "#8b7cf6",
    "accent_dark": "#6d5bd6",
    "green": "#7ac7a4",
    "green_dark": "#3e9e78",
    "blue": "#7aa7ff",
    "blue_dark": "#557ed8",
    "red": "#ff7b7b",
    "red_dark": "#d95f5f",
    "ready": "#eaf8ef",
}
