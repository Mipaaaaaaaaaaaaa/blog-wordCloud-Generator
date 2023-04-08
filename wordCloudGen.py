import base64
import datetime
import json
import os
import random
import time
from wordcloud import WordCloud
import matplotlib.pyplot as plt
from notion.client import NotionClient
from notion.block import ImageBlock
# Display the generated image:
# the matplotlib way:

import re
import requests as rq
import jieba

from config import *
# 使worldCloudGen.py能够读取到config.py中的变量
from time import sleep
from tqdm import tqdm

plt.ion()

def notionnext_crawler():
    print("Get All Urls...")
    content = rq.get(ARCHIVE_URL).content.decode("utf-8")
    regex = re.compile('href="/article/(.*?)">')
    urls = re.findall(regex, content)
    print("Get All Urls Sucess!")
    print("Count = " + str(len(urls)))
    # 获取了所有的url，逐个访问
    dataList = []
    for url in tqdm(urls):

        articleContent = rq.get(ARTICLE_URL+url).content.decode("utf-8")
        textRegex = re.compile('<div class="notion-text \S*">(.*?)</div>')
        articleLines = re.findall(textRegex, articleContent)
        dataList = dataList + articleLines

    d = os.path.dirname(__file__) if "__file__" in locals() else os.getcwd()
    with open(os.path.join(d, TEXT_PATH), "w", encoding="utf-8") as fp:
        fp.write('\n'.join(str(i) for i in dataList))

    print("Crawl Sucess!")

def wordcloud_draw():
    print("Draw WordCloud...")
    # get data directory (using getcwd() is needed to support running example in generated IPython notebook)
    d = os.path.dirname(__file__) if "__file__" in locals() else os.getcwd()
    font_path = d + FRONT_PATH
    # Read the whole text.
    text = open(os.path.join(d, TEXT_PATH), "r", encoding="utf-8").read()

    # Generate a word cloud image
    mywordlist = []
    seg_list = jieba.cut(text, cut_all=False)
    liststr = "/".join(seg_list)
    stopwords_path = d + '/stopwords_cn_en.txt'

    with open(stopwords_path, encoding='utf-8') as f_stop:
        f_stop_text = f_stop.read()
        f_stop_seg_list = f_stop_text.splitlines()

    for myword in liststr.split('/'):
        if not (myword.strip() in f_stop_seg_list) and len(myword.strip()) > 1:
            mywordlist.append(myword)
    wc = WordCloud(font_path=font_path, background_color="white", max_words=200,
               max_font_size=150, random_state=100, width=1000, height=1000, margin=10, colormap='pink')
    # f = open(os.path.join(d, 'saveJson.json'), "w", encoding="utf-8")
    # json.dump(mywordlist, f)
    # f.close()
    random.shuffle(mywordlist) # 随机一下列表
    # print(mywordlist)
    wc.generate(' '.join(mywordlist))
    wc.to_file(TARGET_IMG_PATH)
    print("Draw Sucess!")

def get_imageUrl():
    # 自己想要请求的接口地址
    with open(TARGET_IMG_PATH, "rb") as f_abs: # 以2进制方式打开图片
        img_data = f_abs.read()
        base64_data = base64.b64encode(img_data)
        body = {
            "source":base64_data,
        }
        # 上传图片的时候，不使用data和json，用files
        response = rq.post(url=IMAGE_UPLOAD_URL, data=body).text
        jsonDic = json.loads(response)
        # print(jsonDic)
        if jsonDic["image"] == None:
            print("Get Image Failed! Reason:\n")
            print(jsonDic)
            return ""
        else:
            return jsonDic["image"]["url"]

def wordcloud_update():
    print("Upload to Notion.so...")

    # Obtain the `token_v2` value by inspecting your browser cookies on a logged-in (non-guest) session on Notion.so
    client = NotionClient(token_v2=NOTION_TOKEN)

    # Replace this URL with the URL of the page you want to edit
    page = client.get_block(PAGE_CODE)

    imageUrl = get_imageUrl()
    if imageUrl == "":
        print("Upload Failed! Time: " + str(datetime.datetime.now()) + "\n")
        return

    # 这里我用的是先删再加的方式，如果你想要更新的话，可以直接修改图片的url
    # page.children[0].set_source_url(get_imageUrl())    
    for child in page.children:
        child.remove()

    image = page.children.add_new(ImageBlock, width=1000, height=1000)

    image.set_source_url(imageUrl)
    print("Upload Success!")

def daily_update():
    print("Daily Update start...")
    notionnext_crawler()
    wordcloud_draw()
    wordcloud_update()
    print("Daily Update Success!")

def main():
    waitTime = 60 * 60 * 24
    print("Update start...")
    # while True:
    daily_update()
        # time.sleep(waitTime)

if __name__ == "__main__":
    main()