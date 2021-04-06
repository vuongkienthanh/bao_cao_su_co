# from schema import *
from init import *
from my_classes import MyResponse
from create_pdf import create_pdf
import create_thptsc_word
import sql
import my_email
import io
from typing import Optional, List
import datetime as dt
import csv
import os
from collections import defaultdict
from fastapi import (FastAPI, Request, Form, Query,
                     status, Depends, HTTPException,
                     UploadFile, File,
                     BackgroundTasks)
from fastapi.responses import StreamingResponse, FileResponse, RedirectResponse
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
<li>Form báo cáo, gửi về hệ thống lưu trữ bằng sqlite database.</li>
<li>Có thể upload hình ảnh, video.</li>
<li>Quản lý báo cáo.</li>
<li>Báo cáo cho phép tạo file pdf, tải về CSV để phân tích.</li>
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
    for f in [data_folder, tai_lieu_folder]:
        if not os.path.exists(f):
            os.mkdir(f)
    if not os.path.exists(db_path):
        sql.create_db()


@app.get("/", summary="Form báo cáo", tags=['Giao diện chính'], name='homepage')
async def root(request: Request):
    '''Giao diện form báo cáo chính'''
    return templates.TemplateResponse(
        "index.html",
        {"request": request})


@app.post("/create_user",
          summary="Tạo user mới (cần đăng nhập superuser)",
          status_code=status.HTTP_201_CREATED,
          tags=["User"])
async def create_user(username: str, password: str, superuser: bool, super_authen: str = Depends(super_authen)):
    '''Quản lý các tài khoản'''
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
    '''Quản lý các tài khoản'''
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


