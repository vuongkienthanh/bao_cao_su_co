from init import fonts_folder
import textwrap
import os
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.pdfbase import pdfmetrics
from reportlab.lib.units import cm
from reportlab.lib.colors import white
from reportlab.pdfbase.ttfonts import TTFont


pdfmetrics.registerFont(TTFont('TNR', os.path.join(fonts_folder, 'times.ttf')))
pdfmetrics.registerFont(TTFont('TNRBold', os.path.join(fonts_folder, 'timesbd.ttf')))
pdfmetrics.registerFont(TTFont('TNRItalic', os.path.join(fonts_folder, 'timesi.ttf')))
fontname = 'TNR'
fontsize = 12
w, h = A4
ct_x = w * 0.1
ct_x2 = w * 0.13
ct_y = 0.88 * h
ct_w = w * 0.84
r1h = 0.51 * cm
pad = 0.1 * cm
line_x = 0.71 * ct_w
ct_x3 = line_x + pad


def cs(r, line=False):
    def mid(func):
        def inner(c, *arg, **kwarg):
            c.saveState()
            global ct_y
            c.rect(ct_x, ct_y - r1h * r - pad, ct_w, r1h * r + pad)
            if line:
                c.line(line_x, ct_y - r1h * r - pad, line_x, ct_y)
            result = func(c, *arg, **kwarg)
            ct_y = ct_y - r1h * r - pad
            c.restoreState()
            return result
        return inner
    return mid


def d_title(c):
    c.saveState()
    c.setFont('TNRBold', fontsize * 1.2)
    c.drawCentredString(w / 2, h * .91, 'MẪU BÁO CÁO SỰ CỐ Y KHOA')
    c.setFont('TNRItalic', fontsize*0.7)
    c.drawCentredString(w / 2, h * .89, 'Ban hành kèm theo Thông tư số 43/2018/TT-BYT ngày 26/12/2018 của Bộ trưởng Bộ Y Tế')
    c.restoreState()


@cs(r=4, line=True)
def d_top(c, *arg):
    c.setFont('TNRBold', fontsize)
    c.drawCentredString(w * 0.35, ct_y - r1h, 'HÌNH THỨC BÁO CÁO SỰ CỐ Y KHOA:')
    c.setFont('TNR', fontsize)
    c.drawCentredString(w * 0.35, ct_y - r1h * 2, 'Tự nguyện')
    c.acroForm.checkbox(name='tunguyen', checked=(arg[0] == 'Tự nguyện'),
                        x=w * 0.41, y=ct_y - r1h * 2, fillColor=white, size=12)
    c.drawCentredString(w * 0.35, ct_y - r1h * 3, 'Bắt buộc')
    c.acroForm.checkbox(name='batbuoc', checked=(arg[0] == 'Bắt buộc'),
                        x=w * 0.41, y=ct_y - r1h * 3, fillColor=white, size=12)
    textobj = c.beginText()
    textobj.setTextOrigin(ct_x3, ct_y - r1h)
    names = [
        'Mã số sự cố: ',
        'Ngày báo cáo: ',
    ]
    for i, n in enumerate(names):
        textobj.setFont("TNRItalic", fontsize)
        textobj.textOut(n)
        textobj.setFont("TNR", fontsize)
        textobj.textLine(str(arg[i + 1]))
    c.drawText(textobj)
    c.setFont('TNRItalic', fontsize)
    c.drawString(ct_x3, ct_y - r1h * 3, 'Đơn vị báo cáo: ')
    c.setFont('TNR', fontsize)
    c.drawString(ct_x3 + 10, ct_y - r1h * 4, arg[3])


@cs(r=1, line=True)
def d_info(c, *arg):
    c.setFont("TNRBold", fontsize)
    c.drawString(ct_x2, ct_y - r1h, 'Thông tin người bệnh')
    c.drawString(ct_x3, ct_y - r1h, 'Đối tượng xảy ra sự cố')


@cs(r=5, line=True)
def d_info2(c, *arg):
    textobj = c.beginText()
    textobj.setTextOrigin(ct_x2, ct_y - r1h)
    names = [
        'Họ tên người bệnh: ',
        'Số bệnh án: ',
        'Ngày sinh: ',
        'Giới tính: ',
        'Khoa/phòng: '
    ]
    for i, n in enumerate(names):
        textobj.setFont("TNRItalic", fontsize)
        textobj.textOut(n)
        textobj.setFont("TNR", fontsize)
        textobj.textLine(arg[i])
    c.drawText(textobj)
    opts = [
        'Người bệnh',
        'Người nhà hoặc khách đến thăm',
        'Nhân viên y tế',
        'Trang thiết bị hoặc cơ sở hạ tầng',
    ]
    for i, o in enumerate(opts):
        c.acroForm.checkbox(name=o, checked=(arg[5] == o),
                            x=ct_x3, y=ct_y - (i + 1) * r1h,
                            fillColor=white, size=12)
        c.drawString(ct_x3 + 20, ct_y - (i + 1) * r1h, o.replace(' hoặc ', '/'))


