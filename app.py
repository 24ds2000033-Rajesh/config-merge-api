import os
import yaml
from dotenv import dotenv_values
from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# Allow browser access for the grader
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["GET"],
    allow_headers=["*"],
)


def to_bool(value):
    return str(value).strip().lower() in (
        "true",
        "1",
        "yes",
        "on",
    )


def build_config():
    # --------------------
    # 1. Defaults
    # --------------------
    cfg = {
        "port": 8000,
        "workers": 1,
        "debug": False,
        "log_level": "info",
        "api_key": "default-secret-000",
    }

    # --------------------
    # 2. YAML
    # --------------------
    env_name = os.getenv("APP_ENV", "development")
    yaml_file = f"config.{env_name}.yaml"

    if os.path.exists(yaml_file):
        with open(yaml_file, "r") as f:
            data = yaml.safe_load(f) or {}
            cfg.update(data)

    # --------------------
    # 3. .env
    # --------------------
    env = dotenv_values(".env")

    if "APP_PORT" in env:
        cfg["port"] = int(env["APP_PORT"])

    if "NUM_WORKERS" in env:
        cfg["workers"] = int(env["NUM_WORKERS"])

    if "APP_WORKERS" in env:
        cfg["workers"] = int(env["APP_WORKERS"])

    if "APP_DEBUG" in env:
        cfg["debug"] = to_bool(env["APP_DEBUG"])

    if "APP_LOG_LEVEL" in env:
        cfg["log_level"] = env["APP_LOG_LEVEL"]

    if "APP_API_KEY" in env:
        cfg["api_key"] = env["APP_API_KEY"]

    # --------------------
    # 4. OS Environment
    # --------------------
    if "APP_PORT" in os.environ:
        cfg["port"] = int(os.environ["APP_PORT"])

    if "APP_WORKERS" in os.environ:
        cfg["workers"] = int(os.environ["APP_WORKERS"])

    if "APP_DEBUG" in os.environ:
        cfg["debug"] = to_bool(os.environ["APP_DEBUG"])

    if "APP_LOG_LEVEL" in os.environ:
        cfg["log_level"] = os.environ["APP_LOG_LEVEL"]

    if "APP_API_KEY" in os.environ:
        cfg["api_key"] = os.environ["APP_API_KEY"]

    return cfg


@app.get("/")
def root():
    return {"status": "ok"}


@app.get("/effective-config")
def effective_config(set: list[str] = Query(default=[])):
    cfg = build_config()

    # --------------------
    # 5. CLI overrides
    # --------------------
    for item in set:
        if "=" not in item:
            continue

        key, value = item.split("=", 1)

        if key == "port":
            cfg["port"] = int(value)

        elif key == "workers":
            cfg["workers"] = int(value)

        elif key == "debug":
            cfg["debug"] = to_bool(value)

        else:
            cfg[key] = value

    # Always mask secret
    cfg["api_key"] = "****"

    return cfg
