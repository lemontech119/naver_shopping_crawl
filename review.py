import time
from selenium import webdriver
from collections import OrderedDict

driver = webdriver.Chrome('./chromedriver')
"""
#TODO: 네이버쇼핑 리뷰 많은 순으로 400개의 상품 데이터 크롤링
    1. 네이버 쇼핑 카테고리별 크롤링 (여기서는 우선적으로 간편조리식과 기타냉동/간편조리식품만 진행)
    2. 셀레니움으로 무한 스크롤로 데이터 새로 로드되는 것을 가져와야함
    3. 총 10페이지 진행 (400개 상품)
    4. csv 생성
"""


def infinity_scroll():
    SCROLL_PAUSE_TIME = 3

    last_height = driver.execute_script("return document.body.scrollHeight")

    while True:
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(SCROLL_PAUSE_TIME)
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight-1100);")
        time.sleep(SCROLL_PAUSE_TIME)
        new_height = driver.execute_script("return document.body.scrollHeight")
        print(new_height);
        if new_height == last_height:
            break

        last_height = new_height


def crawl_from_shop(product_data_list):
    product_li = driver.find_elements_by_class_name("basicList_item__2XT81")
    print("한 페이지 ", len(product_li))
    for li in product_li:
        try:
            if li.find_element_by_class_name("ad_ad_stk__12U34"):
                continue
        except:
            product_data = OrderedDict()
            product_all_data_div = li.find_element_by_class_name("basicList_inner__eY_mq")
            product_image_div = product_all_data_div.find_element_by_class_name("basicList_img_area__a3NRA")
            product_info_div = product_all_data_div.find_element_by_class_name("basicList_info_area__17Xyo")
            product_store_div = product_all_data_div.find_element_by_class_name("basicList_mall_area__lIA7R")

            product_data["product_name"] = product_info_div.find_element_by_class_name("basicList_title__3P9Q7").find_element_by_tag_name("a").text.replace(",", "")
            product_data["product_price"] = product_info_div.find_element_by_class_name("basicList_price_area__1UXXR").find_element_by_tag_name("span").text.replace(",", "")
            not_sale_count = len(product_info_div.find_elements_by_class_name("basicList_etc__2uAYO"))
            #             if not_sale_count == 3:
            #                 product_data["product_review"] = "X"
            #                 product_data["product_registration"] = product_info_div.find_elements_by_class_name("basicList_etc__2uAYO")[0].text.replace(",", "").replace("등록일 ", "")
            #             el
            if not_sale_count == 4:
                product_data["product_review"] = product_info_div.find_element_by_class_name("basicList_etc_box__1Jzg6").find_element_by_tag_name("em").text.replace(",", "")
                product_data["product_registration"] = product_info_div.find_elements_by_class_name("basicList_etc__2uAYO")[1].text.replace(",", "").replace("등록일 ", "")
            elif not_sale_count == 5:
                product_data["product_review"] = product_info_div.find_element_by_class_name("basicList_etc_box__1Jzg6").find_element_by_tag_name("em").text.replace(",", "")
                product_data["product_registration"] = product_info_div.find_elements_by_class_name("basicList_etc__2uAYO")[2].text.replace(",", "").replace("등록일 ", "")
            place_store = product_store_div.find_element_by_class_name("basicList_mall_title__3MWFY").find_element_by_tag_name("a")
            if len(place_store.text) > 1:
                product_data["place_store"] = place_store.text.replace(",", "")
            else:
                product_data["place_store"] = product_store_div.find_element_by_class_name("basicList_mall_title__3MWFY").find_element_by_tag_name("img").get_attribute("alt")
            product_data["delivery_charge"] = product_store_div.find_element_by_class_name("basicList_mall_option__1qEUo").find_element_by_tag_name("em").text.replace(",", "").replace("배송비 ", "")
            product_data["url"] = product_image_div.find_element_by_tag_name("a").get_attribute("href").replace(",", "")
            product_data_list.append(product_data)
    return product_data_list


def create_product_list_csv(product_data_list, category_name):
    print("CSV 작성!!!! ", len(product_data_list))
    f = open("product_naver_pay.csv", "a")

    for product in product_data_list:
        f.write(category_name + ",")
        for value in product.values():
            f.write(value + ",")
        f.write('\n')

    f.close()
    return


def get_products_from_naver_order_by_review_count(base_url, category_id, category_name, last_paging):
    loading_pause_time = 3
    category_url = f"catId={category_id}&"
    product_data_list = []

    for paging_num in range(1, 5):
        print(paging_num)
        paging_url = f"pagingIndex={paging_num}&"
        crawl_url = base_url + category_url + paging_url

        if paging_num == 1:
            driver.get(crawl_url)
            time.sleep(loading_pause_time)
            driver.find_element_by_class_name("subFilter_seller_filter__3yvWP").find_elements_by_tag_name("li")[2].click()
            time.sleep(loading_pause_time)

        infinity_scroll()

        product_data_list = crawl_from_shop(product_data_list)
        driver.find_elements_by_class_name("pagination_btn_page__FuJaU")[paging_num].click()
        time.sleep(loading_pause_time)

    create_product_list_csv(product_data_list, category_name)

def main():
    base_url = "https://search.shopping.naver.com/search/category?origQuery&pagingSize=100&productSet=total&query&frm=NVSHCHK&sort=review&"
    category_list = {
        "간편조리식": "50001894",
        "기타냉동/간편조리식품": "50001878",
        "수산가공식품": "50001094",
        "축산가공식품": "50001174",
        "떡": "50001888",
        "면류": "50001084",
        "빵류": "50001889",
        "즉석국/즉석탕": "50001876"
    }
    last_paging = 10
    f = open("product_naver_pay.csv", "a")
    f.write("카테고리,상품명,가격,리뷰수,등록일,판매처,배송비,URL\n")
    f.close()

    for category_name, category_id in category_list.items():
        get_products_from_naver_order_by_review_count(base_url, category_id, category_name, last_paging)

    driver.quit()

main()
