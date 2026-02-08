# Elementari System | Synergia RPG Toolkit

**Elementari** is a hybrid infrastructure designed to develop, simulate, and manage the *Synergia Tabletop RPG*. 

This project demonstrates a **Systems Design** approach to game development: it isolates the logical rules engine (Math/Mechanics) from the implementation layer (Web/CLI), ensuring that the game's mathematical truth remains consistent across statistical simulations and player-facing tools.

## 🎯 Project Goals

* **Validation:** Stress-test combat mechanics (damage curves, armor degradation) using Monte Carlo simulations.
* **Balancing:** Algorithmic validation of the "Power Creation" economy to ensure player builds remain within the target power budget.
* **Tooling:** Provide accessible web interfaces (Django + Vue.js) for players to interact with complex underlying math without friction.

## 📂 Architecture

The project is organized into two main domains sharing a central logic library:

```text
Elementari_System/
├── Game_Design_Lab/           # ANALYTICAL TOOLS
│   ├── libs/                  # Shared Core Engine (The "Truth" Source)
│   │   └── synergia_rules.py  # Centralized combat & economy logic
│   ├── simulations/           # CLI tools for Monte Carlo analysis
│   └── data_exports/          # CSV outputs for spreadsheet analysis
│
├── Web_Portal/                # PLAYER FACING APP
│   ├── manage.py              # Django Entry Point
│   ├── rpg_system/            # Web App Logic
│   └── templates/             # Vue.js + Bootstrap Interfaces
```
⚙️ Core Mechanics (The Engine)
The heart of the system is the synergia_rules library, which handles:

Stochastic Combat Resolution:

Simulates dice pools with "Exploding Dice" and "Vicious" mechanics.

Handles dynamic armor degradation (Barrier -> Heavy -> Medium -> None).

Calculates "Advantage/Disadvantage" probability shifts.

Economy Algorithms:

Validates custom spell creation based on a 60-point budget system.

Formula: Cost = (Dice * Tier)/2 + (Range/2) + Area.

🚀 Getting Started
Prerequisites
Python 3.10+

rich (for terminal visualization)

django

Installation
Bash
# 1. Clone the repository
git clone [https://github.com/PedroMagno-prog/Elementari_System.git](https://github.com/PedroMagno-prog/Elementari_System.git)
cd Elementari_System

# 2. Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows

# 3. Install dependencies
pip install django rich
Usage: Game Design Lab (Simulations)
To run a combat simulation and generate efficiency CSVs:

Bash
cd Game_Design_Lab/simulations
# Run the CLI tool (ensure it imports from ../libs)
python run_simulation.py
Usage: Web Portal
To launch the character creator and rules wiki:

Bash
cd Web_Portal
python manage.py runserver
🛠️ Tech Stack
Language: Python 3 (Core Logic & Scripts)

Backend: Django (MVT Architecture)

Frontend: HTML5, Bootstrap 4, Vue.js

Analysis: Custom Monte Carlo scripts, CSV Exporting, Rich library for CLI visualization.

👤 Author
Pedro Magno Systems Designer & Developer GitHub Profile
