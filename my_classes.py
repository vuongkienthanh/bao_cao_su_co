from typing import IO, Generator
from pathlib import Path
from starlette.responses import StreamingResponse


class MyResponse(StreamingResponse):

    def __init__(self, filepath, request, *args, **kwargs):
        path = Path(filepath)
        file = path.open('rb')
        file_size = path.stat().st_size
        content_range = request.headers.get('range')
        content_length = file_size
        status_code = 200
        headers = {}
        if content_range is not None:
            content_range = content_range.strip().lower()
            content_ranges = content_range.split('=')[-1]
            range_start, range_end, *_ = map(str.strip, (content_ranges + '-').split('-'))
            range_start = max(0, int(range_start)) if range_start else 0
            range_end = min(file_size - 1, int(range_end)) if range_end else file_size - 1
            content_length = (range_end - range_start) + 1
            file = self.ranged(file, start=range_start, end=range_end + 1)
            status_code = 206
            headers['Content-Range'] = f'bytes {range_start}-{range_end}/{file_size}'
        super().__init__(
            file,
            media_type='video/mp4',
            status_code=status_code,
            headers={
                'Accept-Ranges': 'bytes',
                'Content-Length': str(content_length),
                **headers,
            })

    def ranged(self, file: IO[bytes], start: int = 0, end: int = None, block_size: int = 8192) -> Generator[bytes, None, None]:
        consumed = 0
        file.seek(start)
        while True:
            data_length = min(block_size, end - start - consumed) if end else block_size
            if data_length <= 0:
                break
            data = file.read(data_length)
            if not data:
                break
            consumed += data_length
            yield data
        if hasattr(file, 'close'):
            file.close()
