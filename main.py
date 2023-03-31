import os
import sys
import asyncio

from pytube import YouTube, Playlist


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
            yt = Playlist(link)

            print(yt.owner)
            
        tasks.append(asyncio.create_task(download_video(yt, output_path=OUTPUT_PATH)))


    await asyncio.gather(*tasks)


async def download_video(yt, output_path):
    # loop = asyncio.get_running_loop()
    yd = yt.streams.filter(progressive=True, type='video').get_highest_resolution()
    # await loop.run_in_executor(None, yd.download, output_path=output_path)
    await asyncio.to_thread(yd.download, output_path=output_path, max_retries=2)


if __name__ == "__main__":
    asyncio.run(main())
    print("Done!")

    # p = Playlist('https://www.youtube.com/playlist?list=PLth0xHD9unvdCvL1aUPXUBDrw60Do4RyI')
    # print(p)
    # with open(file=links_path, mode='w') as file:
    #     txt = '\n'.join(p)
    #     file.write(txt)
