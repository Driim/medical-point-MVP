from src.inspections.application import initialize_application
from src.inspections.configuration import Configuration

config = Configuration()
app = initialize_application(config)
