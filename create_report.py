from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import textwrap

pdfmetrics.registerFont(TTFont('Bitter', 'Bitter-Regular.ttf'))
pdfmetrics.registerFont(TTFont('BitterBold', 'Bitter-Bold.ttf'))
pdfmetrics.registerFont(TTFont('BitterItalic', 'Bitter-Italic.ttf'))
fontname = 'Bitter'
fontsize = 12
width, height = A4


def cs(func):
    def inner(c, *arg, **kwarg):
        c.saveState()
        result = func(c, *arg, **kwarg)
        c.restoreState()
        return result
    return inner


@cs
def d_title(c):
    c.setFont('BitterBold', fontsize * 1.5)
    c.drawCentredString(width / 2, height * .90, 'MẪU BÁO CÁO SỰ CỐ')


@cs
def d_upperright(c, *arg):
    textobj = c.beginText()
    textobj.setTextOrigin(width * 0.6, height * .85)
    textobj.setFont("BitterItalic", fontsize)
    textobj.textLine('Hình thức báo cáo sự cố: ')
    textobj.moveCursor(14, 0)
    textobj.setFont("Bitter", fontsize)
    textobj.textLine(str(arg[0]))
    textobj.moveCursor(-14, 0)
    names = [
        'Mã sự cố: ',
        'Ngày báo cáo: ',
    ]
    for i, n in enumerate(names):
        textobj.setFont("BitterItalic", fontsize)
        textobj.textOut(n)
        textobj.setFont("Bitter", fontsize)
        textobj.textLine(str(arg[i+1]))
    textobj.setFont("BitterItalic", fontsize)
    textobj.textLine('Đơn vị báo cáo: ')
    textobj.setFont("Bitter", fontsize)
    textobj.moveCursor(14, 0)
    textobj.textLine(arg[-1])
    c.drawText(textobj)


@cs
def d_info(c, *arg):
    c.setFont("BitterBold", fontsize)
    c.drawString(width * 0.13, height * .87, 'Thông tin người bệnh')
    textobj = c.beginText()
    textobj.setTextOrigin(width * 0.1, height * .85)
    names = [
        'Họ tên người bệnh:         ',
        'Số bệnh án:                          ',
        'Ngày sinh:                            ',
        'Giới tính:                                ',
        'Khoa/phòng:                       ',
        'Đối tượng xảy ra sự cố: '
    ]
    for i, n in enumerate(names):
        textobj.setFont("BitterItalic", fontsize)
        textobj.textOut(n)
        textobj.setFont("Bitter", fontsize)
        textobj.textLine(arg[i])
    c.drawText(textobj)


@cs
def d_loc(c, *arg):
    textobj = c.beginText()
    textobj.setTextOrigin(width * 0.13, height * .73)
    textobj.setFont("BitterBold", fontsize)
    textobj.textOut('Nơi xảy ra sự cố:            ')
    textobj.setFont("Bitter", fontsize)
    textobj.textLine(f'      Khu {arg[0]} - {arg[1]}')
    textobj.setFont("BitterBold", fontsize)
    textobj.textOut('Thời gian xảy ra sự cố:    ')
    textobj.setFont("Bitter", fontsize)
    textobj.textOut(arg[2])
    c.drawText(textobj)


@cs
def d_describe(c, *arg):
    textobj = c.beginText()
    textobj.setTextOrigin(width * 0.13, height * 0.68)
    textobj.setFont("BitterBold", fontsize)
    textobj.textLine('Mô tả ngắn gọn sự cố:')
    textobj.moveCursor(-14, 0)
    textobj.setFont("Bitter", fontsize)
    for line in arg[0]:
        textobj.textLine(line)
    textobj.moveCursor(14, 10)
    textobj.setFont("BitterBold", fontsize)
    textobj.textLine('Đề xuất giải pháp ban đầu:')
    textobj.moveCursor(-14, 0)
    textobj.setFont("Bitter", fontsize)
    for line in arg[1]:
        textobj.textLine(line)
    textobj.moveCursor(14, 10)
    textobj.setFont("BitterBold", fontsize)
    textobj.textLine('Điều trị/xử lý ban đầu đã được thực hiện:')
    textobj.moveCursor(-14, 0)
    textobj.setFont("Bitter", fontsize)
    for line in arg[2]:
        textobj.textLine(line)
    c.drawText(textobj)
    return sum([len(x) for x in arg])


