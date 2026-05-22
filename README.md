# Best Drinking Temperature Predictor

This Python desktop app predicts how a hot drink cools down over time. The user selects a drink type and cup type, enters or adjusts the starting temperature and room temperature, and the program estimates when the drink is too hot, when it is comfortable to drink, and when it becomes cool.

## Key Features

- Uses Newton's Law of Cooling to model coffee, tea, milk tea, hot chocolate, and other everyday hot drinks.
- Includes a drink type selector with common hot drinks and suggested starting temperatures.
- Supports several cup types: ceramic mug, glass cup, paper cup, lidded takeaway cup, and insulated tumbler.
- Lets users adjust the temperature thresholds for "too hot", "drinkable", and "cool".
- Recalculates from sliders immediately, and from temperature inputs when users press Enter or leave the input field.
- Saves the current setup with the Save button and automatically restores it the next time the app opens.
- Exports prediction data to CSV for presentations or further analysis.
- Demonstrates classes, dataclasses, functions, validation, exception handling, file I/O, and a small unit test suite.

## How to Run

This project only uses the Python standard library, so no third-party packages are required.

```bash
python hot_drink_predictor.py
```

If your computer has multiple Python versions installed, you can also try:

```bash
py hot_drink_predictor.py
```

## Physics Model

The program uses Newton's Law of Cooling:

```text
T(t) = room + (initial - room) * e^(-k*t)
```

Where:

- `T(t)` is the drink temperature after waiting `t` minutes.
- `initial` is the starting temperature.
- `room` is the room temperature.
- `k` is the cup cooling coefficient. A better insulated cup has a smaller `k`.
- Drink type is used to suggest a realistic starting temperature, while cooling speed is controlled by cup type.

The cup cooling coefficients are reasonable approximations for a student project:

| Cup type | Cooling coefficient k / minute | Description |
| --- | ---: | --- |
| Ceramic mug | 0.033 | Balanced heat retention for everyday drinks |
| Glass cup | 0.041 | Cools faster because glass transfers heat well |
| Paper cup | 0.047 | Thin walls lose heat quickly |
| Lidded takeaway cup | 0.026 | Lid reduces evaporation and air flow |
| Insulated tumbler | 0.012 | Strong insulation keeps drinks hot longer |

The drink selector provides suggested starting temperatures that users can still edit:

| Drink type | Suggested starting temperature |
| --- | ---: |
| Black coffee | 88°C |
| Americano | 86°C |
| Latte / Cappuccino | 72°C |
| Milk tea | 82°C |
| Black tea | 90°C |
| Green tea | 80°C |
| Herbal tea | 88°C |
| Hot chocolate | 78°C |
| Matcha latte | 75°C |
| Chai latte | 78°C |
| Hot water / lemon water | 90°C |
| Custom hot drink | 85°C |

## Default Temperature Rules

- Above 65°C: too hot
- 50°C to 60°C: ready to drink
- Below 40°C: cool

These thresholds can be adjusted in the app because different people prefer different drinking temperatures.

## File Structure

```text
.
├── hot_drink_predictor.py   # Main entry point
├── app_ui.py                # Tkinter interface and user interaction
├── cooling_model.py         # Newton cooling model and prediction classes
├── drink_data.py            # Drink/cup profiles, defaults, and theme colors
├── settings_store.py        # Save/load user settings as JSON
├── test_cooling_model.py    # Unit tests for the cooling model
└── README.md                # Project documentation
```

## Running Tests

```bash
python -m unittest test_cooling_model.py
```

## AI Acknowledgement

I acknowledge that artificial intelligence tools were used in this project as learning and support tools. I was responsible for the code and core logic related to the course, including market simulation, product system, customer purchase logic, pricing strategy, upgrades, random events, file handling, and testing.
After I conceived the overall structure and completed the writing of the core logic, I used AI to refine the Python Tkinter interface.

## Link

https://github.com/chma06090-dot/COMP9001-final-project.git