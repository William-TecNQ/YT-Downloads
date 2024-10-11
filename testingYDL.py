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
    
def check_title(url, options):
    # Change arguments to make it less verbose aka quiet
    try: 
        with yt_dlp.YoutubeDL(options) as ydl:
            info_dict = ydl.extract_info(url, download=False)
            video_title = info_dict.get('title', None)
            video_id = info_dict.get('id', None)
            return video_title
    except yt_dlp.utils.DownloadError:
        print('\nDownload Error occured: Check Proxy credentials')


print('\n-- Proxy Authentication --')
username = input('Username: ')
password = getpass()

# YoutubeDL arguments for proxy auth, ffmpeg binary & forcing good codecs
download_options = {
    'proxy': f'http://{username}:{password}@gateway.atcnq.local:3128',
    'ffmpeg_location': '/Users/williambowman/ffmpeg',
    'format': format_selector
}
check_options = {'proxy': f'http://{username}:{password}@gateway.atcnq.local:3128'}

url = input('\nURLS - Enter each YouTube URL one at a time, enter nothing to finish\n>> ')
videos = []
titles = []
# Fetch YT titles !


while url != '':
    # Required so the string slicing doesn't break the link
    if 'https' not in url:
        url.replace('http', 'https')
    if 'youtu.be' in url:
        videos.append(url)
    elif 'youtube.com' in url:
        if len(url) > 43:
            url = url[0:43]
        titles.append(check_title(url, check_options))
        videos.append(url)

    else:
        print('Invalid link')
    url = input('>> ')

def display_videos(titles):
    print('These are the videos in your list:')
# List titles to user
    for i, title in enumerate(titles):
        print(f'{i+1}. {title}')


def edit_videos(check_options, titles):
    display_videos(titles)
    # Provide option to change or clear entire list
    is_editing = input('\nWould you like to edit the list? (Y/N)\n>> ').lower()
    while is_editing not in ['y', 'n']:
        print('Invalid input')
        is_editing = input('\nould you like to edit the list? (Y/N)\n>> ').lower()
    if is_editing == 'y':
    # Change singular list elements by having index's in the provided list
        video_number = int(input('\nPlease enter the video number you wish to change\n>> '))
        while video_number > len(titles) + 1:
            print('Invalid video number')
            video_number = int(input('\nPlease enter the video number you wish to change\n>> '))
        new_url = input('\nPlease enter the new YouTube URL\n>> ')
        titles[video_number - 1] = check_title(new_url, check_options)
    else:
        print('This ended')
        return

edit_videos(check_options, titles)
    






try: 
    print('----- DOWNLOAD STARTED -----')
    with yt_dlp.YoutubeDL(download_options) as ydl:
        ydl.download(videos)
except yt_dlp.utils.DownloadError:
    print('\nDownload Error occured: Check Proxy credentials')