@cs
def d_ghinhan(c, rows, *arg):
    textobj = c.beginText()
    textobj.setTextOrigin(width * 0.13, (height * .57) - (rows * 14))
    names = [
        'Thông báo cho bác sĩ điều trị/người có trách nhiệm: ',
        'Ghi nhận vào hồ sơ bệnh án/giấy tờ liên quan: ',
        'Thông báo cho người nhà/người bảo hộ: ',
        'Thông báo cho người bệnh: ',
        'Phân loại ban đầu về sự cố: ',
        'Đánh giá ban đầu về mức độ ảnh hưởng của sự cố: '
    ]
    for i, n in enumerate(names):
        textobj.setFont("BitterItalic", fontsize)
        textobj.textOut(n)
        textobj.setFont("Bitter", fontsize)
        textobj.textLine(arg[i])
    c.drawText(textobj)


@cs
def d_reporter(c, rows, *arg):
    textobj = c.beginText()
    textobj.setTextOrigin(width * 0.13, (height * .45) - (rows * 14))
    textobj.setFont("BitterBold", fontsize)
    textobj.textLine('Thông tin người báo cáo:')
    textobj.moveCursor(-14, 0)
    names = [
        'Họ tên: ',
        'Số điện thoại: ',
        'Email: ',
        'Chức danh: ',
    ]
    for i, n in enumerate(names):
        textobj.setFont("BitterItalic", fontsize)
        textobj.textOut(n)
        textobj.setFont("Bitter", fontsize)
        textobj.textLine(arg[i])
    c.drawText(textobj)


@cs
def d_obs(c, rows, *arg):
    textobj = c.beginText()
    textobj.setTextOrigin(width * 0.6, (height * .433) - (rows * 14))
    names = [
        'Người chứng kiến 1:',
        'Người chứng kiến 2:'
    ]
    for i, n in enumerate(names):
        textobj.setFont("BitterItalic", fontsize)
        textobj.textLine(n)
        textobj.setFont("Bitter", fontsize)
        textobj.textLine(arg[i])
    c.drawText(textobj)


def create_pdf(stream, **kwarg):
    c = canvas.Canvas(stream, pagesize=A4)
    c.setFont(fontname, fontsize)
    d_title(c)
    d_upperright(c,
                 kwarg['hinh_thuc'],
                 kwarg['id'],
                 kwarg['ngay_bao_cao'],
                 kwarg['don_vi_bao_cao'])
    d_info(c,
           kwarg["ho_ten_nguoi_benh"],
           kwarg["so_benh_an"],
           kwarg["ngay_sinh"],
           kwarg["gioi_tinh"],
           kwarg["khoa_phong"],
           kwarg["doi_tuong"])
    d_loc(c,
          kwarg["vi_tri_xay_ra"],
          kwarg["vi_tri_cu_the"],
          kwarg["thoi_gian_xay_ra"])
    rows = d_describe(c,
                      textwrap.wrap(kwarg["mo_ta"], 80),
                      textwrap.wrap(kwarg["de_xuat_giai_phap"], 80),
                      textwrap.wrap(kwarg["xu_ly_ban_dau"], 80))
    d_ghinhan(c, rows,
              kwarg["thong_bao_cho_bac_si_hoac_nguoi_chiu_trach_nhiem"],
              kwarg["ghi_nhan_ho_so"],
              kwarg["thong_bao_cho_nguoi_nha_hoac_nguoi_bao_ho"],
              kwarg["thong_bao_cho_nguoi_benh"],
              kwarg["phan_loai_ban_dau"],
              kwarg["danh_gia_ban_dau"])
    d_reporter(c,rows,
               kwarg["ho_ten_nguoi_bao_cao"],
               kwarg["so_dien_thoai_nguoi_bao_cao"],
               kwarg["email_nguoi_bao_cao"],
               kwarg["chuc_danh_nguoi_bao_cao"])
    d_obs(c, rows,kwarg["nguoi_chung_kien_1"], kwarg["nguoi_chung_kien_2"])
    c.save()
