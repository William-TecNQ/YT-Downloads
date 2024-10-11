import yt_dlp
from getpass import getpass

# https://www.youtube.com/watch?v=D5kGXI8vUKg
# https://www.youtube.com/watch?v=udNXMAflbU8
# https://www.youtube.com/watch?v=ApYbwdFWytE
def format_selector(ctx):
    """ Select the best video and the best audio that won't result in an mkv.
    NOTE: This is just an example and does not handle all cases """

    # formats are already sorted worst to best
    formats = ctx.get('formats')[::-1]

    # acodec='none' means there is no audio
    best_video = next(f for f in formats
                      if 'avc1' in f['vcodec'] and f['ext'] != 'webm' and f['acodec'] == 'none')

    # find compatible audio extension
    audio_ext = {'mp4': 'm4a'}[best_video['ext']]
    # vcodec='none' means there is no video
    best_audio = next(f for f in formats if (
        f['acodec'] != 'none' and f['vcodec'] == 'none' and f['ext'] == audio_ext))

    # These are the minimum required fields for a merged format
    yield {
        'format_id': f'{best_video["format_id"]}+{best_audio["format_id"]}',
        'ext': best_video['ext'],
        'requested_formats': [best_video, best_audio],
        # Must be + separated list of protocols
        'protocol': f'{best_video["protocol"]}+{best_audio["protocol"]}'
    }


print('\n-- Proxy Authentication --')
username = input('Username: ')
password = getpass()

print('URLS - enter the YouTube link one at a time, enter nothing to finish')

urls = []
url = input('>> ')
while url != '':
    if 'https' not in url:
        url.replace('http', 'https')

    if 'youtu.be' in url:
        # Check link
        urls.append(url)
    elif 'youtube.com' in url:
        # Check link
        if len(url) > 43:
            url = url[0:43]
        urls.append(url)
    else:
        print('Invalid link')
    url = input('>> ')

ydl_opts = {
    'proxy': f'http://{username}:{password}@gateway.atcnq.local:3128',
    # 'simulate': True,
    'ffmpeg_location': '/Users/williambowman/ffmpeg',
    # 'listformats': True,
    'format': format_selector
}

try: 
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download(urls)
except yt_dlp.utils.DownloadError:
    print('\nDownload Error occured: Check Proxy credentials')
