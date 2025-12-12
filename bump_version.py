def bump_version():
    try:
        with open("version.txt", "r") as f:
            v_str = f.read().strip()
            v = float(v_str)
    except (FileNotFoundError, ValueError):
        v = 1.00
    
    new_v = v + 0.01
    new_v_str = f"{new_v:.2f}"
    
    with open("version.txt", "w") as f:
        f.write(new_v_str)
    
    print(f"Bumped version from {v} to {new_v_str}")

if __name__ == "__main__":
    bump_version()
