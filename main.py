from schema import *
from create_report import create_pdf
import sql
import io
from typing import Optional
import datetime as dt
import csv
import os
from fastapi import FastAPI, Request, Form, status, Depends, HTTPException
from fastapi.responses import StreamingResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import constr, EmailStr
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from passlib.hash import bcrypt


app = FastAPI(
    title="Dự án phần mềm báo cáo sự cố",
    description='''Server API, có thể test với <br>{superuser="admin", password="12345"}
<ul>Chức năng:
<li>Tạo superuser, basic user. Quản lý user.</li>
<li>Lưu trữ bằng database sqlite.</li>
<li>Form báo cáo, gửi về hệ thống lưu trữ.</li>
<li>Quản lý báo cáo.</li>
<li>Tạo file pdf, tải về CSV để phân tích.</li>
<li>Cổng dữ liệu API để liên kết với hệ thống dashboard.</li>
</ul>''',
    version="0.1",)
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")
security = HTTPBasic()


def authen(credentials: HTTPBasicCredentials = Depends(security)):
    user = sql.get_user(credentials.username)
    not_authen_msg = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Incorrect username or password",
        headers={"WWW-Authenticate": "Basic"},
    )
    if user:
        if bcrypt.verify(credentials.password, user['hashed_password']):
            return credentials.username
        else:
            raise not_authen_msg
    else:
        raise not_authen_msg


def super_authen(credentials: HTTPBasicCredentials = Depends(security)):
    user = sql.get_user(credentials.username)
    not_authen_msg = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Incorrect username or password for superuser",
        headers={"WWW-Authenticate": "Basic"},
    )
    if user:
        if bcrypt.verify(credentials.password, user['hashed_password']) and user['superuser']:
            return credentials.username
        else:
            raise not_authen_msg
    else:
        raise not_authen_msg


@app.on_event("startup")
async def startup():
    DIR = os.path.dirname(os.path.abspath(__name__))
    f = os.path.join(DIR, sql.db_name)
    if not os.path.exists(f):
        sql.create_db()


@app.get("/", summary="Form báo cáo", tags=['Giao diện'])
async def root(request: Request):
    return templates.TemplateResponse(
        "index.html",
        {"request": request})


@app.post("/create_user",
          summary="Tạo user mới (cần đăng nhập superuser)",
          status_code=status.HTTP_201_CREATED,
          tags=["User"])
async def create_user(username: str, password: str, superuser: bool, super_authen: str = Depends(super_authen)):
    data = {
        'username': username,
        'hashed_password': bcrypt.hash(password),
        'superuser': int(superuser)
    }
    if sql.insert_user(data):
        data.pop("hashed_password")
        return {'created user': data}
    else:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="username already in use"
        )


@app.delete("/delete_user", summary="Xoá user (cần đăng nhập superuser)", tags=["User"])
async def delete_user(username: str, super_authen: str = Depends(super_authen)):
    data = {
        'username': username
    }
    rowcount = sql.delete_user(data)
    if rowcount >= 1:
        return {'deleted_username': username}
    else:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="username doesnt exist"
        )


@app.post("/create_report", summary="Gửi báo cáo", status_code=status.HTTP_201_CREATED, tags=['Giao diện'])
async def create_report(
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
    lastrowid = sql.create_report(data)
    data.update({'id': lastrowid, 'request': request})
    return templates.TemplateResponse(
        "send_report.html", data)


@app.get("/get_report/{id}", summary="Xem báo cáo theo id", tags=['Giao diện', 'Báo cáo'])
async def get_report(request: Request, id: int, username: str = Depends(authen)):
    data = sql.get_report(id)
    if data:
        data.update({'request': request})
        return templates.TemplateResponse(
            "get_report.html", data)
    else:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="report doesnt exist"
        )


@app.delete("/delete_report/{id}",
            summary="Xoá báo cáo theo id (cần đăng nhập superuser)",
            tags=['Báo cáo'])
async def delete_report(id: int, username: str = Depends(super_authen)):
    rowcount = sql.delete_report(id)
    if rowcount >= 1:
        return {'deleted_report_id': id}
    else:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="report doesnt exist"
        )


