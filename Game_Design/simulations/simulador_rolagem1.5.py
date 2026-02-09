import random
import math
import time
import csv

# Tries to import 'rich'. If it fails, warns the user.
try:
    from rich.console import Console
    from rich.panel import Panel
    from rich.text import Text
    from rich.prompt import Prompt
    from rich.progress import Progress, BarColumn, TextColumn, TimeRemainingColumn
except ImportError:
    print("ERROR: The 'rich' library was not found.")
    print("Please install it using: pip install rich")
    exit()

# --- CONSTANTS ---
DICE_TYPES = [4, 6, 8, 10, 12]  # Standard die types
N_SIMULATIONS_SINGLE = 300000  # Simulations for quick test
N_SIMULATIONS_SCENARIO = 100000  # Simulations per cell in scenario (faster)
EXIT_KEYWORD = 'back'  # Keyword to return to main menu


# --- SIMULATION FUNCTIONS (THE "ENGINE") ---
# (These functions are the same as before, no changes)

def degrade_armor(armor_type):
    if armor_type == 'b': return 'p'
    if armor_type == 'p': return 'm'
    if armor_type == 'm': return 's'
    if armor_type == 's': return 's'
    return 's'


def roll_primary_die(die_sides, adv_state):
    roll_list = []
    if adv_state == 0:
        roll = random.randint(1, die_sides)
        return roll, f"Primary: [{roll}]"
    elif adv_state > 0:
        num_rolls = adv_state + 1
        roll_list = [random.randint(1, die_sides) for _ in range(num_rolls)]
        result = max(roll_list)
        return result, f"Primary (Advantage {num_rolls}d{die_sides}): {roll_list} -> [{result}]"
    elif adv_state < 0:
        num_rolls = abs(adv_state) + 1
        roll_list = [random.randint(1, die_sides) for _ in range(num_rolls)]
        result = min(roll_list)
        return result, f"Primary (Disadvantage {num_rolls}d{die_sides}): {roll_list} -> [{result}]"


def simulate_synergia_roll(num_dice, die_sides, adv_state, is_vicious, bonus_damage, armor_type, crit_rule):
    current_adv_state = adv_state
    current_armor_type = armor_type
    roll_details = []

    if current_armor_type == 'b':
        current_adv_state -= 1
        roll_details.append("Info: Armor 'b' applies Disadvantage.")

    primary_roll, primary_detail = roll_primary_die(die_sides, current_adv_state)
    roll_details.append(primary_detail)

    if primary_roll == 1:
        return 0, roll_details, "Miss"

    total_dice_damage = 0
    if num_dice > 1:
        non_primary_rolls = [random.randint(1, die_sides) for _ in range(num_dice - 1)]
        roll_details.append(f"Secondary: {non_primary_rolls}")
        total_dice_damage += sum(non_primary_rolls)

    total_dice_damage += primary_roll
    is_crit = (primary_roll == die_sides)
    status = "Hit"

    if is_crit:
        if crit_rule == 'e':
            status = "Crit (Epic)"
            roll_details.append("Info: Epic Crit! Armor ignored.")
            current_armor_type = 's'
        elif crit_rule == 't':
            status = "Crit (Tactical)"
            new_armor = degrade_armor(current_armor_type)
            roll_details.append(f"Info: Tactical Crit! Armor {current_armor_type} -> {new_armor}")
            current_armor_type = new_armor

        if is_vicious:
            vicious_roll = random.randint(1, die_sides)
            roll_details.append(f"Vicious Extra: [{vicious_roll}]")
            total_dice_damage += vicious_roll

        current_explosion = primary_roll
        while current_explosion == die_sides:
            explode_roll = random.randint(1, die_sides)
            roll_details.append(f"Explosion: [{explode_roll}]")
            total_dice_damage += explode_roll
            current_explosion = explode_roll

            if crit_rule == 't' and current_explosion == die_sides:
                new_armor = degrade_armor(current_armor_type)
                roll_details.append(f"Info: Critical Explosion! Armor {current_armor_type} -> {new_armor}")
                current_armor_type = new_armor

    final_damage = 0
    bonus_to_add = bonus_damage
    apply_halving = False

    if current_armor_type == 's':
        pass
    elif current_armor_type == 'm':
        apply_halving = True
    elif current_armor_type == 'p':
        bonus_to_add = 0
        apply_halving = True
    elif current_armor_type == 'b':
        bonus_to_add = 0
        apply_halving = True

    final_damage = total_dice_damage + bonus_to_add

    if apply_halving:
        final_damage = math.floor(final_damage / 2)
        roll_details.append(f"Info: Damage Halved (Armor {current_armor_type})")

    return final_damage, roll_details, status