@cs(r=1)
def d_loc(c):
    c.setFont("TNRBold", fontsize)
    c.drawString(ct_x2, ct_y - r1h, 'Nơi xảy ra sự cố')


@cs(r=1, line=True)
def d_loc2(c, *arg):
    c.setFont("TNRBold", fontsize)
    c.drawString(ct_x2, ct_y - r1h, 'Khoa/phòng/vị trí xảy ra sự cố')
    c.drawString(ct_x3, ct_y - r1h, 'Vị trí cụ thể')


@cs(r=1, line=True)
def d_loc3(c, *arg):
    c.drawString(ct_x2, ct_y - r1h, arg[0])
    c.drawString(ct_x3, ct_y - r1h, arg[1])


@cs(r=1, line=True)
def d_time(c, *arg):
    if arg[0] == '':
        t = f"Ngày xảy ra sự cố:"
    else:
        t = f"Ngày xảy ra sự cố: {arg[0][:10]}"
    c.drawString(ct_x2, ct_y - r1h, t)
    c.drawString(ct_x3, ct_y - r1h, f'Thời gian: {arg[0][10:]}')


@cs(r=6)
def d_describe(c, *arg):
    t = textwrap.wrap('Mô tả ngắn gọn sự cố: ' + arg[0], 70)
    textobj = c.beginText()
    textobj.setTextOrigin(ct_x2, ct_y - r1h)
    for line in t:
        textobj.textLine(line)
    c.drawText(textobj)


@cs(r=3)
def d_describe2(c, *arg):
    t = textwrap.wrap('Đề xuất giải pháp ban đầu: ' + arg[0], 70)
    textobj = c.beginText()
    textobj.setTextOrigin(ct_x2, ct_y - r1h)
    for line in t:
        textobj.textLine(line)
    c.drawText(textobj)


@cs(r=3)
def d_describe3(c, *arg):
    t = textwrap.wrap('Điều trị/xử lý ban đầu đã được thực hiện: ' + arg[0], 70)
    textobj = c.beginText()
    textobj.setTextOrigin(ct_x2, ct_y - r1h)
    for line in t:
        textobj.textLine(line)
    c.drawText(textobj)


@cs(r=3, line=True)
def d_ghinhan(c, *arg):
    c.setFont("TNRBold", fontsize)
    c.drawString(ct_x2, ct_y - r1h, 'Thông báo cho bác sĩ điều trị/người có')
    c.drawString(ct_x2, ct_y - r1h * 2, 'trách nhiệm:')
    c.drawString(ct_x3, ct_y - r1h, 'Ghi nhận vào hồ sơ bệnh')
    c.drawString(ct_x3, ct_y - r1h * 2, 'án/giấy tờ liên quan:')
    c.setFont("TNR", fontsize)
    c.acroForm.checkbox(name='c0', checked=(arg[0] == 'Có'),
                        x=ct_x2, y=ct_y - r1h * 3, fillColor=white, size=12)
    c.drawString(ct_x2 + 15, ct_y - r1h * 3, 'Có')
    c.acroForm.checkbox(name='k0', checked=(arg[0] == 'Không'),
                        x=ct_x2 + 35, y=ct_y - r1h * 3, fillColor=white, size=12)
    c.drawString(ct_x2 + 50, ct_y - r1h * 3, 'Không')
    c.acroForm.checkbox(name='kgn0', checked=(arg[0] == 'Không ghi nhận'),
                        x=ct_x2 + 90, y=ct_y - r1h * 3, fillColor=white, size=12)
    c.drawString(ct_x2 + 105, ct_y - r1h * 3, 'Không ghi nhận')
    c.acroForm.checkbox(name='c1', checked=(arg[1] == 'Có'),
                        x=ct_x3, y=ct_y - r1h * 3, fillColor=white, size=12)
    c.drawString(ct_x3 + 15, ct_y - r1h * 3, 'Có')
    c.acroForm.checkbox(name='k1', checked=(arg[1] == 'Không'),
                        x=ct_x3 + 35, y=ct_y - r1h * 3, fillColor=white, size=12)
    c.drawString(ct_x3 + 50, ct_y - r1h * 3, 'Không')
    c.acroForm.checkbox(name='kgn1', checked=(arg[1] == 'Không ghi nhận'),
                        x=ct_x3 + 90, y=ct_y - r1h * 3, fillColor=white, size=12)
    c.drawString(ct_x3 + 105, ct_y - r1h * 3, 'Không ghi nhận')


