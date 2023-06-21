
import time
from concurrent.futures.thread import ThreadPoolExecutor
from tornado import gen, web, ioloop

executor = ThreadPoolExecutor(max_workers=2)

class SyncToAsyncThreadHandler(web.RequestHandler):
    async def get(self, *args, **kwargs):
        rest = await ioloop.IOLoop.current().run_in_executor(executor, self.sleep)
        self.write(rest)

    def sleep(self):
        print("休息1...start")
        time.sleep(5)
        print("休息1...end")
        return 'ok'

if __name__ == '__main__':
    url_map = [
        ("/api", SyncToAsyncThreadHandler)
    ]
    app = web.Application(url_map, debug=True)
    app.listen(20001)
    print('started...')
    ioloop.IOLoop.current().start()
