from itemadapter import ItemAdapter
import pymongo


class WineDataProcessingPipeline:
    collection_name = "wine"  # MongoDB에 저장할 컬렉션 이름

    def __init__(self, mongodb_uri, database_name):
        self.mongodb_uri = mongodb_uri
        self.database_name = database_name

    @classmethod
    def from_crawler(cls, crawler):
        mongodb_uri = crawler.settings.get(
            "MONGODB_URI"
        )  # Scrapy 설정에서 MongoDB URI 가져오기
        database_name = crawler.settings.get(
            "MONGODB_DATABASE"
        )  # Scrapy 설정에서 MongoDB 데이터베이스 이름 가져오기
        return cls(mongodb_uri, database_name)

    def open_spider(self, spider):
        self.client = pymongo.MongoClient(self.mongodb_uri)
        self.db = self.client[self.database_name]  # 데이터베이스 선택

    def process_item(self, item, spider):
        adapter = ItemAdapter(item)
        split_keywords = [
            word.strip()
            for phrase in adapter["keywords"]
            for word in phrase.split(",")
            if "." not in word
        ]
        taste_like_to_json = {
            "Light-Bold": float(adapter["taste_like"].get("Light-Bold", 0)),
            "Dry-Sweet": float(adapter["taste_like"].get("Dry-Sweet", 0)),
            "Soft-Acidic": float(adapter["taste_like"].get("Soft-Acidic", 0)),
        }

        # ItemAdapter를 사용하여 item에서 데이터 추출
        adapter = ItemAdapter(item)

        # MongoDB에 저장할 문서 형식 생성
        processed_item = {
            "_id": adapter["id"] + "-" + adapter["year"] + "-" + adapter["price_id"],
            "wine_image": adapter["wine_image"],
            "winery": {
                "name": item["winery_name"],
                "country": adapter["country"],
                "region": adapter["region"],
            },
            "wine": {
                "id": adapter["id"],
                "name": adapter["wine_name"],
                "rating": adapter["rating"],
                "ratings_count": adapter["ratings_count"].split(" ")[0],
                "detail_url": adapter["link"],
            },
            "price_info": {
                "price_id": adapter["price_id"],
                "price": adapter["price"].split(" ")[-1],
                "average_price": adapter["average_price"],
            },
            "tasting_notes": {
                "taste_like": taste_like_to_json,
                "keywords": split_keywords,
            },
            "reviews": adapter["reviews"],
        }

        # MongoDB에 데이터 저장
        # self.db[self.collection_name].insert_one(dict(processed_item))

        # _id가 이미 존재하는지 확인
        existing_item = self.db[self.collection_name].find_one(
            {"_id": processed_item["_id"]}
        )

        # _id가 존재하지 않는 경우에만 삽입
        if not existing_item:
            self.db[self.collection_name].insert_one(processed_item)
        else:
            print(
                f"Item with _id {processed_item['_id']} already exists. Skipping insertion."
            )

        return processed_item

    def close_spider(self, spider):
        self.client.close()
