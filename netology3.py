import requests
import tqdm
import json
import os


class Savephoto:

    def __init__(self, user_id, yatoken):
        self.token = 'PUT VK ACCESS TOKEN HERE'
        self.id = user_id
        self.version = '5.199'
        self.params = {'access_token': self.token, 'v': self.version}
        self.yatoken = yatoken
        self.headers = {'Content-Type': 'application/json',
                        'Accept': 'application/json',
                        'Authorization': f'OAuth {self.yatoken}'}
        self.path = {'path': 'photos'}

    def photo_get(self, album='profile', count='5'):
        self.album = album
        self.count = count
        result = []
        url = 'https://api.vk.com/method/photos.get'
        params = {'owner_id': self.id, 'album_id': self.album,
                  'extended': '1', 'count': f'{count}'}
        response = requests.get(url, params={**self.params, **params})
        answer = response.json()

        for answ in answer['response']['items']:
            likesnum = answ['likes']['count']
            resulting = {'photoname': '', 'size': '', 'url': ''}
            datephoto = answ['date']
            namephoto = str(datephoto) + '_' + str(likesnum)
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
        for i in self.photo_get():
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
    yatoken = input('Введите свой токен от Яндекс Полигона\n')
    user_id = input('Введите свой ID Вконтакте\n')
    a = Savephoto(user_id, yatoken)
    a.initiatesaving()
