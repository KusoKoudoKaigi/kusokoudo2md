from src.form_to_md import *

templete_path = "templete/kusokoudo"
ftm = FormToMarkDown("フォームの回答 1.html", templete_path)
ftm.write("kusokoudo.md")
