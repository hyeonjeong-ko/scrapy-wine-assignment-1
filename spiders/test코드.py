from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import pandas as pd
from time import sleep
from scrapy.http import TextResponse

options = webdriver.ChromeOptions()
# 창 숨기는 옵션 추가
# options.add_argument("headless")

options.add_argument("no-sandbox")
options.add_argument("--disable-dev-shm-usage")
options.add_argument(
    "user-agent={Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.121 Safari/537.36}"
)


driver = webdriver.Chrome(options=options)
red_wine_web_address = "https://www.vivino.com/marques-de-murrieta-castillo-ygay-gran-reserva-especial-blanco/w/5177761?year=1998&price_id=14549868"
driver.get(red_wine_web_address)


driver.implicitly_wait(10)
page_height = driver.execute_script("return document.body.scrollHeight")
browser_window_height = driver.get_window_size(windowHandle="current")["height"]
current_position = driver.execute_script("return window.pageYOffset")
while page_height - current_position > browser_window_height:
    driver.execute_script(
        f"window.scrollTo({current_position}, {browser_window_height + current_position});"
    )
    current_position = driver.execute_script("return window.pageYOffset")
    sleep(1)  # It is necessary here to give it some time to load the content
# driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

# 페이지 소스 가져오기
html_source = driver.page_source

# 파일로 저장
with open("page_source.html", "w", encoding="utf-8") as file:
    file.write(html_source)


# 스크롤 다운 후 가격 정보 추출
price_element = driver.find_element(
    By.CLASS_NAME, "purchaseAvailabilityPPC__amount--2_4GT"
)
price = price_element.text if price_element else None

# 와인 맛 구조 정보 추출
taste_elements = driver.find_elements(
    By.XPATH,
    "/html/body/div[2]/div[7]/div[1]/div/div[2]/div/div[2]/div[1]/table/tbody//tr",  # //tr
)

percent_elements = driver.find_elements(
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
    left_percent = style_attribute.split("left: ")[1].split("%")[0]  # 예: 62.0832

    taste_profiles[left_property + "-" + right_property] = left_percent
    taste_idx += 1


# 각 맛 카드를 찾고, 내부 텍스트 추출
keywords = []

sleep(3)

# keyword1 = driver.find_element(
#     By.XPATH,
#     "/html/body/div[2]/div[7]/div[1]/div/div[2]/div/div[3]/div/div/div/div[1]/button/div[2]/div[1]",
# ).text
# keyword2 = driver.find_element(
#     By.XPATH,
#     "/html/body/div[2]/div[7]/div[1]/div/div[2]/div/div[3]/div/div/div/div[2]/button/div[2]/div[1]",
# ).text
# keyword3 = driver.find_element(
#     By.XPATH,
#     "/html/body/div[2]/div[7]/div[1]/div/div[2]/div/div[3]/div/div/div/div[3]/button/div[2]/div[1]",
# ).text


# "tasteNote__popularKeyword"를 포함하는 클래스를 가진 모든 요소 검색
keywords_list = driver.find_elements(
    By.XPATH, "//*[contains(@class, 'tasteNote__popularKeyword')]"
)

for keyword in keywords_list:
    keywords.append(keyword.text)

# 빈 문자열 제거
keywords = [keyword for keyword in keywords if keyword]

# 리뷰와 평점 정보 추출

# sleep(1)
# reviews = []
# reviews_1 = driver.find_element(
#     By.XPATH,
#     "/html/body/div[2]/div[7]/div[1]/div/div[5]/div/div[2]/div[1]/div[1]/div/div[1]/div[1]/a/span[2]",

# ).text

# reviews.append(reviews_1)
# reviews_2 = driver.find_element(
#     By.XPATH,
#     "/html/body/div[2]/div[7]/div[1]/div/div[5]/div/div[2]/div[1]/div[2]/div/div[1]/div[1]/a/span[2]",
# ).text
# reviews.append(reviews_2)
# 특정 XPath에 위치한 'data-testid="communityReview"'를 가진 div 태그 선택
reviews = []
review_containers = driver.find_elements(
    By.XPATH,
    "//div[@data-testid='communityReview']",
)

# 각 컨테이너에서 두 번째 span 태그의 텍스트 추출
for container in review_containers:
    print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
    print(container.text)
    # container 내의 두 번째 span 태그 선택
    second_span = container.find_elements(By.TAG_NAME, "span")[2]

    writer = container.find_elements(
        By.XPATH, ".//*[contains(@class, 'communityReview__textInfo')]//a"
    )[0].text.split("(")[0]
    created_date = container.find_elements(
        By.XPATH, ".//*[contains(@class, 'communityReview__textInfo')]//a"
    )[1].text.split("(")[0]
    print(writer + "@@@@")
    print(created_date + "@@@@")
    print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
    reviews.append(second_span.text)


print("============================================================================")
print(
    "price",
    price,
    "taste_profiles",
    taste_profiles,
    "reviews",
    reviews,
    "keywords",
    keywords,
)


driver.quit()
