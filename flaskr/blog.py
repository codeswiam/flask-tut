from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
from werkzeug.exceptions import abort

from flaskr.auth import login_required
from flaskr.db import get_db

bp = Blueprint('blog', __name__) # note that this does not have a url prefix

# this bp's index will be the app's main index

# DONE: post detail view
# TODO: implement liking / unliking functionality
# TODO: implement comments
# TODO: implement tags
# TODO: clicking a tag shows all the posts with that tag
# TODO: add a search box that filters by name
# TODO: only show 5 posts per page

@bp.route('/')
def index():
    db = get_db()
    posts = db.execute(
        'SELECT p.id, title, body, created, author_id, username'
        ' FROM post p JOIN user u ON p.author_id = u.id'
        ' ORDER BY created DESC'
    ).fetchall()
    return render_template('blog/index.html', posts=posts)


@bp.route('/create', methods=('GET', 'POST'))
@login_required
def create():
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
            db.execute(
                'INSERT INTO post (title, body, author_id)'
                ' VALUES (?, ?, ?)',
                (title, body, g.user['id'])
            )
            db.commit()
            return redirect(url_for('blog.index'))

    return render_template('blog/create.html')


def get_post(id, check_author=True):
    post = get_db().execute(
        'SELECT p.id, title, body, created, author_id, username'
        ' FROM post p JOIN user u ON p.author_id = u.id'
        ' WHERE p.id = ?',
        (id,)
    ).fetchone()

    # if the post does not exist
    if post is None:
        abort(404, f"Post id {id} doesn't exist.")

    # if the user is not the author
    if check_author and post['author_id'] != g.user['id']:
        abort(403)

    return post

@bp.route('/<int:id>/details', methods=['GET'])
def details(id, show_comment=0):
    post = get_post(id, False)
    db = get_db()
    comments = db.execute(
        'SELECT post_id, c.author_id, content, c.created, username'
        ' FROM post p JOIN comment c ON p.id = c.post_id'
        ' JOIN user u ON u.id = c.author_id'
        ' ORDER BY c.created DESC'
    ).fetchall()
    return render_template('blog/details.html', post=post, comments=comments)


# note how the id param is written in the url
@bp.route('/<int:id>/update', methods=('GET', 'POST'))
@login_required
def update(id):
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
            db.execute(
                'UPDATE post SET title = ?, body = ?'
                ' WHERE id = ?',
                (title, body, id)
            )
            db.commit()
            return redirect(url_for('blog.index'))

    return render_template('blog/update.html', post=post)


@bp.route('/<int:id>/delete', methods=('POST',))
@login_required
def delete(id):
    get_post(id)
    db = get_db()
    db.execute('DELETE FROM post WHERE id = ?', (id,))
    db.commit()
    return redirect(url_for('blog.index'))


@bp.route('/<int:id>/comment', methods=['POST'])
@login_required
def comment(id):
    content = request.form['content']
    if not content:
        flash('Comment cannot be empty.')
    else:
        db = get_db()
        db.execute(
            'INSERT INTO comment (content,post_id, author_id)'
            ' VALUES (?, ?, ?)',
            (content, id, g.user['id'])
        )
        db.commit()

    return redirect(url_for('blog.details', id=id))

@bp.route('/comment/<int:id>/delete', methods=['POST'])
@login_required
def delete_comment(id):
    db = get_db()
    comment =  db.execute(
        'SELECT post_id FROM comment WHERE id = ?', (id,)
    ).fetchone()

    if comment is None:
        abort(404, "Comment not found.")
        
    db.execute('DELETE FROM comment WHERE id = ?', (id,))
    db.commit()

    return redirect(url_for('blog.details', id=comment['post_id']))