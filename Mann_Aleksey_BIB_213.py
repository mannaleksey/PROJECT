from tkinter import *
from selenium.webdriver.common.action_chains import ActionChains
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec
import time
import pickle
import os
import shutil
import datetime


def clear_tasks():
    """
    Эта функция чистит два текстовика и удаляет все скриншоты
    """

    text_books = ['tasks_class.txt', 'tasks_smart.txt']
    for text_book in text_books:
        with open(os.getcwd() + '/tasks/' + text_book, 'w', encoding='utf-8') as all_tasks:
            all_tasks.truncate(0)
    for root, dirs, files in os.walk(os.getcwd() + '/screens'):
        for f in files:
            os.unlink(os.path.join(root, f))
        for d in dirs:
            shutil.rmtree(os.path.join(root, d))


def logins_passwords(auth, accounts):
    """
    Записываю в auth все логины и пароли для smart_lms, classroom и vk
    :param auth - пустой массив, в который в дальнейшем будут записываться log:pass для smart lms ,classroom, vk
    :param accounts - массив, в котором записаны в виде str все текстовики, в которых лежат log:pass
    """

    for acc in accounts:
        with open(os.getcwd() + '/log/' + acc, 'r', encoding='utf-8') as temp:
            auth.append(temp.read().split(':'))
    return auth


def smart_lms(driver, auth):
    """
    Захожу на сайт, с помощью auth[0]
     и записываю в текстовый документ информацию о предстоящих событиях и дополнительно скриню их
     :param driver - сам бразуер, его мы получили в другой функции создания сессии браузера
     :param auth - передаю auth[0], потому что в массиве auth идет 3 массива по порядку, в который находится
     log:pass от smart lms, classroom, vk соответственно для smart lms нужно передать auth[0]
     """

    driver.get('https://edu.hse.ru/calendar/view.php?view=month')
    driver.find_element_by_xpath('//div[@class="potentialidp"]/a').click()
    log_pass = driver.find_elements_by_xpath('//input[@class="text fullWidth"]')
    for elem in log_pass:
        elem.send_keys(auth[0])
        auth.pop(0)
    driver.find_element_by_xpath('//span[@class="submit"]').click()

    elem = driver.find_element_by_xpath(
        '//div[@class="maincalendar"]//div[@class="calendarwrapper"]'
    )
    elem.location_once_scrolled_into_view
    elem.screenshot(os.getcwd() + '/screens' + '/smart_lms_for_month.png')

    tasks_days = driver.find_elements_by_xpath(
        '//div[@class="d-none d-md-block hidden-phone text-xs-center"]//div[@data-region]//li/a'
    )
    temp_day = ''
    now_day = datetime.datetime.now().day
    key = 0
    with open(os.getcwd() + '/tasks/' + 'tasks_smart.txt', 'w', encoding='utf-8') as textbook:
        for task in tasks_days:
            title = task.get_attribute('title')
            link = task.get_attribute('href')
            day = driver.find_element_by_xpath(
                f'//a[@title="{title}"]/../a[@href="{link}"]/../../../../a'
            )
            if int(day.text) >= now_day and key == 0:
                textbook.write('________Актуальные задания ниже________\n\n')
                key = 1

            full_day = day.get_attribute('title')
            if temp_day != full_day:
                textbook.write(' ' * 8 + full_day + '\n' * 2)
            temp_day = full_day
            textbook.write(title + '\n' + '(' + link + ')' + '\n' * 2)


