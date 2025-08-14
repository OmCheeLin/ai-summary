import alibabacloud_oss_v2 as oss
import yaml
from alibabacloud_oss_v2.client import Client

_config = None # 全局变量


def get_yaml_config():
    global _config
    if _config is None:
        with open(r'D:\python_workspace\tecent\config\config.yaml', 'r') as file:
            _config = yaml.safe_load(file)
    return _config


def get_oss_client() -> Client:
    config = get_yaml_config()
    access_key_id = config['oss']['access_key_id']
    access_key_secret = config['oss']['access_key_secret']
    region = config['oss']['region']
    # access_key_id = "LTAI5tS92gY8yFWMKprJBtQ2"
    # access_key_secret = "qU9Zej2e1XmSb7tdbhfBNhd48XENkp"

    cfg = oss.config.load_default()
    cfg.credentials_provider = oss.credentials.StaticCredentialsProvider(access_key_id, access_key_secret)
    cfg.region = region
    return oss.Client(cfg)


def get_llm_api_key() -> str:
    config = get_yaml_config()
    return config['llm']['api_key']