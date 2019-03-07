from selenium import webdriver
from time import sleep
from avro import schema
from avro.datafile import DataFileWriter
from avro.io import DatumWriter, AvroTypeException




def login_using_selenium(driver):
    driver.find_element_by_id("email").send_keys("8125343137")
    driver.find_element_by_id("pass").send_keys("mahi@1981")
    login_button=driver.find_element_by_id("loginbutton")
    login_button.click()


def search_page(driver,page_id,page_name):
    sleep(2)
    search_box = driver.find_element_by_xpath("//input[@data-testid='search_input']")
    search_box.click()
    search_box.send_keys(page_id)
    driver.find_element_by_xpath("//i[@class='_585_']").click()
    sleep(2)
    _website = driver.find_element_by_xpath("//a[starts-with(text(),'"+page_name+"')]")
    _website.click()
    sleep(3)
    post = driver.find_element_by_xpath("//span[contains(text(),'Posts')]")
    post.click()
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    sleep(5)
    """infinite scroll"""
    SCROLL_PAUSE_TIME = 2
    # Get scroll height
    last_height = driver.execute_script("return document.body.scrollHeight")
    while True:
        # Scroll down to bottom
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        # Wait to load page
        sleep(SCROLL_PAUSE_TIME)
        # Calculate new scroll height and compare with last scroll height
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            break
        last_height = new_height
    """infinite scroll end"""
    posts = []
    posts_path = "//div[contains(@class,'5pcr userContentWrapper')]"
    page = driver.find_elements_by_xpath(posts_path)
    for web_element in page:
        try:
            date = web_element.find_element_by_tag_name('abbr').get_attribute("title")
        except:
            date = ""
        try:
            web_element.find_element_by_xpath(".//a[@class='see_more_link']").send_keys("\n")
        except :
            pass
        captions = []
        for i in web_element.find_elements_by_tag_name("p"):
            captions.append(i.text)
        if captions == []:
            description = "no Caption"
        else:
            description="".join(captions)
        #images/videos
        lis = []
        try:
            l_element = web_element.find_element_by_tag_name("ul")
            img_list=l_element.find_elements_by_tag_name("li")
            for each_img in img_list:
                lis.append(each_img.find_element_by_xpath(".//img[starts-with(@src,'https')]").get_attribute('src'))
            source = ", ".join(lis)
            post_type = "images"
        except:
            try:
                source = web_element.find_element_by_xpath(".//video").get_attribute("src")
                post_type = "video"
            except:
                try:
                    source = web_element.find_element_by_xpath(".//img[starts-with(@class,'scaledImage')]").get_attribute("src")
                    post_type = "image"
                except:
                    source = "No images"
                    post_type="text"
        #comments
        try:
            comments = web_element.find_element_by_xpath(".//a[contains(text(),'Comment')]").text
            comments = comments.replace(" Comments","")
            comments = comments.replace(" Comment", "")
        except:
            comments = "0"


        #likes
        dislikes = 0
        likes = 0
        try:
            web_element.find_element_by_xpath(".//span[@class='_4arz']").click()
            sleep(2)
            likes_list = driver.find_elements_by_xpath("//li[starts-with(@class,'_ds- _45hc')]/a/span/span")
            for item in likes_list:
                x = str(item.get_attribute('aria-label'))
                if "people reacted with Like" in x:
                    likes = int(x.replace(" people reacted with Like", ""))
                if "people reacted with Love" in x:
                    likes = likes + int(x.replace(" people reacted with Love", ""))
                if "people reacted with Wow" in x:
                    likes = likes + int(x.replace(" people reacted with Wow", ""))
                if "people reacted with Haha" in x:
                    likes = likes + int(x.replace(" people reacted with Haha", ""))
                if "people reacted with Angry" in x:
                    dislikes = int(x.replace(" people reacted with Angry", ""))
                if "people reacted with Sad" in x:
                    dislikes = dislikes + int(x.replace(" people reacted with Sad", ""))
        except:
            pass
        try:
            driver.find_element_by_xpath("//a[@data-testid='reactions_profile_browser:close']").click()
            sleep(2)
        except:
            pass

        #shares
        try:
            c = web_element.find_element_by_xpath(".//a[@class='_ipm _2x0m']").text
            share = c.replace(" shares","")
            share = share.replace(" share","")
        except Exception:
            share = "0"
        #views
        try:
            c = web_element.find_element_by_xpath(".//span[@class='_ipm _2x0m']").text
            view = c.replace(" views","")
            view = view.replace(" view","")
        except Exception:
            view = "0"

        posts.append({"id":"null","post_url":"null","platform":"Facebook","organisation":page_name,"caption": description,"post_type":post_type, "post_details":source,"source":"official_page","source_details":page_id,"post_time":date,"no_of_likes": likes,"no_of_dislikes":dislikes, "no_of_comments":comments, "no_of_shares":share,"no_of_views":view})

    avro_schema_path = "posts.avsc"
    avro_target_file = "facebook_lazada.avro"

    avro_schema = schema.parse(open(avro_schema_path, 'r+').read())
    avro_writer = DataFileWriter(open(avro_target_file, "wb"), DatumWriter(avro_schema),
                                 writers_schema=avro_schema,
                                 codec="snappy")

    for i in posts:
        print(i)
        avro_writer.append(i)

    avro_writer.close()



if __name__ == '__main__':
    options = webdriver.ChromeOptions()
    options.add_argument("--disable-notifications")
    # options.add_argument('--headless')
    _driver = webdriver.Chrome("/Users/kovuriabhishek/downloads/chromedriver", chrome_options=options)
    _driver.get("https://www.facebook.com/")
    _driver.maximize_window()

    login_using_selenium(_driver)
    # search_page(_driver,"@jd.cominc","JD.com")

    search_page(_driver,"@LazadaIndonesia02","Lazada Indonesia Online Shopping")
    # search_page(_driver,"@ShopeeID","Shopee")