# --- ANALYSIS FUNCTIONS ---

def analyze_roll_config(console, description, num_dice, die_sides, adv_state, is_vicious, bonus_damage, armor_type,
                        crit_rule):
    """
    (SINGLE MODE)
    Executes a full analysis with output formatted by 'rich'.
    """

    console.print(Panel(description, title="[bold cyan]Analyzing Configuration[/bold cyan]", border_style="cyan"))

    # --- Part 1: Theoretical Probability Calculation ---
    Y = die_sides
    prob_miss = 0.0
    prob_crit_first = 0.0

    calc_adv_state = adv_state
    if armor_type == 'b':
        calc_adv_state -= 1

    if calc_adv_state == 0:  # Normal
        prob_miss = 1 / Y
        prob_crit_first = 1 / Y
    elif calc_adv_state > 0:  # Advantage
        num_rolls = calc_adv_state + 1
        prob_miss = (1 / Y) ** num_rolls
        prob_crit_first = 1 - ((Y - 1) / Y) ** num_rolls
    elif calc_adv_state < 0:  # Disadvantage
        num_rolls = abs(calc_adv_state) + 1
        prob_miss = 1 - ((Y - 1) / Y) ** num_rolls
        prob_crit_first = (1 / Y) ** num_rolls

    prob_text = Text()
    prob_text.append(f"Advantage State (Final): {calc_adv_state}\n\n", style="default")
    prob_text.append("Miss Chance (1 on roll): ", style="default")
    prob_text.append(f"{prob_miss * 100:.2f}%\n", style="bold red")
    prob_text.append(f"Crit Chance (Hit {Y}): ", style="bold green")
    prob_text.append(f"{prob_crit_first * 100:.2f}%\n", style="bold green")

    prob_chain = prob_crit_first
    for i in range(2, 6):
        prob_chain *= (1 / Y)
        prob_text.append(f"  {i}th order Crit Chance: ", style="dim")
        prob_text.append(f"{prob_chain * 100:.6f}%\n", style="dim italic")

    console.print(Panel(prob_text, title="[bold green]Theoretical Probabilities[/bold green]", border_style="green",
                        padding=(1, 2)))

    # --- Part 2: Monte Carlo Simulation (WITH SPINNER) ---
    total_damage_sum = 0
    avg_damage = 0
    with console.status(f"[bold yellow]Running {N_SIMULATIONS_SINGLE:,} simulations...", spinner="dots8Bit") as status:
        for _ in range(N_SIMULATIONS_SINGLE):
            damage, _, _ = simulate_synergia_roll(
                num_dice, die_sides, adv_state, is_vicious, bonus_damage, armor_type, crit_rule
            )
            total_damage_sum += damage
        avg_damage = total_damage_sum / N_SIMULATIONS_SINGLE
        time.sleep(0.5)

    sim_text = Text()
    sim_text.append("Effective Average Damage: ", style="default")
    sim_text.append(f"{avg_damage:.3f}", style="bold yellow")

    console.print(
        Panel(sim_text, title="[bold magenta]Damage Simulation[/bold magenta]", border_style="magenta", padding=(1, 2)))

    # --- Part 3: Single Example Roll ---
    ex_dmg, ex_rolls, ex_status = simulate_synergia_roll(
        num_dice, die_sides, adv_state, is_vicious, bonus_damage, armor_type, crit_rule
    )

    status_style = "bold"
    if ex_status == "Miss":
        status_style = "bold red"
    elif "Crit" in ex_status:
        status_style = "bold green"

    example_text = Text()
    example_text.append("Status: ", style="default")
    example_text.append(f"{ex_status}!\n", style=status_style)
    example_text.append("Details: ", style="dim")
    example_text.append(f"{' | '.join(ex_rolls)}\n\n", style="dim")
    example_text.append("Final Damage: ", style="default")
    example_text.append(f"{ex_dmg}", style="bold white")

    console.print(Panel(example_text, title="[bold blue]Single Example Roll[/bold blue]", border_style="blue",
                        padding=(1, 2)))
    console.print("")


