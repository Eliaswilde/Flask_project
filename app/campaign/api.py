# _*_ coding: utf-8 _*_
__author__ = 'nislam <connect2nazrul@gmail.com>'
import datetime, time
from flask.views import MethodView
from flask import jsonify, request, session
from models import Comment
from services.database import db
from flask.ext import login
from config import SQLALCHEMY_PAGINATE_MAX_RESULT
__all__ = ['CommentView']


class CommentView(MethodView):

    def get(self, campaign_id=None):
        _return = {}
        page = int(request.args.get('page')) or 1
        try:
            comments = Comment.query.filter_by(campaign_id=campaign_id, is_hidden=False).order_by(Comment.date.desc())\
                .paginate(page, SQLALCHEMY_PAGINATE_MAX_RESULT, error_out=False)
        except Exception, exc:
            raise exc.message
        else:
            if comments and comments.items:
                _return['meta'] = {'has_next': comments.has_next, 'next_num': comments.next_num,
                                   'total': comments.total, 'generated_on': datetime.datetime.now()}
                _return['objects'] = [{'text': comment.text,
                                       'id': comment.id,
                                       'date': comment.date,
                                       'user_id': comment.user_id,
                                       'by': comment.user.first_name,
                                       } for comment in comments.items]
        return jsonify(_return)

    def post(self, **kwargs):
        user = (login.current_user.is_authenticated() and [login.current_user] or [None])[0]
        s_key = 'last_comment_time_%s' % user.id
        _previous_comment_time = session.get(s_key, None)
        if _previous_comment_time:
            if 5 > (time.time() - float(_previous_comment_time)):
                return jsonify({'abort': True, 'message': u'Please try after a moment'})
        comment = Comment(
            text=request.form.get('comment'),
            date=datetime.datetime.now(),
            is_private=request.form.get('is_private'),
            user_id=user.id,
            campaign_id=request.form.get('campaign_id'),
            is_active=True
        )
        db.session.add(comment)
        db.session.commit()
        session[s_key] = time.time()
        return jsonify({'message': u'successfully commented posted!', 'id': comment.id, 'date': comment.date})

    def put(self, **kwargs):
        comment = Comment.query.get(request.form.get('id'))
        if not comment:
            return jsonify({'error': u'Invalid comment reference or missing'})
        try:
            comment.text = request.form['text']
        except KeyError:
            pass
        try:
            comment.is_hidden = request.form['is_hidden']
        except KeyError:
            pass
        db.session.commit()
        return jsonify({'success': True, 'message': u'success'})

    def delete(self):
        return jsonify({'result': u'this is delete request'})
