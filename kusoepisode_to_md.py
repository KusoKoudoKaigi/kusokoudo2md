from src.form_to_md import *

templete_path = "templete/kusoepisode"
ftm = FormToMarkDown("フォームの回答 1.html", templete_path)
ftm.write("kusoepisode.md")
