from src.organizations.application import initialize_application
from src.organizations.configuration import Configuration


config = Configuration()
app = initialize_application(config)
