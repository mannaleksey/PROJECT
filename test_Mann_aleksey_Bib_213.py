import datetime
import os
import unittest
from unittest.mock import patch, Mock

from Mann_Aleksey_Bib_213 import *


class Tests(unittest.TestCase):

    def test_browser(self):
        browser()
        off_driver()

    def test_clear_tasks(self):
        expected_result = ['', '', []]
        result = []
        clear_tasks()
        files = ['tasks_class.txt', 'tasks_smart.txt']
        for file in files:
            with open(os.getcwd() + '/tasks/' + file, 'r') as temp:
                result.append(temp.read())
        result.append(os.listdir(os.getcwd() + '/screens'))
        self.assertEqual(expected_result, result)

    def test_logins_passwords(self):
        expected_result = [['smart', 'smart_pass'], ['class', 'class_pass'], ['vk', 'vk_pass']]
        result = []
        auth = logins_passwords([], ['smart_lms.txt', 'classroom.txt', 'vk.txt'])
        for i in auth:
            result.append(i)
        self.assertEqual(expected_result, result)

    def test_classroom(self):
        driver = browser()
        clear_tasks()
        auth = logins_passwords([], ['smart_lms.txt', 'classroom.txt', 'vk.txt'])
        classroom(driver, auth[1], WebDriverWait(driver, 15))
        if (os.listdir(os.getcwd() + '/screens').count('classroom this week.png') == 1) and (
                os.listdir(os.getcwd() + '/screens').count('classroom next week.png') == 1
        ):
            result = True
        else:
            result = False
        self.assertEqual(True, result)

    def test_smart_lms(self):
        driver = browser()
        clear_tasks()
        auth = logins_passwords([], ['smart_lms.txt', 'classroom.txt', 'vk.txt'])
        smart_lms(driver, auth[0])
        with open(os.getcwd() + '/tasks/' + 'tasks_smart.txt', 'r') as temp:
            text = temp.read()
        if text.find('________Актуальные задания ниже________') != -1:
            point = text.find('________Актуальные задания ниже________')
            before = text[:point].rfind('События - ') + 12
            after = text[point:].find('События - ') + 12 + point
            before_after = []
            for i in [before, after]:
                while text[i] != ' ':
                    i += 1
                before_after.append(text[i + 1:i + 3])
            now_day = datetime.datetime.now().day
            if (
                    (int(before_after[0]) <= now_day) and (int(before_after[1]) >= now_day)
            ) and (os.listdir(os.getcwd() + '/screens').count('smart_lms_for_month.png') == 1):
                result = True
            else:
                result = False
        elif os.listdir(os.getcwd() + '/screens').count('smart_lms_for_month.png') == 1:
            result = True
        else:
            result = False
        self.assertEqual(True, result)

    def test_vk_with_smart_lms(self):
        driver = browser()
        clear_tasks()
        auth = logins_passwords([], ['smart_lms.txt', 'classroom.txt', 'vk.txt'])
        smart_lms(driver, auth[0])
        result = vk_log(driver, auth[2], WebDriverWait(driver, 15))
        self.assertEqual(True, result)

    def test_vk_with_classroom(self):
        driver = browser()
        clear_tasks()
        auth = logins_passwords([], ['smart_lms.txt', 'classroom.txt', 'vk.txt'])
        classroom(driver, auth[1], WebDriverWait(driver, 15))
        result = vk_log(driver, auth[2], WebDriverWait(driver, 15))
        self.assertEqual(True, result)

    def test_vk_with_classroom_and_smart_lms(self):
        driver = browser()
        clear_tasks()
        auth = logins_passwords([], ['smart_lms.txt', 'classroom.txt', 'vk.txt'])
        smart_lms(driver, auth[0])
        classroom(driver, auth[1], WebDriverWait(driver, 15))
        result = vk_log(driver, auth[2], WebDriverWait(driver, 15))
        self.assertEqual(True, result)

    def test_off_browser(self):
        driver = browser()
        result = off_driver(driver)
        self.assertEqual(True, result)


if __name__ == '__main__':
    unittest.main()