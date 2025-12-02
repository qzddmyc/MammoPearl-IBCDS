import os
import logging
from pathlib import Path
from datetime import datetime


class __LoggerGenerator:
    def __init__(self):
        date_str = datetime.now().strftime("%y%m%d")
        self.log_fileName = f"app.{date_str}.log"
        self.log_dir = os.path.join(".", "logs", "log")
        self.log_file_pth = os.path.join(self.log_dir, self.log_fileName)
        self.ERROR = True  # Init as Error, you should use cls.entity.Initial() to validate it.
        self.logger = None  # Only one instance can be got.

    def Initial(self):
        if os.path.basename(os.getcwd()) == 'src':
            print('You should run this script from the root path of the project.')
            return
        if os.path.exists(self.log_dir) and os.path.exists(self.log_file_pth):
            self.ERROR = False
            return
        model_log_dir = Path("logs/log")
        model_log_dir.mkdir(parents=True, exist_ok=True)
        model_log_file = model_log_dir / self.log_fileName
        model_log_file.touch(exist_ok=True)
        self.ERROR = False

    def generate_logger(self):
        if self.ERROR:
            raise Exception("Error occurred while generating logger.")
        if self.logger:
            return self.logger
        self.logger = logging.getLogger("app")
        self.logger.setLevel(logging.INFO)
        file_handler = None
        if not self.logger.handlers:
            file_handler = logging.FileHandler(self.log_file_pth, mode="a", encoding="utf-8")
            formatter = logging.Formatter(
                fmt="%(asctime)s [%(levelname)s] %(message)s",
                datefmt="%Y-%m-%d %H:%M:%S"
            )
            file_handler.setFormatter(formatter)
            self.logger.addHandler(file_handler)
        return self.logger, file_handler


__L = __LoggerGenerator()
__L.Initial()
Logger, FileHandler = __L.generate_logger()