@app.post("/create_report", summary="Gửi báo cáo", status_code=status.HTTP_201_CREATED, tags=['Báo cáo'])
async def create_report(
        request: Request,
        background_tasks: BackgroundTasks,
        hinh_thuc: Optional[str] = Form(None, description="Hình thức báo cáo sự cố"),
        ngay_gio_bao_cao: dt.datetime = Form(..., description="Ngày giờ báo cáo sự cố, định dạng YYYY-MM-DD hh:mm"),
        don_vi_bao_cao: Optional[str] = Form(None, description="Đơn vị báo cáo là các khoa phòng trong bệnh viện"),
        ho_ten_nguoi_benh: Optional[str] = Form(None, description="Họ tên người bệnh. Ví dụ: Nguyễn Văn A"),
        so_benh_an: Optional[constr(regex="^\d{8}$")] = Form(None, description="Số hồ sơ bệnh án. Ví dụ: 19002000"),
        ngay_sinh: Optional[dt.date] = Form(None, description="Ngày sinh của người bệnh, định dạng YYYY-MM-DD"),
        gioi_tinh: Optional[str] = Form(None, description="Giới tính của người bệnh, nhận 2 giá trị là Nam và Nữ"),
        khoa_phong: Optional[str] = Form(None, description="Các khoa phòng trong bệnh viện"),
        doi_tuong: Optional[str] = Form(None, description="Đối tượng báo cáo: Người bệnh; Người nhà hoặc khách đến thăm; Nhân viên y tế; Trang thiết bị hoặc cơ sở hạ tầng"),
        vi_tri_xay_ra: Optional[str] = Form(None, description="Vị trí xảy ra sự cố. Ví dụ như ở khoa phòng, khuôn viên bệnh viện,.."),
        vi_tri_cu_the: Optional[str] = Form(None, description="Vị trí cụ thể như nhà vệ sinh, bãi giữ xe,.."),
        thoi_gian_xay_ra: Optional[dt.datetime] = Form(None, description="Thời gian xảy ra, định dạng YYYY-MM-DD hh:mm"),
        mo_ta: Optional[str] = Form(None, description="Mô tả ngắn gọn sự cố"),
        su_co_lien_quan: Optional[str] = Form(None),
        su_co_lien_quan_khac: Optional[str] = Form(None),
        de_xuat_giai_phap: Optional[str] = Form(None, description="Đề xuất giải pháp ban đầu"),
        xu_ly_ban_dau: Optional[str] = Form(None, description="Điều trị/xử lý ban đầu"),
        thong_bao_cho_bac_si_hoac_nguoi_chiu_trach_nhiem: Optional[str] = Form(None, description="Thông báo cho bác sĩ điều trị/người chịu trách nhiệm"),
        ghi_nhan_ho_so: Optional[str] = Form(None, description="Ghi nhận vào hồ sơ bệnh án/giấy tờ liên quan"),
        thong_bao_cho_nguoi_nha_hoac_nguoi_bao_ho: Optional[str] = Form(None, description="Thông báo cho người nhà hoặc người bảo hộ"),
        thong_bao_cho_nguoi_benh: Optional[str] = Form(None, description="Thông báo cho người bệnh"),
        phan_loai_ban_dau: Optional[str] = Form(None, description="Phân loại ban đầu"),
        danh_gia_ban_dau: Optional[str] = Form(None, description="Đánh giá ban đầu"),
        ho_ten_nguoi_bao_cao: str = Form(..., description="Họ tên người báo cáo"),
        so_dien_thoai_nguoi_bao_cao: Optional[constr(regex="^\d*$")] = Form(None, description="Số điện thoại người báo cáo"),
        email_nguoi_bao_cao: Optional[EmailStr] = Form(None, description="Email người báo cáo"),
        chuc_danh_nguoi_bao_cao: Optional[str] = Form(None, description="Chức danh người báo cáo:bác sĩ; điều dưỡng; người bệnh; người nhà/khách,.."),
        chuc_danh_khac: Optional[str] = Form(None, description="Chức danh khác (nêu rõ khi chọn khác ở mục trên)"),
        nguoi_chung_kien_1: Optional[str] = Form(None, description="Người chứng kiến 1"),
        nguoi_chung_kien_2: Optional[str] = Form(None, description="Người chứng kiến 2"),
        filepaths: Optional[List[UploadFile]] = File(None)):
    '''Gửi form data để lưu vào database, sau đó trả web thông báo đã nhận'''
    data = {
        "hinh_thuc": hinh_thuc,
        "ngay_gio_bao_cao": ngay_gio_bao_cao,
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
        "mo_ta": [x for x in [mo_ta, su_co_lien_quan, su_co_lien_quan_khac] if x is not None][0],
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
        "chuc_danh_nguoi_bao_cao": chuc_danh_khac if chuc_danh_nguoi_bao_cao == 'Khác' else chuc_danh_nguoi_bao_cao,
        "nguoi_chung_kien_1": nguoi_chung_kien_1,
        "nguoi_chung_kien_2": nguoi_chung_kien_2,
        "filepaths": filepaths}
    filepaths, lastrowid = sql.create_report(data)
    data.update({'id': lastrowid, 'request': request})
    # convert mov to mp4
    background_tasks.add_task(sql.convert_video, filepaths)
    # send mail base on environment variable to login mail server
    if my_email.is_OK():
        background_tasks.add_task(my_email.sendmail, data)
    return templates.TemplateResponse(
        "create_report.html", data)


@app.get("/report/{id}", summary="Xem báo cáo theo id", tags=['Báo cáo'])
async def report(request: Request, id: int, username: str = Depends(authen)):
    '''Xem báo cáo trên trang web, kèm theo link tạo pdf'''
    data = sql.get_report(id)
    if data:
        # extract only filename not the fullpath
        if data['filepaths']:
            data['filepaths'] = data['filepaths'].split(';')
            for i in range(len(data['filepaths'])):
                name = data['filepaths'][i].rsplit(os.path.sep, 1)[-1]
                data['filepaths'][i] = f'{name}'
        data.update({'request': request})
        return templates.TemplateResponse(
            "get_report.html", data)
    else:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="report doesnt exist"
        )


@app.delete("/delete_report/{id}",
            summary="Xoá báo cáo theo ID (cần đăng nhập superuser)",
            tags=['Báo cáo'])
async def delete_report(id: int, username: str = Depends(super_authen)):
    '''Xoá báo cáo theo ID'''
    rowcount = sql.delete_report(id)
    if rowcount >= 1:
        return {'deleted_report_id': id}
    else:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="report doesnt exist"
        )