@app.get("/get_pdf", summary="Tạo đơn báo cáo sự cố", tags=["Tạo file"])
async def get_pdf(
        id: int,
        hinh_thuc: str,
        ngay_bao_cao: str,
        don_vi_bao_cao: str,
        ho_ten_nguoi_benh: str,
        so_benh_an: str,
        ngay_sinh: str,
        gioi_tinh: str,
        doi_tuong: str,
        khoa_phong: str,
        vi_tri_xay_ra: str,
        vi_tri_cu_the: str,
        thoi_gian_xay_ra: str,
        mo_ta: str,
        de_xuat_giai_phap: str,
        xu_ly_ban_dau: str,
        thong_bao_cho_bac_si_hoac_nguoi_chiu_trach_nhiem: str,
        ghi_nhan_ho_so: str,
        thong_bao_cho_nguoi_nha_hoac_nguoi_bao_ho: str,
        thong_bao_cho_nguoi_benh: str,
        phan_loai_ban_dau: str,
        danh_gia_ban_dau: str,
        ho_ten_nguoi_bao_cao: str,
        so_dien_thoai_nguoi_bao_cao: str,
        email_nguoi_bao_cao: str,
        chuc_danh_nguoi_bao_cao: str,
        chuc_danh_khac: str,
        nguoi_chung_kien_1: str,
        nguoi_chung_kien_2: str):
    data = {
        "id": id,
        "hinh_thuc": hinh_thuc,
        "ngay_bao_cao": ngay_bao_cao,
        "don_vi_bao_cao": don_vi_bao_cao,
        "ho_ten_nguoi_benh": ho_ten_nguoi_benh,
        "so_benh_an": so_benh_an,
        "ngay_sinh": ngay_sinh,
        "gioi_tinh": gioi_tinh,
        "doi_tuong": doi_tuong,
        "khoa_phong": khoa_phong,
        "vi_tri_xay_ra": vi_tri_xay_ra,
        "vi_tri_cu_the": vi_tri_cu_the,
        "thoi_gian_xay_ra": thoi_gian_xay_ra,
        "mo_ta": mo_ta,
        "de_xuat_giai_phap": de_xuat_giai_phap,
        "xu_ly_ban_dau": xu_ly_ban_dau,
        "thong_bao_cho_bac_si_hoac_nguoi_chiu_trach_nhiem": thong_bao_cho_bac_si_hoac_nguoi_chiu_trach_nhiem,
        "ghi_nhan_ho_so": ghi_nhan_ho_so,
        "thong_bao_cho_nguoi_nha_hoac_nguoi_bao_ho": thong_bao_cho_nguoi_nha_hoac_nguoi_bao_ho,
        "thong_bao_cho_nguoi_benh": thong_bao_cho_nguoi_benh,
        "phan_loai_ban_dau": phan_loai_ban_dau,
        "danh_gia_ban_dau": danh_gia_ban_dau,
        "ho_ten_nguoi_bao_cao": ho_ten_nguoi_bao_cao,
        "so_dien_thoai_nguoi_bao_cao": so_dien_thoai_nguoi_bao_cao,
        "email_nguoi_bao_cao": email_nguoi_bao_cao,
        "chuc_danh_nguoi_bao_cao": chuc_danh_nguoi_bao_cao,
        "chuc_danh_khac": chuc_danh_khac,
        "nguoi_chung_kien_1": nguoi_chung_kien_1,
        "nguoi_chung_kien_2": nguoi_chung_kien_2}
    stream = io.BytesIO()
    create_pdf(stream, **data)
    stream.seek(0)
    response = StreamingResponse(stream, media_type="text/pdf")
    response.headers["Content-Disposition"] = f"attachment; filename=bao_cao_su_co_id_{id}.pdf"
    return response


@app.get("/get_csv", summary="Tải data (csv) về", tags=["Tạo file"])
async def get_csv(download: Optional[bool] = False, username: str = Depends(authen)):
    stream = io.StringIO()
    headers, data = sql.get_all_reports()
    writer = csv.writer(stream)
    writer.writerow(headers)
    writer.writerows(data)
    response = StreamingResponse(iter([stream.getvalue()]), media_type="text/csv")
    if download:
        response.headers["Content-Disposition"] = "attachment; filename=bao_cao_su_co.csv"
    return response

if __name__ == "__main__":
    # create_db()
    # print(bcrypt.hash('12345'))
    pass
