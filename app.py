import streamlit as st
from pdfminer.high_level import extract_text
from github import Github
import tempfile
import os

# ================================
# 設定
# ================================
st.set_page_config(page_title="PDF→HTML GitHub Pages公開", page_icon="📘", layout="centered")

GITHUB_TOKEN = st.secrets["GITHUB_TOKEN"]  # ← GitHubトークンをStreamlit CloudのSecretsに設定
GITHUB_REPO = "Redboar1021/pdf-html-source"  # あなたのリポジトリ名に変更
HTML_FILENAME = "index.html"

st.title("📘 PDF → HTML 自動公開システム")
st.write("アップロードしたPDFをHTML化してGitHub Pagesに自動公開します（AI参照可）。")

# ================================
# PDFアップロード
# ================================
uploaded_file = st.file_uploader("📤 PDFをアップロードしてください", type=["pdf"])

if uploaded_file:
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
        tmp.write(uploaded_file.read())
        pdf_path = tmp.name

    st.info("🧠 PDF→テキスト抽出中...")
    text = extract_text(pdf_path)

    # HTML生成
    html_content = f"""
    <html>
    <head><meta charset="utf-8"><title>PDF Source</title></head>
    <body style="font-family: sans-serif; line-height: 1.6; white-space: pre-wrap; margin: 40px;">
    {text}
    </body>
    </html>
    """

    # 一時HTMLファイル作成
    tmp_html = tempfile.NamedTemporaryFile(delete=False, suffix=".html")
    tmp_html.write(html_content.encode("utf-8"))
    tmp_html.close()

    st.success("✅ HTML生成完了！GitHubに反映中...")

    # ================================
    # GitHubにアップロード
    # ================================
    try:
        g = Github(GITHUB_TOKEN)
        repo = g.get_repo(GITHUB_REPO)

        # 既存ファイルがある場合は上書き
        try:
            contents = repo.get_contents(HTML_FILENAME)
            repo.update_file(
                path=HTML_FILENAME,
                message="Update HTML via Streamlit",
                content=html_content,
                sha=contents.sha
            )
        except Exception:
            repo.create_file(
                path=HTML_FILENAME,
                message="Create HTML via Streamlit",
                content=html_content
            )

        st.success("✅ GitHub Pages にHTMLをアップロードしました！")

        # 公開URL生成
        username, repo_name = GITHUB_REPO.split("/")
        page_url = f"https://{username}.github.io/{repo_name}/"
        st.markdown(f"🌐 **公開URL:** [{page_url}]({page_url})")

        st.markdown("このURLをAIシステムの参照先に指定すれば、PDF内容を直接取得できます。")

    except Exception as e:
        st.error(f"❌ アップロード中にエラーが発生しました: {e}")
