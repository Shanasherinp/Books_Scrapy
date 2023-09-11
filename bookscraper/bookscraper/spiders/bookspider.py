import scrapy
from bookscraper.items import BookItem

class BookspiderSpider(scrapy.Spider):
    name = "bookspider"
    allowed_domains = ["books.toscrape.com"]
    start_urls = ["https://books.toscrape.com/"]

    custom_settings = {
        'FEEDS' : {
            'booksdata.json' : {'format' : 'json', 'overwrite' : True},
        }
    }

    def parse(self, response):
        books = response.css('article.product_pod')
        for book in books:
            relative_url = book.css('h3 a ::attr(href)').get()
        
            if 'catalogue/' in relative_url:
                book_url = 'https://books.toscrape.com/' + relative_url
            else:
                book_url = 'https://books.toscrape.com/catalogue/' + relative_url

            yield response.follow(book_url, callback= self.parse_book_page)


        # next_page = response.css('li.next a ::attr(href)').get()
        # if next_page is not None:
        #     if 'catalogue/' in next_page:
        #         next_page_url = 'https://books.toscrape.com/' + next_page
        #     else:
        #         next_page_url = 'https://books.toscrape.com/catalogue/' + next_page

        #     yield response.follow(next_page_url, callback= self.parse)


    def parse_book_page(self, response):

        table_rows = response.css("table tr")
        book_item = BookItem()
        table_dict = {}
        for table_row in table_rows:
            key = table_row.css("th ::text").extract_first("")
            value = table_row.css("td ::text").extract_first("")
            table_dict[key] = value
        # print(table_dict)

        
        book_item['url'] = response.url
        book_item['title'] = response.css('.product_main h1::text').get()
        book_item['upc'] = table_dict.get('UPC', "")
        book_item['product_type'] = table_dict.get('Product Type', "")
        book_item['price_excl_tax'] = table_dict.get('Price (excl. tax)', "")
        book_item['price_incl_tax'] = table_dict.get('Price (incl. tax)', "")
        book_item['tax'] = table_dict.get('Tax', "")
        book_item['availability'] = table_dict.get('Availability', "")
        book_item['num_reviews'] = table_dict.get('Number of reviews', "")
        book_item['stars'] = response.css("p.star-rating").attrib['class']
        book_item['category'] = response.xpath("//ul[@class='breadcrumb']/li[@class='active']/preceding-sibling::li[1]/a/text()").get()
        book_item['description'] = response.xpath("//div[@id='product_description']/following-sibling::p/text()").get()
        book_item['price'] = response.css('p.price_color ::text').get()
        # print(book_item)
        yield book_item
