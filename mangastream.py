import bs4
import os
import prettytable
import requests

def select_manga():
    # Get manga list page
    manga_list_url = "http://mangastream.com/manga"
    manga_list_res = requests.get(manga_list_url)
    manga_list_res.raise_for_status()
    
    # Convert to soup for parsing
    manga_list_soup = bs4.BeautifulSoup(manga_list_res.text, "html.parser")

    # Get list of manga and print them
    manga_list = manga_list_soup.select("td a")[::2]
    manga_table = prettytable.PrettyTable(["Index", "Manga"])
    for idx, manga in enumerate(manga_list):
        manga_table.add_row([str(idx + 1), manga.getText()])
    print(manga_table)

    # User select manga
    while True:
        chosen_manga_idx = int(input("\nSelect the manga you want to download.\nPlease input the index on the left.\n")) - 1
        if chosen_manga_idx >= 0 and chosen_manga_idx < len(manga_list):
            break
        else:
            print("Out of range. Index must be between 1 and " + str(len(manga_list)) + ".")
    chosen_manga = manga_list[chosen_manga_idx]
    print("\nYou have chosen " + chosen_manga.getText() + ".")
    
    # Create manga folder
    os.makedirs(chosen_manga.getText(), exist_ok=True)

    return chosen_manga

def select_chapters(chosen_manga):
    # Get chapter list page
    chapter_list_url = chosen_manga.get("href")
    chapter_list_res = requests.get(chapter_list_url)
    chapter_list_res.raise_for_status()
    
    # Convert to soup for parsing
    chapter_list_soup = bs4.BeautifulSoup(chapter_list_res.text, "html.parser")

    # Get list of chapters and print them
    chapter_list = chapter_list_soup.select("td a")
    chapter_table = prettytable.PrettyTable(["Index", "Chapter"])
    for idx, chapter in enumerate(chapter_list):
        chapter_table.add_row([str(idx + 1), chapter.getText()])
    print(chapter_table)

    # User select chapters
    print("\nSelect the chapters you want to download.\nPlease input the index on the left.")
    
    # User select starting chapter
    while True:
        start_chapter = int(input("\nSelect the starting chapter.\n")) - 1
        if start_chapter >= 0 and start_chapter < len(chapter_list):
            break
        else:
            print("Out of range. Index must be between 1 and " + str(len(chapter_list)) + ".")

    # User select ending chapter
    while True:
        end_chapter = int(input("\nSelect the ending chapter.\n")) - 1
        if end_chapter >= start_chapter and end_chapter < len(chapter_list):
            break
        else:
            print("Out of range. Index must be between " + str(start_chapter + 1) + " and " + str(len(chapter_list)) + ".")
    print()

    return chapter_list[start_chapter:end_chapter+1]

def download_images(chosen_manga, chosen_chapters):
    # Go through each chapter
    for chapter in chosen_chapters:
        print("Downloading " + chapter.getText() + " ", end="", flush=True)

        # Create chapter folder
        os.makedirs(os.path.join(chosen_manga.getText(), chapter.getText()), exist_ok=True)
        
        # Get chapter's first page
        chapter_url = chapter.get("href")
        page_res = requests.get(chapter_url)
        page_res.raise_for_status()
    
        # Convert to soup for parsing
        page_soup = bs4.BeautifulSoup(page_res.text, "html.parser")

        # Initialize page number
        page_number = 1

        # Go through each page of a chapter
        while True:
            print(".", end="", flush=True)

            # Get source image page
            img_url = "http:" + page_soup.select("#manga-page")[0].get("src")
            img_res = requests.get(img_url)
            img_res.raise_for_status()

            # Stringify page number
            if page_number < 10:
                page_number_string = "00" + str(page_number)
            elif page_number < 100:
                page_number_string = "0" + str(page_number)
            else:
                page_number_string = str(page_number)

            # Get image file extension
            img_extension = img_url.rsplit(".", 1)[1]

            # Download image
            img_file = open(os.path.join(chosen_manga.getText(), chapter.getText(), page_number_string + "." + img_extension), 'wb')
            for chunk in img_res.iter_content(100000):
                img_file.write(chunk)
            img_file.close()

            # Get next page url
            next_page_url = page_soup.select(".next a")[0].get("href")

            # Are we at the last page? If so, go to the next chapter
            if next_page_url[-3:] == "tip" or next_page_url.rsplit('/', 1)[0] != chapter_url.rsplit('/', 1)[0]:
                print()
                break

            # Get next page
            page_res = requests.get(next_page_url)
            page_res.raise_for_status()

            # Convert to soup for parsing
            page_soup = bs4.BeautifulSoup(page_res.text, "html.parser")

            # Increment page number
            page_number += 1

def main():
    manga = select_manga()
    chapters = select_chapters(manga)
    download_images(manga, chapters)

if __name__ == "__main__":
    main()