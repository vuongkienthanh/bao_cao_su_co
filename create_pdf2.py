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
pdfmetrics.registerFont(TTFont('TNRItalic', os.path.join(fonts_folder, 'timesbi.ttf')))
fontname = 'TNR'
fontsize = 12
w, h = A4
ct_x = w * 0.08
ct_x2 = ct_x + 0.2 * cm
ct_y = 0.84 * h
ct_w = w * 0.85
r1 = 0.74 * cm
r2 = 0.6 * cm
pad = 0.2 * cm
line_x = 0.42 * ct_w
ct_x3 = line_x + pad
ct_x4 = line_x + 7 * cm
line_x2 = 0.26 * ct_w
ct_x32 = line_x2 + pad
ct_x42 = line_x2 + 7 * cm

wr = 90  # wrap


def reset_y():
    global ct_y
    ct_y = 0.84 * h


def next_page(c):
    global ct_y
    c.showPage()
    ct_y = 0.90 * h
    c.setLineWidth(1)
    c.setStrokeColorRGB(0, 0, 0)
    c.setFont(fontname, fontsize)


def cs(r, line=False, line2=False, rh=r1):
    def mid(func):
        def inner(c, *arg, **kwarg):
            c.saveState()
            global ct_y
            c.rect(ct_x, ct_y - rh * r - pad, ct_w, rh * r + pad)
            if line:
                c.line(line_x, ct_y - rh * r - pad, line_x, ct_y)
            if line2:
                c.line(line_x2, ct_y - rh * r - pad, line_x2, ct_y)
            result = func(c, *arg, **kwarg)
            ct_y = ct_y - rh * r - pad
            c.restoreState()
            return result
        return inner
    return mid


def d_title(c, *args):
    c.saveState()
    c.setFont('TNRBold', fontsize * 1.2)
    c.drawCentredString(w / 2, h * .91, 'MẪU TÌM HIỂU VÀ PHÂN TÍCH SỰ CỐ')
    c.drawCentredString(w / 2, h * .87, f'Số báo cáo/Mã số sự cố: {args[0]}')
    c.drawString(ct_x2, h * .85, 'A. Dành cho nhân viên chuyên trách')
    c.setFont('TNRItalic', fontsize * .7)
    c.drawCentredString(w / 2, h * .89, '(Ban hành kèm theo Thông tư số 43/2018/TT-BYT ngày 26/12/2018 của Bộ trưởng Bộ Y tế)')
    c.restoreState()


@cs(r=1)
def p1a(c, *args):
    c.setFont('TNRBold', fontsize)
    c.drawString(ct_x2, ct_y - r1, 'I. Mô tả chi tiết sự cố')


@cs(r=10)
def p1b(c, *args):
    t = textwrap.wrap(args[0], wr)
    for i in range(len(t)):
        c.drawString(ct_x2, ct_y - r2 * (i + 1), t[i])


@cs(r=1)
def p1c(c, *args):
    c.setFont('TNRBold', fontsize)
    c.drawString(ct_x2, ct_y - r1, 'II. Phân loại sự cố theo nhóm sự cố (Incident type)')


@cs(r=10, line=True)
def p1d(c, *args):
    c.drawString(ct_x2, ct_y - r1 * 4, "1. Thực hiện quy trình kỹ")
    c.drawString(ct_x2, ct_y - r1 * 5, "thuật, thủ thuật chuyên môn")
    c.acroForm.checkbox(name='v1a', checked=(args[0] == 1),
                        x=ct_x3, y=ct_y - r1, fillColor=white, size=12)
    c.drawString(ct_x3 + 15, ct_y - r1, "Không có sự đồng ý của người bệnh/người nhà (đối với")
    c.drawString(ct_x3, ct_y - r1 * 2, "những kỹ thuật, thủ thuật quy định phải ký cam kết)")
    c.acroForm.checkbox(name='v1b', checked=(args[1] == 1),
                        x=ct_x3, y=ct_y - r1 * 3, fillColor=white, size=12)
    c.drawString(ct_x3 + 15, ct_y - r1 * 3, "Không thực hiện khi có chỉ định")
    c.acroForm.checkbox(name='v1c', checked=(args[2] == 1),
                        x=ct_x3, y=ct_y - r1 * 4, fillColor=white, size=12)
    c.drawString(ct_x3 + 15, ct_y - r1 * 4, "Thực hiện sai người bệnh")
    c.acroForm.checkbox(name='v1d', checked=(args[3] == 1),
                        x=ct_x3, y=ct_y - r1 * 5, fillColor=white, size=12)
    c.drawString(ct_x3 + 15, ct_y - r1 * 5, "Thực hiện sai thủ thuật/quy trình/phương pháp điều trị")
    c.acroForm.checkbox(name='v1e', checked=(args[4] == 1),
                        x=ct_x3, y=ct_y - r1 * 6, fillColor=white, size=12)
    c.drawString(ct_x3 + 15, ct_y - r1 * 6, "Thực hiện sai vị trí phẫu thuật/thủ thuật")
    c.acroForm.checkbox(name='v1f', checked=(args[5] == 1),
                        x=ct_x3, y=ct_y - r1 * 7, fillColor=white, size=12)
    c.drawString(ct_x3 + 15, ct_y - r1 * 7, "Bỏ sót dụng cụ, vật tư tiêu hao trong quá trình phẫu thuật")
    c.acroForm.checkbox(name='v1g', checked=(args[6] == 1),
                        x=ct_x3, y=ct_y - r1 * 8, fillColor=white, size=12)
    c.drawString(ct_x3 + 15, ct_y - r1 * 8, "Tử vong trong thai kỳ")
    c.acroForm.checkbox(name='v1h', checked=(args[7] == 1),
                        x=ct_x3, y=ct_y - r1 * 9, fillColor=white, size=12)
    c.drawString(ct_x3 + 15, ct_y - r1 * 9, "Tử vong khi sinh")
    c.acroForm.checkbox(name='v1i', checked=(args[8] == 1),
                        x=ct_x3, y=ct_y - r1 * 10, fillColor=white, size=12)
    c.drawString(ct_x3 + 15, ct_y - r1 * 10, "Tử vong sơ sinh")


