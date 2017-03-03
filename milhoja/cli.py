# -*- coding: utf-8 -*-

import click
from cookiecutter.cli import validate_extra_context
from .milhoja import Milhoja # indeed ...
from .utils import open_or_init_repository

@click.group()
@click.option(
    u'-C',
    default=u'.',
    help=u'Run as if milhoja was started in <path> instead of the current working directory.',
    type=click.Path()
)
@click.pass_context
def main(ctx, c):
    """Script entry point for Milhoja commands.

    Arguments:
    ctx -- CLI context.
    c -- Path where to run milhoja
    """
    ctx.obj['milhoja'] = Milhoja(open_or_init_repository(c))

@main.command()
@click.argument('template')
@click.argument(u'extra_context', nargs=-1, callback=validate_extra_context)
@click.option(
    u'-c', u'--checkout',
    help=u'branch, tag or commit to checkout',
    default=u'master'
)
@click.option(
    u'--no-input', is_flag=True,
    help=u'Do not prompt for parameters and only use cookiecutter.json '
         u'file content',
)
@click.pass_context
def install(ctx, template, **kwargs):
    ctx.obj['milhoja'].install(
        template,
        **kwargs
    )

@main.command()
@click.argument(u'extra_context', nargs=-1, callback=validate_extra_context)
@click.option(
    u'-c', u'--checkout',
    help=u'branch, tag or commit to checkout',
)
@click.option(
    u'--no-input', is_flag=True,
    help=u'Do not prompt for parameters and only use cookiecutter.json '
         u'file content',
)
@click.pass_context
def upgrade(ctx, **kwargs):
    ctx.obj['milhoja'].upgrade(**kwargs)
