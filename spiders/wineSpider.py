import scrapy
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from time import sleep
from urllib.parse import urlparse, parse_qs
from scrapy.http import TextResponse
from ..items import WineItem
import re
import logging


WINE_NUMBER = 50  # 와인 50개만 크롤링


class WineSpider(scrapy.Spider):
    name = "winespider"

    def start_requests(self):
        # 셀레니움 드라이버 설정
        options = Options()
        options.add_argument("no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument(
            "user-agent=Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.121 Safari/537.36"
        )

        self.driver = webdriver.Chrome(options=options)

        url = "https://www.vivino.com/explore?e=eJwlhcEKgzAQBf_mnbXQ46Mf4K2XHoqUbbKGQLPKmmr9-yoOzMwtbOzuCHseSAMX8axVPijOFuN7o0vNluaXLOqSFKNHRp0Divx4bQ5QsrHBWp89L-daTLtfizpk00i1P40YI9E"
        self.driver.get(url)
        self.driver.implicitly_wait(10)

        yield scrapy.Request(url, self.parse, meta={"use_selenium": True})

    def parse(self, response):
        # 셀레니움을 사용하여 스크롤 다운
        if response.meta.get("use_selenium"):
            page_height = self.driver.execute_script(
                "return document.body.scrollHeight"
            )
            browser_window_height = self.driver.get_window_size(windowHandle="current")[
                "height"
            ]
            current_position = self.driver.execute_script("return window.pageYOffset")

            while page_height - current_position > browser_window_height:
                self.driver.execute_script(
                    f"window.scrollTo({current_position}, {browser_window_height + current_position});"
                )
                current_position = self.driver.execute_script(
                    "return window.pageYOffset"
                )
                sleep(1)  # 컨텐츠 로딩 대기
        self.driver.implicitly_wait(200)

        cards = self.driver.find_elements(
            By.CLASS_NAME, "card__card--2R5Wh.wineCard__wineCardContent--3cwZt"
        )

        for card in cards:
            if i >= WINE_NUMBER:  # 50개만 크롤링
                return
            i += 1
            # 셀레니움으로부터 얻은 HTML을 Scrapy Response 객체로 변환
            new_response = TextResponse(
                url=response.url,
                body=card.get_attribute("outerHTML"),
                encoding="utf-8",
            )

            wine_image = new_response.css(
                ".wineCard__bottleSection--3Bzic img::attr(src)"
            ).get()
            winery_name = new_response.css(
                ".wineInfoVintage__wineInfoVintage--bXr7s .wineInfoVintage__truncate--3QAtw::text"
            ).get()
            wine_name = new_response.css(".wineInfoVintage__vintage--VvWlU::text").get()
            country = new_response.css(
                ".wineInfoLocation__countryFlag--2Davu::attr(title)"
            ).get()
            region = new_response.css(
                ".wineInfoLocation__regionAndCountry--1nEJz::text"
            ).get()
            rating = new_response.css(".vivinoRating_averageValue__uDdPM::text").get()
            ratings_count = new_response.css(".vivinoRating_caption__xL84P::text").get()
            link = new_response.css(".anchor_anchor__m8Qi-::attr(href)").get()
            price = (
                new_response.css(".addToCart__ppcPrice--ydrd5::text")
                .get()
                .split("\\")[0]
            )
            print(
                f"Wine Image: {wine_image}, Winery Name: {winery_name}, Wine Name: {wine_name}, Country: {country}, Region: {region}, Rating: {rating}, Ratings Count: {ratings_count}, Link: {link}, Price: {price}"
            )
            # logging.info(
            #     f"Wine Image: {wine_image}, Winery Name: {winery_name}, Wine Name: {wine_name}, Country: {country}, Region: {region}, Rating: {rating}, Ratings Count: {ratings_count}, Link: {link}, Price: {price}"
            # )

            # WineItem 인스턴스 생성 후 데이터 삽입
            item = WineItem()

            match = re.search(r"/w/(\d+)", link)
            wine_id = match.group(1)

            item["id"] = wine_id
            item["wine_image"] = wine_image
            item["winery_name"] = winery_name
            item["wine_name"] = wine_name
            item["country"] = country
            item["region"] = region
            item["rating"] = rating
            item["ratings_count"] = ratings_count
            item["link"] = link
            item["price"] = price

            # 각 카드마다 상세 정보 수집
            detail_page_url = response.urljoin(link)
            yield scrapy.Request(
                detail_page_url,
                callback=self.parse_detail_page,
                meta={"item": item},
            )
            self.driver.implicitly_wait(100)

    def parse_detail_page(self, response):
        item = response.meta["item"]

        parsed_url = urlparse(response.url)  # URL을 파싱
        query_params = parse_qs(parsed_url.query)  # 쿼리 매개변수 추출

        # 'year'와 'price_id' 추출
        year = query_params.get("year", [None])[0]
        price_id = query_params.get("price_id", [None])[0]

        item["year"] = year
        item["price_id"] = price_id

        self.driver.get(response.url)

        page_height = self.driver.execute_script("return document.body.scrollHeight")
        browser_window_height = self.driver.get_window_size(windowHandle="current")[
            "height"
        ]
        current_position = self.driver.execute_script("return window.pageYOffset")
        while page_height - current_position > browser_window_height:
            self.driver.execute_script(
                f"window.scrollTo({current_position}, {browser_window_height + current_position});"
            )
            current_position = self.driver.execute_script("return window.pageYOffset")
            sleep(1)
        self.driver.implicitly_wait(3)
        # 스크롤 다운 후 가격 정보 추출
        price_element = self.driver.find_element(
            By.CLASS_NAME, "purchaseAvailabilityPPC__amount--2_4GT"
        )
        price = price_element.text if price_element else None

        # 와인 맛 구조 정보 추출
        taste_elements = self.driver.find_elements(
            By.XPATH,
            "/html/body/div[2]/div[7]/div[1]/div/div[2]/div/div[2]/div[1]/table/tbody//tr",  # //tr
        )

        percent_elements = self.driver.find_elements(
            By.XPATH,
            "/html/body/div[2]/div[7]/div[1]/div/div[2]/div/div[2]/div[1]/table/tbody//span",  # //tr
        )

        taste_profiles = {}
        taste_idx = 0
        for element in taste_elements:
            taste_pair = element.text.split("\n")
            left_property = taste_pair[0]  # Light
            right_property = taste_pair[1]  # Bold
            progress = percent_elements[taste_idx]
            style_attribute = progress.get_attribute("style")
            left_percent = style_attribute.split("left: ")[1].split("%")[
                0
            ]  # ex_62.0832

            taste_profiles[left_property + "-" + right_property] = left_percent
            taste_idx += 1

        # 각 맛 카드를 찾고, 내부 텍스트 추출
        sleep(1)

        # "tasteNote__popularKeyword"를 포함하는 클래스를 가진 요소 검색
        keywords_list = self.driver.find_elements(
            By.XPATH, "//*[contains(@class, 'tasteNote__popularKeyword')]"
        )

        keywords = []
        for keyword in keywords_list:
            keywords.append(keyword.text)

        # 빈 문자열 제거
        keywords = [keyword for keyword in keywords if keyword]

        # 리뷰와 평점 정보 추출
        reviews = []
        review_containers = self.driver.find_elements(
            By.XPATH,
            "//div[@data-testid='communityReview']",
        )

        # 각 컨테이너에서 두 번째 span 태그의 텍스트 추출
        for container in review_containers:
            second_span = container.find_elements(By.TAG_NAME, "span")[2]
            writer = container.find_elements(
                By.XPATH, ".//*[contains(@class, 'communityReview__textInfo')]//a"
            )[0].text.split("(")[0]
            created_date = container.find_elements(
                By.XPATH, ".//*[contains(@class, 'communityReview__textInfo')]//a"
            )[1].text.split("(")[0]
            reviews.append(
                {
                    "content": second_span.text,
                    "writer": writer,
                    "created_date": created_date,
                }
            )

        item["average_price"] = price
        item["taste_like"] = taste_profiles
        item["keywords"] = keywords
        item["reviews"] = reviews
        print("====== wineSpider item saved. ======")
        print(item)
        print("====================================")
        yield item

    def closed(self, reason):
        self.driver.quit()