@cs(r=3, line=True)
def p1e(c, *args):
    c.drawString(ct_x2, ct_y - r1 * 2, "2. Nhiễm khuẩn bệnh viện")
    c.acroForm.checkbox(name='v2a', checked=(args[0] == 1),
                        x=ct_x3, y=ct_y - r1, fillColor=white, size=12)
    c.drawString(ct_x3 + 15, ct_y - r1, "Nhiễm khuẩn huyết")
    c.acroForm.checkbox(name='v2b', checked=(args[1] == 1),
                        x=ct_x4, y=ct_y - r1, fillColor=white, size=12)
    c.drawString(ct_x4 + 15, ct_y - r1, "Nhiễm khuẩn vết mổ")
    c.acroForm.checkbox(name='v2c', checked=(args[2] == 1),
                        x=ct_x3, y=ct_y - r1 * 2, fillColor=white, size=12)
    c.drawString(ct_x3 + 15, ct_y - r1 * 2, "Viêm phổi")
    c.acroForm.checkbox(name='v2d', checked=(args[3] == 1),
                        x=ct_x4, y=ct_y - r1 * 2, fillColor=white, size=12)
    c.drawString(ct_x4 + 15, ct_y - r1 * 2, "Nhiễm khuẩn tiết niệu")
    c.acroForm.checkbox(name='v2e', checked=(args[4] == 1),
                        x=ct_x3, y=ct_y - r1 * 3, fillColor=white, size=12)
    c.drawString(ct_x3 + 15, ct_y - r1 * 3, "Các loại nhiễm khuẩn khác")


@cs(r=5, line=True)
def p1f(c, *args):
    c.drawString(ct_x2, ct_y - r1 * 3, "3. Thuốc và dịch truyền")
    c.acroForm.checkbox(name='v3a', checked=(args[0] == 1),
                        x=ct_x3, y=ct_y - r1, fillColor=white, size=12)
    c.drawString(ct_x3 + 15, ct_y - r1, "Cấp phát sai thuốc, dịch truyền")
    c.acroForm.checkbox(name='v3b', checked=(args[1] == 1),
                        x=ct_x4, y=ct_y - r1, fillColor=white, size=12)
    c.drawString(ct_x4 + 15, ct_y - r1, "Bỏ sót thuốc/liều thuốc")
    c.acroForm.checkbox(name='v3c', checked=(args[2] == 1),
                        x=ct_x3, y=ct_y - r1 * 2, fillColor=white, size=12)
    c.drawString(ct_x3 + 15, ct_y - r1 * 2, "Thiếu thuốc")
    c.acroForm.checkbox(name='v3d', checked=(args[3] == 1),
                        x=ct_x4, y=ct_y - r1 * 2, fillColor=white, size=12)
    c.drawString(ct_x4 + 15, ct_y - r1 * 2, "Sai thuốc")
    c.acroForm.checkbox(name='v3e', checked=(args[4] == 1),
                        x=ct_x3, y=ct_y - r1 * 3, fillColor=white, size=12)
    c.drawString(ct_x3 + 15, ct_y - r1 * 3, "Sai liều, sai hàm lượng")
    c.acroForm.checkbox(name='v3f', checked=(args[5] == 1),
                        x=ct_x4, y=ct_y - r1 * 3, fillColor=white, size=12)
    c.drawString(ct_x4 + 15, ct_y - r1 * 3, "Sai người bệnh")
    c.acroForm.checkbox(name='v3g', checked=(args[6] == 1),
                        x=ct_x3, y=ct_y - r1 * 4, fillColor=white, size=12)
    c.drawString(ct_x3 + 15, ct_y - r1 * 4, "Sai thời gian")
    c.acroForm.checkbox(name='v3h', checked=(args[7] == 1),
                        x=ct_x4, y=ct_y - r1 * 4, fillColor=white, size=12)
    c.drawString(ct_x4 + 15, ct_y - r1 * 4, "Sai đường dùng")
    c.acroForm.checkbox(name='v3i', checked=(args[8] == 1),
                        x=ct_x3, y=ct_y - r1 * 5, fillColor=white, size=12)
    c.drawString(ct_x3 + 15, ct_y - r1 * 5, "Sai y lệnh")


