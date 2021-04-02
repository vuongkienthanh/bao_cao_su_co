from init import data_folder, tai_lieu_folder
import datetime as dt
import sqlite3
import shutil
import os
import subprocess
from passlib.hash import bcrypt
import pyheif
from PIL import Image

db_name = os.path.join(data_folder, 'bao_cao_su_co.db')

headers_bcsc = [
    "id", "hinh_thuc", "ngay_bao_cao", "don_vi_bao_cao",
    "ho_ten_nguoi_benh", "so_benh_an", "ngay_sinh", "gioi_tinh",
    "khoa_phong", "doi_tuong", "vi_tri_xay_ra", "vi_tri_cu_the",
    "thoi_gian_xay_ra", "mo_ta", "de_xuat_giai_phap", "xu_ly_ban_dau",
    "thong_bao_cho_bac_si_hoac_nguoi_chiu_trach_nhiem",
    "ghi_nhan_ho_so", "thong_bao_cho_nguoi_nha_hoac_nguoi_bao_ho",
    "thong_bao_cho_nguoi_benh", "phan_loai_ban_dau",
    "danh_gia_ban_dau", "ho_ten_nguoi_bao_cao",
    "so_dien_thoai_nguoi_bao_cao", "email_nguoi_bao_cao",
    "chuc_danh_nguoi_bao_cao",
    "nguoi_chung_kien_1", "nguoi_chung_kien_2"]
headers_users = [
    "username", "hashed_password", "superuser"]
headers_quick_bcsc = [
    "id", "ngay_gio_bao_cao", "doi_tuong", "vi_tri_xay_ra", "lien_quan",
    "mo_ta", "so_benh_an", "xu_ly", "filepaths"]


def dt_to_int(datetime_dt):
    return int(datetime_dt.strftime('%Y%m%d%H%M'))


def int_to_dt(datetime_int):
    return dt.datetime.strptime(str(datetime_int), "%Y%m%d%H%M")


def conn(func):
    def inner(*arg, **kwarg):
        con = sqlite3.connect(db_name)
        cur = con.cursor()
        try:
            result = func(cur, *arg, **kwarg)
            con.commit()
        except sqlite3.Error as e:
            result = None
            con.rollback()
            raise e
        else:
            con.close()
            return result
    return inner


@ conn
def create_db(cur):
    cur.execute('''CREATE TABLE bao_cao_su_co (
        id INTEGER PRIMARY KEY,
        hinh_thuc TEXT NOT NULL,
        ngay_bao_cao TEXT NOT NULL,
        don_vi_bao_cao TEXT NOT NULL,
        ho_ten_nguoi_benh TEXT NOT NULL,
        so_benh_an TEXT NOT NULL,
        ngay_sinh TEXT NOT NULL,
        gioi_tinh TEXT NOT NULL,
        khoa_phong TEXT NOT NULL,
        doi_tuong TEXT NOT NULL,
        vi_tri_xay_ra TEXT NOT NULL,
        vi_tri_cu_the TEXT NOT NULL,
        thoi_gian_xay_ra INTEGER NOT NULL,
        mo_ta TEXT NOT NULL,
        de_xuat_giai_phap TEXT NOT NULL,
        xu_ly_ban_dau TEXT NOT NULL,
        thong_bao_cho_bac_si_hoac_nguoi_chiu_trach_nhiem TEXT NOT NULL,
        ghi_nhan_ho_so TEXT NOT NULL,
        thong_bao_cho_nguoi_nha_hoac_nguoi_bao_ho TEXT NOT NULL,
        thong_bao_cho_nguoi_benh TEXT NOT NULL,
        phan_loai_ban_dau TEXT NOT NULL,
        danh_gia_ban_dau TEXT NOT NULL,
        ho_ten_nguoi_bao_cao TEXT NOT NULL,
        so_dien_thoai_nguoi_bao_cao TEXT NOT NULL,
        email_nguoi_bao_cao TEXT NOT NULL,
        chuc_danh_nguoi_bao_cao TEXT NOT NULL,
        nguoi_chung_kien_1 TEXT NOT NULL,
        nguoi_chung_kien_2 TEXT NOT NULL
        );''')
    cur.execute('''CREATE TABLE users (
        username TEXT NOT NULL PRIMARY KEY,
        hashed_password TEXT NOT NULL,
        superuser INTEGER DEFAULT 0 NOT NULL
        );''')
    cur.execute('''CREATE TABLE quick_bcsc (
        id INTEGER PRIMARY KEY,
        ngay_gio_bao_cao TEXT NOT NULL,
        doi_tuong TEXT NOT NULL,
        vi_tri_xay_ra TEXT NOT NULL,
        lien_quan TEXT NOT NULL,
        mo_ta TEXT,
        so_benh_an TEXT,
        xu_ly TEXT,
        filepaths TEXT
        );''')
    cur.execute(
        '''INSERT INTO users VALUES (?, ?, ?);''',
        ('admin', bcrypt.hash('12345'), 1)
    )


