import logging
import os
import replifactory

logging.basicConfig(
    level=os.environ.get("LOGGING_LEVEL", logging.INFO),
)

app = replifactory.create_app()