@app.get("/get_upload_file", summary="Xem tài liệu hình ảnh, video",
         tags=['File'])
async def get_upload_file(request: Request, filename: str,
                          username: str = Depends(authen)):
    '''Dùng đẻ tải file tài liệu vào trang *get_quick_report*'''
    full_path = os.path.join(tai_lieu_folder, filename)
    if not full_path.lower().endswith('mp4'):
        return FileResponse(full_path)
    else:
        return MyResponse(full_path, request)


@app.get("/get_report_csv", summary="Tải data (csv) về", tags=["File"])
async def get_report_csv(
        download: Optional[bool] = False,
        start: Optional[dt.date] = dt.date(dt.date.today().year, 1, 1),
        end: Optional[dt.date] = dt.date.today() + dt.timedelta(days=1),
        full: Optional[bool] = False,
        username: str = Depends(authen)):
    '''Tải data (csv) về, với các tham số:
- *download*: Cho phép tải về trực tiếp vào máy. Mặc định: `false`.
- *start*: Thời điểm bắt đầu để lọc báo cáo. Mặc định là ngày đầu năm.
- *end*: Thời điểm kết thúc để lọc báo cáo. Mặc định là ngày hôm nay + 1.
- *full*: Tải tất cả dữ liệu. Mặc định: `false`.
    '''
    stream = io.StringIO()
    headers, data = sql.get_reports(start, end, full)
    writer = csv.writer(stream)
    writer.writerow(headers)
    writer.writerows(data)
    response = StreamingResponse(iter([stream.getvalue()]), media_type="text/csv")
    if download:
        response.headers["Content-Disposition"] = "attachment; filename=bao_cao_su_co.csv"
    return response


@app.get("/get_report_pdf", summary="Tạo đơn báo cáo sự cố", tags=["File"])
async def get_report_pdf(
        id: Optional[str] = Query(""),
        hinh_thuc: Optional[str] = Query(""),
        ngay_gio_bao_cao: Optional[str] = Query(""),
        don_vi_bao_cao: Optional[str] = Query(""),
        ho_ten_nguoi_benh: Optional[str] = Query(""),
        so_benh_an: Optional[str] = Query(""),
        ngay_sinh: Optional[str] = Query(""),
        gioi_tinh: Optional[str] = Query(""),
        doi_tuong: Optional[str] = Query(""),
        khoa_phong: Optional[str] = Query(""),
        vi_tri_xay_ra: Optional[str] = Query(""),
        vi_tri_cu_the: Optional[str] = Query(""),
        thoi_gian_xay_ra: Optional[str] = Query(""),
        mo_ta: Optional[str] = Query(""),
        de_xuat_giai_phap: Optional[str] = Query(""),
        xu_ly_ban_dau: Optional[str] = Query(""),
        thong_bao_cho_bac_si_hoac_nguoi_chiu_trach_nhiem: Optional[str] = Query(""),
        ghi_nhan_ho_so: Optional[str] = Query(""),
        thong_bao_cho_nguoi_nha_hoac_nguoi_bao_ho: Optional[str] = Query(""),
        thong_bao_cho_nguoi_benh: Optional[str] = Query(""),
        phan_loai_ban_dau: Optional[str] = Query(""),
        danh_gia_ban_dau: Optional[str] = Query(""),
        ho_ten_nguoi_bao_cao: Optional[str] = Query(""),
        so_dien_thoai_nguoi_bao_cao: Optional[str] = Query(""),
        email_nguoi_bao_cao: Optional[str] = Query(""),
        chuc_danh_nguoi_bao_cao: Optional[str] = Query(""),
        nguoi_chung_kien_1: Optional[str] = Query(""),
        nguoi_chung_kien_2: Optional[str] = Query("")):
    '''Tạo file pdf từ các tham số query, mẫu theo Bộ Y Tế'''
    data = {
        "id": id,
        "hinh_thuc": hinh_thuc,
        "ngay_gio_bao_cao": ngay_gio_bao_cao,
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
        "nguoi_chung_kien_1": nguoi_chung_kien_1,
        "nguoi_chung_kien_2": nguoi_chung_kien_2}
    stream = io.BytesIO()
    create_pdf(stream, **data)
    stream.seek(0)
    response = StreamingResponse(stream, media_type="text/pdf")
    response.headers["Content-Disposition"] = f"attachment; filename=bao_cao_su_co_id_{id}.pdf"
    return response


