ボタンにコマンドを割り当てて、クリックよりコマンドを実行するツール

【コマンド】
・コマンドを左クリックより、設定されたコマンドが実行
・コマンドを右クリックより、以下の基本操作を選択可能
	・編集：選択コマンドの以下の設定を編集
		・コマンド名：選択コマンドのコマンド名を入力
		・実行コマンド：ここで入力された内容を改行コードに区切りって、逐次実行される
		・並列実行：ONの時は各行が並列実行される（順番に実行する必要があるものはこの設定をOFFにする）
		・実行：コマンドを実行（「ctrl+e」でも可能）
		・保存：入力内容を保存（「ctrl+s」でも可能）
	・コピー：選択コマンドの設定をコピー
	・貼り付け：選択コマンドでコピーした設定を張り付け
・「ctrl+右クリック」からドラッグ＆ドロップでコマンドの並びを変更可能

【タブ】
・コマンド上で右クリックより、以下の基本操作を選択可能
	・タブ名の変更：選択タブのタブ名を変更
	・タブをコピー：選択タブをコピー（タブ名、タブ以下の全コマンドの設定）
	・タブを貼り付け：選択タブにコピーしたタブで上書き
	・タブを追加：選択タブの右隣に新規タブを挿入（タブは最大で6つまで）
	・タブを削除：選択タブを削除（タブの右端のバツアイコンでも可能）
・ドラッグ＆ドロップでタブの並びを変更可能

【コマンドの呼び出され方について】
コマンドは「実行コマンド」の入力内容を「並列実行」の設定別に整形された内容が実行
・ONの場合	->各行のコマンドを「start cmd /c command」の形式に整形
・OFFの場合	->各行のコマンドを「start cmd /c "command1 && command2 && ... && command{N}"」に連結形式に整形
※「start cmd /c command」は新規コマンドプロンプトを開き、「cmd /c command」を実行するコマンド（「/c」はコマンド終了後に自動的に新規コマンドプロンプトを閉じるオプション）

【Tips】
・タブを跨いで、個別にコマンドを移動させたい場合は、移動元コマンドをコピーし、移送先コマンドにペースト
・起動時にconfig.yamlがbackupフォルダにコピーされるため、config.yamlにリネームし、実行ファイルと同じディレクトリに移動することでロールバックが可能
・コマンド実行時に新規コマンドプロンプトが自動的に閉じない場合、呼び出し内容に自動的に終了しないコマンドが含まれている場合が多い
（pauseコマンド等のインテラクティブなコマンドや特殊な実行ファイルなど）

・設定ファイルのtab_num、btn_sizeを変更することでタブの最大数とボタンの配置数を変更することが可能
（余りにも大きいサイズは動作が重くなるだけでなく、何かの拍子に意図せずクリックしたことによるコマンド実行の確率が高くなるので非推奨）
// config.yamlの先頭部分の抜粋
tab_num: 6	# 最大タブ数（デフォルトは6）
btn_size:
- 4		# ボタンの列数（デフォルトは4）
- 4		# ボタンの行数（デフォルトは4）
※設定が不正（0以下の値）の場合は設定内容が初期化されるので注意

・一部のコマンドが意図通りに実行されない場合がある
	【Case1】cd > output.txt」：output.txtにカレントディレクトリが出力されない
	→「start cmd /c "{command}"」に整形されることで同時に実行できないパイプライン(start)とリダイレクト(>)の内、前者のみが実行されるため
	ダミーのコマンドを挟むと意図通りに実行される（「cd > output.text && echo dummy command」等）