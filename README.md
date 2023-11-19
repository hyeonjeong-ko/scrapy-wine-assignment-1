# 🍇 scrapy-wine-assignment-1

### 📊 데이터 크롤링 결과
<img width="486" alt="gdgd" src="https://github.com/hyeonjeong-ko/scrapy-wine-assignment-1/assets/72601276/9b9a3d80-a3a3-48c8-b929-8b212cf12087">


### 📄 이슈 및 원인 분석
- 와인 리스트는 모두 크롤링되나(`def parse` 함수), 상세링크 크롤링이 동작할 때마다 크롤링 개수 값이 달라짐 (13~20개 사이).
- 상세링크 크롤링 함수(`callback=self.parse_detail_page`) 부분에서 문제 예상.
- 크롤러의 일관성 없는 동작❓
- 알아보니 Scrapy의 **비동기적 특성**과 셀레니움의 **동기적 특성** 간의 차이를 고려해야 하는데 이를 고려하지 못했음.
- 셀레니움을 사용하여 동적 콘텐츠를 처리하고 Scrapy로 요청을 전달하는 과정에서 문제가 발생한 것을 예상.
- 셀레니움의 `implicitly_wait` 설정이 Scrapy의 비동기 처리와 충돌을 일으킴을 예상.
- Scrapy는 동시에 진행할 수 있는 요청의 수에 제한을 두고 있다고 함. `CONCURRENT_REQUESTS` 설정이 너무 낮으면, 한 번에 많은 요청을 처리하지 못할 수 있다 함.
- 실제로 `CONCURRENT_REQUESTS`와 `DEFAULT_DELAY` 설정에 따라 크롤링 개수가 달라졌음.
