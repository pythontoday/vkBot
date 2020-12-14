import json
import os
import youtube_dl
import requests
from auth_data import token

# group_name = input("Введите название группы: ")
#
# url = f"https://api.vk.com/method/wall.get?domain={group_name}&count=40&access_token={token}&v=5.52"
# req = requests.get(url)
# print(req.text)


def get_wall_posts(group_name):
    url = f"https://api.vk.com/method/wall.get?domain={group_name}&count=40&access_token={token}&v=5.52"
    req = requests.get(url)
    src = req.json()

    # проверяем существует ли директория с именем группы
    if os.path.exists(f"{group_name}"):
        print(f"Директория с именем {group_name} уже существует!")
    else:
        os.mkdir(group_name)

    # сохраняем данные в json файл, чтобы видеть структуру
    with open(f"{group_name}/{group_name}.json", "w", encoding="utf-8") as file:
        json.dump(src, file, indent=4, ensure_ascii=False)

    # собираем ID новых постов в список
    fresh_posts_id = []
    posts = src["response"]["items"]

    for fresh_post_id in posts:
        fresh_post_id = fresh_post_id["id"]
        fresh_posts_id.append(fresh_post_id)

    """Проверка, если файла не существует, значит это первый
    парсинг группы(отправляем все новые посты). Иначе начинаем
    проверку и отправляем только новые посты."""
    if not os.path.exists(f"{group_name}/exist_posts_{group_name}.txt"):
        print("Файла с ID постов не существует, создаём файл!")

        with open(f"{group_name}/exist_posts_{group_name}.txt", "w") as file:
            for item in fresh_posts_id:
                file.write(str(item) + "\n")

        # извлекаем данные из постов
        for post in posts:

            # функция для сохранения изображений
            def download_img(url, post_id, group_name):
                res = requests.get(url)

                # создаем папку group_name/files
                if not os.path.exists(f"{group_name}/files"):
                    os.mkdir(f"{group_name}/files")

                with open(f"{group_name}/files/{post_id}.jpg", "wb") as img_file:
                    img_file.write(res.content)

            # функция для сохранения видео
            def download_video(url, post_id, group_name):
                # создаем папку group_name/files
                if not os.path.exists(f"{group_name}/video_files"):
                    os.mkdir(f"{group_name}/video_files")

                try:
                    ydl_opts = {"outtmpl": f"{group_name}/video_files/{post_id}"}
                    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
                        video_info = ydl.extract_info(url, download=False)
                        video_duration = video_info["duration"]
                        if video_duration > 300:
                            print("Видео слишком долгое")
                        else:
                            print(f"Видео длится {video_duration} секунд. Сохраняем видео...")
                            ydl.download([url])
                except Exception:
                    print("Не удалось скачать видео...")

            post_id = post["id"]
            print(f"Отправляем пост с ID {post_id}")

            try:
                if "attachments" in post:
                    post = post["attachments"]

                    photo_quality = [
                        "photo_2560",
                        "photo_1280",
                        "photo_807",
                        "photo_604",
                        "photo_130",
                        "photo_75"
                    ]

                    # проверка на 1 или несколько фото/видео в посте
                    if len(post) == 1:

                        # забираем фото
                        if post[0]["type"] == "photo":

                            for pq in photo_quality:
                                if pq in post[0]["photo"]:
                                    post_photo = post[0]["photo"][pq]
                                    print(f"Фото с расширением {pq}")
                                    print(post_photo)
                                    download_img(post_photo, post_id, group_name)
                                    break
                        # забираем видео
                        elif post[0]["type"] == "video":
                            print("Видео пост")

                            # формируем данные для составления запроса на получение ссылки на видео
                            video_access_key = post[0]["video"]["access_key"]
                            video_post_id = post[0]["video"]["id"]
                            video_owner_id = post[0]["video"]["owner_id"]

                            video_get_url = f"https://api.vk.com/method/video.get?videos={video_owner_id}_{video_post_id}_{video_access_key}&access_token={token}&v=5.52"
                            req = requests.get(video_get_url)
                            res = req.json()
                            video_url = res["response"]["items"][0]["player"]
                            print(video_url)
                            download_video(video_url, post_id, group_name)
                        else:
                            print("Либо линк, либо аудио, либо репост...")
                    else:
                        photo_post_count = 0
                        for post_item_photo in post:
                            if post_item_photo["type"] == "photo":
                                for pq in photo_quality:
                                    if pq in post_item_photo["photo"]:
                                        post_photo = post_item_photo["photo"][pq]
                                        print(f"Фото с расширением {pq}")
                                        print(post_photo)
                                        post_id_counter = str(post_id) + f"_{photo_post_count}"
                                        download_img(post_photo, post_id_counter, group_name)
                                        photo_post_count += 1
                                        break
                                        # забираем видео
                            elif post_item_photo["type"] == "video":
                                print("Видео пост")

                                # формируем данные для составления запроса на получение ссылки на видео
                                video_access_key = post_item_photo["video"]["access_key"]
                                video_post_id = post_item_photo["video"]["id"]
                                video_owner_id = post_item_photo["video"]["owner_id"]

                                video_get_url = f"https://api.vk.com/method/video.get?videos={video_owner_id}_{video_post_id}_{video_access_key}&access_token={token}&v=5.52"
                                req = requests.get(video_get_url)
                                res = req.json()
                                video_url = res["response"]["items"][0]["player"]
                                print(video_url)
                                post_id_counter = str(post_id) + f"_{photo_post_count}"
                                download_video(video_url, post_id_counter, group_name)
                                photo_post_count += 1
                            else:
                                print("Либо линк, либо аудио, либо репост...")

            except Exception:
                print(f"Что-то пошло не так с постом ID {post_id}!")

    else:
        print("Файл с ID постов найден, начинаем выборку свежих постов!")


def main():
    group_name = input("Введите название группы: ")
    get_wall_posts(group_name)


if __name__ == '__main__':
    main()