@cs(r=3, line=True)
def p1g(c, *args):
    c.drawString(ct_x2, ct_y - r1 * 1.5, "4. Máu và các chế phẩm")
    c.drawString(ct_x2, ct_y - r1 * 2.5, "máu")
    c.acroForm.checkbox(name='v4a', checked=(args[0] == 1),
                        x=ct_x3, y=ct_y - r1, fillColor=white, size=12)
    c.drawString(ct_x3 + 15, ct_y - r1, "Phản ứng phụ, tai biến khi truyền máu")
    c.acroForm.checkbox(name='v4b', checked=(args[1] == 1),
                        x=ct_x3, y=ct_y - r1 * 2, fillColor=white, size=12)
    c.drawString(ct_x3 + 15, ct_y - r1 * 2, "Truyền nhầm máu, chế phẩm máu")
    c.acroForm.checkbox(name='v4c', checked=(args[2] == 1),
                        x=ct_x3, y=ct_y - r1 * 3, fillColor=white, size=12)
    c.drawString(ct_x3 + 15, ct_y - r1 * 3, "Truyền sai liều, sai thời điểm")


@cs(r=3, line=True)
def p2a(c, *args):
    c.drawString(ct_x2, ct_y - r1 * 2, "5. Thiết bị y tế")
    c.acroForm.checkbox(name='v5a', checked=(args[0] == 1),
                        x=ct_x3, y=ct_y - r1, fillColor=white, size=12)
    c.drawString(ct_x3 + 15, ct_y - r1, "Thiếu thông tin hướng dẫn sử dụng")
    c.acroForm.checkbox(name='v5b', checked=(args[1] == 1),
                        x=ct_x3, y=ct_y - r1 * 2, fillColor=white, size=12)
    c.drawString(ct_x3 + 15, ct_y - r1 * 2, "Lỗi thiết bị")
    c.acroForm.checkbox(name='v5c', checked=(args[2] == 1),
                        x=ct_x3, y=ct_y - r1 * 3, fillColor=white, size=12)
    c.drawString(ct_x3 + 15, ct_y - r1 * 3, "Thiết bị thiếu hoặc không phù hợp")


@cs(r=6, line=True)
def p2b(c, *args):
    c.drawString(ct_x2, ct_y - r1 * 2.5, "6. Hành vi")
    c.acroForm.checkbox(name='v6a', checked=(args[0] == 1),
                        x=ct_x3, y=ct_y - r1, fillColor=white, size=12)
    c.drawString(ct_x3 + 15, ct_y - r1, "Khuynh hướng tự gây hại, tự tử")
    c.acroForm.checkbox(name='v6b', checked=(args[1] == 1),
                        x=ct_x3, y=ct_y - r1 * 2, fillColor=white, size=12)
    c.drawString(ct_x3 + 15, ct_y - r1 * 2, "Có hành động tự tử")
    c.acroForm.checkbox(name='v6c', checked=(args[2] == 1),
                        x=ct_x3, y=ct_y - r1 * 3, fillColor=white, size=12)
    c.drawString(ct_x3 + 15, ct_y - r1 * 3, "Quấy rối tình dục bởi nhân viên")
    c.acroForm.checkbox(name='v6d', checked=(args[3] == 1),
                        x=ct_x3, y=ct_y - r1 * 4, fillColor=white, size=12)
    c.drawString(ct_x3 + 15, ct_y - r1 * 4, "Trốn viện")
    c.acroForm.checkbox(name='v6e', checked=(args[4] == 1),
                        x=ct_x3, y=ct_y - r1 * 5, fillColor=white, size=12)
    c.drawString(ct_x3 + 15, ct_y - r1 * 5, "Quấy rối tình dục bởi người bệnh/khách đến thăm")
    c.acroForm.checkbox(name='v6f', checked=(args[5] == 1),
                        x=ct_x3, y=ct_y - r1 * 6, fillColor=white, size=12)
    c.drawString(ct_x3 + 15, ct_y - r1 * 6, "Xâm hại cơ thể bởi người bệnh/khách đến thăm")


@cs(r=1, line=True)
def p2c(c, *args):
    c.drawString(ct_x2, ct_y - r1, "7. Tai nạn đối với người bệnh")
    c.acroForm.checkbox(name="v7", checked=(args[0] == 1),
                        x=ct_x3, y=ct_y - r1, fillColor=white, size=12)
    c.drawString(ct_x3 + 15, ct_y - r1, "Té ngã")


@cs(r=2, line=True)
def p2d(c, *args):
    c.drawString(ct_x2, ct_y - r1 * 1.5, "8. Hạ tầng cơ sở")
    c.acroForm.checkbox(name="v8a", checked=(args[0] == 1),
                        x=ct_x3, y=ct_y - r1, fillColor=white, size=12)
    c.drawString(ct_x3 + 15, ct_y - r1, "Bị hư hỏng, bị lỗi")
    c.acroForm.checkbox(name="v8b", checked=(args[1] == 1),
                        x=ct_x3, y=ct_y - r1 * 2, fillColor=white, size=12)
    c.drawString(ct_x3 + 15, ct_y - r1 * 2, "Thiếu hoặc không phù hợp")