def calculate_average_damage(num_dice, die_sides, adv_state, is_vicious, bonus_damage, armor_type, crit_rule):
    """
    (SCENARIO MODE)
    "Silent" function that only calculates and returns average damage.
    """
    total_damage_sum = 0
    for _ in range(N_SIMULATIONS_SCENARIO):
        damage, _, _ = simulate_synergia_roll(
            num_dice, die_sides, adv_state, is_vicious, bonus_damage, armor_type, crit_rule
        )
        total_damage_sum += damage
    return total_damage_sum / N_SIMULATIONS_SCENARIO


# --- MENU AND INPUT VALIDATION FUNCTIONS ---

def parse_roll_input(console, roll_str):
    if roll_str.lower() in ['stop', EXIT_KEYWORD]:
        return EXIT_KEYWORD, EXIT_KEYWORD
    try:
        parts = roll_str.lower().split('d')
        if len(parts) != 2: return None, None
        num_dice = int(parts[0])
        die_sides = int(parts[1])
        if num_dice <= 0 or die_sides not in DICE_TYPES + [20]:  # Allows d20 in single mode
            console.print(f"[prompt.invalid]Die 'd{die_sides}' is not a valid die {DICE_TYPES}.")
            return None, None
        return num_dice, die_sides
    except Exception:
        return None, None


def get_adv_state(console):
    choice = Prompt.ask(
        "[bold cyan]Advantage (v), Disadvantage (d) or Normal (n)?[/]",
        choices=["v", "d", "n", "stop", EXIT_KEYWORD],
        show_choices=False
    )
    if choice in ['stop', EXIT_KEYWORD]: return EXIT_KEYWORD
    adv_state_map = {'v': 1, 'd': -1, 'n': 0}
    return adv_state_map[choice]


def get_yes_no_input(console, prompt):
    choice = Prompt.ask(
        f"[bold cyan]{prompt} (s/n)?[/]",
        choices=["s", "n", "stop", EXIT_KEYWORD],
        show_choices=False
    )
    if choice in ['stop', EXIT_KEYWORD]: return EXIT_KEYWORD
    return (choice == 's')


def get_bonus_input(console):
    while True:
        val = console.input("[bold cyan]What is the fixed damage bonus (e.g., 5, 0)?[/] ")
        if val.lower() in ['stop', EXIT_KEYWORD]: return EXIT_KEYWORD
        try:
            return int(val)
        except ValueError:
            console.print("[prompt.invalid]Invalid input. Please enter an integer.")


def get_validated_input(console, prompt, valid_options):
    choice = Prompt.ask(
        f"[bold cyan]{prompt}[/]",
        choices=valid_options + ["stop", EXIT_KEYWORD],
        show_choices=False
    )
    if choice in ['stop', EXIT_KEYWORD]: return EXIT_KEYWORD
    return choice


def get_max_dice_input(console):
    while True:
        val = console.input("[bold cyan]What is the MAXIMUM number of dice to test (e.g., 10)? [/] ")
        if val.lower() in ['stop', EXIT_KEYWORD]: return EXIT_KEYWORD
        try:
            max_dice = int(val)
            if max_dice > 0 and max_dice <= 50:  # Limit of 50 to avoid long run times
                return max_dice
            else:
                console.print("[prompt.invalid]Please enter a number between 1 and 50.")
        except ValueError:
            console.print("[prompt.invalid]Invalid input. Please enter an integer.")


