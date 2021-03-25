from schema import *
import sql
import io
import datetime as dt
import csv
import os
from fastapi import FastAPI, Request, Form
from fastapi.responses import StreamingResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from typing import Optional
from pydantic import constr, EmailStr


app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")

templates = Jinja2Templates(directory="templates")


@app.get("/", summary="Form báo cáo")
async def root(request: Request):
    return templates.TemplateResponse(
        "index.html",
        {"request": request})


@app.get("/initdb", summary="Tạo mới database (có backup db cũ)")
async def initdb():
    DIR = os.path.dirname(os.path.abspath(__name__))
    f = os.path.join(DIR, sql.dbname)
    if os.path.exists(f):
        os.rename(
            f,
            'bcsc {}.dbbk'.format(dt.datetime.now().strftime('%Y%m%d_%H%m'))
        )
        os.remove(f)
    sql.create_db()
    return {'Initialize database': 1}


@app.post("/send_report", summary="Gửi báo cáo")
async def send_report(
        request: Request,
        hinh_thuc: Hinh_Thuc = Form(..., description="Hình thức báo cáo sự cố"),
        ngay_bao_cao: dt.date = Form(..., description="Ngày báo cáo sự cố, định dạng YYYY-MM-DD"),
        don_vi_bao_cao: Khoa_Phong = Form(..., description="Đơn vị báo cáo là các khoa phòng trong bệnh viện"),
        ho_ten_nguoi_benh: str = Form(..., description="Họ tên người bệnh. Ví dụ: Nguyễn Văn A"),
        so_benh_an: constr(regex="^\d{8}$") = Form(..., description="Số hồ sơ bệnh án. Ví dụ: 19002000"),
        ngay_sinh: dt.date = Form(..., description="Ngày sinh của người bệnh, định dạng YYYY-MM-DD"),
        gioi_tinh: Gioi_Tinh = Form(..., description="Giới tính của người bệnh, nhận 2 giá trị là Nam và Nữ"),
        khoa_phong: Khoa_Phong = Form(..., description="Các khoa phòng trong bệnh viện"),
        doi_tuong: Doi_Tuong = Form(..., description="Đối tượng báo cáo: Người bệnh; Người nhà hoặc khách đến thăm; Nhân viên y tế; Trang thiết bị hoặc cơ sở hạ tầng"),
        vi_tri_xay_ra: Vi_Tri_Xay_Ra = Form(..., description="Vị trí xảy ra sự cố. Ví dụ như ở khoa phòng, khuôn viên bệnh viện,.."),
        vi_tri_cu_the: str = Form(..., description="Vị trí cụ thể như nhà vệ sinh, bãi giữ xe,.."),
        thoi_gian_xay_ra: dt.datetime = Form(..., description="Thời gian xảy ra, định dạng YYYY-MM-DD hh:mm"),
        mo_ta: str = Form(..., description="Mô tả ngắn gọn sự cố"),
        de_xuat_giai_phap: str = Form(..., description="Đề xuất giải pháp ban đầu"),
        xu_ly_ban_dau: str = Form(..., description="Điều trị/xử lý ban đầu"),
        thong_bao_cho_bac_si_hoac_nguoi_chiu_trach_nhiem: Ghi_Nhan_Enum = Form(..., description="Thông báo cho bác sĩ điều trị/người chịu trách nhiệm"),
        ghi_nhan_ho_so: Ghi_Nhan_Enum = Form(..., description="Ghi nhận vào hồ sơ bệnh án/giấy tờ liên quan"),
        thong_bao_cho_nguoi_nha_hoac_nguoi_bao_ho: Ghi_Nhan_Enum = Form(..., description="Thông báo cho người nhà hoặc người bảo hộ"),
        thong_bao_cho_nguoi_benh: Ghi_Nhan_Enum = Form(..., description="Thông báo cho người bệnh"),
        phan_loai_ban_dau: Phan_Loai_Ban_Dau = Form(..., description="Phân loại ban đầu"),
        danh_gia_ban_dau: Danh_Gia_Ban_Dau = Form(..., description="Đánh giá ban đầu"),
        ho_ten_nguoi_bao_cao: str = Form(..., description="Họ tên người báo cáo"),
        so_dien_thoai_nguoi_bao_cao: constr(regex="^\d*$") = Form(..., description="Số điện thoại người báo cáo"),
        email_nguoi_bao_cao: EmailStr = Form(..., description="Email người báo cáo"),
        chuc_danh_nguoi_bao_cao: Chuc_Danh_Nguoi_Bao_Cao = Form(..., description="Chức danh người báo cáo:bác sĩ; điều dưỡng; người bệnh; người nhà/khách,.."),
        chuc_danh_khac: Optional[str] = Form(None, description="Chức danh khác (nêu rõ khi chọn khác ở mục trên)"),
        nguoi_chung_kien_1: str = Form(..., description="Người chứng kiến 1"),
        nguoi_chung_kien_2: str = Form(..., description="Người chứng kiến 2")):
    data = {
        "hinh_thuc": hinh_thuc.value,
        "ngay_bao_cao": ngay_bao_cao,
        "don_vi_bao_cao": don_vi_bao_cao.value,
        "ho_ten_nguoi_benh": ho_ten_nguoi_benh,
        "so_benh_an": so_benh_an,
        "ngay_sinh": ngay_sinh,
        "gioi_tinh": gioi_tinh.value,
        "doi_tuong": doi_tuong.value,
        "khoa_phong": khoa_phong.value,
        "vi_tri_xay_ra": vi_tri_xay_ra.value,
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
        "nguoi_chung_kien_2": nguoi_chung_kien_2}
    lastrowid = sql.insert_report(data)
    data.update({"request": request, "lastrowid": lastrowid})
    return templates.TemplateResponse(
        "send_report.html", data)


@app.get("/get_csv", summary="Tải data (csv) về")
async def get_csv():
    stream = io.StringIO()
    headers, data = sql.get_all_reports()
    writer = csv.writer(stream)
    writer.writerow(headers)
    writer.writerows(data)

    response = StreamingResponse(iter([stream.getvalue()]), media_type="text/csv")
    response.headers["Content-Disposition"] = "attachment; filename=export.csv"
    return response


@app.get("/read_report/{id}", summary="Xem báo cáo theo id")
async def read_report(request: Request, id: int):
    data = sql.read_report(id)
    data.update({'request': request})
    return templates.TemplateResponse(
        "read_report.html", data)


@app.get("/delete_report/{id}", summary="Xoá báo cáo theo id")
async def delete_report(id: int):
    sql.delete_report(id)
    return {'deleted_report_id': id}
