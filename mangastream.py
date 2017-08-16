import bs4, os, prettytable, requests

def to_html(url):
    response = requests.get(url)
    response.raise_for_status()
    return response.text

def print_table(col_header, data):
    table = prettytable.PrettyTable(["Index", col_header])
    for idx, value in enumerate(data):
        table.add_row([str(idx + 1), value])
    print(table)

def int_input(prompt, lower, upper):
    while True:
        user_input = int(input(prompt))
        if user_input >= lower and user_input <= upper:
            break
        else:
            print("Out of range. Index must be between "+ str(lower) + " and " + str(upper) + ".")
    return user_input - 1 # zero-based indexing

def clean(string):
    reserved_characters = "\/:*?\"<>|"
    for reserved in reserved_characters:
        string = string.replace(reserved, " ")
    return string

def write_image(url, filename):
    response = requests.get(url)
    response.raise_for_status()

    img_file = open(filename, 'wb')
    for chunk in response.iter_content(100000):
        img_file.write(chunk)
    img_file.close()

class Downloader:
    def __init__(self):
        # Soup objects
        self.chosen_manga = None
        self.chosen_chapters = None

    def select_manga(self):
        # Parse manga list page
        manga_list_url = "http://mangastream.com/manga"
        manga_list_html = to_html(manga_list_url)
        manga_list_soup = bs4.BeautifulSoup(manga_list_html, "html.parser")

        # Get list of manga and print them
        manga_list = manga_list_soup.select("td a")[::2]
        print_table("Manga", [manga.getText() for manga in manga_list])

        # User select manga
        chosen_manga_idx = int_input("\nSelect the manga you want to download.\nPlease input the index on the left.\n", 1, len(manga_list))
        self.chosen_manga = manga_list[chosen_manga_idx]
        print("\nYou have chosen " + self.chosen_manga.getText() + ".")
        
        # Create manga folder
        manga_dir = clean(self.chosen_manga.getText())
        os.makedirs(manga_dir, exist_ok=True)

    def select_chapters(self):
        # Parse chapter list page
        chapter_list_url = self.chosen_manga.get("href")
        chapter_list_html = to_html(chapter_list_url)
        chapter_list_soup = bs4.BeautifulSoup(chapter_list_html, "html.parser")

        # Get list of chapters and print them
        chapter_list = chapter_list_soup.select("td a")
        print_table("Chapter", [chapter.getText() for chapter in chapter_list])

        # User select starting and ending chapters
        print("\nSelect the chapters you want to download.\nPlease input the index on the left.")
        start_chapter = int_input("\nSelect the starting chapter.\n", 1, len(chapter_list))
        end_chapter = int_input("\nSelect the ending chapter.\n", start_chapter + 1, len(chapter_list))
        print()

        self.chosen_chapters = chapter_list[start_chapter:end_chapter+1]

    def download_images(self):
        # Go through each chapter
        for chapter in self.chosen_chapters:
            print("Downloading " + chapter.getText() + " ", end="", flush=True)

            # Create chapter folder
            chapter_dir = os.path.join(clean(self.chosen_manga.getText()), clean(chapter.getText()))
            os.makedirs(chapter_dir, exist_ok=True)

            # Parse chapter's first page
            page_url = chapter.get("href")
            page_html = to_html(page_url)
            page_soup = bs4.BeautifulSoup(page_html, "html.parser")

            # Chapter url
            chapter_url = page_url.rsplit('/', 1)[0]

            # Initialize page number
            page_number = 1

            # Go through each page of a chapter
            while True:
                print(".", end="", flush=True)

                # Source image url
                img_url = "http:" + page_soup.select("#manga-page")[0].get("src")
                
                # Filename
                page_number_string = str(page_number).zfill(3)
                img_extension = img_url.rsplit(".", 1)[1]
                filename = os.path.join(clean(self.chosen_manga.getText()), clean(chapter.getText()), page_number_string + "." + img_extension)

                # Download image
                write_image(img_url, filename)

                # Get next page url
                next_page_url = page_soup.select(".next a")[0].get("href")

                # Are we at the last page? If so, go to the next chapter
                if next_page_url[-3:] == "tip" or next_page_url.rsplit('/', 1)[0] != chapter_url:
                    print()
                    break

                # Parse next page
                page_html = to_html(next_page_url)
                page_soup = bs4.BeautifulSoup(page_html, "html.parser")

                # Increment page number
                page_number += 1

def main():
    downloader = Downloader()
    downloader.select_manga()
    downloader.select_chapters()
    downloader.download_images()

if __name__ == "__main__":
    main()