@cs(r=2, line=True)
def d_ghinhan2(c, *arg):
    c.setFont("TNRBold", fontsize)
    c.drawString(ct_x2, ct_y - r1h, 'Thông báo cho người nhà/người bảo hộ')
    c.drawString(ct_x3, ct_y - r1h, 'Thông báo cho người bệnh')
    c.setFont("TNR", fontsize)
    c.acroForm.checkbox(name='c2', checked=(arg[0] == 'Có'),
                        x=ct_x2, y=ct_y - r1h * 2, fillColor=white, size=12)
    c.drawString(ct_x2 + 15, ct_y - r1h * 2, 'Có')
    c.acroForm.checkbox(name='k2', checked=(arg[0] == 'Không'),
                        x=ct_x2 + 35, y=ct_y - r1h * 2, fillColor=white, size=12)
    c.drawString(ct_x2 + 50, ct_y - r1h * 2, 'Không')
    c.acroForm.checkbox(name='kgn2', checked=(arg[0] == 'Không ghi nhận'),
                        x=ct_x2 + 90, y=ct_y - r1h * 2, fillColor=white, size=12)
    c.drawString(ct_x2 + 105, ct_y - r1h * 2, 'Không ghi nhận')
    c.acroForm.checkbox(name='c3', checked=(arg[1] == 'Có'),
                        x=ct_x3, y=ct_y - r1h * 2, fillColor=white, size=12)
    c.drawString(ct_x3 + 15, ct_y - r1h * 2, 'Có')
    c.acroForm.checkbox(name='k3', checked=(arg[1] == 'Không'),
                        x=ct_x3 + 35, y=ct_y - r1h * 2, fillColor=white, size=12)
    c.drawString(ct_x3 + 50, ct_y - r1h * 2, 'Không')
    c.acroForm.checkbox(name='kgn3', checked=(arg[1] == 'Không ghi nhận'),
                        x=ct_x3 + 90, y=ct_y - r1h * 2, fillColor=white, size=12)
    c.drawString(ct_x3 + 105, ct_y - r1h * 2, 'Không ghi nhận')


@cs(r=2)
def d_phanloai(c, *arg):
    c.setFont("TNRBold", fontsize)
    c.drawString(ct_x2, ct_y - r1h, 'Phân loại ban đầu về sự cố')
    c.setFont("TNR", fontsize)
    c.acroForm.checkbox(name='ch', checked=(arg[0] == 'Chưa xảy ra'),
                        x=ct_x2, y=ct_y - r1h * 2, fillColor=white, size=12)
    c.drawString(ct_x2 + 20, ct_y - r1h * 2, 'Chưa xảy ra')
    c.acroForm.checkbox(name='da', checked=(arg[0] == 'Đã xảy ra'),
                        x=ct_x2 + 100, y=ct_y - r1h * 2, fillColor=white, size=12)
    c.drawString(ct_x2 + 120, ct_y - r1h * 2, 'Đã xảy ra')


@cs(r=2)
def d_danhgia(c, *arg):
    c.setFont("TNRBold", fontsize)
    c.drawString(ct_x2, ct_y - r1h, 'Đánh giá ban đầu về mức độ ảnh hưởng của sự cố')
    c.setFont("TNR", fontsize)
    c.acroForm.checkbox(name='na', checked=(arg[0] == 'Nặng'),
                        x=ct_x2, y=ct_y - r1h * 2, fillColor=white, size=12)
    c.drawString(ct_x2 + 20, ct_y - r1h * 2, 'Nặng')
    c.acroForm.checkbox(name='tb', checked=(arg[0] == 'Trung bình'),
                        x=ct_x2 + 60, y=ct_y - r1h * 2, fillColor=white, size=12)
    c.drawString(ct_x2 + 80, ct_y - r1h * 2, 'Trung bình')
    c.acroForm.checkbox(name='nh', checked=(arg[0] == 'Nhẹ'),
                        x=ct_x2 + 150, y=ct_y - r1h * 2, fillColor=white, size=12)
    c.drawString(ct_x2 + 170, ct_y - r1h * 2, 'Nhẹ')


@cs(r=1)
def d_reporter(c):
    c.setFont("TNRBold", fontsize)
    c.drawString(ct_x2, ct_y - r1h, 'Thông tin người báo cáo')


@cs(r=1)
def d_reporter2(c, *arg):
    t = f"Họ tên: {arg[0]}   Số điện thoại: {arg[1]}   Email: {arg[2]}"
    c.drawString(ct_x2, ct_y - r1h, t)


