def bump_version():
    filename = "version.txt"
    try:
        with open(filename, "r") as f:
            v_str = f.read().strip()
    except FileNotFoundError:
        v_str = "1.0.0"

    parts = v_str.split(".")
    
    # Handle "1.1" -> "1.1.0" -> "1.1.0" + 0.0.1 logic? 
    # User said: "Versjon skal nå vare 1.1 og nye 0.0.1 opp hver gang etter det"
    # This implies 1.1 -> 1.1.1 -> 1.1.2
    
    # Ensure at least 3 parts for standard semver, or just increment last part?
    # If currently "1.1", we treat it as 1.1.0 implicitly? Or just append .1?
    # "1.1" -> "1.1.1"
    
    if len(parts) < 3:
        # If 1.1, we want next to be 1.1.1
        # So effectively we append a '1' if the patch version is missing, matches logic of "1.1" -> "1.1.1"
        new_parts = parts + ['1']
    else:
        # 1.1.1 -> 1.1.2
        try:
            last_val = int(parts[-1])
            parts[-1] = str(last_val + 1)
            new_parts = parts
        except ValueError:
            # Fallback for non-integer last part
            new_parts = parts + ['1']

    new_v_str = ".".join(new_parts)
    
    with open(filename, "w") as f:
        f.write(new_v_str)
    
    print(f"Bumped version from {v_str} to {new_v_str}")

if __name__ == "__main__":
    bump_version()
