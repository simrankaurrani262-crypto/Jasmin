import orjson
import os


def get_user_list(config, key):
    with open("{}/Emilia/{}".format(os.getcwd(), config), "rb") as json_file:
        return orjson.loads(json_file.read())[key]


class Config(object):
    API_HASH = "79b81186aefef9ca9216c646152ffe45"
    API_ID =32772113

    BOT_ID = int(TOKEN.split(":")[0]) if ":" in TOKEN else 521
    BOT_USERNAME = "Miss_JasminBot"

    MONGO_DB_URL = "mongodb+srv://rj5706603:O95nvJYxapyDHfkw@cluster0.fzmckei.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"

    SUPPORT_CHAT = "APNA_WORLD1"
    UPDATE_CHANNEL = "lolspot"
    START_PIC = "https://pic-bstarstatic.akamaized.net/ugc/9e98b6c8872450f3e8b19e0d0aca02deff02981f.jpg@1200w_630h_1e_1c_1f.webp"
    DEV_USERS = [7028236763]
    TOKEN = "8317830358:AAH_fcUdH1g8DpgwaRh3IoKpjiVEMUnc3Cw"
    CLONE_LIMIT = 50

    REDIS_URL = os.getenv("REDIS_URL", "rediss://default:AVJQAAIjcDEwNTYxNjg0MzQyNWI0YzQ2OWM1NjI4MTNhMjEzZWY0MXAxMA@fine-flounder-25319.upstash.io:6379")
    REDIS_PASSWORD = os.getenv("REDIS_PASSWORD", "AVJQAAIjcDEwNTYxNjg0MzQyNWI0YzQ2OWM1NjI4MTNhMjEzZWY0MXAxMA")

    EVENT_LOGS = -1003877180460
    OWNER_ID = 7028236763

    TEMP_DOWNLOAD_DIRECTORY = "./"
    BOT_NAME = "Jasmin"
    WALL_API = "6950f53"
    GROQ_API_KEY = "gsk_mm"


class Production(Config):
    LOGGER = True


class Development(Config):
    LOGGER = True
