import orjson
import os


def get_user_list(config, key):
    with open("{}/Emilia/{}".format(os.getcwd(), config), "rb") as json_file:
        return orjson.loads(json_file.read())[key]


class Config(object):
    API_HASH = os.getenv("API_HASH")
    API_ID = int(os.getenv("API_ID"))

    TOKEN = os.getenv("TOKEN")
    BOT_ID = int(TOKEN.split(":")[0]) if ":" in TOKEN else 521
    BOT_USERNAME = os.getenv("BOT_USERNAME")

    MONGO_DB_URL = os.getenv("MONGO_DB_URL")
    

    SUPPORT_CHAT = os.getenv("SUPPORT_CHAT")
    UPDATE_CHANNEL = os.getenv("UPDATE_CHANNEL")
    
    START_PIC = "https://pic-bstarstatic.akamaized.net/ugc/9e98b6c8872450f3e8b19e0d0aca02deff02981f.jpg@1200w_630h_1e_1c_1f.webp"
    DEV_USERS = [7028236763]
    CLONE_LIMIT = 50

    REDIS_URL = os.getenv("REDIS_URL")
    REDIS_PASSWORD = os.getenv("REDIS_PASSWORD")

    EVENT_LOGS = int(os.getenv("EVENT_LOGS"))
    OWNER_ID = int(os.getenv("OWNER_ID"))

    TEMP_DOWNLOAD_DIRECTORY = "./"
    BOT_NAME = os.getenv("BOT_NAME")
    WALL_API = "6950f53"
    GROQ_API_KEY = "gsk_mm"


class Production(Config):
    LOGGER = True


class Development(Config):
    LOGGER = True
