import math
import csv
import time

def validate_all_builds():
    """
    Tests all combinations of Damage, Range, and Area
    to find valid builds within the PC (Creation Points) budget.
    """
    print("Starting validation of all builds...")
    start_time = time.time()

    # --- System Constants ---
    MAX_PC_BUDGET = 60
    MAX_ALCANCE = 20
    MAX_AREA = 36

    # Maximum 'X' dice to test.
    # If (X*4)/2 = 60 (d4 damage), X = 30.
    # Using 30 as a safe ceiling.
    MAX_DICE_X = 30

    DIE_TYPES_Y = [4, 6, 8, 10, 12]  # d4, d6, d8, d10, d12
    # -----------------------------

    valid_builds = []
    total_iterations = 0

    # 4 nested loops to test all combinations
    for y_die in DIE_TYPES_Y:
        for x_dice in range(1, MAX_DICE_X + 1):
            for range_val in range(0, MAX_ALCANCE + 1):
                for area_val in range(0, MAX_AREA + 1):

                    total_iterations += 1

                    # --- Cost Calculation (Your Formulas) ---
                    damage_cost = (x_dice * y_die) / 2
                    range_cost = math.ceil(range_val / 2)
                    area_cost = area_val

                    total_pc_cost = damage_cost + range_cost + area_cost

                    # --- Validation ---
                    if total_pc_cost <= MAX_PC_BUDGET:
                        # Calculates average damage for analysis
                        # Average of 1 die Y = (Y + 1) / 2
                        calculated_avg_damage = x_dice * ((y_die + 1) / 2)

                        build_info = {
                            "Damage_Description": f"{x_dice}d{y_die}",
                            "Range_Blocks": range_val,
                            "Area_Blocks": area_val,
                            "Total_PC_Cost": total_pc_cost,
                            "Avg_Damage": round(calculated_avg_damage, 2),
                            "Damage_Cost": damage_cost,
                            "Range_Cost": range_cost,
                            "Area_Cost": area_cost
                        }
                        valid_builds.append(build_info)

    end_time = time.time()
    print(f"Validation completed in {end_time - start_time:.2f} seconds.")
    print(f"Total of {total_iterations:,} combinations tested.")

    # --- Analysis and Report Generation ---
    if not valid_builds:
        print("No valid build found with the provided parameters.")
        return

    print(f"Total of {len(valid_builds):,} valid builds (<= {MAX_PC_BUDGET} PC) found.")

    # Save to CSV
    output_filename = "power_builds_validation.csv"
    try:
        with open(output_filename, 'w', newline='', encoding='utf-8') as f:
            # Gets keys from first dictionary to use as header
            fieldnames = valid_builds[0].keys()
            writer = csv.DictWriter(f, fieldnames=fieldnames)

            writer.writeheader()
            writer.writerows(valid_builds)

        print(f"\n[SUCCESS] All valid builds were saved in '{output_filename}'")

    except Exception as e:
        print(f"\n[ERROR] Could not save CSV file: {e}")

    # --- Quick Analysis (Insights) ---
    print("\n--- Quick Builds Analysis ---")

    # Find build with highest possible Average Damage (the "Glass Cannon")
    build_max_damage_general = max(valid_builds, key=lambda b: b["Avg_Damage"])
    print(f"🥇 Build with Highest Avg Damage (General):")
    print(f"   {build_max_damage_general['Damage_Description']} (Avg: {build_max_damage_general['Avg_Damage']})")
    print(f"   Range: {build_max_damage_general['Range_Blocks']}, Area: {build_max_damage_general['Area_Blocks']}")
    print(f"   Cost: {build_max_damage_general['Total_PC_Cost']} PC")

    # Find builds that cost exactly 60 PC
    builds_max_level = [b for b in valid_builds if b["Total_PC_Cost"] == MAX_PC_BUDGET]

    if builds_max_level:
        print(f"\nFound {len(builds_max_level)} 'max level' builds (exactly 60 PC).")

        # Find 60 PC build with highest damage
        build_max_damage_60pc = max(builds_max_level, key=lambda b: b["Avg_Damage"])
        print(f"🎯 Highest Damage Build (costing exactly 60 PC):")
        print(f"   {build_max_damage_60pc['Damage_Description']} (Avg: {build_max_damage_60pc['Avg_Damage']})")
        print(f"   Range: {build_max_damage_60pc['Range_Blocks']}, Area: {build_max_damage_60pc['Area_Blocks']}")

        # Find 60 PC build with highest range
        build_max_range_60pc = max(builds_max_level, key=lambda b: b["Range_Blocks"])
        print(f"🔭 Highest Range Build (costing exactly 60 PC):")
        print(f"   {build_max_range_60pc['Damage_Description']} (Avg: {build_max_range_60pc['Avg_Damage']})")
        print(f"   Range: {build_max_range_60pc['Range_Blocks']}, Area: {build_max_range_60pc['Area_Blocks']}")

        # Find 60 PC build with highest area
        build_max_area_60pc = max(builds_max_level, key=lambda b: b["Area_Blocks"])
        print(f"💥 Highest Area Build (costing exactly 60 PC):")
        print(f"   {build_max_area_60pc['Damage_Description']} (Avg: {build_max_area_60pc['Avg_Damage']})")
        print(f"   Range: {build_max_area_60pc['Range_Blocks']}, Area: {build_max_area_60pc['Area_Blocks']}")
    else:
        print("\nNo build found that costs exactly 60 PC.")


# --- To Run the Script ---
if __name__ == "__main__":
    validate_all_builds()