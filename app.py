import os
import yaml
from dotenv import dotenv_values
from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# Allow browser access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["GET"],
    allow_headers=["*"],
)

# ------------------------
# Defaults
# ------------------------
config = {
    "port": 8000,
    "workers": 1,
    "debug": False,
    "log_level": "info",
    "api_key": "default-secret-000",
}

# ------------------------
# YAML
# ------------------------
if os.path.exists("config.development.yaml"):
    with open("config.development.yaml") as f:
        yaml_cfg = yaml.safe_load(f)
        if yaml_cfg:
            config.update(yaml_cfg)

# ------------------------
# .env
# ------------------------
env_cfg = dotenv_values(".env")

if "APP_PORT" in env_cfg:
    config["port"] = int(env_cfg["APP_PORT"])

if "NUM_WORKERS" in env_cfg:
    config["workers"] = int(env_cfg["NUM_WORKERS"])

if "APP_WORKERS" in env_cfg:
    config["workers"] = int(env_cfg["APP_WORKERS"])

if "APP_LOG_LEVEL" in env_cfg:
    config["log_level"] = env_cfg["APP_LOG_LEVEL"]

if "APP_DEBUG" in env_cfg:
    config["debug"] = env_cfg["APP_DEBUG"].lower() in (
        "true",
        "1",
        "yes",
        "on",
    )

if "APP_API_KEY" in env_cfg:
    config["api_key"] = env_cfg["APP_API_KEY"]

# ------------------------
# OS Environment
# ------------------------
if "APP_PORT" in os.environ:
    config["port"] = int(os.environ["APP_PORT"])

if "APP_WORKERS" in os.environ:
    config["workers"] = int(os.environ["APP_WORKERS"])

if "APP_LOG_LEVEL" in os.environ:
    config["log_level"] = os.environ["APP_LOG_LEVEL"]

if "APP_DEBUG" in os.environ:
    config["debug"] = os.environ["APP_DEBUG"].lower() in (
        "true",
        "1",
        "yes",
        "on",
    )

if "APP_API_KEY" in os.environ:
    config["api_key"] = os.environ["APP_API_KEY"]


def convert_bool(v):
    return str(v).lower() in ("true", "1", "yes", "on")


@app.get("/")
def home():
    return {"status": "ok"}


@app.get("/effective-config")
def effective_config(set: list[str] = Query(default=[])):
    cfg = dict(config)

    for item in set:
        if "=" not in item:
            continue

        key, value = item.split("=", 1)

        if key == "port":
            cfg["port"] = int(value)

        elif key == "workers":
            cfg["workers"] = int(value)

        elif key == "debug":
            cfg["debug"] = convert_bool(value)

        else:
            cfg[key] = value

    cfg["api_key"] = "****"

    return cfg
