import sqlite3
import uuid
import copy
db_name = 'bao_cao_su_co.db'


def conn(func):
    def inner(*arg, **kwarg):
        con = sqlite3.connect(db_name)
        cur = con.cursor()
        result = func(cur, *arg, **kwarg)
        con.commit()
        con.close()
        return result
    return inner


@conn
def create_db(cur):
    cur.execute('''create table bao_cao_su_co (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
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


@conn
def insert_report(cur, val):
    cur.execute("insert into bao_cao_su_co "
                "('hinh_thuc','ngay_bao_cao','don_vi_bao_cao','ho_ten_nguoi_benh','so_benh_an',"
                "'ngay_sinh','gioi_tinh','khoa_phong','doi_tuong','vi_tri_xay_ra','vi_tri_cu_the',"
                "'thoi_gian_xay_ra','mo_ta','de_xuat_giai_phap','xu_ly_ban_dau',"
                "'thong_bao_cho_bac_si_hoac_nguoi_chiu_trach_nhiem','ghi_nhan_ho_so',"
                "'thong_bao_cho_nguoi_nha_hoac_nguoi_bao_ho','thong_bao_cho_nguoi_benh','phan_loai_ban_dau',"
                "'danh_gia_ban_dau','ho_ten_nguoi_bao_cao','so_dien_thoai_nguoi_bao_cao','email_nguoi_bao_cao',"
                "'chuc_danh_nguoi_bao_cao','chuc_danh_khac','nguoi_chung_kien_1','nguoi_chung_kien_2')"
                " values (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?);",
                (val['hinh_thuc'],
                 val['ngay_bao_cao'],
                 val['don_vi_bao_cao'],
                 val['ho_ten_nguoi_benh'],
                 val['so_benh_an'],
                 val['ngay_sinh'],
                 val['gioi_tinh'],
                 val['khoa_phong'],
                 val['doi_tuong'],
                 val['vi_tri_xay_ra'],
                 val['vi_tri_cu_the'],
                 val['thoi_gian_xay_ra'],
                 val['mo_ta'],
                 val['de_xuat_giai_phap'],
                 val['xu_ly_ban_dau'],
                 val['thong_bao_cho_bac_si_hoac_nguoi_chiu_trach_nhiem'],
                 val['ghi_nhan_ho_so'],
                 val['thong_bao_cho_nguoi_nha_hoac_nguoi_bao_ho'],
                 val['thong_bao_cho_nguoi_benh'],
                 val['phan_loai_ban_dau'],
                 val['danh_gia_ban_dau'],
                 val['ho_ten_nguoi_bao_cao'],
                 val['so_dien_thoai_nguoi_bao_cao'],
                 val['email_nguoi_bao_cao'],
                 val['chuc_danh_nguoi_bao_cao'],
                 val['chuc_danh_khac'],
                 val['nguoi_chung_kien_1'],
                 val['nguoi_chung_kien_2']))
    return cur.lastrowid


@conn
def get_all_reports(cur):
    cur.execute("PRAGMA table_info(bao_cao_su_co);")
    headers = [h[1] for h in cur.fetchall()]
    cur.execute("select * from bao_cao_su_co;")
    data = cur.fetchall()
    return headers, data


@conn
def read_report(cur, id):
    cur.execute("PRAGMA table_info(bao_cao_su_co);")
    headers = [h[1] for h in cur.fetchall()]
    cur.execute("select * from bao_cao_su_co where id=?;", str(id))
    item = cur.fetchone()
    return {h: i for h, i in zip(headers, item)}


@conn
def delete_report(cur, id):
    cur.execute("DELETE FROM bao_cao_su_co WHERE id=?;", str(id))


if __name__ == "__main__":
    create_db()
    # print(read_db())
