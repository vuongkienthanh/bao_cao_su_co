from typing import Optional
import datetime as dt
from enum import Enum
from pydantic import BaseModel, constr, EmailStr, Field

class Hinh_Thuc(str, Enum):
    tu_nguyen = "Tự nguyện"
    bat_buoc = "Bắt buộc"

class Gioi_Tinh(str, Enum):
    nam = "Nam"
    nu = "Nữ"

class Khoa_Phong(str, Enum):
    ngoai_than_kinh = "Ngoại thần kinh"
    noi_tong_quat = "Nội tổng quát"
    duoc = "Dược"
    xet_nghiem = "Xét nghiệm"
    quan_ly_chat_luong = "Quản lý chất lượng"
    tai_chinh_ke_toan = "Tài chính kế toán"
    ke_hoach_tong_hop = "Kế hoạch tổng hợp"
    to_chuc_can_bo = "Tổ chức cán bộ"
    ngoai_tong_hop = "Ngoại tổng hợp"
    phau_thuat_GMHS = "Phẫu thuật GMHS"
    ngoai_long_nguc = "Ngoại lồng ngực"
    so_sinh = "Sơ sinh"
    tai_mui_hong = "Tai mũi họng"
    tim_mach = "Tim mạch"
    ho_hap = "Hô hấp"
    tieu_hoa = "Tiêu hoá"
    than_noi_tiet = "Thận nội tiết"
    huyet_hoc_lam_sang = "Huyết học lâm sàng"


class Doi_Tuong(str, Enum):
    nguoi_benh = "Người bệnh"
    nguoi_nha_hoac_khach_den_tham = "Người nhà hoặc khách đến thăm"
    nhan_vien_y_te = "Nhân viên y tế"
    trang_thiet_bi_hoac_co_so_ha_tang = "Trang thiết bị hoặc cơ sở hạ tầng"

class Vi_Tri_Xay_Ra(str, Enum):
    ngoai_than_kinh = "Ngoại thần kinh"
    noi_tong_quat = "Nội tổng quát"
    duoc = "Dược"
    xet_nghiem = "Xét nghiệm"
    quan_ly_chat_luong = "Quản lý chất lượng"
    tai_chinh_ke_toan = "Tài chính kế toán"
    ke_hoach_tong_hop = "Kế hoạch tổng hợp"
    to_chuc_can_bo = "Tổ chức cán bộ"
    ngoai_tong_hop = "Ngoại tổng hợp"
    phau_thuat_GMHS = "Phẫu thuật GMHS"
    ngoai_long_nguc = "Ngoại lồng ngực"
    so_sinh = "Sơ sinh"
    tai_mui_hong = "Tai mũi họng"
    tim_mach = "Tim mạch"
    ho_hap = "Hô hấp"
    tieu_hoa = "Tiêu hoá"
    than_noi_tiet = "Thận nội tiết"
    huyet_hoc_lam_sang = "Huyết học lâm sàng"
    khac = "Khác"

class Ghi_Nhan_Enum(str, Enum):
    co = "Có"
    khong = "Không"
    khong_ghi_nhan = "Không ghi nhận"

class Phan_Loai_Ban_Dau(str, Enum):
    chua_xay_ra = "Chưa xảy ra"
    da_xay_ra = "Đã xảy ra"

class Danh_Gia_Ban_Dau(str,Enum):
    nang = "Nặng"
    trung_binh = "Trung bình"
    nhe = "Nhẹ"

class Chuc_Danh_Nguoi_Bao_Cao(str, Enum):
    bac_si = "Bác sĩ"
    dieu_duong = "Điều dưỡng"
    nguoi_benh = "Người bệnh"
    nguoi_nha_hoac_khach_den_tham = "Người nhà hoặc khách đến thăm"
    khac = "Khác"

class BCSC(BaseModel):
    hinh_thuc : Hinh_Thuc
    ngay_bao_cao: dt.date
    don_vi_bao_cao : Khoa_Phong
    ho_ten_nguoi_benh : str
    so_benh_an : constr(regex="^\d{8}$")
    ngay_sinh : dt.date
    gioi_tinh : Gioi_Tinh
    doi_tuong : Doi_Tuong
    vi_tri_xay_ra : Vi_Tri_Xay_Ra
    vi_tri_cu_the : str
    thoi_gian_xay_ra : dt.datetime
    mo_ta : str
    de_xuat_giai_phap : str
    xu_ly_ban_dau : str
    thong_bao_cho_bac_si_hoac_nguoi_chiu_trach_nhiem : Ghi_Nhan_Enum
    ghi_nhan_ho_so : Ghi_Nhan_Enum
    thong_bao_cho_nguoi_nha_hoac_nguoi_bao_ho : Ghi_Nhan_Enum
    thong_bao_cho_nguoi_benh : Ghi_Nhan_Enum
    phan_loai_ban_dau : Phan_Loai_Ban_Dau
    danh_gia_ban_dau : Danh_Gia_Ban_Dau
    ho_ten_nguoi_bao_cao : str
    so_dien_thoai_nguoi_bao_cao : constr(regex="^\d*$")
    email_nguoi_bao_cao: EmailStr
    chuc_danh_nguoi_bao_cao : Chuc_Danh_Nguoi_Bao_Cao
    chuc_danh_khac: Optional[str]
    nguoi_chung_kien_1 : str
    nguoi_chung_kien_2 : str