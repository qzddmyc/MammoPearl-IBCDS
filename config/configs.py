import os
import yaml

__DOTS = '..' if os.path.basename(os.getcwd()) == 'config' else '.'


# you should not use this func in other py-files use var BASE_CONFIG instead
def __get_base_config():
    config_path = os.path.join(__DOTS, "config", 'config.yaml')
    with open(config_path, "r", encoding="utf-8") as f:
        config = yaml.safe_load(f)
    if config and "COLORS" in config:
        for k, v in config["COLORS"].items():
            config["COLORS"][k] = v.encode().decode("unicode_escape")
    return config


# the same, use var DATABASE_CONFIG instead
def __get_database_config():
    config_path = os.path.join(__DOTS, "config", 'database.yaml')
    with open(config_path, "r", encoding="utf-8") as f:
        config = yaml.safe_load(f)
    return config


# use AI_CONFIG
def __get_ai_config():
    config_path = os.path.join(__DOTS, "config", 'ai.yaml')
    with open(config_path, "r", encoding="utf-8") as f:
        config = yaml.safe_load(f)
    return config


BASE_CONFIG = __get_base_config()
DATABASE_CONFIG = __get_database_config()
AI_CONFIG = __get_ai_config()
