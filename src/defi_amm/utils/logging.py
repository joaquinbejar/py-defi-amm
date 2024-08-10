import logging
import os

# Set up basic configuration
log_level = os.getenv('LOG_LEVEL', 'DEBUG').upper()
numeric_level = getattr(logging, log_level, logging.INFO)

logging.basicConfig(
    level=numeric_level,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
    handlers=[
        # logging.FileHandler("app.log"), # Uncomment this line to log to a file
        logging.StreamHandler()
    ]
)

# Create logger for the current module
logger = logging.getLogger(__name__)

# Set matplotlib and PIL loggers to a higher level
for module in ['matplotlib', 'PIL']:
    logging.getLogger(module).setLevel(logging.WARNING)

# Optionally, suppress all matplotlib warnings
import warnings
warnings.filterwarnings("ignore", category=UserWarning, module="matplotlib")