@cs(r=4, line=True)
def p2e(c, *args):
    c.drawString(ct_x2, ct_y - r1 * 2.5, "9. Quản lý nguồn lực, tổ chức")
    c.acroForm.checkbox(name="v9a", checked=(args[0] == 1),
                        x=ct_x3, y=ct_y - r1, fillColor=white, size=12)
    c.drawString(ct_x3 + 15, ct_y - r1, "Tính phù hợp, đầy đủ của dịch vụ khám bệnh, chữa bệnh")
    c.acroForm.checkbox(name="v9b", checked=(args[1] == 1),
                        x=ct_x3, y=ct_y - r1 * 2, fillColor=white, size=12)
    c.drawString(ct_x3 + 15, ct_y - r1 * 2, "Tính phù hợp, đầy đủ của nguồn lực")
    c.acroForm.checkbox(name="v9c", checked=(args[2] == 1),
                        x=ct_x3, y=ct_y - r1 * 3, fillColor=white, size=12)
    c.drawString(ct_x3 + 15, ct_y - r1 * 3, "Tính phù hợp, đầy đủ của chính sách, quy định, quy trình")
    c.drawString(ct_x3, ct_y - r1 * 4, "hướng dẫn chuyên môn")


@cs(r=6, line=True)
def p2f(c, *args):
    c.drawString(ct_x2, ct_y - r1 * 2.5, "10. Hồ sơ, tài liệu, thủ tục")
    c.drawString(ct_x2, ct_y - r1 * 3.5, "hành chính")
    c.acroForm.checkbox(name="v10a", checked=(args[0] == 1),
                        x=ct_x3, y=ct_y - r1, fillColor=white, size=12)
    c.drawString(ct_x3 + 15, ct_y - r1, "Tài liệu mất hoặc thiếu")
    c.acroForm.checkbox(name="v10b", checked=(args[1] == 1),
                        x=ct_x3, y=ct_y - r1 * 2, fillColor=white, size=12)
    c.drawString(ct_x3 + 15, ct_y - r1 * 2, "Cung cấp hồ sơ tài liệu chậm")
    c.acroForm.checkbox(name="v10c", checked=(args[2] == 1),
                        x=ct_x3, y=ct_y - r1 * 3, fillColor=white, size=12)
    c.drawString(ct_x3 + 15, ct_y - r1 * 3, "Tài liệu không rõ ràng, không hoàn thiện")
    c.acroForm.checkbox(name="v10d", checked=(args[3] == 1),
                        x=ct_x3, y=ct_y - r1 * 4, fillColor=white, size=12)
    c.drawString(ct_x3 + 15, ct_y - r1 * 4, "Nhầm hồ sơ tài liệu")
    c.acroForm.checkbox(name="v10e", checked=(args[4] == 1),
                        x=ct_x3, y=ct_y - r1 * 5, fillColor=white, size=12)
    c.drawString(ct_x3 + 15, ct_y - r1 * 5, "Thời gian chờ đợi kéo dài")
    c.acroForm.checkbox(name="v10f", checked=(args[5] == 1),
                        x=ct_x3, y=ct_y - r1 * 6, fillColor=white, size=12)
    c.drawString(ct_x3 + 15, ct_y - r1 * 6, "Thủ tục hành chính phức tạp")


@cs(r=1, line=True)
def p2g(c, *args):
    c.drawString(ct_x2, ct_y - r1, "11. Khác")
    c.acroForm.checkbox(name="v11a", checked=(args[0] == 1),
                        x=ct_x3, y=ct_y - r1, fillColor=white, size=12)
    c.drawString(ct_x3 + 15, ct_y - r1, "Các sự cố không đề cập trong các mục từ 1 đến 10")


@cs(r=1)
def p2h(c, *args):
    c.drawString(ct_x2, ct_y - r1, args[0])


@cs(r=1)
def p2i(c):
    c.setFont('TNRBold', fontsize)
    c.drawString(ct_x2, ct_y - r1, 'III. Điều trị/y lệnh đã được thực hiện')


@cs(r=3)
def p2j(c, *args):
    c.drawString(ct_x2, ct_y - r1, args[0])


@cs(r=1, rh=r2)
def p3a(c):
    c.setFont('TNRBold', fontsize)
    c.drawString(ct_x2, ct_y - r2, 'IV. Phân loại sự cố theo nhóm nguyên nhân gây sự cố')


@cs(r=7, line2=True, rh=r2)
def p3b(c, *args):
    c.drawString(ct_x2, ct_y - r2, "1. Nhân viên")
    c.acroForm.checkbox(name="v12a", checked=(args[0] == 1),
                        x=ct_x32, y=ct_y - r2, fillColor=white, size=12)
    c.drawString(ct_x32 + 15, ct_y - r2, "Nhận thức (kiến thức, hiểu biết, quan niệm)")
    c.acroForm.checkbox(name="v12b", checked=(args[1] == 1),
                        x=ct_x32, y=ct_y - r2 * 2, fillColor=white, size=12)
    c.drawString(ct_x32 + 15, ct_y - r2 * 2, "Thực hành (kỹ năng thực hành không đúng quy định, hướng dẫn chuẩn")
    c.drawString(ct_x32, ct_y - r2 * 3, "hoặc thực hành theo quy định, hướng dẫn sai)")
    c.acroForm.checkbox(name="v12c", checked=(args[2] == 1),
                        x=ct_x32, y=ct_y - r2 * 4, fillColor=white, size=12)
    c.drawString(ct_x32 + 15, ct_y - r2 * 4, "Thái độ, hành vi, cảm xúc")
    c.acroForm.checkbox(name="v12d", checked=(args[3] == 1),
                        x=ct_x32, y=ct_y - r2 * 5, fillColor=white, size=12)
    c.drawString(ct_x32 + 15, ct_y - r2 * 5, "Giao tiếp")
    c.acroForm.checkbox(name="v12e", checked=(args[4] == 1),
                        x=ct_x32, y=ct_y - r2 * 6, fillColor=white, size=12)
    c.drawString(ct_x32 + 15, ct_y - r2 * 6, "Tâm sinh lý, thể chất, bệnh lý")
    c.acroForm.checkbox(name="v12f", checked=(args[5] == 1),
                        x=ct_x32, y=ct_y - r2 * 7, fillColor=white, size=12)
    c.drawString(ct_x32 + 15, ct_y - r2 * 7, "Các yếu tố xã hội")