# --- EXECUTION MODES ---

def run_avulso_mode(console):
    """Runs the loop for individual tests."""

    console.print(Panel(
        f"Single Test Mode\nType '[bold red]{EXIT_KEYWORD}[/bold red]' or '[bold red]stop[/bold red]' at any time to return to main menu.",
        title="[bold]Single Mode[/bold]",
        padding=(1, 2),
        border_style="yellow"
    ))

    while True:
        # 1. Get Roll
        num_dice, die_sides = None, None
        while num_dice is None:
            roll_str = console.input("\n[bold cyan]Enter roll (e.g., 2d6, 1d12):[/] ").strip()
            num_dice, die_sides = parse_roll_input(console, roll_str)
            if num_dice == EXIT_KEYWORD: return  # Returns to main menu
            if num_dice is None:
                console.print("[prompt.invalid]Invalid format. Use 'XdY'.")

        # 2. Get Advantage/Disadvantage (State)
        adv_state = get_adv_state(console)
        if adv_state == EXIT_KEYWORD: return

        # 3. Get Vicious
        is_vicious = get_yes_no_input(console, "Is the attack 'Vicious'?")
        if is_vicious == EXIT_KEYWORD: return

        # 4. Get Bonus
        bonus = get_bonus_input(console)
        if bonus == EXIT_KEYWORD: return

        # 5. Get Armor
        armor_type = get_validated_input(console, "What is the target's armor (s, m, p, b)?", ['s', 'm', 'p', 'b'])
        if armor_type == EXIT_KEYWORD: return

        # 6. Get Crit Rule
        crit_rule = get_validated_input(console, "What is the crit rule (e - epic, t - tactical)?", ['e', 't'])
        if crit_rule == EXIT_KEYWORD: return

        # 7. Assemble description and run analysis
        desc = (
            f"[bold]Roll:[/] {num_dice}d{die_sides} | [bold]Adv. State:[/] {adv_state} | "
            f"[bold]Vicious:[/] {is_vicious} | [bold]Bonus:[/] +{bonus} | "
            f"[bold]Armor:[/] {armor_type.upper()} | [bold]Crit:[/] {crit_rule.upper()}"
        )

        analyze_roll_config(
            console, desc, num_dice, die_sides, adv_state,
            is_vicious, bonus, armor_type, crit_rule
        )

        console.print("--- Next Single Analysis ---", justify="center")


