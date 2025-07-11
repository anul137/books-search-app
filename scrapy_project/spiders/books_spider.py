import scrapy
import json
import os

class BooksSpider(scrapy.Spider):
    name = 'books'
    start_urls = ['https://books.toscrape.com/']
    
    def parse(self, response):
        # Extract book URLs from the current page
        book_urls = response.css('article.product_pod h3 a::attr(href)').getall()
        
        for book_url in book_urls:
            yield response.follow(book_url, self.parse_book)
        
        # Follow pagination links
        next_page = response.css('li.next a::attr(href)').get()
        if next_page:
            yield response.follow(next_page, self.parse)
    
    def parse_book(self, response):
        # Extract book information
        title = response.css('h1::text').get()
        price = response.css('p.price_color::text').get()
        availability = response.css('p.instock.availability::text').getall()
        availability = ''.join(availability).strip() if availability else 'Not available'
        
        # Extract rating
        rating_class = response.css('div.product_main p.star-rating::attr(class)').get()
        rating = rating_class.split()[-1] if rating_class else 'No rating'
        
        # Extract description
        description = response.css('div#product_description + p::text').get()
        if not description:
            description = "No description available"
        
        # Extract category
        category = response.css('ul.breadcrumb li:nth-child(3) a::text').get()
        
        # Extract image URL
        image_url = response.css('div.item.active img::attr(src)').get()
        if image_url:
            image_url = response.urljoin(image_url)
        
        yield {
            'title': title,
            'price': price,
            'availability': availability,
            'rating': rating,
            'description': description,
            'category': category,
            'image_url': image_url,
            'url': response.url
        }