@app.post("/add_email", summary="Thêm địa chỉ email nhận thông báo", tags=["Email"])
async def add_email(
        email_: EmailStr = Query(..., description="email cần thêm vào"),
        username: str = Depends(authen)):
    '''Thêm địa chỉ email vào danh sách nhận thông báo khi có báo cáo mới'''
    if my_email.add_receiver_email(email_):
        return {'add_email': 'succeed'}
    else:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="email already in receiver list"
        )


@app.get("/get_emails", summary="Xem danh sách địa chỉ email nhận thông báo", tags=['Email'])
async def get_emails(username: str = Depends(authen)):
    '''Xem danh sách địa chỉ email nhận thông báo khi có báo cáo mới.'''
    return {'receiver_email_list': my_email.get_receiver_emails()}


@app.delete("/remove_email", summary="Xoá địa chỉ email nhận thông báo", tags=["Email"])
async def remove_email(
        email_: EmailStr = Query(..., description="email cần xoá"),
        username: str = Depends(authen)):
    '''Xoá địa chỉ email trong danh sách nhận thông báo khi có báo cáo mới'''
    if my_email.remove_receiver_email(email_):
        return {'remove_email': 'succeed'}
    else:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="email not in receiver list"
        )


@app.get('/thptsc/{id}', summary="Form tìm hiểu và phân tích sự cố", tags=['Báo cáo'])
async def thptsc(
        request: Request,
        id: int,
        username: str = Depends(authen)):
    '''Tìm hiểu và phân tích sự cố.'''
    # try get data from thptsc_db if none then from bao_cao_su_co
    data = defaultdict(lambda: None)
    res = sql.get_thptsc(id)
    if res:
        data.update(res)
        data.update({'in_thptsc_db': True})
    else:
        res2 = sql.get_report(id)
        if res2:
            data.update(res2)
            data.update({'in_thptsc_db': False})
    if data:
        data.update({'request': request})
        return templates.TemplateResponse(
            "thptsc.html", data)
    else:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND
        )


