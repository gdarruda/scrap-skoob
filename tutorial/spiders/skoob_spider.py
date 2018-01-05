import scrapy


class ReviewsSkoob(scrapy.Spider):
    name = "reviewsSkoob"

    def start_requests(self):

        # Total of books is 456921
        urls = ["https://www.skoob.com.br/livro/resenhas/" + str(i) for i in range(1, 10000)]

        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse)

    def get_user(self, user):
        return user.split('/')[-1]

    def get_review(self, review):
        return ' '.join(review)

    def parse(self, response):

        self.log(f"Processing {response.url} ...")

        book_info = response.xpath("//div[@id='pg-livro-menu-principal-container']")
        author = book_info.xpath(".//a[contains(@href, '/autor/')]/text()").extract_first()
        book_name = book_info.xpath(".//strong[@class='sidebar-titulo']/text()").extract_first()

        reviews = []

        for review in response.xpath("//div[re:test(@id, 'resenha[0-9]+')]"):

            review_id = review.xpath("./@id").extract_first()
            user_id = self.get_user(review.xpath(".//a[contains(@href, '/usuario/')]/@href").extract_first())
            rating = review.xpath(".//star-rating/@rate").extract_first()
            text = self.get_review(response.xpath(f".//div[@id='resenhac{review_id[7:]}']/text()").extract())

            reviews.append({'review_id': review_id,
                            'user_id': user_id,
                            'rating': int(rating),
                            'text': text})

            self.log(f"Review {review_id} processed for {book_name}")

        if len(reviews) > 0:
            yield {
                'author': author,
                'book_name': book_name,
                'reviews': reviews
            }

        next_page = response.css('div.proximo')

        if next_page is not None:
            relative_url = next_page.xpath('.//a/@href').extract_first()
            yield response.follow(relative_url, callback=self.parse)
