import youtube_dl

url = "video_url"

try:
    ydl_opts = {"outtmpl": "post_id"}
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