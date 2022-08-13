'''
Google フォームの回答一覧をスプレッドシート経由で .html で出力されたものを .md にするやつ
'''

import os
from pathlib import Path
import json

from bs4 import BeautifulSoup

'''
ナンバーは変数名 index 固定
'''

PathLike = str | bytes | os.PathLike

class FormToMarkDown:
    def __init__(self, form_data_path: PathLike, templete_path: PathLike) -> None:
        self.__load_templete(templete_path)
        self.__load_form_data(form_data_path)
        self.__numbering()

    def __load_templete(self, templete_path: PathLike) -> None:
        templete_path = Path(templete_path)

        # 変数設定を読み込み
        variables_json = json.load(open(templete_path.joinpath("variables.json"), encoding="utf-8"))
        self.index_to_var = {}
        self.ord_setting = {}
        for var_json in variables_json:
            if var_json["type"] == "ord":
                self.ord_setting = var_json
            elif var_json["type"] in ("str", "raw-str", "no-break-str", "google-drive-image"):
                # ここもそのうちリスト別に分けたいね
                self.index_to_var[var_json["index"]] = var_json

        # テンプレートの読み込み
        with open(templete_path.joinpath("templete.md"), encoding="utf-8") as f:
            self.markdown_templete = f.read()

    def __image_link_to_md_image(self, url: str) -> str:
        if not url:
            return "null"

        converted_url = url.replace("open?", "uc?export=view&")
        return f"![image]({converted_url})"

    def __list_to_structured_data(self, data_list: list[str]) -> dict:
        structured_data = {}
        for i, data in enumerate(data_list):
            var = self.index_to_var.get(i)
            if var == None:
                continue

            # いつか dict{var_type: func} でまとめるかも
            var_type = var["type"]
            var_name = var["name"]
            if var_type == "str":
                structured_data[var_name] = data.replace("\n", "<br>")
            elif var_type == "raw-str":
                structured_data[var_name] = data

            elif var_type == "no-break-str":
                structured_data[var_name] = data.replace("\n", "")

            elif var_type == "google-drive-image":
                structured_data[var_name] = self.__image_link_to_md_image(data)

        return structured_data

    def __load_form_data(self, form_data_path: PathLike) -> None:
        # issue: #1
        # この方法では一部扱えない文字(空白文字のみで情報を表現した行)が存在するが, その場合は pastebin などのサービスを使ってもらうようにする。
        with open(form_data_path, "r", encoding="utf-8", errors="ignore") as f:
            html = f.read()
        soup = BeautifulSoup(html, 'html.parser')
        for i in soup.select("br"):
            i.replace_with("\n")

        table = soup.findAll("table")[0]
        rows  = table.findAll("tr")

        self.structured_datum: list[dict] = []
        for r in rows:
            data_list = []
            for cell in r.findAll(['td', 'th']):
                data_list.append(cell.text)

            try:
                if int(data_list[0]) < 2:
                    # 1行目のラベル部分はいらない
                    # data_list[0] は 行数
                    continue
            except:
                # なぜか紛れ込む邪魔な行を削除
                continue

            else:
                self.structured_datum.append(self.__list_to_structured_data(data_list))

    def __numbering(self) -> None:
        # ランダムにするやつも入れたほうがいいかも
        max_n = len(self.structured_datum)
        for i in range(max_n):
            self.structured_datum[i]["index"] = i

    def __structured_data_to_markdown(self, structured_data: dict) -> str:
        ans = self.markdown_templete
        for key, value in structured_data.items():
            # 正規表現で高速化する
            ans = ans.replace(f"[[{key}]]", str(value))
        return ans

    def write(self, mark_down_path: PathLike) -> None:
        shaped_answers: list[str] = map(self.__structured_data_to_markdown, self.structured_datum)

        with open(mark_down_path, "w", encoding="utf-8", errors="ignore") as f:
            f.write("\n".join(shaped_answers))
