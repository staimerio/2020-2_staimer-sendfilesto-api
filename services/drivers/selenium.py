# Selenium
from selenium import webdriver
from selenium.webdriver.common.keys import Keys


# Utils
from services.utils.general import is_windows


def download_file(url):
    _path_phantom = r'public/bin/phantomjs'
    if(is_windows()):
        _path_phantom += '.exe'
    html = webdriver.PhantomJS(executable_path=_path_phantom)
    html.get(url)
    html.close()
    # TODO: Implement
    return html
