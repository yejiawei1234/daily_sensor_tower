from PIL import Image
from io import BytesIO
import os
import pandas as pd
import sys
import aiohttp
import asyncio
import time
import pprint
from .mytoken import Mytoken

# https://api.sensortower.com:443/v1/ios/apps?app_ids=495582516&auth_token=


class MyGameInfo:

    def __init__(self, json):
        self.json = json
        self.name = None
        self.rating = None
        self.icon_url = None
        self.screenshot_urls = []
        self.tablet_screenshot_urls = []
        self.app_url = None
        self.app_id = None
        self.description = None

    def unpack_info(self):
        self.name = self.json.get("apps")[0].get('name')
        self.rating = self.json.get("apps")[0].get('rating')
        self.icon_url = self.json.get("apps")[0].get('icon_url')
        self.app_id = self.json.get("apps")[0].get('app_id')
        self.description = list(self.json.get("apps")[0].get('description'))
        if self.json.get("apps")[0].get('screenshot_urls'):
            for i in self.json.get("apps")[0].get('screenshot_urls'):
                self.screenshot_urls.append(i)
        else:
            self.screenshot_urls = None
        if self.json.get("apps")[0].get('tablet_screenshot_urls'):
            for i in self.json.get("apps")[0].get('tablet_screenshot_urls'):
                self.tablet_screenshot_urls.append(i)
        else:
            self.tablet_screenshot_urls = None


def get_game_url(app_id):
    if '.' not in str(app_id):
        base_url = 'https://api.sensortower.com:443/v1/'
        token = Mytoken.info
        url = base_url + 'ios'
        url = url + '/apps?app_ids={}&auth_token={}'.format(app_id, token)
    else:
        base_url = 'https://api.sensortower.com:443/v1/android/apps?'
        token = Mytoken.info
        url = base_url + f'app_ids={app_id}&auth_token={token}'
    return url


async def get_my_app(url):
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as resp:
            app_json = await resp.json()
            g = MyGameInfo(app_json)
            g.unpack_info()
    return g


class pdb1:
    def __init__(self, game, dir):
        self.game = game
        self.rootpath = '/Users/yeye/Desktop/{}'.format(dir)
        self.icon_name = 'icon.png'
        self.dir = dir
        self.sub_dir_path = None
        self.create_sub()
        self.tasks = []

    def write(self):
        with open('{}/description.txt'.format(self.sub_dir_path), 'w') as f:
            for i in self.game.description:
                f.write(i)
        with open('{}/{}_.txt'.format(self.sub_dir_path, self.game.app_id), 'w') as f:
            f.write('')

    async def download_pic(self, url, p_id):
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as resp:
                basename = 'screenshot{id}.jpg'.format(id=p_id)
                filename = os.path.join(self.sub_dir_path, basename)
                chunk = await resp.content.read()
                pic = Image.open(BytesIO(chunk))
                width, height = pic.size
                try:
                    # print(pic.mode)
                    if pic.mode == 'RGBA':
                        pass
                    else:
                        if width < height:
                            size = 200, 400  # size = 200, 400
                            pic.thumbnail(size, Image.ANTIALIAS)
                            pic.save(filename)
                        else:
                            size = 400, 200  # size = 400, 200
                            pic.thumbnail(size, Image.ANTIALIAS)
                            pic.save(filename)

                except:
                    pass


    async def download_icon(self, url):
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as resp:
                basename = 'icon.png'
                filename = os.path.join(self.sub_dir_path, basename)
                s_basename = 'small_icon.png'
                s_filename = os.path.join(self.sub_dir_path, s_basename)
                chunk = await resp.content.read()
                pic = Image.open(BytesIO(chunk))
                size = 100, 100
                s_size = 45, 45
                pic1 = pic.copy()
                pic.thumbnail(size, Image.ANTIALIAS)
                pic.save(filename)
                pic1.thumbnail(s_size, Image.ANTIALIAS)
                pic1.save(s_filename)

    def create_sub(self):
        self.sub_dir_path = os.path.join(self.rootpath, self.game.name)
        if os.path.exists(self.sub_dir_path):
            print('This game {} has already been there'.format(self.game.name))
        else:
            os.makedirs(self.sub_dir_path)


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print('please give a path')
        sys.exit()
    elif len(sys.argv) == 2:
        dir = sys.argv[1]
    else:
        print("you are giving too much argv!!!")
        sys.exit()
    app_df = pd.read_excel('/Users/yeye/my_file/senser_tower.xlsx')
    id_list = app_df['id'].tolist()
    t1 = time.time()
    # id_list = [529479190, 945274928, 1236677535]
    url_list = []
    tasks = []
    for i in id_list:
        url_list.append(get_game_url(i))
    for num, i in enumerate(url_list):
        name = 'g' + str(num)
        name = get_my_app(i)
        tasks.append(asyncio.ensure_future(name))

    loop = asyncio.get_event_loop()
    done, pending = loop.run_until_complete(asyncio.wait(tasks))
    g_list = []
    for future in done:
        g_list.append(future.result())
    for num, i in enumerate(g_list):
        print(i.name)

    pic_tasks = []
    for game in g_list:
        p = pdb1(game, dir)
        p.write()
        if len(game.screenshot_urls) >= 5:
            screenshot_5urls = game.screenshot_urls[:5]
        else:
            screenshot_5urls = game.screenshot_urls
        for num, pic in enumerate(screenshot_5urls, start=1):
            pic_tasks.append(asyncio.ensure_future(p.download_pic(pic, num)))
        pic_tasks.append(asyncio.ensure_future(p.download_icon(game.icon_url)))

    pic_loop = asyncio.get_event_loop()
    pic_loop.run_until_complete(asyncio.wait(pic_tasks))
    t2 = time.time()
    print('Time: ', t2 - t1)

