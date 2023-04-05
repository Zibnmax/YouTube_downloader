import os
import sys
import asyncio
import aiohttp

from pytube import YouTube, Playlist, Channel, exceptions
from tqdm.asyncio import tqdm_asyncio
import tqdm.asyncio
from tqdm import tqdm


OUTPUT_PATH = "videos"

links_path = f"{os.curdir}/download_links.txt"

def make_list() -> list:

    if not os.path.exists(links_path):
        print("There is no download_links.txt file. Make one.")
        sys.exit(0)
    if not os.stat(links_path).st_size:
        print("download_links.txt is empty, nothing to download.")
        sys.exit(0)

    with open(file=links_path, mode='r') as file:
        links = file.read().split('\n')

    while '' in links:
        links.remove('')
    print(links)
    return links


async def main():

    tasks = []
    for link in make_list():
        try:
            yt = YouTube(link)
        except:
            try:
                pl = Playlist(link)
                print(f'Playlist from {pl.owner} found. Title: {pl.title}')
                for video in pl.videos:
                    tasks.append(asyncio.create_task(download_video(video, output_path=os.path.join(OUTPUT_PATH, pl.title))))

            except:
                try:
                    ch = Channel(link)
                    print(f'Channel {ch.channel_name} found.')
                    for video in ch.videos:
                        tasks.append(asyncio.create_task(download_video(video, output_path=os.path.join(OUTPUT_PATH, ch.channel_name))))
            
                except exceptions.RegexMatchError:
                    print(f'Wrong link found "{link}". Ignoring...')
                    continue
        else:
            tasks.append(asyncio.ensure_future(download_video(yt, output_path=OUTPUT_PATH)))

    await tqdm_asyncio.gather(*tasks, desc='Files total')


# async def download_video(yt, output_path):

#     yd = yt.streams.filter(progressive=True, type='video').get_highest_resolution()
#     os.makedirs(output_path, exist_ok=True)
#     tqdm.write(f'Downloading {yt.title}')
#     await asyncio.to_thread(yd.download, output_path=output_path, max_retries=1)
#     await asyncio.to_thread(yd.on_progress)

# Working p-bars!
# async def download_video(yt, output_path):
#     yd = yt.streams.filter(progressive=True, type='video').get_highest_resolution()
#     os.makedirs(output_path, exist_ok=True)
#     with open(os.path.join(output_path, yd.default_filename), "wb") as f:
#         async with aiohttp.ClientSession() as session:
#             async with session.get(yd.url, timeout=None) as resp:
#                 total = int(resp.headers.get("Content-Length", 0))
#                 pbar = tqdm(total=total, unit="B", unit_scale=True)
#                 while True:
#                     chunk = await resp.content.read(8192)
#                     if not chunk:
#                         break
#                     f.write(chunk)
#                     pbar.update(len(chunk))
#                 pbar.close()

async def download_video(yt, output_path):
    yd = yt.streams.filter(progressive=True, type='video').get_highest_resolution()
    os.makedirs(output_path, exist_ok=True)
    file_path = os.path.join(output_path, f'{yt.title}.mp4')
    pbar = tqdm(total=int(yd.filesize), unit='B', unit_scale=True)
    with open(file_path, 'wb') as f:
        def on_progress(chunk, file_handler, bytes_remaining):
            f.write(chunk)
            pbar.update(len(chunk))
        yd.on_progress = on_progress
        await asyncio.to_thread(yd.download, output_path=output_path, max_retries=1)
    pbar.close()


if __name__ == "__main__":
    asyncio.run(main())
    tqdm.write("\nDone!")