@cs(r=7, line2=True, rh=r2)
def p3c(c, *args):
    c.drawString(ct_x2, ct_y - r2, "2. Người bệnh")
    c.acroForm.checkbox(name="v13a", checked=(args[0] == 1),
                        x=ct_x32, y=ct_y - r2, fillColor=white, size=12)
    c.drawString(ct_x32 + 15, ct_y - r2, "Nhận thức (kiến thức, hiểu biết, quan niệm)")
    c.acroForm.checkbox(name="v13b", checked=(args[1] == 1),
                        x=ct_x32, y=ct_y - r2 * 2, fillColor=white, size=12)
    c.drawString(ct_x32 + 15, ct_y - r2 * 2, "Thực hành (kỹ năng thực hành không đúng quy định, hướng dẫn chuẩn")
    c.drawString(ct_x32, ct_y - r2 * 3, "hoặc thực hành theo quy định, hướng dẫn sai)")
    c.acroForm.checkbox(name="v13c", checked=(args[2] == 1),
                        x=ct_x32, y=ct_y - r2 * 4, fillColor=white, size=12)
    c.drawString(ct_x32 + 15, ct_y - r2 * 4, "Thái độ, hành vi, cảm xúc")
    c.acroForm.checkbox(name="v13d", checked=(args[3] == 1),
                        x=ct_x32, y=ct_y - r2 * 5, fillColor=white, size=12)
    c.drawString(ct_x32 + 15, ct_y - r2 * 5, "Giao tiếp")
    c.acroForm.checkbox(name="v13e", checked=(args[4] == 1),
                        x=ct_x32, y=ct_y - r2 * 6, fillColor=white, size=12)
    c.drawString(ct_x32 + 15, ct_y - r2 * 6, "Tâm sinh lý, thể chất, bệnh lý")
    c.acroForm.checkbox(name="v13f", checked=(args[5] == 1),
                        x=ct_x32, y=ct_y - r2 * 7, fillColor=white, size=12)
    c.drawString(ct_x32 + 15, ct_y - r2 * 7, "Các yếu tố xã hội")


@cs(r=4, line2=True, rh=r2)
def p3d(c, *args):
    c.drawString(ct_x2, ct_y - r2, "3. Môi trường")
    c.drawString(ct_x2, ct_y - r2 * 2, "làm việc")
    c.acroForm.checkbox(name="v14a", checked=(args[0] == 1),
                        x=ct_x32, y=ct_y - r2, fillColor=white, size=12)
    c.drawString(ct_x32 + 15, ct_y - r2, "Cơ sở vật chất, hạ tầng, trang thiết bị")
    c.acroForm.checkbox(name="v14b", checked=(args[1] == 1),
                        x=ct_x32, y=ct_y - r2 * 2, fillColor=white, size=12)
    c.drawString(ct_x32 + 15, ct_y - r2 * 2, "Khoảng cách đến nơi làm việc quá xa")
    c.acroForm.checkbox(name="v14c", checked=(args[2] == 1),
                        x=ct_x32, y=ct_y - r2 * 3, fillColor=white, size=12)
    c.drawString(ct_x32 + 15, ct_y - r2 * 3, "Đánh giá về độ an toàn, các nguy cơ rủi ro của môi trường làm việc")
    c.acroForm.checkbox(name="v14d", checked=(args[3] == 1),
                        x=ct_x32, y=ct_y - r2 * 4, fillColor=white, size=12)
    c.drawString(ct_x32 + 15, ct_y - r2 * 4, "Nội quy, quy định và đặc tính kỹ thuật")


@cs(r=4, line2=True, rh=r2)
def p3e(c, *args):
    c.drawString(ct_x2, ct_y - r2, "4. Tổ chức/")
    c.drawString(ct_x2, ct_y - r2 * 2, "dịch vụ")
    c.acroForm.checkbox(name="v15a", checked=(args[0] == 1),
                        x=ct_x32, y=ct_y - r2, fillColor=white, size=12)
    c.drawString(ct_x32 + 15, ct_y - r2, "Các chính sách, quy trình, hướng dẫn chuyên môn")
    c.acroForm.checkbox(name="v15b", checked=(args[1] == 1),
                        x=ct_x32, y=ct_y - r2 * 2, fillColor=white, size=12)
    c.drawString(ct_x32 + 15, ct_y - r2 * 2, "Tuân thủ quy trình thực hành chuẩn")
    c.acroForm.checkbox(name="v15c", checked=(args[2] == 1),
                        x=ct_x32, y=ct_y - r2 * 3, fillColor=white, size=12)
    c.drawString(ct_x32 + 15, ct_y - r2 * 3, "Văn hoá tổ chức")
    c.acroForm.checkbox(name="v15d", checked=(args[3] == 1),
                        x=ct_x32, y=ct_y - r2 * 4, fillColor=white, size=12)
    c.drawString(ct_x32 + 15, ct_y - r2 * 4, "Làm việc nhóm")


