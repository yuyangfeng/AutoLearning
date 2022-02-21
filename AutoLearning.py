import configparser
import datetime
import os
import time

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.ui import WebDriverWait


def getWebDriver(broswer_type, driver_path, port):
    driver_name = 'chromedriver.exe'
    if( broswer_type == "CHROME") :
        driver_name = 'chromedriver.exe'
    service = Service(driver_path + driver_name, int(port))
    options = webdriver.ChromeOptions()
    options.add_experimental_option('w3c', True)
    options.add_experimental_option('excludeSwitches', ['enable-logging'])
    driver = webdriver.Chrome(service=service, options=options)
    return driver

def loadConfigure(config_path):
    cf = configparser.ConfigParser()
    cf.read(config_path)
    user = cf.get("Account", "user")
    password = cf.get("Account", "password")
    port = cf.get("System", "port")
    return user, password, port

def main(driver):

    # login
    driver.find_element(By.ID, "loginName").send_keys(user)
    driver.find_element(By.ID, "password").send_keys(password)
    driver.find_element(By.CLASS_NAME, 'login_Btn').click()
    # 进入“学习地图”
    WebDriverWait(driver, 10, 0.5).until(lambda el:driver.find_element(By.XPATH, '//span[@data-txt="学习地图"]'))
    driver.find_element(By.XPATH, '//span[@data-txt="学习地图"]').click()
    time.sleep(3)
    driver.switch_to.frame(3)
    # 选择需要学习的课程
    # 1. 删选年份
    year = datetime.date.today().year
    year_selector = Select(driver.find_element(By.ID, 'elsLearnMapStatus'))
    year_selector.select_by_value(str(year))
    time.sleep(3)
    # 2. 选择未完成
    driver.find_element(By.ID, 'els-learn-rm-not-finish').click()
    time.sleep(3)
    task_list = driver.find_element(By.XPATH, '//*[@id="trackList"]/ul').find_elements(By.XPATH, 'li')
    # 遍历任务列表
    for i in range(len(task_list)):
        i += 1
        a = driver.find_element(By.XPATH, '//div[@id="trackList"]/ul/li[' + str(i) + ']//a[@class="track-list-linktoName"]')
        title = a._execute("getElementText")['value']
        print('@@@@@@@ 开始学习 ： 《 ', title, ' 》。')
        a.click() # 点击标题进入课程界面
        time.sleep(3)
        # 子课程列表
        sub_task_list = driver.find_elements(By.XPATH, '//*[@id="userCourseDiv"]/div/ul/li')
        for x in range(len(sub_task_list)):
            x += 1
            sub_task = driver.find_element(By.XPATH, '//*[@id="userCourseDiv"]/div/ul/li[' + str(x) + ']')
            sub_task_class = driver.find_element(By.XPATH, '//*[@id="userCourseDiv"]/div/ul/li[' + str(x) + ']').get_attribute("class")
            sub_title = driver.find_element(By.XPATH, '//*[@id="userCourseDiv"]/div/ul/li[' + str(x) + ']//a')._execute("getElementText")['value']
            # 跳过已学习的课程
            if "innerpass" in sub_task_class:
                print('@@@@@@@ 子课程 ： 《 ', sub_title, ' 》。已学习。')
                continue
            # 点击子课程
            sub_task.click()
            print('@@@@@@@ 开始学习子课程 ： 《 ', sub_title, ' 》。')
            # 等待窗口加载，不然selenium无法获取
            time.sleep(3)
            # 切换窗口
            tabs = driver.window_handles
            driver.switch_to.window(tabs[-1])
            # 切换iframe
            driver.switch_to.frame(0)
            # 遍历视频播放列表
            video_list = driver.find_elements(By.XPATH, '//div[@class="section"]/li')
            print("@@@@@@@    本子课程共 ", len(video_list), " 个视频内容需要观看。")
            for video_index in range(len(video_list)):
                video_index += 1
                video_title = driver.find_element(By.XPATH, '//div[@class="section"]/li[' + str(video_index)
                                                  + ']/div[1]/span[1]').get_attribute("title")
                driver.find_element(By.XPATH, '//div[@class="section"]/li[' + str(video_index) + ']').click()
                print("@@@@@@@    开始观看第 ", video_index, " 个视频:《", video_title, "》")
                index = 0
                while True:
                    index += 1
                    content = driver.find_element(By.XPATH, '//div[@class="section"]/li[' + str(video_index)
                                                  + ']/div[1]/span[2]')._execute("getElementText")['value']
                    if "已完成" == content:
                        break
                    else:
                        time.sleep(30)
                    if(index % 10 == 0) :
                        print('@@@@@@@    《 ' + video_title + ' 》已观看', index/2, '分钟。')
                print("@@@@@@@    第 ", video_index, " 个视频:《", video_title, "》已学习完成。")
                continue

            # 等待“下一步”按钮出现
            # index = 0
            # while True:
            #     index = index + 1
            #     try:
            #         # button = driver.find_element(By.XPATH, '//li[@id="goNextStep"]/a') # "下一步"按钮被hide属性影藏
            #         button_class = driver.find_element(By.XPATH, '//li[@id="goNextStep"]').get_attribute('class')
            #         if "hide" not in button_class:
            #             break
            #         else:
            #             time.sleep(30)
            #     except :
            #         time.sleep(30)
            #         print("视频等待异常！")
            #     print('第', index, '次等待，共等待', index / 2, '分钟')
            # 所有视屏观看结束后，暂停3秒等待“下一步”按钮出现
            time.sleep(3)
            # 切出iframe
            driver.switch_to.default_content()
            driver.find_element(By.XPATH, '//li[@id="goNextStep"]/a').click()
            print('@@@@@@@ 课程学习完成 ： 《 ', sub_title, ' 》。进入评分环节。')
            # 进入评分页面
            WebDriverWait(driver, 10, 0.5).until(lambda el: driver.find_element(By.XPATH, '//p[@class="cs-eval-score"]/input[5]'))
            # 课程评分
            driver.find_element(By.XPATH, '//p[@class="cs-eval-score"]/input[5]').click()
            time.sleep(2)
            print('@@@@@@@ 课程 ： 《 ', sub_title, ' 》。评分完成。')
            # 单选题
            questions = driver.find_elements(By.XPATH, '//*[@id="courseEvaluateForm"]/div[1]/ul/li')
            for y in range(len(questions)):
                y = y + 1
                driver.find_element(By.XPATH, '//*[@id="courseEvaluateForm"]/div[1]/ul/li[' + str(y) + ']/div[5]//mark').click()
                time.sleep(1)
            print('@@@@@@@ 课程 ： 《 ', sub_title, ' 》。单选题完成。')
            # 点击提交
            driver.find_element(By.ID, 'courseEvaluateSubmit').click()
            time.sleep(3)
            driver.find_element(By.XPATH, '//*[@id="layui-layer2"]/div[3]/a[2]').click()
            time.sleep(2)
            # 关闭当前tab
            driver.close()
            driver.switch_to.window(driver.window_handles[0])
            driver.switch_to.frame(3)
    print("已全部学习完成！")

