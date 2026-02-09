import random
import math


class DiceEngine:
    """
    Generic dice rolling engine.
    Centralizes the system's randomness.
    Based on your old 'dice_roller.py'.
    """

    @staticmethod
    def roll_XdY(qtd_dados, lados):
        """Rolls X dice with Y sides and returns the list of results."""
        return [random.randint(1, lados) for _ in range(qtd_dados)]

    @staticmethod
    def roll_XdY_drop_lowest(qtd_dados, lados, drop_n=1):
        """Rolls X dice, drops the N lowest."""
        rolls = sorted(DiceEngine.roll_XdY(qtd_dados, lados))
        return rolls[drop_n:]

    @staticmethod
    def roll_XdY_explode(qtd_dados, lados, threshold):
        """Rolls X dice, exploding results >= threshold."""
        results = DiceEngine.roll_XdY(qtd_dados, lados)
        final_sum = sum(results)

        # Recursive explosion logic (simplified for sum)
        if results and results[0] >= threshold:
            # Note: Did the original logic explode only the first die or all?
            # Assuming standard recursive explosion behavior
            final_sum += DiceEngine.roll_XdY_explode(qtd_dados, lados, threshold)

        return final_sum


class CombatMechanics:
    """
    Specific combat rules for Synergia RPG.
    Based on 'simulador_rolagem1.5.py'.
    """

    ARMOR_TIERS = ['b', 'p', 'm', 's']  # Armored (Blindada), Heavy (Pesada), Medium (Média), None (Sem)

    @staticmethod
    def degrade_armor(current_armor):
        """Armor degradation rule: b->p->m->s->s"""
        mapping = {'b': 'p', 'p': 'm', 'm': 's', 's': 's'}
        return mapping.get(current_armor, 's')

    @staticmethod
    def resolve_attack(num_dice, die_sides, adv_state, is_vicious, bonus_damage, armor_type, crit_rule):
        """
        Executes a full attack round and returns a dictionary with the results.
        Returns structured data, not formatted text (better for Web and Analysis).
        """
        logs = []
        current_armor = armor_type
        current_adv = adv_state

        # 1. Initial armor adjustment
        if current_armor == 'b':
            current_adv -= 1
            logs.append("Armor 'b' applied Disadvantage.")

        # 2. Primary Roll
        primary_rolls = []
        final_primary_val = 0

        if current_adv == 0:
            val = random.randint(1, die_sides)
            primary_rolls = [val]
            final_primary_val = val
        else:
            qtd = abs(current_adv) + 1
            rolls = [random.randint(1, die_sides) for _ in range(qtd)]
            primary_rolls = rolls
            final_primary_val = max(rolls) if current_adv > 0 else min(rolls)

        # Critical Failure Check
        if final_primary_val == 1:
            return {
                "damage": 0,
                "status": "Miss",
                "logs": logs,
                "rolls": primary_rolls
            }

        # 3. Secondary dice damage
        secondary_damage = 0
        secondary_rolls = []
        if num_dice > 1:
            secondary_rolls = DiceEngine.roll_XdY(num_dice - 1, die_sides)
            secondary_damage = sum(secondary_rolls)

        total_dice_damage = final_primary_val + secondary_damage

        # 4. Handle Crits
        is_crit = (final_primary_val == die_sides)
        status = "Hit"

        if is_crit:
            if crit_rule == 'e':  # Epic
                status = "Crit (Epic)"
                current_armor = 's'  # Ignores armor
            elif crit_rule == 't':  # Tactical
                status = "Crit (Tactical)"
                current_armor = CombatMechanics.degrade_armor(current_armor)

            # Vicious
            if is_vicious:
                vicious_val = random.randint(1, die_sides)
                total_dice_damage += vicious_val
                logs.append(f"Vicious +{vicious_val}")

            # Explosion
            current_explode_val = final_primary_val
            while current_explode_val == die_sides:
                explode_val = random.randint(1, die_sides)
                total_dice_damage += explode_val
                logs.append(f"Explosion +{explode_val}")
                current_explode_val = explode_val

                # Explosion degrades armor in Tactical
                if crit_rule == 't' and current_explode_val == die_sides:
                    current_armor = CombatMechanics.degrade_armor(current_armor)

        # 5. Final Calculation with Damage Reduction
        final_damage = total_dice_damage + bonus_damage

        # Armor Reduction Rules
        # b and p negate fixed bonus? (Based on your original script)
        if current_armor in ['p', 'b']:
            final_damage -= bonus_damage  # Removes the bonus that was added before

        if current_armor in ['m', 'p', 'b']:
            final_damage = math.floor(final_damage / 2)
            logs.append(f"Damage halved (Armor {current_armor})")

        return {
            "damage": final_damage,
            "status": status,
            "final_armor": current_armor,
            "logs": logs,
            "details": {
                "primary": final_primary_val,
                "secondary_sum": secondary_damage
            }
        }


class PowerEconomy:
    """
    Power construction and cost rules.
    Based on 'balancete_magico.py'.
    """

    MAX_PC_BUDGET = 60  # System constant

    @staticmethod
    def calculate_cost(qtd_dados, tipo_dado, alcance, area):
        """
        Calculates the Creation Points (PC) cost of an ability.
        Formula: (X*Y)/2 + Range/2 + Area
        """
        custo_dano = (qtd_dados * tipo_dado) / 2
        custo_alcance = math.ceil(alcance / 2)
        custo_area = area

        total = custo_dano + custo_alcance + custo_area

        return {
            "total_pc": total,
            "custo_dano": custo_dano,
            "custo_alcance": custo_alcance,
            "custo_area": custo_area,
            "is_valid": total <= PowerEconomy.MAX_PC_BUDGET
        }

    @staticmethod
    def estimate_avg_damage(qtd_dados, tipo_dado):
        """Returns the statistical average damage (excluding crits/misses)."""
        return qtd_dados * ((tipo_dado + 1) / 2)