from ebooklib import epub
from htmldom import htmldom
from argparse import ArgumentParser
import urllib.request
from urllib.parse import urlparse
from jsonc_parser.parser import JsoncParser

class EpubProcessor:
    def __init__(self,title="No Title", author="Testy McTestFace"):
        self.book = epub.EpubBook()
        self.img_dict = {}
        # set metadata
        self.book.set_title(args.title)
        self.book.set_language('en')

        self.book.add_author(author)

        self.chapters = []
        self.index=1

    def get_file(self,url):
        path = urlparse(url)
        
        with urllib.request.urlopen(url) as f:
            out = f.read() 
            return out
            #with open(outfilename, 'wb') as file:
            #    file.write(out)

    def find_images(self,dom):
        
        imgs = dom.find( "img" )
        for img in imgs:
            orig_url = img.attr('src')
            path = urlparse(orig_url)
            outfilename = (path.netloc + path.path).replace("/","_")
            img.attr('src', "imgs/"+outfilename)
            
            if outfilename not in self.img_dict:
                self.img_dict[outfilename] = {"orignal_url" : orig_url, "added": False}
            
        for key, value in self.img_dict.items():
            content = self.get_file(value['orignal_url'])
            
            if content and value['added'] == False:
                print(value)
                img_item = epub.EpubItem(file_name="imgs/"+key, media_type="image/png", content=content)
                self.book.add_item(img_item)
                value["added"] = True
            #with open(key, 'rb') as file:
            #    print(key)
            #    
            #    img_item = epub.EpubItem(file_name="imgs/"+key, media_type="image/png", content=file.read())
            #    book.add_item(img_item)

    def extract_chapter(self,html_string,container_id):

        dom = htmldom.HtmlDom().createDom(html_string)

        self.find_images(dom)

        title = dom.find( "title" )
        
        content = "<html><head>"
        content = content + title.html()
        content = content + "</head>"
        
        divs = dom.find( "div" )
        
        print(container_id)
        if container_id == None:
            print("No div id so using raw document.")
            content= content + dom.find("body").html()
        else:
            content = content + "<body>"
            for div in divs:
                print(div.attr('id'))
                if div.attr('id') == container_id:
                    pass
                    content = content + div.html()
        
            content = content + "</body>"
        
        return (title.text(), content)

    def add_chapter(self,html,container_id):
        title, content = self.extract_chapter(html,container_id)
        
        # create chapter  
        print(title)
        
        chapter = epub.EpubHtml(title=title, file_name=('chap_%i.xhtml' % self.index), lang='en')  
        chapter.content = content
        self.chapters.append(chapter)

        # add chapter
        self.book.add_item(chapter)
        self.index=self.index+1

    def generate_book(self,output_filename):
        # define Table Of Contents
        self.book.toc = (self.chapters)

        # add default NCX and Nav file
        self.book.add_item(epub.EpubNcx())
        self.book.add_item(epub.EpubNav())

        # define CSS style
        style = 'BODY {color: white;}'
        nav_css = epub.EpubItem(uid="style_nav", file_name="style/nav.css", media_type="text/css", content=style)

        # add CSS file
        self.book.add_item(nav_css)

        # basic spine
        self.book.spine = ['nav'] + self.chapters

        # write to the file
        epub.write_epub(output_filename, self.book, {})

parser = ArgumentParser()
parser.add_argument('--div_id',help='id of div to use to get content from in HTML mode')
parser.add_argument('--title',help='title of book')
parser.add_argument('--author',help='author')
parser.add_argument('--json',help='add files as drescribed by the json file')
parser.add_argument('--html', action='append',help='foo help')
parser.add_argument('--md', action='append',help="add markdown document to book")
parser.add_argument('--out',help='output filename')
args = parser.parse_args()

epub_processor = EpubProcessor(title=args.title,author=args.author)

import os
from subprocess import Popen, PIPE

if args.json:
    file = JsoncParser.parse_file(args.json)

    if "cover" in file:
         # add cover image
        epub_processor.book.set_cover("image.jpg", open(file["cover"], 'rb').read())

    for chapter in file["chapters"]:
        args_popen = ['pandoc']

        if 'pandoc-format' in chapter:
            args_popen += ["-f",chapter["pandoc-format"]]
        
        args_popen += [chapter["filename"], '--to=HTML']
        stdout, stderr = Popen(args_popen, stdout=PIPE, stderr=PIPE).communicate()

        content = "<html><title>"+chapter["name"]+"</title><body>"+stdout.decode('utf-8')+"</body></html>"

        epub_processor.add_chapter(content,None)

if args.md:
    for url in args.md:
        print("##### %s looking for '%s'" % (url.split(':'), args.div_id))
        
        url_split = url.split(':')

        if len(url_split) > 1:
            title = url_split[1]
        else:
            title = url_split[0]

        filename = url_split[0]
        args_popen = ['pandoc', filename, '--to=HTML']
        stdout, stderr = Popen(args_popen, stdout=PIPE, stderr=PIPE).communicate()

        content = "<html><title>"+title+"</title><body>"+stdout.decode('utf-8')+"</body></html>"

        epub_processor.add_chapter(content,None)

if args.html:
    for url in args.html:
        print("##### %s looking for '%s'" % (url, args.div_id))
        div_id = args.div_id
        
        with open(url,'r') as file:
            epub_processor.add_chapter(file.read(), div_id)

epub_processor.generate_book(args.out)