@app.post('/create_thptsc', summary="Gửi thptsc", tags=["Báo cáo"])
async def create_thptsc(
        request: Request,
        id: int = Form(None),
        mo_ta: Optional[str] = Form(None),
        v1a: Optional[str] = Form(None),
        v1b: Optional[str] = Form(None),
        v1c: Optional[str] = Form(None),
        v1d: Optional[str] = Form(None),
        v1e: Optional[str] = Form(None),
        v1f: Optional[str] = Form(None),
        v1g: Optional[str] = Form(None),
        v1h: Optional[str] = Form(None),
        v1i: Optional[str] = Form(None),
        v2a: Optional[str] = Form(None),
        v2b: Optional[str] = Form(None),
        v2c: Optional[str] = Form(None),
        v2d: Optional[str] = Form(None),
        v2e: Optional[str] = Form(None),
        v3a: Optional[str] = Form(None),
        v3b: Optional[str] = Form(None),
        v3c: Optional[str] = Form(None),
        v3d: Optional[str] = Form(None),
        v3e: Optional[str] = Form(None),
        v3f: Optional[str] = Form(None),
        v3g: Optional[str] = Form(None),
        v3h: Optional[str] = Form(None),
        v3i: Optional[str] = Form(None),
        v4a: Optional[str] = Form(None),
        v4b: Optional[str] = Form(None),
        v4c: Optional[str] = Form(None),
        v5a: Optional[str] = Form(None),
        v5b: Optional[str] = Form(None),
        v5c: Optional[str] = Form(None),
        v6a: Optional[str] = Form(None),
        v6b: Optional[str] = Form(None),
        v6c: Optional[str] = Form(None),
        v6d: Optional[str] = Form(None),
        v6e: Optional[str] = Form(None),
        v6f: Optional[str] = Form(None),
        v7: Optional[str] = Form(None),
        v8a: Optional[str] = Form(None),
        v8b: Optional[str] = Form(None),
        v9a: Optional[str] = Form(None),
        v9b: Optional[str] = Form(None),
        v9c: Optional[str] = Form(None),
        v10a: Optional[str] = Form(None),
        v10b: Optional[str] = Form(None),
        v10c: Optional[str] = Form(None),
        v10d: Optional[str] = Form(None),
        v10e: Optional[str] = Form(None),
        v10f: Optional[str] = Form(None),
        v11: Optional[str] = Form(None),
        xu_ly: Optional[str] = Form(None),
        v12a: Optional[str] = Form(None),
        v12b: Optional[str] = Form(None),
        v12c: Optional[str] = Form(None),
        v12d: Optional[str] = Form(None),
        v12e: Optional[str] = Form(None),
        v12f: Optional[str] = Form(None),
        v13a: Optional[str] = Form(None),
        v13b: Optional[str] = Form(None),
        v13c: Optional[str] = Form(None),
        v13d: Optional[str] = Form(None),
        v13e: Optional[str] = Form(None),
        v13f: Optional[str] = Form(None),
        v14a: Optional[str] = Form(None),
        v14b: Optional[str] = Form(None),
        v14c: Optional[str] = Form(None),
        v14d: Optional[str] = Form(None),
        v15a: Optional[str] = Form(None),
        v15b: Optional[str] = Form(None),
        v15c: Optional[str] = Form(None),
        v15d: Optional[str] = Form(None),
        v16a: Optional[str] = Form(None),
        v16b: Optional[str] = Form(None),
        v16c: Optional[str] = Form(None),
        v17: Optional[str] = Form(None),
        khac_phuc: Optional[str] = Form(None),
        de_xuat: Optional[str] = Form(None),
        danh_gia: Optional[str] = Form(None),
        v18: Optional[str] = Form(None),
        v19a: Optional[str] = Form(None),
        v19b: Optional[str] = Form(None),
        v20: Optional[str] = Form(None),
        v21a: Optional[str] = Form(None),
        v21b: Optional[str] = Form(None),
        v21c: Optional[str] = Form(None),
        v21d: Optional[str] = Form(None),
        v21e: Optional[str] = Form(None),
        v21f: Optional[str] = Form(None),
        v21g: Optional[str] = Form(None),
        chuc_danh: Optional[str] = Form(None),
        ngay_gio: dt.datetime = Form(...),
        username: str = Depends(authen)):
    data = {
        "id": id,
        "mo_ta": mo_ta,
        "v1a": 1 if v1a == 'true' else 0,
        "v1b": 1 if v1b == 'true' else 0,
        "v1c": 1 if v1c == 'true' else 0,
        "v1d": 1 if v1d == 'true' else 0,
        "v1e": 1 if v1e == 'true' else 0,
        "v1f": 1 if v1f == 'true' else 0,
        "v1g": 1 if v1g == 'true' else 0,
        "v1h": 1 if v1h == 'true' else 0,
        "v1i": 1 if v1i == 'true' else 0,
        "v2a": 1 if v2a == 'true' else 0,
        "v2b": 1 if v2b == 'true' else 0,
        "v2c": 1 if v2c == 'true' else 0,
        "v2d": 1 if v2d == 'true' else 0,
        "v2e": 1 if v2e == 'true' else 0,
        "v3a": 1 if v3a == 'true' else 0,
        "v3b": 1 if v3b == 'true' else 0,
        "v3c": 1 if v3c == 'true' else 0,
        "v3d": 1 if v3d == 'true' else 0,
        "v3e": 1 if v3e == 'true' else 0,
        "v3f": 1 if v3f == 'true' else 0,
        "v3g": 1 if v3g == 'true' else 0,
        "v3h": 1 if v3h == 'true' else 0,
        "v3i": 1 if v3i == 'true' else 0,
        "v4a": 1 if v4a == 'true' else 0,
        "v4b": 1 if v4b == 'true' else 0,
        "v4c": 1 if v4c == 'true' else 0,
        "v5a": 1 if v5a == 'true' else 0,
        "v5b": 1 if v5b == 'true' else 0,
        "v5c": 1 if v5c == 'true' else 0,
        "v6a": 1 if v6a == 'true' else 0,
        "v6b": 1 if v6b == 'true' else 0,
        "v6c": 1 if v6c == 'true' else 0,
        "v6d": 1 if v6d == 'true' else 0,
        "v6e": 1 if v6e == 'true' else 0,
        "v6f": 1 if v6f == 'true' else 0,
        "v7": 1 if v7 == 'true' else 0,
        "v8a": 1 if v8a == 'true' else 0,
        "v8b": 1 if v8b == 'true' else 0,
        "v9a": 1 if v9a == 'true' else 0,
        "v9b": 1 if v9b == 'true' else 0,
        "v9c": 1 if v9c == 'true' else 0,
        "v10a": 1 if v10a == 'true' else 0,
        "v10b": 1 if v10b == 'true' else 0,
        "v10c": 1 if v10c == 'true' else 0,
        "v10d": 1 if v10d == 'true' else 0,
        "v10e": 1 if v10e == 'true' else 0,
        "v10f": 1 if v10f == 'true' else 0,
        "v11": 1 if v11 == 'true' else 0,
        "xu_ly": xu_ly,
        "v12a": 1 if v12a == 'true' else 0,
        "v12b": 1 if v12b == 'true' else 0,
        "v12c": 1 if v12c == 'true' else 0,
        "v12d": 1 if v12d == 'true' else 0,
        "v12e": 1 if v12e == 'true' else 0,
        "v12f": 1 if v12f == 'true' else 0,
        "v13a": 1 if v13a == 'true' else 0,
        "v13b": 1 if v13b == 'true' else 0,
        "v13c": 1 if v13c == 'true' else 0,
        "v13d": 1 if v13d == 'true' else 0,
        "v13e": 1 if v13e == 'true' else 0,
        "v13f": 1 if v13f == 'true' else 0,
        "v14a": 1 if v14a == 'true' else 0,
        "v14b": 1 if v14b == 'true' else 0,
        "v14c": 1 if v14c == 'true' else 0,
        "v14d": 1 if v14d == 'true' else 0,
        "v15a": 1 if v15a == 'true' else 0,
        "v15b": 1 if v15b == 'true' else 0,
        "v15c": 1 if v15c == 'true' else 0,
        "v15d": 1 if v15d == 'true' else 0,
        "v16a": 1 if v16a == 'true' else 0,
        "v16b": 1 if v16b == 'true' else 0,
        "v16c": 1 if v16c == 'true' else 0,
        "v17": 1 if v17 == 'true' else 0,
        "khac_phuc": khac_phuc,
        "de_xuat": de_xuat,
        "danh_gia": danh_gia,
        "v18": v18,
        "v19a": v19a,
        "v19b": v19b,
        "v20": v20,
        "v21a": 1 if v21a == 'true' else 0,
        "v21b": 1 if v21b == 'true' else 0,
        "v21c": 1 if v21c == 'true' else 0,
        "v21d": 1 if v21d == 'true' else 0,
        "v21e": 1 if v21e == 'true' else 0,
        "v21f": 1 if v21f == 'true' else 0,
        "v21g": 1 if v21g == 'true' else 0,
        "ngay_gio": ngay_gio,
    }
    sql.create_thptsc(data)
    return RedirectResponse(request.url_for('homepage') + f'thptsc/{id}', status_code=303)


