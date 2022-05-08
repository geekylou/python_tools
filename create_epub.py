from ebooklib import epub
from htmldom import htmldom
from argparse import ArgumentParser
import urllib.request
from urllib.parse import urlparse

def get_file(url):
    path = urlparse(url)
    
    with urllib.request.urlopen(url) as f:
        out = f.read() 
        return out
        #with open(outfilename, 'wb') as file:
        #    file.write(out)

def find_images(book,dom):
    img_dict = {}
    imgs = dom.find( "img" )
    for img in imgs:
        path = urlparse(img.attr('src'))
        outfilename = (path.netloc + path.path).replace("/","_")
        img.attr('src', "imgs/"+outfilename)
        
        img_dict[outfilename] = {}
        
    for key, value in img_dict.items():
        content = get_file(key)
        
        if content:
            img_item = epub.EpubItem(file_name="imgs/"+key, media_type="image/png", content=content)
            book.add_item(img_item)
        
        #with open(key, 'rb') as file:
        #    print(key)
        #    
        #    img_item = epub.EpubItem(file_name="imgs/"+key, media_type="image/png", content=file.read())
        #    book.add_item(img_item)
def extract_chapter(book,url,container_id):
    dom = htmldom.HtmlDom(url).createDom()

    find_images(book,dom)

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

def add_chapter(url,container_id,index,chapters,book):
    title, content = extract_chapter(book,url,container_id)
    
    # create chapter  
    print(title)
      
    chapter = epub.EpubHtml(title=title, file_name=('chap_%i.xhtml' % index), lang='en')  
    chapter.content = content
    chapters.append(chapter)

    # add chapter
    book.add_item(chapter)

parser = ArgumentParser()
parser.add_argument('--div_id',help='foo help')
parser.add_argument('--title',help='foo help')
parser.add_argument('--url', action='append',help='foo help')
args = parser.parse_args()

book = epub.EpubBook()

# set metadata
book.set_title(args.title)
book.set_language('en')

book.add_author('Testy McTestFace')

chapters = []
index=1
for url in args.url:
    print("##### %s looking for '%s'" % (url, args.div_id))
    div_id = args.div_id
    
    add_chapter(url, div_id, index, chapters, book)
    index=index+1

# define Table Of Contents
book.toc = (chapters)

# add default NCX and Nav file
book.add_item(epub.EpubNcx())
book.add_item(epub.EpubNav())

# define CSS style
style = 'BODY {color: white;}'
nav_css = epub.EpubItem(uid="style_nav", file_name="style/nav.css", media_type="text/css", content=style)

# add CSS file
book.add_item(nav_css)

# basic spine
book.spine = ['nav'] + chapters

# write to the file
epub.write_epub('test_out.epub', book, {})