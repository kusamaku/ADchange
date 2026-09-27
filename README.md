# 積分型（二重積分型）ADC 学習シミュレータ（Streamlit版）

旭川高専の学習用を想定した、積分型（二重積分型）ADCのステップ・バイ・ステップ可視化プログラムです。

## 必要ファイル

- `app.py`
- `requirements.txt`

## ローカルで実行

```bash
pip install -r requirements.txt
streamlit run app.py
```

ブラウザで `http://localhost:8501` を開きます。

## GitHub + Streamlit Community Cloudで公開

1. GitHubに新しいリポジトリを作成
2. `app.py` と `requirements.txt` をアップロード
3. Streamlit Community CloudでGitHub連携
4. `Create app` からリポジトリ、ブランチ、`app.py` を指定
5. Deploy

デプロイ後に発行される `https://xxxxx.streamlit.app` のURLを共有できます。
