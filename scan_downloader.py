import httpx
import urllib.parse
from pathlib import Path
import time
import random


def download_with_retry(url, headers, max_retries=5):
    """Download with retry logic and exponential backoff"""
    for attempt in range(max_retries):
        try:
            response = httpx.get(url, headers=headers, timeout=30)
            return response
        except (httpx.RemoteProtocolError, httpx.ConnectError, httpx.TimeoutException, 
                httpx.ReadTimeout, httpx.NetworkError) as e:
            if attempt == max_retries - 1:
                print(f"Failed after {max_retries} attempts: {e}")
                raise
            
            wait_time = (2 ** attempt) + random.uniform(0, 1)  # Exponential backoff with jitter
            print(f"Network error on attempt {attempt + 1}: {e}")
            print(f"Retrying in {wait_time:.1f} seconds...")
            time.sleep(wait_time)

def scan_downloader(manga_name: str):
    # check if a progress file exists for this manga
    progress_file = Path(f"scans/{manga_name}/progress.txt")
    if progress_file.exists():
        with open(progress_file, "r") as f:
            content = f.read().strip()
            if content == "Completed":
                print(f"All chapters for {manga_name} have already been downloaded.")
                return
            else:
                try:
                    start_chapter, start_page, max_chapter = map(int, content.split()[:3])
                    print(f"Resuming download from Chapter {start_chapter}, Page {start_page}, Max Chapter {max_chapter}")
                except ValueError:
                    print("Progress file is corrupted. Starting from the beginning.")
                    start_chapter = int(input("Enter starting chapter number (default 1): "))
                    start_page = int(input("Enter starting page number (default 1): "))
                    max_chapter = int(input("Enter maximum chapter number to download: "))
    else:
        start_chapter = int(input("Enter starting chapter number (default 1): "))
        start_page = int(input("Enter starting page number (default 1): "))
        max_chapter = int(input("Enter maximum chapter number to download: "))

    chapter_number = start_chapter
    page_number = start_page
    img_type = "jpg"


    headers = {
        'Referer': 'https://anime-sama.fr/catalogue/hajime-no-ippo/scan/vf/',
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/139.0.0.0 Safari/537.36',
        'sec-ch-ua': '"Not;A=Brand";v="99", "Google Chrome";v="139", "Chromium";v="139"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"macOS"'
    }

    while chapter_number <= max_chapter:
        # Build URL
        encoded_manga = urllib.parse.quote(manga_name)
        url = f"https://anime-sama.fr/s2/scans/{encoded_manga}/{chapter_number}/{page_number}.{img_type}"
        
        print(f"Downloading: Chapter {chapter_number}, Page {page_number}")
        
        # Make request
        response = download_with_retry(url, headers)
        
        if response.status_code == 200: # type: ignore
            # Save the image
            Path(f"scans/{manga_name}").mkdir(exist_ok=True)
            filename = f"ch{chapter_number:03d}_p{page_number:03d}.{img_type}"

            with open(f"scans/{manga_name}/{filename}", "wb") as f:
                f.write(response.content) # type: ignore
            
            print(f"Saved: {filename}")
            page_number += 1
            
            # Random delay between 1-10 seconds
            # delay = random.randint(1, 2)
            # print(f"Waiting {delay} seconds...")
            # time.sleep(delay)
            
        elif response.status_code == 404: # type: ignore
            print(f"Page {page_number} not found (404). Moving to next chapter.")
            print("-" * 40)
            print(f"Completed Chapter {chapter_number}/{max_chapter} - {((chapter_number / max_chapter) * 100):.2f}%")
            chapter_number += 1
            page_number = 1
            
        else:
            print(f"Error {response.status_code}, skipping...") # type: ignore
            page_number += 1

        # write a txt file with the last downloaded chapter and page and max chapter to resume later format : 2 12 52 -> chapter 2 page 12 max chapter 52
        with open(f"scans/{manga_name}/progress.txt", "w") as f:
            f.write(f"{chapter_number} {page_number} {max_chapter} {((chapter_number / max_chapter) * 100):.2f}%")

    # Download complete
    with open(f"scans/{manga_name}/progress.txt", "w") as f:
        f.write(f"Completed")
    print("Download complete!")
