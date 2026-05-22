from pathlib import Path
import unittest

from cooling_model import CoolingModel
from drink_data import (
    CUP_PROFILES,
    DEFAULT_COLD_LIMIT,
    DEFAULT_GOOD_HIGH,
    DEFAULT_GOOD_LOW,
    DEFAULT_HOT_LIMIT,
    DRINK_PROFILES,
)
from settings_store import load_settings, save_settings


class CoolingModelTests(unittest.TestCase):
    def setUp(self):
        self.model = CoolingModel(88, 22, CUP_PROFILES["Ceramic mug"])

    def test_temperature_decreases_over_time(self):
        self.assertGreater(self.model.temperature_at(0), self.model.temperature_at(10))
        self.assertGreater(self.model.temperature_at(10), self.model.temperature_at(30))

    def test_time_to_temperature_matches_target(self):
        minute = self.model.time_to_temperature(60)
        self.assertIsNotNone(minute)
        self.assertAlmostEqual(self.model.temperature_at(minute), 60, places=6)

    def test_prediction_milestones_are_ordered(self):
        result = self.model.predict(
            DEFAULT_HOT_LIMIT,
            DEFAULT_GOOD_HIGH,
            DEFAULT_GOOD_LOW,
            DEFAULT_COLD_LIMIT,
        )
        self.assertLess(result.too_hot_until, result.drinkable_from)
        self.assertLess(result.drinkable_from, result.peak_recommendation)
        self.assertLess(result.peak_recommendation, result.drinkable_until)
        self.assertLess(result.drinkable_until, result.cold_from)

    def test_already_too_cool_never_enters_drinkable_window(self):
        cool_model = CoolingModel(45, 22, CUP_PROFILES["Ceramic mug"])
        result = cool_model.predict(
            DEFAULT_HOT_LIMIT,
            DEFAULT_GOOD_HIGH,
            DEFAULT_GOOD_LOW,
            DEFAULT_COLD_LIMIT,
        )
        self.assertIsNone(result.drinkable_from)
        self.assertIsNone(result.peak_recommendation)

    def test_common_drink_profiles_are_available(self):
        expected_drinks = {
            "Black coffee",
            "Americano",
            "Latte / Cappuccino",
            "Milk tea",
            "Black tea",
            "Green tea",
            "Herbal tea",
            "Hot chocolate",
            "Matcha latte",
            "Chai latte",
            "Hot water / lemon water",
            "Custom hot drink",
        }
        self.assertTrue(expected_drinks.issubset(DRINK_PROFILES))
        for drink in DRINK_PROFILES.values():
            self.assertGreaterEqual(drink.suggested_temp, 30)
            self.assertLessEqual(drink.suggested_temp, 100)

    def test_settings_can_be_saved_and_loaded(self):
        path = Path("test_saved_settings.json")
        settings = {
            "drink_type": "Milk tea",
            "cup_type": "Paper cup",
            "initial_temp": "82",
            "room_temp": "22",
            "hot_limit": 65,
        }

        try:
            save_settings(settings, path)
            self.assertEqual(load_settings(path), settings)
        finally:
            if path.exists():
                path.unlink()


if __name__ == "__main__":
    unittest.main()
