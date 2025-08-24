import yaml, os

CFG = "config/anthro.yml"

def load_anthro():
    if not os.path.exists(CFG):
        return None
    with open(CFG, "r") as f:
        return yaml.safe_load(f)
