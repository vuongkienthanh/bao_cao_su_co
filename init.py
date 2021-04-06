import os

DIRNAME = os.path.dirname(os.path.abspath(__name__))
fonts_folder = os.path.join(DIRNAME, 'static', 'fonts')

data_folder = os.path.join(DIRNAME, 'data')
tai_lieu_folder = os.path.join(data_folder, 'tai_lieu')
db_path = os.path.join(data_folder, 'bao_cao_su_co.db')