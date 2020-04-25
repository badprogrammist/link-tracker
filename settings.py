from environs import Env

_env = Env()
_env.read_env()

LOG_LEVEL = _env.log_level("LOG_LEVEL", default="INFO")

REDIS_HOST = _env.str("REDIS_HOST", default=None)
REDIS_PORT = _env.int("REDIS_PORT", default=6379)
REDIS_USER = _env.str("REDIS_USER", default=None)
REDIS_PASSWORD = _env.str("REDIS_PASSWORD", default=None)