@cs(r=2)
def d_reporter3(c, *arg):
    c.acroForm.checkbox(name='dr0', checked=(arg[0] == 'Điều dưỡng'),
                        x=ct_x2, y=ct_y - r1h, fillColor=white, size=12)
    c.drawString(ct_x2 + 15, ct_y - r1h, 'Điều dưỡng')
    c.acroForm.checkbox(name='dr1', checked=(arg[0] == 'Người bệnh'),
                        x=ct_x2 + 90, y=ct_y - r1h, fillColor=white, size=12)
    c.drawString(ct_x2 + 105, ct_y - r1h, 'Người bệnh')
    c.acroForm.checkbox(name='dr2', checked=(arg[0] == 'Người nhà hoặc khách đến thăm'),
                        x=ct_x2 + 175, y=ct_y - r1h, fillColor=white, size=12)
    c.drawString(ct_x2 + 190, ct_y - r1h, 'Người nhà/khách đến thăm')
    c.acroForm.checkbox(name='dr3', checked=(arg[0] == 'Bác sĩ'),
                        x=ct_x2, y=ct_y - r1h * 2, fillColor=white, size=12)
    c.drawString(ct_x2 + 15, ct_y - r1h * 2, 'Bác sĩ')
    check_khac = (arg[0] not in ['Điều dưỡng', 'Người bệnh', 'Người nhà hoặc khách đến thăm', 'Bác sĩ', ''])
    c.acroForm.checkbox(name='dr4',
                        checked=check_khac,
                        x=ct_x2 + 90, y=ct_y - r1h * 2, fillColor=white, size=12)
    c.drawString(ct_x2 + 105, ct_y - r1h * 2, f'Khác: {arg[0]}' if check_khac else "Khác")


@cs(r=2)
def d_obs(c, *arg):
    for i, n in enumerate(arg):
        t = f"Người chứng kiến {i+1}: {n}"
        c.drawString(ct_x2, ct_y - r1h * (i + 1), t)


def d_footer(c):
    t = 'Phụ lục 3: Mẫu báo cáo sự cố y khoa'
    c.setFont("TNR", fontsize * 0.6)
    c.drawString(w * 0.08, h * 0.1, t)
    t = "BM/BB.03/QT.QLCL.07 [2.0]"
    c.setFont("TNRItalic", fontsize * 0.6)
    c.drawString(w * 0.8, h * 0.1, t)


def create_pdf(stream, **kwarg):
    global ct_y
    if kwarg['id'] == -1:
        kwarg['id'] = ''
    c = canvas.Canvas(stream, pagesize=A4)
    c.setLineWidth(1)
    c.setStrokeColorRGB(0, 0, 0)
    c.setFont(fontname, fontsize)
    d_title(c)
    d_top(c,
          kwarg['hinh_thuc'],
          kwarg['id'],
          kwarg['ngay_gio_bao_cao'],
          kwarg['don_vi_bao_cao'])
    d_info(c)
    d_info2(c,
            kwarg["ho_ten_nguoi_benh"],
            kwarg["so_benh_an"],
            kwarg["ngay_sinh"],
            kwarg["gioi_tinh"],
            kwarg["khoa_phong"],
            kwarg["doi_tuong"])
    d_loc(c)
    d_loc2(c)
    d_loc3(c,
           kwarg["vi_tri_xay_ra"],
           kwarg["vi_tri_cu_the"])
    d_time(c, kwarg["thoi_gian_xay_ra"])
    d_describe(c, kwarg["mo_ta"])
    d_describe2(c, kwarg["de_xuat_giai_phap"])
    d_describe3(c, kwarg["xu_ly_ban_dau"])

    d_ghinhan(c,
              kwarg["thong_bao_cho_bac_si_hoac_nguoi_chiu_trach_nhiem"],
              kwarg["ghi_nhan_ho_so"])
    d_ghinhan2(c,
               kwarg["thong_bao_cho_nguoi_nha_hoac_nguoi_bao_ho"],
               kwarg["thong_bao_cho_nguoi_benh"])
    d_phanloai(c, kwarg["phan_loai_ban_dau"])
    d_danhgia(c, kwarg["danh_gia_ban_dau"])
    d_reporter(c)
    d_reporter2(c,
                kwarg["ho_ten_nguoi_bao_cao"],
                kwarg["so_dien_thoai_nguoi_bao_cao"],
                kwarg["email_nguoi_bao_cao"])
    d_reporter3(c, kwarg["chuc_danh_nguoi_bao_cao"])
    d_obs(c, kwarg["nguoi_chung_kien_1"], kwarg["nguoi_chung_kien_2"])
    d_footer(c)
    c.save()
    ct_y = 0.88 * h
