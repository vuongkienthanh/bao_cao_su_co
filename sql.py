from init import tai_lieu_folder, db_path
import datetime as dt
import sqlite3
import shutil
import os
import subprocess
from passlib.hash import bcrypt
import pyheif
from PIL import Image


headers_bcsc = [
    "id", "hinh_thuc", "ngay_gio_bao_cao", "don_vi_bao_cao",
    "ho_ten_nguoi_benh", "so_benh_an", "ngay_sinh", "gioi_tinh",
    "khoa_phong", "doi_tuong", "vi_tri_xay_ra", "vi_tri_cu_the",
    "thoi_gian_xay_ra", "mo_ta", "de_xuat_giai_phap", "xu_ly_ban_dau",
    "thong_bao_cho_bac_si_hoac_nguoi_chiu_trach_nhiem",
    "ghi_nhan_ho_so", "thong_bao_cho_nguoi_nha_hoac_nguoi_bao_ho",
    "thong_bao_cho_nguoi_benh", "phan_loai_ban_dau",
    "danh_gia_ban_dau", "ho_ten_nguoi_bao_cao",
    "so_dien_thoai_nguoi_bao_cao", "email_nguoi_bao_cao",
    "chuc_danh_nguoi_bao_cao",
    "nguoi_chung_kien_1", "nguoi_chung_kien_2", "filepaths"]
headers_users = [
    "username", "hashed_password", "superuser"]
headers_thptsc = [
    "id", "mo_ta",
    "v1a", "v1b", "v1c", "v1d", "v1e", "v1f", "v1g", "v1h", "v1i",
    "v2a", "v2b", "v2c", "v2d", "v2e",
    "v3a", "v3b", "v3c", "v3d", "v3e", "v3f", "v3g", "v3h", "v3i",
    "v4a", "v4b", "v4c", "v5a", "v5b", "v5c",
    "v6a", "v6b", "v6c", "v6d", "v6e", "v6f",
    "v7", "v8a", "v8b", "v9a", "v9b", "v9c",
    "v10a", "v10b", "v10c", "v10d", "v10e", "v10f",
    "v11", "xu_ly",
    "v12a", "v12b", "v12c", "v12d", "v12e", "v12f",
    "v13a", "v13b", "v13c", "v13d", "v13e", "v13f",
    "v14a", "v14b", "v14c", "v14d",
    "v15a", "v15b", "v15c", "v15d",
    "v16a", "v16b", "v16c", "v17",
    "khac_phuc", "de_xuat", "danh_gia",
    "v18", "v19a", "v19b", "v20",
    "v21a", "v21b", "v21c", "v21d", "v21e", "v21f", "v21g",
    "ngay_gio"
]


def dt_to_int(datetime_dt):
    return int(datetime_dt.strftime('%Y%m%d%H%M'))


def int_to_dt(datetime_int):
    return dt.datetime.strptime(str(datetime_int), "%Y%m%d%H%M")


def conn(func):
    def inner(*arg, **kwarg):
        con = sqlite3.connect(db_path)
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


