import sqlite3
from passlib.hash import bcrypt
db_name = 'bao_cao_su_co.db'


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


@conn
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
        thoi_gian_xay_ra TEXT NOT NULL,
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
        chuc_danh_khac TEXT,
        nguoi_chung_kien_1 TEXT NOT NULL,
        nguoi_chung_kien_2 TEXT NOT NULL
        );''')
    cur.execute('''CREATE TABLE users (
        username TEXT NOT NULL PRIMARY KEY,
        hashed_password TEXT NOT NULL,
        superuser INTEGER DEFAULT 0 NOT NULL
        );''')
    cur.execute(
        '''INSERT INTO users VALUES (?, ?, ?);''',
        ('admin', bcrypt.hash('12345'), 1)
    )


@conn
def create_report(cur, data):
    cur.execute("""INSERT INTO bao_cao_su_co
                (hinh_thuc, ngay_bao_cao,don_vi_bao_cao,ho_ten_nguoi_benh,so_benh_an,
                ngay_sinh, gioi_tinh,khoa_phong,doi_tuong,vi_tri_xay_ra,vi_tri_cu_the,
                thoi_gian_xay_ra, mo_ta,de_xuat_giai_phap,xu_ly_ban_dau,
                thong_bao_cho_bac_si_hoac_nguoi_chiu_trach_nhiem, ghi_nhan_ho_so,
                thong_bao_cho_nguoi_nha_hoac_nguoi_bao_ho, thong_bao_cho_nguoi_benh,phan_loai_ban_dau,
                danh_gia_ban_dau, ho_ten_nguoi_bao_cao,so_dien_thoai_nguoi_bao_cao,email_nguoi_bao_cao,
                chuc_danh_nguoi_bao_cao, chuc_danh_khac,nguoi_chung_kien_1,nguoi_chung_kien_2)
                 VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?);""",
                tuple(data.values()))
    return cur.lastrowid


@conn
def get_all_reports(cur):
    cur.execute("PRAGMA table_info(bao_cao_su_co);")
    headers = [h[1] for h in cur.fetchall()]
    cur.execute("SELECT * FROM bao_cao_su_co;")
    data = cur.fetchall()
    return headers, data


@conn
def get_report(cur, id):
    cur.execute("PRAGMA table_info(bao_cao_su_co);")
    headers = [h[1] for h in cur.fetchall()]
    cur.execute("SELECT * FROM bao_cao_su_co WHERE id=?;", (str(id),))
    item = cur.fetchone()
    if item:
        return {h: i for h, i in zip(headers, item)}
    else:
        return None


@conn
def delete_report(cur, id):
    rowcount = cur.execute("DELETE FROM bao_cao_su_co WHERE id=?;", (str(id),)).rowcount
    return rowcount


@conn
def get_user(cur, username):
    cur.execute("PRAGMA table_info(users);")
    headers = [h[1] for h in cur.fetchall()]
    cur.execute("SELECT * FROM users WHERE username=?;", (username,))
    item = cur.fetchone()
    if item:
        return {h: i for h, i in zip(headers, item)}
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


if __name__ == "__main__":
    # create_db()
    # print(get_user_hashed_password('asd'))
    pass
