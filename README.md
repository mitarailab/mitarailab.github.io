# 御手洗グループのホームページ

- 公開先: https://mitarailab.github.io/
- 管理: mitarailab organization
- Qubit Factory 日本語版: https://mitarailab.github.io/the-qubit-factory-jp/

`main` に変更をpushすると、GitHub ActionsがJekyllでビルドしてGitHub Pagesへ公開します。
論文一覧の自動更新は `Update Publications` が毎日実行し、成功後にサイトを再公開します。
更新にはリポジトリの `GITHUB_TOKEN` を使い、個人のSSH鍵は必要ありません。

## ページの編集

Jekyllの [Minima](https://github.com/jekyll/minima) をベースにしています。
ニュースは `_posts/` 以下に新しいMarkdownファイルを作成します。
主な静的ページは `index.md`（トップ）、`about.md`（研究内容）、
`publications.md`（論文一覧）、`members.md`（メンバー）、`archive.md`（教材など）です。
論文自動更新の元データは [ResearchMap](https://researchmap.jp/kosuke-mitarai) です。

## 大学ドメインへの切り替え

大学ドメインのDNSを切り替えるまでは、旧リポジトリ
`kosukemtr/kosukemtr.github.io` と旧Qubit Factoryリポジトリの公開を維持します。
今後の開発はorganization側で行います。

切り替え時は、旧HPの独自ドメイン設定・所有確認を確認して移行し、
このリポジトリのPages設定に `mitarai.qc.ee.es.osaka-u.ac.jp` を登録します。
大学側DNSのCNAMEを `mitarailab.github.io` に変更し、HTTPSを確認します。
`_config.yml` の `url` とQubit Factory READMEの公開URLも更新します。
既存のプロジェクトサイトはorganization側の同名リポジトリに揃えてから切り替えます。