def run_cenario_mode(console):
    """Runs the scenario definition and CSV generation mode."""

    console.print(Panel(
        f"Scenario Definition Mode\n"
        f"You will define a scenario (armor, bonus, etc.) and the program will calculate the average damage for multiple rolls (1dY to XdY).\n"
        f"Type '[bold red]{EXIT_KEYWORD}[/bold red]' or '[bold red]stop[/bold red]' at any time to return to main menu.",
        title="[bold]Scenario Mode[/bold]",
        padding=(1, 2),
        border_style="yellow"
    ))

    # --- Collect Scenario ---
    console.print("\n[bold]--- 1. Define Scenario ---[/bold]")
    adv_state = get_adv_state(console)
    if adv_state == EXIT_KEYWORD: return

    is_vicious = get_yes_no_input(console, "Is the scenario 'Vicious'?")
    if is_vicious == EXIT_KEYWORD: return

    bonus = get_bonus_input(console)
    if bonus == EXIT_KEYWORD: return

    armor_type = get_validated_input(console, "What is the target's armor (s, m, p, b)?", ['s', 'm', 'p', 'b'])
    if armor_type == EXIT_KEYWORD: return

    crit_rule = get_validated_input(console, "What is the crit rule (e - epic, t - tactical)?", ['e', 't'])
    if crit_rule == EXIT_KEYWORD: return

    console.print("\n[bold]--- 2. Define Test Limits ---[/bold]")
    max_dice = get_max_dice_input(console)
    if max_dice == EXIT_KEYWORD: return

    desc_cenario = (
        f"Adv: {adv_state} | Vicious: {is_vicious} | Bonus: +{bonus} | "
        f"Armor: {armor_type.upper()} | Crit: {crit_rule.upper()}"
    )
    console.print(Panel(f"Scenario Defined: {desc_cenario}\nTesting from 1dY to {max_dice}dY.",
                        title="[bold cyan]Summary[/bold cyan]"))

    # --- Process Batch ---
    console.print(f"\n[bold]--- 3. Processing {max_dice * len(DICE_TYPES)} combinations ---[/bold]")

    csv_data = []
    header = ["Dice Count"] + [f"d{y}" for y in DICE_TYPES]
    csv_data.append(header)

    total_steps = max_dice * len(DICE_TYPES)

    # Configura a barra de progresso
    progress_bar = Progress(
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        "[progress.percentage]{task.percentage:>3.0f}%",
        TimeRemainingColumn(),
        console=console
    )

    with progress_bar as progress:
        task = progress.add_task("[green]Calculating Damage...", total=total_steps)

        for i in range(1, max_dice + 1):  # Rows (1d, 2d, ... Xd)
            current_row = [f"{i}d"]
            for y in DICE_TYPES:  # Columns (d4, d6, ...)
                avg_dmg = calculate_average_damage(
                    num_dice=i,
                    die_sides=y,
                    adv_state=adv_state,
                    is_vicious=is_vicious,
                    bonus_damage=bonus,
                    armor_type=armor_type,
                    crit_rule=crit_rule
                )
                current_row.append(f"{avg_dmg:.3f}")
                progress.update(task, advance=1)
            csv_data.append(current_row)

    # --- Salvar o Arquivo CSV ---
    filename = "synergia_cenario_output.csv"
    try:
        with open(filename, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f ,delimiter=';')
            writer.writerows(csv_data)

        console.print(Panel(
            f"[bold green]Sucesso![/bold green]\n"
            f"O cenário foi processado e os resultados foram salvos em:\n"
            f"[bold cyan]{filename}[/bold cyan]",
            title="[bold]Exportação Concluída[/bold]",
            padding=(1, 2)
        ))

    except Exception as e:
        console.print(Panel(
            f"[bold red]Erro ao Salvar o Arquivo![/bold red]\n"
            f"Não foi possível salvar o .csv. Detalhes do erro:\n"
            f"[italic]{e}[/italic]",
            title="[bold]Falha na Exportação[/bold]",
            padding=(1, 2)
        ))

    console.print(f"\n--- Retornando ao Menu Principal ---", justify="center")
    time.sleep(1)  # Pausa para o usuário ler a msg de sucesso/erro
    return  # Retorna ao menu main


# --- FUNÇÃO PRINCIPAL (O MENU) ---

def main():
    """Roda o loop principal do menu (Avulso vs. Cenário)."""
    console = Console()

    welcome_panel = Panel.fit(
        "[bold green]Bem-vindo ao Analisador de Rolagens Synergia (v4)[/bold green]\n"
        "Selecione um modo de operação.",
        title="[bold]Synergia[/bold]",
        padding=(1, 3)
    )
    console.print(welcome_panel)

    while True:
        console.print("\n[bold]--- Menu Principal ---[/bold]")
        choice = Prompt.ask(
            "O que você deseja fazer?\n\n"
            "[bold](A)[/bold]vulsos | [bold](C)[/bold]enário | [bold](S)[/bold]air",
            choices=["a", "c", "s"],
            show_choices=False  # Adicionado para não poluir a tela
        )

        if choice == 'a':
            run_avulso_mode(console)

        elif choice == 'c':
            run_cenario_mode(console)

        elif choice == 's':
            console.print("\n[bold blue]Obrigado por usar o Analisador Synergia! Até mais.[/bold blue]")
            break  # Sai do loop principal e encerra o programa


# --- Ponto de Entrada do Script ---
if __name__ == "__main__":
    main()