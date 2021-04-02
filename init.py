import os


DIRNAME = os.path.dirname(os.path.abspath(__name__))
fonts_folder = os.path.join(DIRNAME, 'static', 'fonts')

data_folder = os.path.join(DIRNAME, 'data')
tai_lieu_folder = os.path.join(data_folder, 'tai_lieu')
config_path = os.path.join(data_folder, "email_config.json")


for f in [data_folder, tai_lieu_folder]:
    if not os.path.exists(f):
        os.mkdir(f)
