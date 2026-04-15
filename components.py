"""
このファイルは、画面表示に特化した関数定義のファイルです。
"""

############################################################
# ライブラリの読み込み
############################################################
import os
import streamlit as st
import utils
import constants as ct


############################################################
# 関数定義
############################################################

def _display_download_button(file_path, key):
    """
    ファイルが存在する場合、ダウンロードボタンを表示する補助関数
    """
    if file_path.startswith("http"):
        return
    if os.path.exists(file_path):
        file_name = os.path.basename(file_path)
        with open(file_path, "rb") as f:
            file_data = f.read()
        st.download_button(
            label=f"💾 {file_name} をダウンロード",
            data=file_data,
            file_name=file_name,
            mime="application/pdf" if file_name.endswith(".pdf") else "application/octet-stream",
            key=key
        )

def display_app_title():
    """
    タイトル表示
    """
    st.markdown(f'<div class="app-title">{ct.APP_NAME}</div>', unsafe_allow_html=True)


def display_select_mode():
    """
    回答モードのラジオボタン・機能説明をサイドバーに表示
    """
    with st.sidebar:
        st.markdown('<div class="section-header">機能選択</div>', unsafe_allow_html=True)
        st.session_state.mode = st.radio(
            "実行するメニューを選択してください",
            options=[ct.ANSWER_MODE_1, ct.ANSWER_MODE_2],
            label_visibility="collapsed"
        )

        # 機能説明
        st.markdown('<div class="section-header">現在のモード</div>', unsafe_allow_html=True)
        if st.session_state.mode == ct.ANSWER_MODE_1:
            st.markdown(f"**{ct.ANSWER_MODE_1}**")
            st.info("キーワードに関連する社内資料の場所を特定します。")
            
            # 質問の例を追加
            st.markdown("**💡 質問の例:**")
            st.caption("""
            - 「〇〇プロジェクトのキックオフミーティング議事録はどこ？」
            - 「昨日の開発定例の決定事項を探して」
            """)
            
        else:
            st.markdown(f"**{ct.ANSWER_MODE_2}**")
            st.info("資料の内容をもとに、AIがあなたの質問に回答します。")

            # 質問の例を追加
            st.markdown("**💡 質問の例:**")
            st.caption("""
            - 「当社の主なサービスとその料金を教えて」
            - 「会社のビジョンや目標は何ですか？」
            - 「〇〇会社の担当者名と連絡先は？」
            - 「営業部の〇〇さんの得意分野は？」
            """)
        



def display_initial_ai_message():
    """
    AIメッセージの初期表示
    """
    with st.chat_message("assistant"):
        st.markdown(f"**{ct.APP_NAME}** へようこそ。社内ナレッジを活用して業務をサポートします。")
        st.info("画面下部のチャット欄に質問を入力してください。")