@conn
def create_db(cur):
    cur.execute('''CREATE TABLE bao_cao_su_co (
        id INTEGER PRIMARY KEY,
        hinh_thuc TEXT,
        ngay_gio_bao_cao TEXT NOT NULL,
        don_vi_bao_cao TEXT,
        ho_ten_nguoi_benh TEXT,
        so_benh_an TEXT,
        ngay_sinh TEXT,
        gioi_tinh TEXT,
        khoa_phong TEXT,
        doi_tuong TEXT,
        vi_tri_xay_ra TEXT,
        vi_tri_cu_the TEXT,
        thoi_gian_xay_ra INTEGER,
        mo_ta TEXT NOT NULL,
        de_xuat_giai_phap TEXT,
        xu_ly_ban_dau TEXT,
        thong_bao_cho_bac_si_hoac_nguoi_chiu_trach_nhiem TEXT,
        ghi_nhan_ho_so TEXT,
        thong_bao_cho_nguoi_nha_hoac_nguoi_bao_ho TEXT,
        thong_bao_cho_nguoi_benh TEXT,
        phan_loai_ban_dau TEXT,
        danh_gia_ban_dau TEXT,
        ho_ten_nguoi_bao_cao TEXT NOT NULL,
        so_dien_thoai_nguoi_bao_cao TEXT,
        email_nguoi_bao_cao TEXT,
        chuc_danh_nguoi_bao_cao TEXT,
        nguoi_chung_kien_1 TEXT,
        nguoi_chung_kien_2 TEXT,
        filepaths TEXT
        );''')
    cur.execute('''CREATE TABLE users (
        username TEXT NOT NULL PRIMARY KEY,
        hashed_password TEXT NOT NULL,
        superuser INTEGER DEFAULT 0 NOT NULL
        );''')
    cur.execute('''CREATE TABLE receiver_emails (
        email TEXT PRIMARY KEY
        );''')
    cur.execute('''CREATE TABLE thptsc (
        id INTEGER PRIMARY KEY,
        mo_ta TEXT,
        v1a INTEGER,
        v1b INTEGER,
        v1c INTEGER,
        v1d INTEGER,
        v1e INTEGER,
        v1f INTEGER,
        v1g INTEGER,
        v1h INTEGER,
        v1i INTEGER,
        v2a INTEGER,
        v2b INTEGER,
        v2c INTEGER,
        v2d INTEGER,
        v2e INTEGER,
        v3a INTEGER,
        v3b INTEGER,
        v3c INTEGER,
        v3d INTEGER,
        v3e INTEGER,
        v3f INTEGER,
        v3g INTEGER,
        v3h INTEGER,
        v3i INTEGER,
        v4a INTEGER,
        v4b INTEGER,
        v4c INTEGER,
        v5a INTEGER,
        v5b INTEGER,
        v5c INTEGER,
        v6a INTEGER,
        v6b INTEGER,
        v6c INTEGER,
        v6d INTEGER,
        v6e INTEGER,
        v6f INTEGER,
        v7 INTEGER,
        v8a INTEGER,
        v8b INTEGER,
        v9a INTEGER,
        v9b INTEGER,
        v9c INTEGER,
        v10a INTEGER,
        v10b INTEGER,
        v10c INTEGER,
        v10d INTEGER,
        v10e INTEGER,
        v10f INTEGER,
        v11 INTEGER,
        xu_ly TEXT,
        v12a INTEGER,
        v12b INTEGER,
        v12c INTEGER,
        v12d INTEGER,
        v12e INTEGER,
        v12f INTEGER,
        v13a INTEGER,
        v13b INTEGER,
        v13c INTEGER,
        v13d INTEGER,
        v13e INTEGER,
        v13f INTEGER,
        v14a INTEGER,
        v14b INTEGER,
        v14c INTEGER,
        v14d INTEGER,
        v15a INTEGER,
        v15b INTEGER,
        v15c INTEGER,
        v15d INTEGER,
        v16a INTEGER,
        v16b INTEGER,
        v16c INTEGER,
        v17 INTEGER,
        khac_phuc TEXT,
        de_xuat TEXT,
        danh_gia TEXT,
        v18 TEXT,
        v19a TEXT,
        v19b TEXT,
        v20 TEXT,
        v21a INTEGER,
        v21b INTEGER,
        v21c INTEGER,
        v21d INTEGER,
        v21e INTEGER,
        v21f INTEGER,
        v21g INTEGER,
        ngay_gio INTEGER
        );''')
    cur.execute(
        '''INSERT INTO users VALUES (?, ?, ?);''',
        ('admin', bcrypt.hash('12345'), 1)
    )


