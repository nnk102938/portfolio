# 動作確認 ターミナルで↓
# cd projects/code-practice-app
# python3 app.py
# http://127.0.0.1:5000/

# ─────────────────────────────
# (1)ライブラリのimport
# ─────────────────────────────
from flask import Flask, render_template, request, session
                          #Flask → Webアプリ本体を作る
                          #render_template → HTMLを表示する
                          #request → ユーザーの入力を受け取る（フォームなど）
                          #session → ユーザーごとのデータ保存
import random          # 問題をランダムに選ぶ
import io              # print()の出力を受け取る
import contextlib      # print()の出力先を切り替える

from questions import question_list  # 問題一覧の読み込み


# ─────────────────────────────
# (2)アプリの初期設定
# ─────────────────────────────
app = Flask(__name__)          # Flaskでwebアプリとして起動する
app.secret_key = "secret-key"  # セッションの安全化

TOTAL_QUESTIONS = 5


# ─────────────────────────────
# (3)セッション初期化処理
# ─────────────────────────────
def init_practice():
    session["questions"] = random.sample(question_list, TOTAL_QUESTIONS)
    session["index"] = 0
    session["score"] = 0
# どの問題を出しているか、今何問目か、スコアはいくつかをユーザーごとに保持

# ─────────────────────────────
# (4)判定処理
# ─────────────────────────────
def judge(user_code, correct_answer):

    output = io.StringIO()

    if "import" in user_code.lower():
        return "importは禁止です", "", False

    if "__" in user_code:
        return "特殊構文は禁止です", "", False

# 使用できる関数を以下に制限 ↓
    try:
        safe_builtins = {
            "print": print,
            "len": len,
            "range": range
        }

        with contextlib.redirect_stdout(output):
            exec(user_code, {"__builtins__": safe_builtins})

        result = output.getvalue().strip()
    except:
        result = ""

    if result.strip() == correct_answer.strip():
        return "正解！", result, True
    else:
        return "不正解", result, False

# ─────────────────────────────
# (5)メイン画面
# ─────────────────────────────
@app.route("/", methods=["GET", "POST"])
def index():

    if "questions" not in session:
        init_practice()

    qlist = session["questions"]

    i = session["index"]
    if i >= len(qlist):
        return render_template(
            "result.html",
            score=session["score"],
            total=TOTAL_QUESTIONS
        )

    score = session["score"]

    # 回答処理
    example = None
    user_code = ""
    message = ""
    output = ""

    if request.method == "POST":

        user_code = request.form["code"]
        correct = qlist[i]["answer"]

        message, output, is_correct = judge(user_code, correct)

        if is_correct:
            session["score"] = score + 1

        example = qlist[i]["example"]


    return render_template(
        "index.html",
        question=qlist[i]["question"],
        example=example,
        message=message,
        output=output,
        current=i + 1,
        total=TOTAL_QUESTIONS,
        score=session["score"],
        user_code=user_code
    )


# ─────────────────────────────
# (6)次の問題
# ─────────────────────────────
@app.route("/next")
def next_question():

    if "questions" not in session:
        init_practice()

    session["index"] += 1

    if session["index"] >= TOTAL_QUESTIONS:
        return render_template(
            "result.html",
            score=session["score"],
            total=TOTAL_QUESTIONS
        )

    return index()


# ─────────────────────────────
# (7)もう一度挑戦
# ─────────────────────────────
@app.route("/restart")
def restart():

    init_practice()

    return index()

# ─────────────────────────────
# (8)アプリ起動処理
# ─────────────────────────────
if __name__ == "__main__":
    app.run(debug=True)