def display_conversation_log():
    """
    会話ログの一覧表示
    """
    # 会話ログのループ処理
    for msg_index, message in enumerate(st.session_state.messages):
        # 「message」辞書の中の「role」キーには「user」か「assistant」が入っている
        with st.chat_message(message["role"]):

            # ユーザー入力値の場合、そのままテキストを表示するだけ
            if message["role"] == "user":
                st.markdown(message["content"])
            
            # LLMからの回答の場合
            else:
                # 「社内文書検索」の場合、テキストの種類に応じて表示形式を分岐処理
                if message["content"]["mode"] == ct.ANSWER_MODE_1:
                    
                    # ファイルのありかの情報が取得できた場合（通常時）の表示処理
                    if not "no_file_path_flg" in message["content"]:
                        # ==========================================
                        # ユーザー入力値と最も関連性が高いメインドキュメントのありかを表示
                        # ==========================================
                        # 補足文の表示
                        st.markdown(message["content"]["main_message"], unsafe_allow_html=True)

                        # 参照元のありかに応じて、適したアイコンを取得
                        icon = utils.get_source_icon(message['content']['main_file_path'])
                        # メインドキュメントの表示部分
                        if "main_page_number" in message["content"]:
                            page_number = message['content']['main_page_number']
                            st.success(f"{message['content']['main_file_path']} (ページNo.{page_number})", icon=icon)
                        else:
                            st.success(f"{message['content']['main_file_path']}", icon=icon)
                        
                        _display_download_button(
                            message['content']['main_file_path'], 
                            key=f"dl_log_main_{msg_index}_{message['content']['main_file_path']}"
                        )
                        
                        # ==========================================
                        # ユーザー入力値と関連性が高いサブドキュメントのありかを表示
                        # ==========================================
                        if "sub_message" in message["content"]:
                            # 補足メッセージの表示
                            st.markdown(message["content"]["sub_message"], unsafe_allow_html=True)

                            # サブドキュメントのありかを一覧表示
                            for idx, sub_choice in enumerate(message["content"].get("sub_choices", [])):
                                # 参照元のありかに応じて、適したアイコンを取得
                                icon = utils.get_source_icon(sub_choice['source'])
                                # サブドキュメントの表示部分
                                if "page_number" in sub_choice:
                                    page_number = sub_choice['page_number']
                                    st.info(f"{sub_choice['source']} (ページNo.{page_number})", icon=icon)
                                else:
                                    st.info(f"{sub_choice['source']}", icon=icon)
                                
                                _display_download_button(
                                    sub_choice['source'], 
                                    key=f"dl_log_sub_{msg_index}_{idx}_{sub_choice['source']}"
                                )
                    # ファイルのありかの情報が取得できなかった場合、LLMからの回答のみ表示
                    else:
                        st.markdown(message["content"]["answer"])
                
                # 「社内問い合わせ」の場合の表示処理
                else:
                    # LLMからの回答を表示
                    st.markdown(message["content"]["answer"])

                    # 参照元のありかを一覧表示
                    if "file_info_list" in message["content"]:
                        # 区切り線の表示
                        st.divider()
                        # 「情報源」の文字を太字で表示
                        st.markdown('<div class="section-header">参照文献</div>', unsafe_allow_html=True)
                        # ドキュメントのありかを一覧表示
                        for idx, file_info in enumerate(message["content"]["file_info_list"]):
                            if isinstance(file_info, dict):
                                disp_text = file_info["display_text"]
                                f_path = file_info["file_path"]
                            else:
                                disp_text = file_info
                                f_path = file_info.split(" (")[0]
                                
                            # 参照元のありかに応じて、適したアイコンを取得
                            icon = utils.get_source_icon(disp_text)
                            st.info(disp_text, icon=icon)
                            
                            _display_download_button(
                                f_path, 
                                key=f"dl_log_contact_{msg_index}_{idx}_{f_path}"
                            )


