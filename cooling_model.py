"""Physics model for hot drink cooling predictions."""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import List, Optional

from drink_data import CupProfile, SIMULATION_MINUTES


@dataclass
class CoolingPoint:
    """A single point in the simulated cooling curve."""

    minute: float
    temperature: float
    state: str


@dataclass
class PredictionResult:
    """Milestones and curve data produced by the cooling model."""

    points: List[CoolingPoint]
    too_hot_until: Optional[float]
    drinkable_from: Optional[float]
    drinkable_until: Optional[float]
    cold_from: Optional[float]
    peak_recommendation: Optional[float]


class CoolingModel:
    """Newton cooling model: T(t) = room + (initial - room) * e^(-kt)."""

    def __init__(self, initial_temp: float, room_temp: float, cup: CupProfile):
        self.initial_temp = initial_temp
        self.room_temp = room_temp
        self.cup = cup

    def temperature_at(self, minute: float) -> float:
        return self.room_temp + (self.initial_temp - self.room_temp) * math.exp(
            -self.cup.cooling_rate * minute
        )

    def time_to_temperature(self, target_temp: float) -> Optional[float]:
        """Return minutes until the drink cools down to target_temp."""

        if self.initial_temp == target_temp:
            return 0.0
        if self.initial_temp < target_temp:
            return None
        if target_temp <= self.room_temp:
            return None

        ratio = (target_temp - self.room_temp) / (self.initial_temp - self.room_temp)
        if ratio <= 0 or ratio >= 1:
            return None

        return -math.log(ratio) / self.cup.cooling_rate

    def classify(
        self,
        temperature: float,
        hot_limit: float,
        good_high: float,
        good_low: float,
        cold_limit: float,
    ) -> str:
        if temperature > hot_limit:
            return "Too hot"
        if good_low <= temperature <= good_high:
            return "Ready to drink"
        if temperature < cold_limit:
            return "Cool"
        if temperature > good_high:
            return "Still hot"
        return "Warm"

    def predict(
        self,
        hot_limit: float,
        good_high: float,
        good_low: float,
        cold_limit: float,
        duration: int = SIMULATION_MINUTES,
    ) -> PredictionResult:
        points: List[CoolingPoint] = []
        for minute in range(duration + 1):
            temperature = self.temperature_at(minute)
            points.append(
                CoolingPoint(
                    minute,
                    temperature,
                    self.classify(
                        temperature,
                        hot_limit,
                        good_high,
                        good_low,
                        cold_limit,
                    ),
                )
            )

        too_hot_until = (
            0.0 if self.initial_temp <= hot_limit else self.time_to_temperature(hot_limit)
        )

        if self.initial_temp < good_low:
            drinkable_from = None
            drinkable_until = 0.0
        elif self.initial_temp <= good_high:
            drinkable_from = 0.0
            drinkable_until = self.time_to_temperature(good_low)
        else:
            drinkable_from = self.time_to_temperature(good_high)
            drinkable_until = self.time_to_temperature(good_low)

        cold_from = (
            0.0 if self.initial_temp <= cold_limit else self.time_to_temperature(cold_limit)
        )

        target_best = (good_high + good_low) / 2
        if self.initial_temp < good_low:
            peak_recommendation = None
        elif self.initial_temp <= target_best:
            peak_recommendation = 0.0
        else:
            peak_recommendation = self.time_to_temperature(target_best)

        return PredictionResult(
            points=points,
            too_hot_until=too_hot_until,
            drinkable_from=drinkable_from,
            drinkable_until=drinkable_until,
            cold_from=cold_from,
            peak_recommendation=peak_recommendation,
        )