def classroom(driver, auth, wait):
    """
    Захожу на сайт, с помощью auth[1] (по возможности по куки)
     и записываю в текстовый документ информацию о предстоящих событиях и дополнительно скриню их
     :param driver - сам бразуер, его мы получили в другой функции создания сессии браузера
     :param auth - передаю auth[1], потому что в массиве auth идет 3 массива по порядку, в который находится
     log:pass от smart lms, classroom, vk соответственно для classroom нужно передать auth[1]
     :param wait - сюда передается WebDriverWait(driver, 15),
     данный параметр необходим для ожидания элементов на странице
     """

    driver.get('https://classroom.google.com/u/5/a/not-turned-in/all')
    if 'cookies_classroom' in os.listdir(os.getcwd()):
        for cookie in pickle.load(open('cookies_classroom', 'rb')):
            try:
                driver.add_cookie(cookie)
            except:
                pass
        driver.get('https://classroom.google.com/u/5/a/not-turned-in/all')
    try:
        driver.implicitly_wait(3)
        driver.find_element_by_xpath('//input[@type="email"]')
        driver.implicitly_wait(20)
        print('cookies invalid')
        if 'cookies_classroom' in os.listdir(os.getcwd()):
            os.remove(os.getcwd() + '/cookies_classroom')
        driver.find_element_by_xpath('//input[@type="email"]').send_keys(auth[0], Keys.ENTER)
        wait.until(ec.element_to_be_clickable((By.XPATH, '//input[@type="password"]')))
        driver.find_element_by_xpath('//input[@type="password"]').send_keys(auth[1], Keys.ENTER)
        time.sleep(1)
        driver.get('https://classroom.google.com/u/5/a/not-turned-in/all')
        wait.until(ec.presence_of_element_located((
            By.XPATH, '//div[@class="ovsVve LBlAUc "]'
        )))
        pickle.dump(driver.get_cookies(), open('cookies_classroom', 'wb'))
    except:
        driver.implicitly_wait(20)
    elements = driver.find_elements_by_xpath('//div[@class="ovsVve LBlAUc "]')
    for element in elements[1:3]:
        driver.execute_script("arguments[0].setAttribute('aria-expanded','true')", element)
    elements[1].location_once_scrolled_into_view
    elements[1].screenshot(os.getcwd() + '/screens' + '/classroom this week.png')
    elements[2].location_once_scrolled_into_view
    elements[2].screenshot(os.getcwd() + '/screens' + '/classroom next week.png')
    tasks = driver.find_elements_by_xpath(
        '//div[@class="ovsVve LBlAUc "]//h2[contains(text(),"недел")][1]/../following-sibling::div//a'
    )
    temp_date = ''
    with open(os.getcwd() + '/tasks/' + 'tasks_class.txt', 'w', encoding='utf-8') as textbook:
        for task in tasks:
            title = task.text
            link = task.get_attribute('href')[28:]
            dates = driver.find_element_by_xpath(
                f'//div[@class="ovsVve LBlAUc "]//a[@href="{link}"]/../../../../..//h2[1]/..'
            ).text
            date = dates.split('\n')
            if date[0] != temp_date:
                textbook.write(' ' * 8 + date[0] + '\n' * 2)
            textbook.write(title + '\n' + '(' + 'https://classroom.google.com' + link + ')' + '\n' * 2)
            temp_date = date[0]


def vk_log(driver, auth, wait):
    """
    Захожу в вк по auth[2] (по возможности по куки) и захожу в свою беседу для данного проекта,
    где по очереди добавляю полученную информацию
    :param driver - сам бразуер, его мы получили в другой функции создания сессии браузера
    :param auth - передаю auth[2], потому что в массиве auth идет 3 массива по порядку, в который находится
    log:pass от smart lms, classroom, vk соответственно для vk нужно передать auth[2]
    :param wait - сюда передается WebDriverWait(driver, 15),
    данный параметр необходим для ожидания элементов на странице
    """

    driver.get('https://vk.com/')
    if 'cookies_vk' in os.listdir(os.getcwd()):
        for cookie in pickle.load(open('cookies_vk', 'rb')):
            try:
                driver.add_cookie(cookie)
            except:
                pass
        driver.refresh()
    try:
        driver.implicitly_wait(4)
        driver.find_element_by_xpath('//ol[@class="side_bar_ol"]/li[8]')
        driver.implicitly_wait(20)
    except:
        driver.implicitly_wait(20)
        driver.find_element_by_xpath(
            '//div[@class="page_block index_login"]//input[@name="email"]'
        ).send_keys(auth[0])
        driver.find_element_by_xpath(
            '//div[@class="page_block index_login"]//input[@name="pass"]'
        ).send_keys(auth[1], Keys.ENTER)
        wait.until(ec.presence_of_element_located((
            By.XPATH, '//ol[@class="side_bar_ol"]/li[8]'
        )))
        pickle.dump(driver.get_cookies(), open('cookies_vk', 'wb'))

    driver.get('https://vk.me/join/WvKydIgoR0tT30XyMinmY2wPC2Hg7BbBmuc=')
    screens = os.listdir(os.getcwd() + '/screens')
    text_books = []
    for i in screens:
        if i.find('classroom') != -1:
            text_books.append('tasks_class.txt')
        if i.find('smart') != -1:
            text_books.append('tasks_smart.txt')
    print(text_books)
    key1 = 0
    key2 = 0
    for text_book in text_books:
        with open(os.getcwd() + '/tasks/' + text_book, 'r', encoding='utf-8') as textbook:
            elem = driver.find_element_by_xpath('//div[@class="im_editable im-chat-input--text _im_text"]')
            elem.send_keys('1')
            time.sleep(1)

            menu = driver.find_element(By.XPATH, '//div[@class="im_chat-input--buttons"]/following-sibling::button')
            actions = ActionChains(driver)
            actions.move_to_element(menu)
            actions.pause(1)
            actions.perform()
            driver.find_element(By.XPATH, '//div[@data-val="1"]').click()

            elem.clear()
            text = textbook.read()

            screen_elem = driver.find_element_by_xpath('//div[@class="im_chat-input--buttons"]//input')
            driver.execute_script("arguments[0].setAttribute('height','1000px')", screen_elem)
            driver.execute_script("arguments[0].setAttribute('width','1000px')", screen_elem)
            driver.execute_script("arguments[0].setAttribute('opacity','1')", screen_elem)

            if (key1 == 0) and ('classroom this week.png' in os.listdir(os.getcwd() + '/screens')):
                if text.find('        Следующая неделя') != -1:
                    elem.send_keys(text[:text.find('        Следующая неделя')])
                else:
                    elem.send_keys(text[text.find('        На этой неделе'):])
                screen_elem.send_keys(os.getcwd() + '/screens/' + 'classroom this week.png')
                key1 = 1
            elif (key2 == 0) and ('classroom next week.png' in os.listdir(os.getcwd() + '/screens')):
                elem.send_keys(text[text.find('        Следующая неделя'):])
                screen_elem.send_keys(os.getcwd() + '/screens/' + 'classroom next week.png')
                key2 = 1
            elif 'smart_lms_for_month.png' in os.listdir(os.getcwd() + '/screens'):
                elem.send_keys(text)
                screen_elem.send_keys(os.getcwd() + '/screens/' + 'smart_lms_for_month.png')
        driver.find_element_by_xpath('//div[@class="im_chat-input--buttons"]/following-sibling::button').click()
        time.sleep(1)
        driver.refresh()
        time.sleep(6)
    return True