@cs(r=3, line2=True, rh=r2)
def p3f(c, *args):
    c.drawString(ct_x2, ct_y - r2, "5. Yếu tố")
    c.drawString(ct_x2, ct_y - r2 * 2, "bên ngoài")
    c.acroForm.checkbox(name="v16a", checked=(args[0] == 1),
                        x=ct_x32, y=ct_y - r2, fillColor=white, size=12)
    c.drawString(ct_x32 + 15, ct_y - r2, "Môi trường tự nhiên")
    c.acroForm.checkbox(name="v16b", checked=(args[1] == 1),
                        x=ct_x32, y=ct_y - r2 * 2, fillColor=white, size=12)
    c.drawString(ct_x32 + 15, ct_y - r2 * 2, "Sản phẩm, công nghệ và cơ sở hạ tầng")
    c.acroForm.checkbox(name="v16c", checked=(args[2] == 1),
                        x=ct_x32, y=ct_y - r2 * 3, fillColor=white, size=12)
    c.drawString(ct_x32 + 15, ct_y - r2 * 3, "Quy trình, hệ thống dịch vụ")


@cs(r=1, line2=True, rh=r2)
def p3g(c, *args):
    c.drawString(ct_x2, ct_y - r2, "6. Khác")
    c.acroForm.checkbox(name="v16a", checked=(args[0] == 1),
                        x=ct_x32, y=ct_y - r2, fillColor=white, size=12)
    c.drawString(ct_x32 + 15, ct_y - r2, "Các yếu tố không đề cập trong các mục từ 1 đến 5")


@cs(r=1, rh=r2)
def p3h(c, *args):
    c.drawString(ct_x2, ct_y - r2, args[0])


@cs(r=1, rh=r2)
def p3i(c):
    c.setFont('TNRBold', fontsize)
    c.drawString(ct_x2, ct_y - r2, 'V. Hành động khắc phục sự cố')


@cs(r=2, rh=r2)
def p3j(c, *args):
    t = textwrap.wrap(args[0], wr)
    for i in range(len(t)):
        c.drawString(ct_x2, ct_y - r2 * (i + 1), t[i])


@cs(r=1, rh=r2)
def p3k(c):
    c.setFont('TNRBold', fontsize)
    c.drawString(ct_x2, ct_y - r2, 'VI. Đề xuất khuyến cáo phòng ngừa sự cố')


@cs(r=2, rh=r2)
def p3l(c, *args):
    t = textwrap.wrap(args[0], wr)
    for i in range(len(t)):
        c.drawString(ct_x2, ct_y - r2 * (i + 1), t[i])


def p4a(c):
    global ct_y
    c.saveState()
    c.setFont('TNRBold', fontsize * 1.2)
    c.drawString(ct_x2, ct_y, 'B. Dành cho cấp quản lý')
    c.restoreState()
    ct_y -= r1


@cs(r=1)
def p4b(c):
    c.setFont('TNRBold', fontsize)
    c.drawString(ct_x2, ct_y - r1, 'I. Đánh giá của Trưởng nhóm chuyên gia')


@cs(r=3)
def p4c(c, *args):
    t = textwrap.wrap(args[0])
    for i in range(len(t)):
        c.drawString(ct_x2, ct_y - r1 * (i + 1), t[i])


@cs(r=2)
def p4d(c, *args):
    c.drawString(ct_x2, ct_y - r1, 'Đã thảo luận đưa khuyến cáo/hướng xử lý với người báo cáo')
    c.acroForm.checkbox(name="v18a", checked=(args[0] == "Có"),
                        x=ct_x2, y=ct_y - r1 * 2, fillColor=white, size=12)
    c.drawString(ct_x2 + 15, ct_y - r1 * 2, "Có")
    c.acroForm.checkbox(name="v18b", checked=(args[0] == "Không"),
                        x=ct_x2 + 90, y=ct_y - r1 * 2, fillColor=white, size=12)
    c.drawString(ct_x2 + 105, ct_y - r1 * 2, "Không")
    c.acroForm.checkbox(name="v18c", checked=(args[0] == "Không ghi nhận"),
                        x=ct_x2 + 200, y=ct_y - r1 * 2, fillColor=white, size=12)
    c.drawString(ct_x2 + 215, ct_y - r1 * 2, "Không ghi nhận")