def display_search_llm_response(llm_response):
    """
    「社内文書検索」モードにおけるLLMレスポンスを表示

    Args:
        llm_response: LLMからの回答

    Returns:
        LLMからの回答を画面表示用に整形した辞書データ
    """
    # LLMからのレスポンスに参照元情報が入っており、かつ「該当資料なし」が回答として返された場合
    if llm_response["context"] and llm_response["answer"] != ct.NO_DOC_MATCH_ANSWER:

        # ==========================================
        # ユーザー入力値と最も関連性が高いメインドキュメントのありかを表示
        # ==========================================
        # LLMからのレスポンス（辞書）の「context」属性の中の「0」に、最も関連性が高いドキュメント情報が入っている
        main_file_path = llm_response["context"][0].metadata["source"]

        # 補足メッセージの表示
        st.markdown('<div class="section-header">優先度の高い資料</div>', unsafe_allow_html=True)
        
        # 参照元のありかに応じて、適したアイコンを取得
        icon = utils.get_source_icon(main_file_path)
        # メインドキュメントの表示部分
        if "page" in llm_response["context"][0].metadata:
            main_page_number = llm_response["context"][0].metadata["page"] + 1  # 1スタートに修正
            st.success(f"{main_file_path} (ページNo.{main_page_number})", icon=icon)
        else:
            st.success(f"{main_file_path}", icon=icon)

        # ダウンロードボタンの表示
        current_msg_len = len(st.session_state.messages) if "messages" in st.session_state else 0
        _display_download_button(
            main_file_path, 
            key=f"dl_main_{current_msg_len}_{main_file_path}"
        )

        # ==========================================
        # ユーザー入力値と関連性が高いサブドキュメントのありかを表示
        # ==========================================
        # メインドキュメント以外で、関連性が高いサブドキュメントを格納する用のリストを用意
        sub_choices = []
        # 重複チェック用のリストを用意
        duplicate_check_list = []

        # ドキュメントが2件以上検索できた場合（サブドキュメントが存在する場合）のみ、サブドキュメントのありかを一覧表示
        # 「source_documents」内のリストの2番目以降をスライスで参照（2番目以降がなければfor文内の処理は実行されない）
        for document in llm_response["context"][1:]:
            # ドキュメントのファイルパスを取得
            sub_file_path = document.metadata["source"]

            # メインドキュメントのファイルパスと重複している場合、処理をスキップ（表示しない）
            if sub_file_path == main_file_path:
                continue
            
            # 同じファイル内の異なる箇所を参照した場合、2件目以降のファイルパスに重複が発生する可能性があるため、重複を除去
            if sub_file_path in duplicate_check_list:
                continue

            # 重複チェック用のリストにファイルパスを順次追加
            duplicate_check_list.append(sub_file_path)
            
            # ページ番号が取得できない場合のための分岐処理
            if "page" in document.metadata:
                # ページ番号を取得
                sub_page_number = document.metadata["page"] + 1  # 1スタートに修正
                # 「サブドキュメントのファイルパス」と「ページ番号」の辞書を作成
                sub_choice = {"source": sub_file_path, "page_number": sub_page_number}
            else:
                # 「サブドキュメントのファイルパス」の辞書を作成
                sub_choice = {"source": sub_file_path}
            
            # 後ほど一覧表示するため、サブドキュメントに関する情報を順次リストに追加
            sub_choices.append(sub_choice)
        
        # サブドキュメントが存在する場合のみの処理
        if sub_choices:
            # 補足メッセージの表示
            st.markdown('<div class="section-header">関連する可能性のある資料</div>', unsafe_allow_html=True)

            # サブドキュメントに対してのループ処理
            for idx, sub_choice in enumerate(sub_choices):
                # 参照元のありかに応じて、適したアイコンを取得
                icon = utils.get_source_icon(sub_choice['source'])
                # サブドキュメントの表示部分
                if "page_number" in sub_choice:
                    page_number = sub_choice['page_number']
                    st.info(f"{sub_choice['source']} (ページNo.{page_number})", icon=icon)
                else:
                    st.info(f"{sub_choice['source']}", icon=icon)
                
                # ダウンロードボタンの表示
                _display_download_button(
                    sub_choice['source'], 
                    key=f"dl_sub_{current_msg_len}_{idx}_{sub_choice['source']}"
                )
        
        # 表示用の会話ログに格納するためのデータを用意
        # - 「mode」: モード（「社内文書検索」or「社内問い合わせ」）
        # - 「main_message」: メインドキュメントの補足メッセージ
        # - 「main_file_path」: メインドキュメントのファイルパス
        # - 「main_page_number」: メインドキュメントのページ番号
        # - 「sub_message」: サブドキュメントの補足メッセージ
        # - 「sub_choices」: サブドキュメントの情報リスト
        content = {}
        content["mode"] = ct.ANSWER_MODE_1
        content["main_message"] = '<div class="section-header">優先度の高い資料</div>'
        content["main_file_path"] = main_file_path
        # メインドキュメントのページ番号は、取得できた場合にのみ追加
        if "page" in llm_response["context"][0].metadata:
            content["main_page_number"] = main_page_number
        # サブドキュメントの情報は、取得できた場合にのみ追加
        if sub_choices:
            content["sub_message"] = '<div class="section-header">関連する可能性のある資料</div>'
            content["sub_choices"] = sub_choices
    
    # LLMからのレスポンスに、ユーザー入力値と関連性の高いドキュメント情報が入って「いない」場合
    else:
        # 関連ドキュメントが取得できなかった場合のメッセージ表示
        st.markdown(ct.NO_DOC_MATCH_MESSAGE)

        # 表示用の会話ログに格納するためのデータを用意
        # - 「mode」: モード（「社内文書検索」or「社内問い合わせ」）
        # - 「answer」: LLMからの回答
        # - 「no_file_path_flg」: ファイルパスが取得できなかったことを示すフラグ（画面を再描画時の分岐に使用）
        content = {}
        content["mode"] = ct.ANSWER_MODE_1
        content["answer"] = ct.NO_DOC_MATCH_MESSAGE
        content["no_file_path_flg"] = True
    
    return content


