# -*- coding: utf-8 -*-
from flask import (  # noqa
    request,
    redirect,
    url_for,
    abort,
    current_app,
    render_template
)

from flask.views import MethodView

from stepbystep import cache
from stepbystep.models import ProblemModel, RoleModel, UserModel, CategoryModel

ORDINAL = {
    'junior': 0,
    'middle': 1,
    'senior': 2
}


class StepPojView(MethodView):

    template = 'step.html'

    @cache.cached(timeout=21600)
    def get(self, ordinal):
        role = RoleModel.objects(name=ordinal).first()
        ordinal = CategoryModel.objects.get_or_404(
            ordinal=ORDINAL.get(ordinal), origin_oj='poj')
        problems = ProblemModel.objects(
            origin_oj='poj',
            genera=ordinal
        ).all()
        problems = list(problems)
        problems.sort(cmp=ProblemModel.p_cmp)
        users = UserModel.objects(roles=role).all()

        return render_template(
            self.template,
            problems=problems,
            users=users,
            ordinal=ordinal)
