# プロジェクトテンプレート

Django プロジェクト用の Git テンプレート

## 開発の準備

```console
$ python3 -m venv .venv
$ source .venv/bin/activate
$ pip install -r requirements.txt
$ python scripts/gen_secret_key.py > "asoviva/local_settings.py"
```

注: `$PROJECT_DIR` はプロジェクト毎に異なるため，適宜置き換える必要がある．