def display_contact_llm_response(llm_response):
    """
    「社内問い合わせ」モードにおけるLLMレスポンスを表示

    Args:
        llm_response: LLMからの回答

    Returns:
        LLMからの回答を画面表示用に整形した辞書データ
    """
    # LLMからの回答を表示
    st.markdown(llm_response["answer"])

    # ユーザーの質問・要望に適切な回答を行うための情報が、社内文書のデータベースに存在しなかった場合
    if llm_response["answer"] != ct.INQUIRY_NO_MATCH_ANSWER:
        # 区切り線を表示
        st.divider()

        # 補足メッセージを表示
        st.markdown('<div class="section-header">回答の根拠となった資料</div>', unsafe_allow_html=True)

        # 参照元のファイルパスの一覧を格納するためのリストを用意
        file_path_list = []
        file_info_list = []

        # LLMが回答生成の参照元として使ったドキュメントの一覧が「context」内のリストの中に入っているため、ループ処理
        for document in llm_response["context"]:
            # ファイルパスを取得
            file_path = document.metadata["source"]
            # ファイルパスの重複は除去
            if file_path in file_path_list:
                continue

            # ページ番号が取得できた場合のみ、ページ番号を表示（ドキュメントによっては取得できない場合がある）
            if "page" in document.metadata:
                # ページ番号を取得
                page_number = document.metadata["page"] + 1  # 1スタートに修正
                # 「ファイルパス」と「ページ番号」
                file_info = f"{file_path} (ページNo.{page_number})"
            else:
                # 「ファイルパス」のみ
                file_info = f"{file_path}"

            # 参照元のありかに応じて、適したアイコンを取得
            icon = utils.get_source_icon(file_path)
            # ファイル情報を表示
            st.info(file_info, icon=icon)

            current_msg_len = len(st.session_state.messages) if "messages" in st.session_state else 0
            _display_download_button(
                file_path, 
                key=f"dl_contact_{current_msg_len}_{len(file_info_list)}_{file_path}"
            )

            # 重複チェック用に、ファイルパスをリストに順次追加
            file_path_list.append(file_path)
            # ファイル情報をリストに順次追加
            file_info_list.append({
                "display_text": file_info,
                "file_path": file_path
            })

    # 表示用の会話ログに格納するためのデータを用意
    # - 「mode」: モード（「社内文書検索」or「社内問い合わせ」）
    # - 「answer」: LLMからの回答
    # - 「message」: 補足メッセージ
    # - 「file_path_list」: ファイルパスの一覧リスト
    content = {}
    content["mode"] = ct.ANSWER_MODE_2
    content["answer"] = llm_response["answer"]
    # 参照元のドキュメントが取得できた場合のみ
    if llm_response["answer"] != ct.INQUIRY_NO_MATCH_ANSWER:
        content["message"] = '<div class="section-header">回答の根拠となった資料</div>'
        content["file_info_list"] = file_info_list

    return content