if __name__ == '__main__':
    print("===================================================================================")
    print("重要声明：")
    print("    1. 本程序仅供Python和Selenium开发学习使用。请不要使用此程序挂机刷云端学习任务，后果自负。")
    print("==================================================================================")
    # 获取软件当前位置
    path = os.getcwd()
    # 加载配置文件及驱动
    driver_path = path + "/browser/driver/"
    config_path = path + "/config.ini"
    user, password, port = loadConfigure(config_path)
    # open url
    driver = getWebDriver("CHROME", driver_path, port)
    driver.implicitly_wait(5)
    driver.get("http://e-learning.jsnx.net/os/html/deskTop.init.do")
    driver.maximize_window()
    try:
        main(driver)
    except:
        print(">>>>>>>>>>>>>>>>>>>>>>>>>>    发生异常！请阅读软件包中《readme.pdf》文件，按需要修改电脑配置！！！     <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<")
    finally:
        # 退出当前账号
        driver.switch_to.default_content()
        # ActionChains(driver).move_to_element(driver.find_element(By.XPATH, '//div[@role="personal"]/button[@class="tbc-os-btm-btn"]')).perform()
        driver.find_element(By.XPATH, '//div[@role="personal"]/button[@class="tbc-os-btm-btn"]').click()
        # WebDriverWait(driver).until(lambda el:driver.find_element(By.XPATH, '//div[@class="tbc-startMenu-container"]/ul/li[3]'), 10, 0.5)
        time.sleep(1)
        driver.find_element(By.XPATH, '//div[@class="tbc-startMenu-container"]/ul/li[3]').click()
        time.sleep(1)
        driver.close()
        print("==================================================================================")
        print("     (๑•̀ㅂ•́)و✧    (๑•̀ㅂ•́)و✧     (๑•̀ㅂ•́)و✧     (๑•̀ㅂ•́)و✧    (๑•̀ㅂ•́)و✧")
        print("      (*^▽^*)      (*^▽^*)       (*^▽^*)       (*^▽^*)      (*^▽^*)")
        print("==================================================================================")
    os.system("pause")
