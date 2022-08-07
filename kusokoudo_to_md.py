from bs4 import BeautifulSoup

'''
Kuso Koudo 募集フォームの .csv を md にするやつ。
'''

def data_to_dict(data):
    '''
    とりあえず、1セット分のデータをdictにする。
    data format:
        タイムスタンプ, ペンネーム, 自己紹介, コード, 使用した言語, コードの説明, 自由
    '''
    keys = ("n", "time", "name", "intro", "code", "lang", "description", "free")
    data[0] = int(data[0]) - 1

    return dict(zip(keys, data))

with open("フォームの回答 1.html", "r", encoding="utf-8", errors="ignore") as f:
    html = f.read()

# セルを順番に打ち込む
soup  = BeautifulSoup(html, 'html.parser')
for i in soup.select("br"):
   i.replace_with("\n")
table = soup.findAll("table")[0]
rows  = table.findAll("tr")
datas = []
for row in rows:
    data = []
    for cell in row.findAll(['td', 'th']):
        data.append(cell.text)
    
    # 最初の方の変なやついらない。
    try:
        if int(data[0]) < 2:
            continue
    except:
        print("format error")
        continue
    
    # print(data_to_dict(data))
    datas.append(data_to_dict(data))

# 書き込み
with open("kusokoudo.md", "w", encoding="utf-8", errors="ignore") as f:
    for data in datas:
        f.write("***\n\n")
        f.write("# No." + str(data["n"])+"\n")
        f.write("# " + data["name"]+" さんからいただきました。\n")

        f.write("## [自己語り欄]\n")
        f.write(data["intro"].replace("\n", "  \n")+"\n\n")
        
        f.write("### [使用言語:"+data["lang"]+"]\n")
        f.write("```"+data["lang"]+"\n")
        f.write(data["code"] + "\n")
        f.write("```\n\n")
        
        f.write("## [コードの説明]\n")
        f.write(data["description"].replace("\n", "  \n") + "\n\n")
        f.write("## [自由記入欄]\n")
        f.write(data["free"].replace("\n", "  \n") + "\n\n")
        f.write("***\n")