@app.get("/get_thptsc_csv", summary="Tải data thptsc (csv) về", tags=["File"])
async def get_thptsc_csv(
        download: Optional[bool] = False,
        start: Optional[dt.date] = dt.date(dt.date.today().year, 1, 1),
        end: Optional[dt.date] = dt.date.today() + dt.timedelta(days=1),
        full: Optional[bool] = False,
        username: str = Depends(authen)):
    '''Tải data (csv) về, với các tham số:
- *download*: Cho phép tải về trực tiếp vào máy. Mặc định: `false`.
- *start*: Thời điểm bắt đầu để lọc báo cáo. Mặc định là ngày đầu năm.
- *end*: Thời điểm kết thúc để lọc báo cáo. Mặc định là ngày hôm nay + 1.
- *full*: Tải tất cả dữ liệu. Mặc định: `false`.
    '''
    stream = io.StringIO()
    headers, data = sql.get_thptscs(start, end, full)
    writer = csv.writer(stream)
    writer.writerow(headers)
    writer.writerows(data)
    response = StreamingResponse(iter([stream.getvalue()]), media_type="text/csv")
    if download:
        response.headers["Content-Disposition"] = "attachment; filename=thptsc.csv"
    return response


@app.get("/get_thptsc_word", summary="Tạo mẫu tìm hiểu phân tích sự cố", tags=["File"])
def get_thptsc_word(
        id: Optional[str] = Query(''),
        mo_ta: Optional[str] = Query(''),
        v1a: Optional[int] = Query(0),
        v1b: Optional[int] = Query(0),
        v1c: Optional[int] = Query(0),
        v1d: Optional[int] = Query(0),
        v1e: Optional[int] = Query(0),
        v1f: Optional[int] = Query(0),
        v1g: Optional[int] = Query(0),
        v1h: Optional[int] = Query(0),
        v1i: Optional[int] = Query(0),
        v2a: Optional[int] = Query(0),
        v2b: Optional[int] = Query(0),
        v2c: Optional[int] = Query(0),
        v2d: Optional[int] = Query(0),
        v2e: Optional[int] = Query(0),
        v3a: Optional[int] = Query(0),
        v3b: Optional[int] = Query(0),
        v3c: Optional[int] = Query(0),
        v3d: Optional[int] = Query(0),
        v3e: Optional[int] = Query(0),
        v3f: Optional[int] = Query(0),
        v3g: Optional[int] = Query(0),
        v3h: Optional[int] = Query(0),
        v3i: Optional[int] = Query(0),
        v4a: Optional[int] = Query(0),
        v4b: Optional[int] = Query(0),
        v4c: Optional[int] = Query(0),
        v5a: Optional[int] = Query(0),
        v5b: Optional[int] = Query(0),
        v5c: Optional[int] = Query(0),
        v6a: Optional[int] = Query(0),
        v6b: Optional[int] = Query(0),
        v6c: Optional[int] = Query(0),
        v6d: Optional[int] = Query(0),
        v6e: Optional[int] = Query(0),
        v6f: Optional[int] = Query(0),
        v7: Optional[int] = Query(0),
        v8a: Optional[int] = Query(0),
        v8b: Optional[int] = Query(0),
        v9a: Optional[int] = Query(0),
        v9b: Optional[int] = Query(0),
        v9c: Optional[int] = Query(0),
        v10a: Optional[int] = Query(0),
        v10b: Optional[int] = Query(0),
        v10c: Optional[int] = Query(0),
        v10d: Optional[int] = Query(0),
        v10e: Optional[int] = Query(0),
        v10f: Optional[int] = Query(0),
        v11: Optional[int] = Query(0),
        xu_ly: Optional[str] = Query(''),
        v12a: Optional[int] = Query(0),
        v12b: Optional[int] = Query(0),
        v12c: Optional[int] = Query(0),
        v12d: Optional[int] = Query(0),
        v12e: Optional[int] = Query(0),
        v12f: Optional[int] = Query(0),
        v13a: Optional[int] = Query(0),
        v13b: Optional[int] = Query(0),
        v13c: Optional[int] = Query(0),
        v13d: Optional[int] = Query(0),
        v13e: Optional[int] = Query(0),
        v13f: Optional[int] = Query(0),
        v14a: Optional[int] = Query(0),
        v14b: Optional[int] = Query(0),
        v14c: Optional[int] = Query(0),
        v14d: Optional[int] = Query(0),
        v15a: Optional[int] = Query(0),
        v15b: Optional[int] = Query(0),
        v15c: Optional[int] = Query(0),
        v15d: Optional[int] = Query(0),
        v16a: Optional[int] = Query(0),
        v16b: Optional[int] = Query(0),
        v16c: Optional[int] = Query(0),
        v17: Optional[int] = Query(0),
        khac_phuc: Optional[str] = Query(''),
        de_xuat: Optional[str] = Query(''),
        danh_gia: Optional[str] = Query(''),
        v18: Optional[str] = Query(''),
        v19a: Optional[str] = Query(''),
        v19b: Optional[str] = Query(''),
        v20: Optional[str] = Query(''),
        v21a: Optional[int] = Query(0),
        v21b: Optional[int] = Query(0),
        v21c: Optional[int] = Query(0),
        v21d: Optional[int] = Query(0),
        v21e: Optional[int] = Query(0),
        v21f: Optional[int] = Query(0),
        v21g: Optional[int] = Query(0),
        chuc_danh: Optional[str] = Query(''),
        ngay_gio: Optional[str] = Query('')):
    data = {
        "id": id,
        "mo_ta": mo_ta,
        "v1a": v1a,
        "v1b": v1b,
        "v1c": v1c,
        "v1d": v1d,
        "v1e": v1e,
        "v1f": v1f,
        "v1g": v1g,
        "v1h": v1h,
        "v1i": v1i,
        "v2a": v2a,
        "v2b": v2b,
        "v2c": v2c,
        "v2d": v2d,
        "v2e": v2e,
        "v3a": v3a,
        "v3b": v3b,
        "v3c": v3c,
        "v3d": v3d,
        "v3e": v3e,
        "v3f": v3f,
        "v3g": v3g,
        "v3h": v3h,
        "v3i": v3i,
        "v4a": v4a,
        "v4b": v4b,
        "v4c": v4c,
        "v5a": v5a,
        "v5b": v5b,
        "v5c": v5c,
        "v6a": v6a,
        "v6b": v6b,
        "v6c": v6c,
        "v6d": v6d,
        "v6e": v6e,
        "v6f": v6f,
        "v7": v7,
        "v8a": v8a,
        "v8b": v8b,
        "v9a": v9a,
        "v9b": v9b,
        "v9c": v9c,
        "v10a": v10a,
        "v10b": v10b,
        "v10c": v10c,
        "v10d": v10d,
        "v10e": v10e,
        "v10f": v10f,
        "v11": v11,
        "xu_ly": xu_ly,
        "v12a": v12a,
        "v12b": v12b,
        "v12c": v12c,
        "v12d": v12d,
        "v12e": v12e,
        "v12f": v12f,
        "v13a": v13a,
        "v13b": v13b,
        "v13c": v13c,
        "v13d": v13d,
        "v13e": v13e,
        "v13f": v13f,
        "v14a": v14a,
        "v14b": v14b,
        "v14c": v14c,
        "v14d": v14d,
        "v15a": v15a,
        "v15b": v15b,
        "v15c": v15c,
        "v15d": v15d,
        "v16a": v16a,
        "v16b": v16b,
        "v16c": v16c,
        "v17": v17,
        "khac_phuc": khac_phuc,
        "de_xuat": de_xuat,
        "danh_gia": danh_gia,
        "v18": v18,
        "v19a": v19a,
        "v19b": v19b,
        "v20": v20,
        "v21a": v21a,
        "v21b": v21b,
        "v21c": v21c,
        "v21d": v21d,
        "v21e": v21e,
        "v21f": v21f,
        "v21g": v21g,
        "ngay_gio": ngay_gio
    }
    stream = io.BytesIO()
    create_thptsc_word.create(stream, **data)
    stream.seek(0)
    response = StreamingResponse(stream, media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document")
    response.headers["Content-Disposition"] = f"attachment; filename=thptsc_{id}.docx"
    return response


@app.delete("/delete_thptsc/{id}",
            summary="Xoá thptsc theo ID (cần đăng nhập superuser)",
            tags=['Báo cáo'])
async def delete_thptsc(id: int, username: str = Depends(super_authen)):
    '''Xoá báo cáo theo ID'''
    rowcount = sql.delete_thptsc(id)
    if rowcount >= 1:
        return {'deleted_thptsc_id': id}
    else:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="thptsc doesnt exist"
        )
