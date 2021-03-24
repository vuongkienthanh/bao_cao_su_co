from schema import *

import datetime as dt
from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from typing import Optional
from pydantic import constr, EmailStr


app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")

templates = Jinja2Templates(directory="templates")


@app.get("/")
def root(request: Request):
    return templates.TemplateResponse(
        "index.html",
        {"request": request})


@app.post("/send_report")
def send_report(
        request: Request,
        hinh_thuc: Hinh_Thuc=Form(...),
        ngay_bao_cao: dt.date=Form(...),
        don_vi_bao_cao: Khoa_Phong=Form(...),
        ho_ten_nguoi_benh: str=Form(...),
        so_benh_an: constr(regex="^\d{8}$")=Form(...),
        ngay_sinh: dt.date=Form(...),
        gioi_tinh: Gioi_Tinh=Form(...),
        khoa_phong: Khoa_Phong=Form(...),
        doi_tuong: Doi_Tuong=Form(...),
        vi_tri_xay_ra: str=Form(...),
        vi_tri_cu_the: str=Form(...),
        thoi_gian_xay_ra: dt.datetime=Form(...),
        mo_ta: str=Form(...),
        de_xuat_giai_phap: str=Form(...),
        xu_ly_ban_dau: str=Form(...),
        thong_bao_cho_bac_si_hoac_nguoi_chiu_trach_nhiem: Ghi_Nhan_Enum=Form(...),
        ghi_nhan_ho_so: Ghi_Nhan_Enum=Form(...),
        thong_bao_cho_nguoi_nha_hoac_nguoi_bao_ho: Ghi_Nhan_Enum=Form(...),
        thong_bao_cho_nguoi_benh: Ghi_Nhan_Enum=Form(...),
        phan_loai_ban_dau: Phan_Loai_Ban_Dau=Form(...),
        danh_gia_ban_dau: Danh_Gia_Ban_Dau=Form(...),
        ho_ten_nguoi_bao_cao: str=Form(...),
        so_dien_thoai_nguoi_bao_cao: constr(regex="^\d*$")=Form(...),
        email_nguoi_bao_cao: EmailStr=Form(...),
        chuc_danh_nguoi_bao_cao: Chuc_Danh_Nguoi_Bao_Cao=Form(...),
        chuc_danh_khac: Optional[str]=Form(None),
        nguoi_chung_kien_1: str=Form(...),
        nguoi_chung_kien_2: str=Form(...)):
    return templates.TemplateResponse(
        "send_report.html",
        {"request": request,
         "hinh_thuc": hinh_thuc.value,
         "ngay_bao_cao": ngay_bao_cao,
         "don_vi_bao_cao": don_vi_bao_cao.value,
         "ho_ten_nguoi_benh": ho_ten_nguoi_benh,
         "so_benh_an": so_benh_an,
         "ngay_sinh": ngay_sinh,
         "gioi_tinh": gioi_tinh.value,
         "doi_tuong": doi_tuong.value,
         "khoa_phong": khoa_phong.value,
         "vi_tri_xay_ra": vi_tri_xay_ra,
         "vi_tri_cu_the": vi_tri_cu_the,
         "thoi_gian_xay_ra": thoi_gian_xay_ra,
         "mo_ta": mo_ta,
         "de_xuat_giai_phap": de_xuat_giai_phap,
         "xu_ly_ban_dau": xu_ly_ban_dau,
         "thong_bao_cho_bac_si_hoac_nguoi_chiu_trach_nhiem": thong_bao_cho_bac_si_hoac_nguoi_chiu_trach_nhiem.value,
         "ghi_nhan_ho_so": ghi_nhan_ho_so.value,
         "thong_bao_cho_nguoi_nha_hoac_nguoi_bao_ho": thong_bao_cho_nguoi_nha_hoac_nguoi_bao_ho.value,
         "thong_bao_cho_nguoi_benh": thong_bao_cho_nguoi_benh.value,
         "phan_loai_ban_dau": phan_loai_ban_dau.value,
         "danh_gia_ban_dau": danh_gia_ban_dau.value,
         "ho_ten_nguoi_bao_cao": ho_ten_nguoi_bao_cao,
         "so_dien_thoai_nguoi_bao_cao": so_dien_thoai_nguoi_bao_cao,
         "email_nguoi_bao_cao": email_nguoi_bao_cao,
         "chuc_danh_nguoi_bao_cao": chuc_danh_nguoi_bao_cao.value,
         "chuc_danh_khac": chuc_danh_khac,
         "nguoi_chung_kien_1": nguoi_chung_kien_1,
         "nguoi_chung_kien_2": nguoi_chung_kien_2})