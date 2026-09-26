"""Local static preview with HTTP byte ranges for reliable MP4 seeking."""
import argparse
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
import re

HERE=Path(__file__).resolve().parent
SITE=HERE if (HERE/'index.html').exists() else HERE.parent


class RangeHandler(SimpleHTTPRequestHandler):
    def end_headers(self):
        self.send_header('Accept-Ranges','bytes')
        super().end_headers()

    def send_head(self):
        self.remaining=None
        path=Path(self.translate_path(self.path))
        requested=self.headers.get('Range')
        if not requested or not path.is_file():
            return super().send_head()
        match=re.fullmatch(r'bytes=(\d*)-(\d*)',requested.strip())
        if not match or not any(match.groups()):
            return super().send_head()
        size=path.stat().st_size
        left,right=match.groups()
        if left:
            start=int(left)
            end=min(int(right),size-1) if right else size-1
        else:
            start=max(0,size-int(right))
            end=size-1
        if start>=size or end<start:
            self.send_response(416)
            self.send_header('Content-Range',f'bytes */{size}')
            self.send_header('Content-Length','0')
            self.end_headers()
            return None
        stream=path.open('rb')
        stream.seek(start)
        self.remaining=end-start+1
        self.send_response(206)
        self.send_header('Content-Type',self.guess_type(str(path)))
        self.send_header('Content-Range',f'bytes {start}-{end}/{size}')
        self.send_header('Content-Length',str(self.remaining))
        self.send_header('Last-Modified',self.date_time_string(path.stat().st_mtime))
        self.end_headers()
        return stream

    def copyfile(self,source,outputfile):
        if self.remaining is None:
            return super().copyfile(source,outputfile)
        while self.remaining:
            chunk=source.read(min(64*1024,self.remaining))
            if not chunk:
                break
            outputfile.write(chunk)
            self.remaining-=len(chunk)


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--port',type=int,default=8765)
    args=parser.parse_args()
    server=ThreadingHTTPServer(('127.0.0.1',args.port),partial(RangeHandler,directory=str(SITE)))
    print(f'APCL preview: http://127.0.0.1:{args.port}/',flush=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()


if __name__=='__main__':
    main()