@ conn
def create_report(cur, data):
    data['thoi_gian_xay_ra'] = dt_to_int(data['thoi_gian_xay_ra'])
    cur.execute("INSERT INTO bao_cao_su_co ({a}) VALUES ({b});".format(
        a=','.join(headers_bcsc[1:]),
        b=','.join(len(headers_bcsc[1:]) * ['?'])),
        tuple(data.values()))
    return cur.lastrowid


@ conn
def create_quick_report(cur, data):
    data['ngay_gio_bao_cao1'] = dt_to_int(data['ngay_gio_bao_cao1'])
    files = data.pop('gui_tai_lieu')
    cur.execute("INSERT INTO quick_bcsc ({a}) VALUES ({b});".format(
        a=','.join(headers_quick_bcsc[1:-1]),
        b=','.join(len(headers_quick_bcsc[1:-1]) * ['?'])),
        tuple(data.values()))
    rid = cur.lastrowid
    filepaths = []
    for f in files:
        if f.filename == "":
            break
        else:
            f.filename = ''.join(f.filename.split(' '))
            name, ext = f.filename.rsplit('.', 1)
            f.filename = ''.join(name.split('.')) + '.' + ext
            filepath = os.path.join(tai_lieu_folder, str(rid) + "_" + f.filename)
            if filepath.lower().endswith('heic') or filepath.lower().endswith('heif'):
                filepath = filepath[:-4] + 'jpg'
                hf = pyheif.read(f.file)
                image = Image.frombytes(
                    hf.mode,
                    hf.size,
                    hf.data,
                    "raw",
                    hf.mode,
                    hf.stride,
                )
                image.save(filepath, "JPEG")
            elif filepath.lower().endswith('mov'):
                filepath = filepath[:-3] + 'mp4'
            with open(filepath, "wb") as buffer:
                shutil.copyfileobj(f.file, buffer)
            filepaths.append(filepath)
    cur.execute(f"UPDATE quick_bcsc SET filepaths=? WHERE id={rid};",
                (";".join(filepaths),))
    return filepaths, rid


def convert_video(filepaths):
    fp = filter(lambda fn: fn.lower().endswith('mov'), filepaths)
    for f in fp:
        new_f = f[:-3] + 'mp4'
        command = ['ffmpeg', '-y', '-i', f, new_f]
        process = subprocess.run(command)
        if process.returncode == 0:
            os.remove(f)


@ conn
def get_report(cur, id):
    cur.execute("SELECT * FROM bao_cao_su_co WHERE id=?;", (str(id),))
    item = cur.fetchone()
    if item:
        res = {h: i for h, i in zip(headers_bcsc, item)}
        return res
    else:
        return None


@ conn
def get_quick_report(cur, id):
    cur.execute("SELECT * FROM quick_bcsc WHERE id=?;", (str(id),))
    item = cur.fetchone()
    if item:
        res = {h: i for h, i in zip(headers_quick_bcsc, item)}
        res['ngay_gio_bao_cao'] = int_to_dt(res['ngay_gio_bao_cao'])
        return res
    else:
        return None


@ conn
def get_reports(cur, start, end, full):
    if full:
        cur.execute("SELECT * FROM bao_cao_su_co")
        return headers_bcsc, cur.fetchall()
    if end < start:
        start = end - dt.timedelta(days=1)
    start = dt_to_int(start)
    end = dt_to_int(end)
    cur.execute("SELECT * FROM bao_cao_su_co WHERE "
                "thoi_gian_xay_ra>=? AND thoi_gian_xay_ra<=?;", (start, end))
    data = cur.fetchall()
    res = {h:i for h,i in zip}
    return headers_bcsc, data


@ conn
def delete_report(cur, id):
    rowcount = cur.execute("DELETE FROM bao_cao_su_co WHERE id=?;", (str(id),)).rowcount
    return rowcount


@ conn
def delete_report(cur, id):
    rowcount = cur.execute("DELETE FROM quick_bcsc WHERE id=?;", (str(id),)).rowcount
    return rowcount


@ conn
def get_user(cur, username):
    cur.execute("SELECT * FROM users WHERE username=?;", (username,))
    item = cur.fetchone()
    if item:
        return {h: i for h, i in zip(headers_users, item)}
    else:
        return None


@ conn
def create_user(cur, data):
    try:
        cur.execute("""INSERT INTO users VALUES (?,?,?);""",
                    tuple(data.values()))
    except sqlite3.IntegrityError:
        return None
    return cur.lastrowid


@ conn
def delete_user(cur, data):
    rowcount = cur.execute("""DELETE FROM users WHERE username=?;""",
                           tuple(data.values())).rowcount
    return rowcount


if __name__ == "__main__":
    # create_db()
    # print(get_user_hashed_password('asd'))
    pass