def browser():
    """Запуск браузера"""
    options = webdriver.ChromeOptions()
    options.add_experimental_option('excludeSwitches', ['enable-logging'])
    # options.add_argument("--headless")
    driver = webdriver.Chrome(options=options, executable_path=r'chromedriver.exe')
    driver.implicitly_wait(20)
    driver.delete_all_cookies()
    return driver


def off_driver(driver):
    """
    Закрытие браузера
    :param driver - сам бразуер, его мы получили в другой функции создания сессии браузера
    """

    driver.close()
    driver.quit()
    return True


def main():
    """
    Главная функция, в которой запускаю мини-приложение с возможность выбрать, какую информацию я хочу получить
    """

    def btn_classroom():
        """Получаю и загружаю в беседу вк информацию по заданиям classroom"""
        info['text'] = 'Открывается браузер...'
        driver = browser()
        clear_tasks()
        auth = logins_passwords([], ['smart_lms.txt', 'classroom.txt', 'vk.txt'])
        info['text'] = 'Открывается сайт...'
        classroom(driver, auth[1], WebDriverWait(driver, 15))
        info['text'] = 'Задания classroom собраны.\nОткрывается вк...'
        vk_log(driver, auth[2], WebDriverWait(driver, 15))
        info['text'] = 'Задания отправлены'
        off_driver(driver)
        return True

    def btn_smart_lms():
        """Получаю и загружаю в беседу вк информацию по заданиям smart lms"""
        info['text'] = 'Открывается браузер...'
        driver = browser()
        clear_tasks()
        auth = logins_passwords([], ['smart_lms.txt', 'classroom.txt', 'vk.txt'])
        info['text'] = 'Открывается smart_lms...'
        smart_lms(driver, auth[0])
        info['text'] = 'Задания smart lms собраны.\nОткрывается classroom...'
        vk_log(driver, auth[2], WebDriverWait(driver, 15))
        info['text'] = 'Задания отправлены'
        off_driver(driver)
        return True

    def btn_smart_lms_and_classroom():
        """Получаю и загружаю в беседу вк информацию по заданиям classroom и smart lms"""
        info['text'] = 'Открывается браузер...'
        driver = browser()
        clear_tasks()
        auth = logins_passwords([], ['smart_lms.txt', 'classroom.txt', 'vk.txt'])
        info['text'] = 'Открывается smart_lms...'
        smart_lms(driver, auth[0])
        info['text'] = 'Задания smart lms собраны.\nОткрывается classroom...'
        classroom(driver, auth[1], WebDriverWait(driver, 15))
        info['text'] = 'Задания classroom собраны.\nОткрывается вк...'
        vk_log(driver, auth[2], WebDriverWait(driver, 15))
        info['text'] = 'Задания отправлены'
        off_driver(driver)
        return True

    root = Tk()
    root['bg'] = '#fafafa'
    root.title('Проект АиП')
    root.wm_attributes('-alpha', 1)
    root.geometry('240x180')
    root.resizable(width=False, height=False)
    frame = Frame(root, bg='#ffb700', bd=5)
    frame.place(relx=0.15, rely=0.7, relwidth=0.69,relheight=0.23)
    info = Label(frame, text='Статус процесса', bg='#ffb700')
    info.pack()
    Label(root, text='Выберите откуда нужно узнать\nпредстоящие задания:', bg='white').pack()
    Button(root, text='Classroom', command=btn_classroom).place(relx=0.15, rely=0.23, relwidth=0.3, relheight=0.15)
    Button(root, text='Smart_lms', command=btn_smart_lms).place(relx=0.55, rely=0.23, relwidth=0.3, relheight=0.15)
    Button(root, text='Classroom и Smart_lms', command=btn_smart_lms_and_classroom).place(
        relx=0.2, rely=0.43, relwidth=0.6, relheight=0.15
    )
    root.mainloop()


if __name__ == '__main__':
    main()
