import requests
import tqdm
import json
import os
import datetime
import configparser

class Vkphoto:

    def __init__(self, token, user_id):
        self.token = token
        self.id = user_id
        self.version = '5.199'
        self.params = {'access_token': self.token, 'v': self.version}
        self.path = {'path': 'photos'}

    def getuser(self):
        urluser = 'https://api.vk.com/method/users.get'
        params = {'user_ids':self.id}
        response = requests.get(urluser, params={**self.params, **params})
        try:
            answer = response.json()['response'][0]['id']
        except:
            answer = 'Не удалось получить ID пользователя'
        return answer

    def photo_get(self, count, album='profile'):
        self.album = album
        self.count = count
        result = []
        url = 'https://api.vk.com/method/photos.get'
        params = {'owner_id': self.getuser(), 'album_id': self.album,
                  'extended': '1', 'count': f'{count}'}
        response = requests.get(url, params={**self.params, **params})
        answer = response.json()
        likercount = []
        for answ in answer['response']['items']:
            likesnum = answ['likes']['count']
            resulting = {'photoname': '', 'size': '', 'url': ''}
            datephoto = answ['date']
            if likesnum in likercount:
                namephoto = str(likesnum) + '_' + \
                            str(datetime.datetime.fromtimestamp(datephoto))
            else:
                namephoto = str(likesnum)
            likercount.append(likesnum)
            ir = 0
            for sizes in answ['sizes']:
                if sizes['height'] + sizes['width'] > ir:
                    ir = sizes['height'] + sizes['width']
                    url = sizes['url']
                    type = sizes['type']
            resulting['photoname'] = namephoto
            resulting['size'] = type
            resulting['url'] = url
            result.append(resulting)
        return result

class Savephoto:

    def __init__(self, yatoken, photoset):
        self.yatoken = yatoken
        self.photoset = photoset
        self.headers = {'Content-Type': 'application/json',
                        'Accept': 'application/json',
                        'Authorization': f'OAuth {self.yatoken}'}
        self.path = {'path': 'photos'}


    def createfolder(self):
        url = 'https://cloud-api.yandex.net/v1/disk/resources'
        putrespones = requests.put(url, headers=self.headers,
                                   params=self.path)
        if putrespones.status_code == 201:
            print('Папка photos успешно создана')
        else:
            print('Папка создана не была')
            print(putrespones.json()['message'])

        return putrespones.json()

    def uploadfile(self):
        url = 'https://cloud-api.yandex.net/v1/disk/resources/upload'
        filejson = []
        z = 0
        self.pbar = tqdm.tqdm(range(15), ncols=100, position=0, leave=True)
        for i in self.photoset:
            dictjson = {'filename': '', 'size': ''}
            parametrs = {'url': f'{i["url"]}',
                         'path': f'disk:/photos/{i["photoname"]}'}
            uploadresp = requests.post(url, headers=self.headers,
                                       params=parametrs)
            dictjson['filename'] = i["photoname"]
            dictjson['size'] = i['size']
            filejson.append(dictjson)
            z += 1
            self.pbar.update(z)
        try:
            with open('result.json', 'w') as outfile:
                json.dump(filejson, outfile)
            print(f'Сохранён json файл с результатом,'
                  f' расположен в {os.getcwd()}\\result.json')
        except:
            print('Json файл сохранить не удалось')
        print('Файлы успешно сохранены'
              ' в https://disk.yandex.ru/client/disk/photos')

    def initiatesaving(self):
        self.createfolder()
        self.uploadfile()


if __name__ == '__main__':
    config = configparser.ConfigParser()
    config.read("settings.ini")
    yatoken = config['Tokens']['yatoken']
    vktoken = config['Tokens']['vktoken']

    user_id = input('Введите свой ID или имя аккаунта Вконтакте\n')
    count = input('Введите количество фото для выгрузки\n')

    VK = Vkphoto(vktoken, user_id)
    photoset = VK.photo_get(count=count)

    ya = Savephoto(yatoken, photoset)
    ya.initiatesaving()
