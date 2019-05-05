from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
from werkzeug.exceptions import abort

from flaskr.auth import login_required
from flaskr.db import get_db

import datetime
from bson import ObjectId

bp = Blueprint('blog', __name__)


@bp.route('/')
def index():
    db = get_db()
    for post in db.posts.find({}):
        pidStr = post.get('id')
        if not pidStr:
            pid = post.get('_id')
            pidStr = str(post.get('_id'))
            db.posts.update({'_id': pid}, {'$set': {'id': pidStr}})
            
    posts = db.posts.find({'$query': {}, '$orderby': {'created': -1}})
    return render_template('blog/index.html', posts=posts)

@bp.route('/create', methods=('GET', 'POST'))
@login_required
def create():
    if request.method == 'POST':
        title = request.form['title']
        body = request.form['body']
        created = datetime.datetime.now()
        error = None

        if not title:
            error = 'Title is required.'

        if error is not None:
            flash(error)
        else:
            db = get_db()
            db.posts.insert_one(
                {'title': title,
                 'body': body,
                 'username': g.user['username'],
                 'author_id': g.user['_id'],
                 'created': created}
            )
            return redirect(url_for('blog.index'))

    return render_template('blog/create.html')

def get_post(id, check_author=True):
    db = get_db()
    post = db.posts.find_one({'_id': id})

    if post is None:
        abort(404, "Post id {0} doesn't exist.".format(id))

    if check_author and post['author_id'] != g.user['_id']:
        abort(403)

    return post

@bp.route('/<string:id>/update', methods=('GET', 'POST'))
@login_required
def update(id):
    id = ObjectId(id)
    post = get_post(id)

    if request.method == 'POST':
        title = request.form['title']
        body = request.form['body']
        error = None

        if not title:
            error = 'Title is required.'

        if error is not None:
            flash(error)
        else:
            db = get_db()
            db.posts.update_one(
                {'_id': id},
                {'$set': {'title': title, 'body': body}})
            return redirect(url_for('blog.index'))

    return render_template('blog/update.html', post=post)

@bp.route('/<string:id>/delete', methods=('POST',))
@login_required
def delete(id):
    id = ObjectId(id)
    get_post(id)
    db = get_db()
    db.posts.delete_one({'_id': id})
    return redirect(url_for('blog.index'))