@cs(r=3)
def p4e(c, *args):
    c.drawString(ct_x2, ct_y - r1, 'Phù hợp với các khuyến cáo chính thức được ban hành')
    c.drawString(ct_x2, ct_y - r1 * 2, 'Ghi cụ thể khuyến cáo:' + args[0])
    c.acroForm.checkbox(name="v19a", checked=(args[1] == "Có"),
                        x=ct_x2, y=ct_y - r1 * 3, fillColor=white, size=12)
    c.drawString(ct_x2 + 15, ct_y - r1 * 3, "Có")
    c.acroForm.checkbox(name="v19b", checked=(args[1] == "Không"),
                        x=ct_x2 + 90, y=ct_y - r1 * 3, fillColor=white, size=12)
    c.drawString(ct_x2 + 105, ct_y - r1 * 3, "Không")
    c.acroForm.checkbox(name="v19c", checked=(args[1] == "Không ghi nhận"),
                        x=ct_x2 + 200, y=ct_y - r1 * 3, fillColor=white, size=12)
    c.drawString(ct_x2 + 215, ct_y - r1 * 3, "Không ghi nhận")


@cs(r=1)
def p4f(c):
    c.setFont('TNRBold', fontsize)
    c.drawString(ct_x2, ct_y - r1, 'II. Đánh giá mức độ tổn thương')


@cs(r=1)
def p4g(c):
    c.setFont('TNRBold', fontsize)
    c.drawString(ct_x2, ct_y - r1, 'Trên người bệnh')


@cs(r=4)
def p4h(c, *args):
    c.drawString(ct_x2, ct_y - r1, '1. Chưa xảy ra (NC0)')
    c.acroForm.checkbox(name="v20a", checked=(args[0] == "A"),
                        x=ct_x2 + 200, y=ct_y - r1, fillColor=white, size=12)
    c.drawString(ct_x2 + 215, ct_y - r1, 'A')
    c.drawString(ct_x2, ct_y - r1 * 2, '2. Tổn thương nhẹ (NC1)')
    c.acroForm.checkbox(name="v20b", checked=(args[0] == "B"),
                        x=ct_x2 + 200, y=ct_y - r1 * 2, fillColor=white, size=12)
    c.drawString(ct_x2 + 215, ct_y - r1 * 2, 'B')
    c.acroForm.checkbox(name="v20c", checked=(args[0] == "C"),
                        x=ct_x2 + 240, y=ct_y - r1 * 2, fillColor=white, size=12)
    c.drawString(ct_x2 + 255, ct_y - r1 * 2, 'C')
    c.acroForm.checkbox(name="v20d", checked=(args[0] == "D"),
                        x=ct_x2 + 280, y=ct_y - r1 * 2, fillColor=white, size=12)
    c.drawString(ct_x2 + 295, ct_y - r1 * 2, 'D')
    c.drawString(ct_x2, ct_y - r1 * 3, '3. Tổn thương trung bình (NC2)')
    c.acroForm.checkbox(name="v20e", checked=(args[0] == "E"),
                        x=ct_x2 + 200, y=ct_y - r1 * 3, fillColor=white, size=12)
    c.drawString(ct_x2 + 215, ct_y - r1 * 3, 'E')
    c.acroForm.checkbox(name="v20f", checked=(args[0] == "F"),
                        x=ct_x2 + 240, y=ct_y - r1 * 3, fillColor=white, size=12)
    c.drawString(ct_x2 + 255, ct_y - r1 * 3, 'F')
    c.drawString(ct_x2, ct_y - r1 * 4, '4. Tổn thương nặng (NC3)')
    c.acroForm.checkbox(name="v20g", checked=(args[0] == "G"),
                        x=ct_x2 + 200, y=ct_y - r1 * 4, fillColor=white, size=12)
    c.drawString(ct_x2 + 215, ct_y - r1 * 4, 'G')
    c.acroForm.checkbox(name="v20h", checked=(args[0] == "H"),
                        x=ct_x2 + 240, y=ct_y - r1 * 4, fillColor=white, size=12)
    c.drawString(ct_x2 + 255, ct_y - r1 * 4, 'H')
    c.acroForm.checkbox(name="v20i", checked=(args[0] == "I"),
                        x=ct_x2 + 280, y=ct_y - r1 * 4, fillColor=white, size=12)
    c.drawString(ct_x2 + 295, ct_y - r1 * 4, 'I')


@cs(r=1)
def p4i(c):
    c.setFont('TNRBold', fontsize)
    c.drawString(ct_x2, ct_y - r1, 'Trên tổ chức')


