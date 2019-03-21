from bs4 import BeautifulSoup
from selenium.webdriver import Chrome, ChromeOptions
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
import account

USER = account.Account['AccountID']
PASS = account.Account['LoginPassword']

options = ChromeOptions()
options.add_argument('-headless')
browser = Chrome(options=options)

# ログインページにアクセス
url_login = "https://www.benefit401k.com/customer/RkDCMember/Common/JP_D_BFKLogin.aspx"
browser.get(url_login)
print("ログインページにアクセスしました")

# テキストボックスにユーザーネームを入力
e = browser.find_element_by_id("txtUserID")
e.clear()
e.send_keys(USER)
# テキストボックスにパスワードを入力
f = browser.find_element_by_id("txtPassword")
f.clear()
f.send_keys(PASS)

# アカウントを入力してフォームを送信
frm = browser.find_element_by_id("btnLogin")
frm.click()
print("情報を入力してログインボタンを押しました")

# ページのロード完了まで待機
WebDriverWait(browser, 10).until(EC.presence_of_element_located((By.ID, "D_Chart_Asset:Chart1Map")))
print("ログインできました")

# 資産状況のページへ遷移
a = browser.find_element_by_id("D_Header1_uscD_CategoryMenu1_rptFunctionMenuTable__ctl2_btnMenuData")
a.click()

WebDriverWait(browser, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, "#D_Header1_lblKojinCurrencyUnit01")))
print("資産状況のページへ移動しました")

page_source = browser.page_source
soup = BeautifulSoup(page_source, 'html.parser')

element = soup.find(id="D_Header1_lblKojinBalanceAssets")
BalanceAssets = int(element.string.replace(',', ''))

table_element = soup.find_all("table", id="grdSyouhinzangaku")

with open("table.csv", mode='w', encoding='utf-8', newline="\r\n") as f:
    # table > tbodyにあるtrを全て取得
    rows = soup.find_all("table", id="grdSyouhinzangaku")
    for row in rows:
        # 1つのtrの中にあるtdを全部取得
        content = ""
        position1 = 0
        position2 = 0
        column = row.find_all("tr")
        for tr in column:
            tds = tr.find_all("td")
            for td in tds:
                tex = td.text.replace('\n', '')
                tex = tex.replace('\r', '')
                tex = tex.replace('\t', '')
                if tex == "損益損益率":
                    tex = '損益（円）","損益率（％）'
                    content += '"' + tex + '"'
                    break
                elif tex == "時価単価(1万口当り)":
                    content += '"' + tex + '"'
                elif tex.find('円') >= 0 and tex.find('％') >= 0:
                    position1 = tex.find('円')
                    position2 = tex.find('％')
                    content += "\"" + tex[0:position1] + "\","
                    content += "\"" + tex[position1+1:position2] + "\""
                    break
                elif (tex.find('円') >= 0 or tex.find('口') >= 0) and (tex.find('％') < 0):
                    tex = tex.replace('円', '')
                    tex = tex.replace('口', '')
                    content += '"' + tex + '"'
                    content += ','
                else:
                    content += '"' + tex + '"'
                    content += ','
            f.write(content + '\n')
            content = ""
f.close()

logout = browser.find_element_by_id("D_Header1_btnLogout")
logout.click()
print("ログアウトしました")

browser.quit()

print("ブラウザを閉じました")
