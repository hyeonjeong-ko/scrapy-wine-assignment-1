# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class WineItem(scrapy.Item):
    id = scrapy.Field()
    wine_image = scrapy.Field()
    winery_name = scrapy.Field()
    wine_name = scrapy.Field()
    country = scrapy.Field()
    region = scrapy.Field()
    rating = scrapy.Field()
    ratings_count = scrapy.Field()
    link = scrapy.Field()
    price = scrapy.Field()

    average_price = scrapy.Field()  # 평균 가격
    taste_like = scrapy.Field()  # 맛 구조 정보
    keywords = scrapy.Field()  # 키워드
    reviews = scrapy.Field()  # 리뷰
    year = scrapy.Field()
    price_id = scrapy.Field()
