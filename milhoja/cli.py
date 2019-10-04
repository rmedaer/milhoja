import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))  # noqa: E402


import json
import logging
import click
from cookiecutter.cli import validate_extra_context
from cookiecutter.exceptions import CookiecutterException
from milhoja.core import Milhoja
from milhoja.utils import open_repository, open_or_init_repository
from milhoja.errors import MilhojaException


logger = logging.getLogger(__name__)
logger.addHandler(logging.StreamHandler())


@click.group()
@click.option(
    u'-C',
    default=u'.',
    help=u'Run as if milhoja was started in <path> instead of the current working directory.',
    type=click.Path()
)
@click.option(
    u'--verbose',
    default=False,
    is_flag=True,
    help=u'Enables the debug logging.'
)
@click.pass_context
def main(ctx, c, verbose):
    """Script entry point for Milhoja commands.

    Arguments:
    ctx -- CLI context.
    c -- Path where to run milhoja
    verbose -- Enables debug logging
    """
    ctx.obj = dict()
    ctx.obj.update({
        'target': c,
        'verbose': verbose
    })

    if verbose:
        logger.setLevel(logging.DEBUG)
    else:
        logger.setLevel(logging.INFO)


@main.command()
@click.pass_context
def show(ctx, **kwargs):
    try:
        milhoja = Milhoja(open_repository(ctx.obj['target']))
        template, checkout = milhoja.get_template()
        context = milhoja.get_context()

        logger.info('Template: %s' % template)
        logger.info('Checkout: %s' % checkout)
        logger.info('Context:')
        logger.info(json.dumps(context, indent=4, separators=(',', ': ')))
    except (MilhojaException, CookiecutterException) as error:
        raise click.ClickException from error


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
    try:
        milhoja = Milhoja(open_or_init_repository(ctx.obj['target']))
        milhoja.install(template, **kwargs)
    except (MilhojaException, CookiecutterException) as error:
        raise click.ClickException from error


@main.command()
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
def upgrade(ctx, **kwargs):
    try:
        milhoja = Milhoja(open_repository(ctx.obj['target']))
        milhoja.upgrade(**kwargs)
    except (MilhojaException, CookiecutterException) as error:
        raise click.ClickException from error


if __name__ == '__main__':
    main()