@conn
def create_report(cur, data):
    data = data.copy()
    if data['thoi_gian_xay_ra']:
        data['thoi_gian_xay_ra'] = dt_to_int(data['thoi_gian_xay_ra'])
    data['ngay_gio_bao_cao'] = dt_to_int(data['ngay_gio_bao_cao'])
    files = data.pop('filepaths')
    cur.execute("INSERT INTO bao_cao_su_co ({a}) VALUES ({b});".format(
        a=','.join(headers_bcsc[1:-1]),
        b=','.join(len(headers_bcsc[1:-1]) * ['?'])),
        [data[k] for k in headers_bcsc[1:-1]])
    rid = cur.lastrowid
    filepaths = []
    if files[0].filename != "":
        for f in files:
            f.filename = ''.join(f.filename.split(' '))
            name, ext = f.filename.rsplit('.', 1)
            f.filename = ''.join(name.split('.')) + '.' + ext
            filepath = os.path.join(tai_lieu_folder, str(rid) + "_" + f.filename)
            if filepath.lower().endswith('heic') or filepath.lower().endswith('heif'):
                filepath = filepath[:-4] + 'jpg'
                hf = pyheif.read(f.file)
                print(filepath)
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
            else:
                with open(filepath, "wb") as buffer:
                    shutil.copyfileobj(f.file, buffer)
            filepaths.append(filepath)
        cur.execute(f"UPDATE bao_cao_su_co SET filepaths=? WHERE id={rid};",
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


@conn
def get_report(cur, id):
    cur.execute("SELECT * FROM bao_cao_su_co WHERE id=?;", (str(id),))
    item = cur.fetchone()
    if item:
        data = {h: i for h, i in zip(headers_bcsc, item)}
        data['ngay_gio_bao_cao'] = int_to_dt(data['ngay_gio_bao_cao'])
        if data['thoi_gian_xay_ra']:
            data['thoi_gian_xay_ra'] = int_to_dt(data['thoi_gian_xay_ra'])
        return data
    else:
        return None


@conn
def get_reports(cur, start, end, full):
    if full:
        cur.execute("SELECT * FROM bao_cao_su_co")
        return headers_bcsc, cur.fetchall()
    if end < start:
        start = end - dt.timedelta(days=1)
    start = dt_to_int(start)
    end = dt_to_int(end)
    cur.execute("SELECT * FROM bao_cao_su_co WHERE "
                "ngay_gio_bao_cao>=? AND ngay_gio_bao_cao<=?;", (start, end))
    data = cur.fetchall()
    return headers_bcsc, data


@conn
def delete_report(cur, id):
    rowcount = cur.execute("DELETE FROM bao_cao_su_co WHERE id=?;", (str(id),)).rowcount
    return rowcount


@conn
def get_user(cur, username):
    cur.execute("SELECT * FROM users WHERE username=?;", (username,))
    item = cur.fetchone()
    if item:
        return {h: i for h, i in zip(headers_users, item)}
    else:
        return None


@conn
def create_user(cur, data):
    try:
        cur.execute("""INSERT INTO users VALUES (?,?,?);""",
                    tuple(data.values()))
    except sqlite3.IntegrityError:
        return None
    return cur.lastrowid


@conn
def delete_user(cur, data):
    rowcount = cur.execute("""DELETE FROM users WHERE username=?;""",
                           tuple(data.values())).rowcount
    return rowcount


@conn
def add_email(cur, email):
    try:
        cur.execute("""INSERT INTO receiver_emails VALUES (?);""", (email,))
    except sqlite3.IntegrityError:
        return None
    return cur.lastrowid


@conn
def remove_email(cur, email):
    rowcount = cur.execute("""DELETE FROM receiver_emails WHERE email=(?);""", (email,))
    return rowcount


@conn
def get_emails(cur):
    cur.execute('''SELECT * FROM receiver_emails;''')
    return cur.fetchall()


@conn
def create_thptsc(cur, data):
    data = data.copy()
    data['ngay_gio'] = dt_to_int(data['ngay_gio'])
    cur.execute('SELECT count(*) FROM thptsc where id=?;', (data['id'],))
    x = cur.fetchone()[0]
    print(x)
    if x == 0:
        print('insert')
        cur.execute("INSERT INTO thptsc ({a}) VALUES ({b});".format(
            a=','.join(headers_thptsc),
            b=','.join(len(headers_thptsc) * ['?'])),
            [data[k] for k in headers_thptsc])
        return cur.lastrowid
    else:
        cur.execute("UPDATE thptsc SET {a} WHERE id={b};".format(
            a=",".join([k + "=?" for k in headers_thptsc[1:]]),
            b=data['id']),
            [data[k] for k in headers_thptsc[1:]])
        return data['id']


@conn
def get_thptsc(cur, id):
    cur.execute("SELECT * FROM thptsc WHERE id=?", (id,))
    item = cur.fetchone()
    if item:
        data = {h: i for h, i in zip(headers_thptsc, item)}
        data['ngay_gio'] = int_to_dt(data['ngay_gio'])
        return data
    else:
        return None


@ conn
def delete_thptsc(cur, id):
    rowcount = cur.execute("DELETE FROM thptsc WHERE id=?;", (str(id),)).rowcount
    return rowcount


@conn
def get_thptscs(cur, start, end, full):
    if full:
        cur.execute("SELECT * FROM thptsc")
        return headers_thptsc, cur.fetchall()
    if end < start:
        start = end - dt.timedelta(days=1)
    start = dt_to_int(start)
    end = dt_to_int(end)
    cur.execute("SELECT * FROM thptsc WHERE "
                "ngay_gio>=? AND ngay_gio<=?;", (start, end))
    data = cur.fetchall()
    return headers_thptsc, data
