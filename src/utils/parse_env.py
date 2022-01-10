import yaml


def parse_env():
    with open("env.yml") as file:
        json_env = yaml.safe_load(file)
    return json_env
