# -*- coding: utf-8 -*-

from flask import (  # noqa
    request,
    redirect,
    url_for,
    flash,
    render_template
)

from flask.views import MethodView
from flask.ext.login import current_user, login_user

from stepbystep.forms import LoginForm


class LoginView(MethodView):

    template = 'auth/login.html'

    def get(self):
        if current_user.is_authenticated():
            return redirect(url_for('index.index'))
        form = LoginForm()
        return render_template(self.template, form=form)

    def post(self):
        form = LoginForm()
        if not form.validate():
            return render_template(self.template, form=form)
        login_user(form.user, form.remember_me)
        flash('Login success')
        return redirect(request.args.get('next') or url_for('index.index'))
