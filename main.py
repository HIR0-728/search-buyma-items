import requests as rq
import csv
from bs4 import BeautifulSoup
from time import sleep
from typing import List, Dict

BUYMA_CATEGORY_URL = "https://www.buyma.com/sitemap/category.html"
BYUMA_GENRE_PAGE_URL = "https://www.buyma.com"

CSV_FILE_NAME = "buyma-category.csv"
CSV_HEADERS = ["category_name", "total_count", "url"]

def create_csv(file_name):
    with open(file_name, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=CSV_HEADERS)
        writer.writeheader()

def write_csv(file_name, contents):
    with open(file_name, "a", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=CSV_HEADERS)
        writer.writerow(contents)

def main():
    create_csv(CSV_FILE_NAME)
    
    session = rq.session()
    res = session.get(BUYMA_CATEGORY_URL, timeout=(1.0, 12.0))
    soup = BeautifulSoup(res.text, "html.parser")

    wrapper = soup.find("div", id="wrapper")
    sitemap_cat = wrapper.find("div", id="sitemap_cat")
    sections = sitemap_cat.find_all("div", class_="section")

    genre_lists:List[Dict] = []
    for i, section in enumerate(sections):
        section_name = section.find("h2").text
        print("section_name:{}".format(section_name))
        smaplist_first = section.find("ul", class_="smaplist_first")
        smaplist_seconds = smaplist_first.find_all("ul", class_="smaplist_second")
        for smaplist_second in smaplist_seconds:
            genres = smaplist_second.find_all("li")
            for genre in genres:
                genre_name = genre.text
                a = genre.select("a")
                genre_url = a[0].get("href")
                genre_lists.append({"genre_name":genre_name, "genre_url":genre_url})

    exception_count=0
    for genre_list in genre_lists:
        target_name = genre_list.get("genre_name")
        target_url = BYUMA_GENRE_PAGE_URL + genre_list.get("genre_url")
        
        res = None
        try:
            res = session.get(target_url, timeout=(3.0, 18.0))
            res.raise_for_status()
            sleep(8)
        except Exception as e:
            print("Exception:{}".format(e))
            exception_count += 1
            if exception_count > 10:
                print("Exception Count Over!!")
                exit(1)
        
        if res is not None:
            soup = BeautifulSoup(res.text, "html.parser")
            total_item_numwrap = soup.find("p", id="totalitem_numwrap")
            totalitem_num = total_item_numwrap.find("span", id="totalitem_num").text
            totalitem_num = int(totalitem_num.replace(",",""))
            print("TargetName:{},  TotalNum:{}".format(target_name, str(totalitem_num)))

            write_contents = {"category_name":target_name, "total_count": totalitem_num, "url":target_url}
            write_csv(CSV_FILE_NAME, write_contents)

if __name__ == "__main__":
    main()