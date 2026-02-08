import random
import math


class DiceEngine:
    """
    Motor genérico de rolagens de dados.
    Centraliza a aleatoriedade do sistema.
    Baseado no seu antigo 'dice_roller.py'.
    """

    @staticmethod
    def roll_XdY(qtd_dados, lados):
        """Rola X dados de Y lados e retorna a lista de resultados."""
        return [random.randint(1, lados) for _ in range(qtd_dados)]

    @staticmethod
    def roll_XdY_drop_lowest(qtd_dados, lados, drop_n=1):
        """Rola X dados, remove os N menores."""
        rolls = sorted(DiceEngine.roll_XdY(qtd_dados, lados))
        return rolls[drop_n:]

    @staticmethod
    def roll_XdY_explode(qtd_dados, lados, threshold):
        """Rola X dados, explodindo resultados >= threshold."""
        results = DiceEngine.roll_XdY(qtd_dados, lados)
        final_sum = sum(results)

        # Lógica recursiva de explosão (simplificada para soma)
        if results and results[0] >= threshold:
            # Nota: A lógica original explodia apenas o primeiro dado ou todos?
            # Assumindo comportamento recursivo padrão de explosão
            final_sum += DiceEngine.roll_XdY_explode(qtd_dados, lados, threshold)

        return final_sum


class CombatMechanics:
    """
    Regras específicas de combate do Synergia RPG.
    Baseado no 'simulador_rolagem1.5.py'.
    """

    ARMOR_TIERS = ['b', 'p', 'm', 's']  # Blindada, Pesada, Média, Sem

    @staticmethod
    def degrade_armor(current_armor):
        """Regra de degradação de armadura: b->p->m->s->s"""
        mapping = {'b': 'p', 'p': 'm', 'm': 's', 's': 's'}
        return mapping.get(current_armor, 's')

    @staticmethod
    def resolve_attack(num_dice, die_sides, adv_state, is_vicious, bonus_damage, armor_type, crit_rule):
        """
        Executa uma rodada de ataque completa e retorna um dicionário com os resultados.
        Retorna dados estruturados, não texto formatado (melhor para Web e Análise).
        """
        logs = []
        current_armor = armor_type
        current_adv = adv_state

        # 1. Ajuste inicial de armadura
        if current_armor == 'b':
            current_adv -= 1
            logs.append("Armadura 'b' aplicou Desvantagem.")

        # 2. Rolagem Primária
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

        # Checagem de Falha Crítica
        if final_primary_val == 1:
            return {
                "damage": 0,
                "status": "Miss",
                "logs": logs,
                "rolls": primary_rolls
            }

        # 3. Dano dos dados secundários
        secondary_damage = 0
        secondary_rolls = []
        if num_dice > 1:
            secondary_rolls = DiceEngine.roll_XdY(num_dice - 1, die_sides)
            secondary_damage = sum(secondary_rolls)

        total_dice_damage = final_primary_val + secondary_damage

        # 4. Tratar Críticos
        is_crit = (final_primary_val == die_sides)
        status = "Hit"

        if is_crit:
            if crit_rule == 'e':  # Épico
                status = "Crit (Épico)"
                current_armor = 's'  # Ignora armadura
            elif crit_rule == 't':  # Tático
                status = "Crit (Tático)"
                current_armor = CombatMechanics.degrade_armor(current_armor)

            # Vicious
            if is_vicious:
                vicious_val = random.randint(1, die_sides)
                total_dice_damage += vicious_val
                logs.append(f"Vicious +{vicious_val}")

            # Explosão
            current_explode_val = final_primary_val
            while current_explode_val == die_sides:
                explode_val = random.randint(1, die_sides)
                total_dice_damage += explode_val
                logs.append(f"Explosão +{explode_val}")
                current_explode_val = explode_val

                # Explosão degrada armadura no Tático
                if crit_rule == 't' and current_explode_val == die_sides:
                    current_armor = CombatMechanics.degrade_armor(current_armor)

        # 5. Cálculo Final com Redução de Dano
        final_damage = total_dice_damage + bonus_damage

        # Regras de Redução por Armadura
        # b e p anulam bônus fixo? (Baseado no seu script original)
        if current_armor in ['p', 'b']:
            final_damage -= bonus_damage  # Remove o bônus que foi somado antes

        if current_armor in ['m', 'p', 'b']:
            final_damage = math.floor(final_damage / 2)
            logs.append(f"Dano reduzido pela metade (Armadura {current_armor})")

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
    Regras de construção e custo de poderes.
    Baseado no 'balancete_magico.py'.
    """

    MAX_PC_BUDGET = 60  # Constante do sistema

    @staticmethod
    def calculate_cost(qtd_dados, tipo_dado, alcance, area):
        """
        Calcula o custo em Pontos de Criação (PC) de uma habilidade.
        Fórmula: (X*Y)/2 + Alcance/2 + Área
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
        """Retorna a média estatística de dano (sem contar críticos/erros)."""
        return qtd_dados * ((tipo_dado + 1) / 2)