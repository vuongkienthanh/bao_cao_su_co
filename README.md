# Báo cáo sự cố y khoa

- Cài đặt: `pip3 install -r requirements.txt`
- Vào folder gốc chứa `main.py`
- Chạy server: `uvicorn main:app --reload --host 127.0.0.1 --port 8000`
- Test trên browser http://127.0.0.1:8000/
    - Tại database: http://127.0.0.1:8000/initdb
    - Điền form : http://127.0.0.1:8000/
    - Xem báo cáo với id=1: http://127.0.0.1:8000/read_report/1
    - Xoá báo cáo với id=1: http://127.0.0.1:8000/delete_report/1
    - Tải toàn bộ data (csv): http://127.0.0.1:8000/get_csv
    - Xem docs http://127.0.0.1:8000/docs
