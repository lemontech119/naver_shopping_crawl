import time
from selenium import webdriver
from collections import OrderedDict

driver = webdriver.Chrome('./chromedriver')
"""
#TODO: 네이버쇼핑 리뷰 많은 순으로 400개의 상품 데이터 크롤링
    1. 네이버 쇼핑 카테고리별 크롤링 (여기서는 우선적으로 간편조리식과 기타냉동/간편조리식품만 진행)
    2. 셀레니움으로 무한 스크롤로 데이터 새로 로드되는 것을 가져와야함
    3. 총 4페이지 진행 (400개 상품)
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
        # try:
        #     if li.find_element_by_class_name("ad_ad_stk__12U34"):
        #         continue
        # except:
        product_data = OrderedDict()
        product_all_data_div = li.find_element_by_class_name("basicList_inner__eY_mq")
        product_image_div = product_all_data_div.find_element_by_class_name("basicList_img_area__a3NRA")
        product_info_div = product_all_data_div.find_element_by_class_name("basicList_info_area__17Xyo")
        product_store_div = product_all_data_div.find_element_by_class_name("basicList_mall_area__lIA7R")


        category_elements = product_info_div.find_elements_by_class_name("basicList_category__wVevj")
        category_count = len(category_elements)
        if category_count == 4:
            product_data["product_category_0"] = category_elements[0].text
            product_data["product_category_1"] = category_elements[1].text
            product_data["product_category_2"] = category_elements[2].text
            product_data["product_category_3"] = category_elements[3].text
        elif category_count == 3:
            product_data["product_category_0"] = category_elements[0].text
            product_data["product_category_1"] = category_elements[1].text
            product_data["product_category_2"] = category_elements[2].text
            product_data["product_category_3"] = ""
        elif category_count == 2:
            product_data["product_category_0"] = category_elements[0].text
            product_data["product_category_1"] = category_elements[1].text
            product_data["product_category_2"] = ""
            product_data["product_category_3"] = ""

        

        product_data["product_name"] = product_info_div.find_element_by_class_name("basicList_link__1MaTN").text.replace(",", "")
        product_data["product_price"] = product_info_div.find_element_by_class_name("basicList_price_area__1UXXR").text.replace(",", "")
        not_sale_count = len(product_info_div.find_elements_by_class_name("basicList_etc__2uAYO"))
        
        

        # return

        if not_sale_count == 3:
            product_data["product_review"] = "X"
            product_data["product_registration"] = product_info_div.find_elements_by_class_name("basicList_etc__2uAYO")[0].text.replace(",", "").replace("등록일 ", "")
        elif not_sale_count == 4:
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
        # product_image_div.click()
        # Open a new window
        driver.execute_script("window.open('');")

        driver.switch_to.window(driver.window_handles[1])
        driver.get(product_data["url"])

        # _2pgHN-ntx6
        time.sleep(2)
        product_star = driver.find_elements_by_class_name("_2Q0vrZJNK1")
        if len(product_star) == 2:
            product_data["star"] = product_star[1].find_element_by_tag_name("strong").text.replace("\n/\n5", "")
        
            
        # print(product_data["star"])

        driver.close()
        driver.switch_to.window(driver.window_handles[0])

        product_data_list.append(product_data)
        
    return product_data_list


def create_product_list_csv(product_data_list):
    print("CSV 작성!!!! ", len(product_data_list))
    f = open("대표님 요청사항10.csv", "a")

    for product in product_data_list:
        for value in product.values():
            f.write(value + ",")
        f.write('\n')

    f.close()
    return


def get_products_from_naver_order_by_review_count(base_url, last_paging):
    loading_pause_time = 3
    product_data_list = []

    for paging_num in range(96, last_paging+96):
        print(paging_num)
        paging_url = f"pagingIndex={paging_num}&"
        crawl_url = base_url + paging_url
        driver.get(crawl_url)
        # if paging_num == 1:
        #     driver.get(crawl_url)
        #     time.sleep(loading_pause_time)
        #     driver.find_element_by_class_name("subFilter_seller_filter__3yvWP").find_elements_by_tag_name("li")[2].click()
        #     time.sleep(loading_pause_time)

        infinity_scroll()

        product_data_list = crawl_from_shop(product_data_list)
        # driver.find_elements_by_class_name("pagination_num__-IkyP")[paging_num].click()
        time.sleep(loading_pause_time)

    create_product_list_csv(product_data_list)

def main():
    base_url = "https://search.shopping.naver.com/search/category?catId=50000006&frm=NVSHCAT&origQuery&pagingSize=40&productSet=window&query&sort=rel&timestamp=&viewType=list&window=fresh&"
    
    last_paging = 10
    f = open("대표님 요청사항10.csv", "a")
    f.write("대분류,중분류,소분류,세분류,상품명,가격,리뷰수,등록일,판매처,배송비,URL,평점\n")
    f.close()

    get_products_from_naver_order_by_review_count(base_url, last_paging)

    driver.quit()

main()
