from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.types import DateTime
from datetime import datetime, date

app = Flask(__name__)
# よくわからんけど無いと__init__.pyでエラーになる
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///todo.db'
db = SQLAlchemy(app)


# flask-sqlalchemyを使うとpythonオブジェクトのようにDBを扱える


class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(30), nullable=False)
    detail = db.Column(db.String(100))
    due = db.Column(db.DateTime, nullable=False)  # 期限


@app.route('/', methods=['GET', 'POST'])  # methodsの記述がないとGETしか受け取れない
def index():
    if request.method == 'GET':
        posts = Post.query.order_by(Post.due).all()  # requestがgetなら全部取り出してtoppageに渡す
        return render_template('index.html', posts=posts, today=date.today())
    else:
        # postなら入力フォームの内容を一旦変数に入れる（htmlに対応）
        title = request.form.get('title')
        detail = request.form.get('detail')
        due = request.form.get('due')

        due = datetime.strptime(due, '%Y-%m-%d')
        # dueを成型した後、取得した値で新規レコード生成
        new_post = Post(title=title, detail=detail, due=due)

        db.session.add(new_post)
        db.session.commit()
        # DBにinsertした後ルートディレクトリ(=index.html)にリダイレクト
        return redirect('/')


@app.route('/create')
def create():
    return render_template('create.html')


@app.route('/detail/<int:id>')
def read(id):
    # Postテーブルからid一致行を取得
    post = Post.query.get(id)
    # detail.htmlに遷移するときに変数postの内容をPOSTする（detail表示したいレコードを特定する）
    return render_template('detail.html', post=post)


@app.route('/delete/<int:id>')
def delete(id):
    post = Post.query.get(id)

    db.session.delete(post)
    db.session.commit()
    return redirect('/')


@app.route('/update/<int:id>', methods=['GET', 'POST'])
def update(id):
    post = Post.query.get(id)
    if request.method == 'GET':
        return render_template('update.html', post=post)
    else:
        post.title = request.form.get('title')
        post.detail = request.form.get('detail')
        post.due = datetime.strptime(request.form.get('due'), '%Y-%m-%d')

        db.session.commit()
        return redirect('/')


if __name__ == '__main__':
    app.run()
