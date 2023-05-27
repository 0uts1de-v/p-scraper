import pixivpy3
import os, re
from get_refresh_token import login

def get_username(user_id, aapi):
    result_user_json = aapi.user_detail(user_id)

    user = result_user_json.user

    username = f"{user.name}_({user.account})"

    username = re.sub(r'[\\/:*?"<>|]+', '-', username)
    # remove characters unusable for filenames

    return username


def get_images(result_json, directory, aapi):
    print(f"Downloading {directory}...")
    while True:
        for illust in result_json.illusts:
            if len(illust.meta_pages) == 0:
                #for one image
                img = illust.meta_single_page.original_image_url
                aapi.download(img, path=directory)
                print(f"Downloaded -> {os.path.basename(img)}")
                # need some sleep?

            else:
                #for multi images
                for page in illust.meta_pages:
                    img = page.image_urls.original
                    aapi.download(img, path=directory)
                    print(f"Downloaded -> {os.path.basename(img)}")
                    # I'm a short sleeper
        
        next_qs = aapi.parse_qs(result_json.next_url)

        if next_qs is None:
            break

        result_json = aapi.user_illusts(**next_qs)


def scrape(user_id, aapi):
    username = get_username(user_id, aapi)
    
    username_illust = os.path.join(username, "illust")
    username_manga = os.path.join(username, "manga")

    if not os.path.exists(username):
        os.mkdir(username)
    if not os.path.exists(username_illust):
        os.mkdir(username_illust)
    if not os.path.exists(username_manga):
        os.mkdir(username_manga)
    
    result_illust_json = aapi.user_illusts(user_id, "illust")
    result_manga_json = aapi.user_illusts(user_id, "manga")

    get_images(result_illust_json, username_illust, aapi)
    get_images(result_manga_json, username_manga, aapi)

    print(f"Downloaded {username} ({user_id}).")


def main():
    aapi = pixivpy3.AppPixivAPI()

    # aapi.auth(refresh_token="xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx")
    # if you already have the refresh token
    # NOT recommended bacause the refresh token's lifetime is very short

    # need a docker container with selenium and vnc server
    print("Login via selenium...")
    aapi.auth(refresh_token=login())
    print("Logged in.")

    # ID is a number of digits
    while True:
        user_id = input("\nEnter Pixiv User ID: ")
        scrape(user_id, aapi)


if __name__ == "__main__":
    main()
