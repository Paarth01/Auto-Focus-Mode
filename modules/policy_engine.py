import yaml

def load_policy(config_path='config.yaml'):
    with open(config_path) as f:
        return yaml.safe_load(f)

def check_app_category(app_name, config):
    if app_name in config['productive_apps']:
        return 'productive'
    elif app_name in config['distracting_apps']:
        return 'distracting'
    return 'neutral'