@cs(r=9)
def p4j(c, *args):
    c.acroForm.checkbox(name="v21a", checked=(args[0] == 1),
                        x=ct_x2, y=ct_y - r1, fillColor=white, size=12)
    c.drawString(ct_x2 + 15, ct_y - r1, "Tổn hại tài sản")
    c.acroForm.checkbox(name="v21b", checked=(args[1] == 1),
                        x=ct_x2, y=ct_y - r1 * 2, fillColor=white, size=12)
    c.drawString(ct_x2 + 15, ct_y - r1 * 2, "Tăng nguồn lực phục vụ cho người bệnh")
    c.acroForm.checkbox(name="v21c", checked=(args[2] == 1),
                        x=ct_x2, y=ct_y - r1 * 3, fillColor=white, size=12)
    c.drawString(ct_x2 + 15, ct_y - r1 * 3, "Quan tâm của truyền thông")
    c.acroForm.checkbox(name="v21d", checked=(args[3] == 1),
                        x=ct_x2, y=ct_y - r1 * 4, fillColor=white, size=12)
    c.drawString(ct_x2 + 15, ct_y - r1 * 4, "Khiếu nại của người bệnh")
    c.acroForm.checkbox(name="v21e", checked=(args[4] == 1),
                        x=ct_x2, y=ct_y - r1 * 5, fillColor=white, size=12)
    c.drawString(ct_x2 + 15, ct_y - r1 * 5, "Tổn hại danh tiếng")
    c.acroForm.checkbox(name="v21f", checked=(args[5] == 1),
                        x=ct_x2, y=ct_y - r1 * 6, fillColor=white, size=12)
    c.drawString(ct_x2 + 15, ct_y - r1 * 6, "Can thiệp của pháp luật")
    c.acroForm.checkbox(name="v21g", checked=(args[6] == 1),
                        x=ct_x2, y=ct_y - r1 * 7, fillColor=white, size=12)
    c.drawString(ct_x2 + 15, ct_y - r1 * 7, "Khác")
    t = textwrap.wrap(args[7])
    for i in range(len(t)):
        c.drawString(ct_x2, ct_y - r1 * (i + 8), t[i])


def p4k(c, *args):
    name = args[1] + " " + args[0]
    date = f"Ngày {args[2][8:10]} tháng {args[2][5:7]} năm {args[2][:4]}"
    x = 0.8 * w
    c.drawCentredString(x, ct_y - r1 * 1, date)
    c.drawCentredString(x, ct_y - r1 * 2, 'Ký tên')
    c.drawCentredString(x, ct_y - r1 * 5, name)


def create_pdf2(stream, **kwargs):
    global ct_y
    c = canvas.Canvas(stream, pagesize=A4)
    c.setLineWidth(1)
    c.setStrokeColorRGB(0, 0, 0)
    c.setFont(fontname, fontsize)
    d_title(c, kwargs['id'])
    p1a(c)
    p1b(c, kwargs['mo_ta'])
    p1c(c)
    p1d(c, kwargs['v1a'], kwargs['v1b'], kwargs['v1c'],
        kwargs['v1d'], kwargs['v1e'], kwargs['v1f'],
        kwargs['v1g'], kwargs['v1h'], kwargs['v1i'])
    p1e(c, kwargs['v2a'], kwargs['v2b'], kwargs['v2c'],
        kwargs['v2d'], kwargs['v2e'])
    p1f(c, kwargs['v3a'], kwargs['v3b'], kwargs['v3c'],
        kwargs['v3d'], kwargs['v3e'], kwargs['v3f'],
        kwargs['v3g'], kwargs['v3h'], kwargs['v3i'])
    p1g(c, kwargs['v4a'], kwargs['v4b'], kwargs['v4c'])
    next_page(c)
    p2a(c, kwargs['v5a'], kwargs['v5b'], kwargs['v5c'])
    p2b(c, kwargs['v6a'], kwargs['v6b'], kwargs['v6c'],
        kwargs['v6d'], kwargs['v6e'], kwargs['v6f'])
    p2c(c, kwargs['v7'])
    p2d(c, kwargs['v8a'], kwargs['v8b'])
    p2e(c, kwargs['v9a'], kwargs['v9b'], kwargs['v9c'])
    p2f(c, kwargs['v10a'], kwargs['v10b'], kwargs['v10c'],
        kwargs['v10d'], kwargs['v10e'], kwargs['v10f'])
    p2g(c, kwargs['v11a'])
    p2h(c, kwargs['v11b'])
    p2i(c)
    p2j(c, kwargs['xu_ly'])
    next_page(c)
    p3a(c)
    p3b(c, kwargs['v12a'], kwargs['v12b'], kwargs['v12c'],
        kwargs['v12d'], kwargs['v12e'], kwargs['v12f'])
    p3c(c, kwargs['v13a'], kwargs['v13b'], kwargs['v13c'],
        kwargs['v13d'], kwargs['v13e'], kwargs['v13f'])
    p3d(c, kwargs['v14a'], kwargs['v14b'], kwargs['v14c'],
        kwargs['v14d'])
    p3e(c, kwargs['v15a'], kwargs['v15b'], kwargs['v15c'],
        kwargs['v15d'])
    p3f(c, kwargs['v16a'], kwargs['v16b'], kwargs['v16c'])
    p3g(c, kwargs['v17a'])
    p3h(c, kwargs['v17b'])
    p3i(c)
    p3j(c, kwargs['khac_phuc'])
    p3k(c)
    p3l(c, kwargs['de_xuat'])
    next_page(c)
    p4a(c)
    p4b(c)
    p4c(c, kwargs['danh_gia'])
    p4d(c, kwargs['v18'])
    p4e(c, kwargs['v19a'], kwargs['v19b'])
    p4f(c)
    p4g(c)
    p4h(c, kwargs['v20'])
    p4i(c)
    p4j(c, kwargs['v21a'], kwargs['v21b'], kwargs['v21c'],
        kwargs['v21d'], kwargs['v21e'], kwargs['v21f'],
        kwargs['v21g'], kwargs['v21h'])
    p4k(c, kwargs['ten'], kwargs['chuc_danh'], kwargs['ngay_gio'])
    c.save()
    reset_y()
