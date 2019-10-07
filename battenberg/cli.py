import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))  # noqa: E402


import json
import logging
import click
from cookiecutter.cli import validate_extra_context
from cookiecutter.exceptions import CookiecutterException
from battenberg.core import Battenberg
from battenberg.utils import open_repository, open_or_init_repository
from battenberg.errors import BattenbergException


logger = logging.getLogger(__name__)
# Ensure we always receive debug messages.
handler = logging.StreamHandler()
handler.setLevel(logging.DEBUG)
logger.addHandler(handler)


@click.group()
@click.option(
    '-C',
    default='.',
    help='Run as if battenberg was started in <path> instead of the current working directory.',
    type=click.Path()
)
@click.option(
    '--context-file',
    default='.cookiecutter.json',
    help='Path where we can find the output of the cookiecutter template context',
    type=click.Path()
)
@click.option(
    '--verbose',
    default=False,
    is_flag=True,
    help='Enables the debug logging.'
)
@click.pass_context
def main(ctx, c, context_file, verbose):
    """Script entry point for Battenberg commands.

    Arguments:
    ctx -- CLI context.
    c -- Path where to run battenberg
    context_file -- Path where we can find the output of the cookiecutter template context
    verbose -- Enables debug logging
    """
    ctx.obj = dict()
    ctx.obj.update({
        'context_file': context_file,
        'target': c,
        'verbose': verbose
    })

    level = logging.DEBUG if verbose else logging.INFO
    logger.setLevel(level)


@main.command()
@click.pass_context
def show(ctx, **kwargs):
    try:
        battenberg = Battenberg(open_repository(ctx.obj['target']), ctx.obj['context_file'])
        template, checkout = battenberg.get_template()
        context = battenberg.get_context()

        logger.info(f'Template: {template}')
        logger.info(f'Checkout: %{checkout}')
        logger.info('Context:')
        logger.info(json.dumps(context, indent=4, separators=(',', ': ')))
    except (BattenbergException, CookiecutterException) as error:
        raise click.ClickException from error


@main.command()
@click.argument('template')
@click.argument('extra_context', nargs=-1, callback=validate_extra_context)
@click.option(
    '-c', '--checkout',
    help='branch, tag or commit to checkout',
    default='master'
)
@click.option(
    '--no-input', is_flag=True,
    help='Do not prompt for parameters and only use cookiecutter.json file content',
)
@click.pass_context
def install(ctx, template, **kwargs):
    try:
        battenberg = Battenberg(open_or_init_repository(ctx.obj['target']), ctx.obj['context_file'])
        battenberg.install(template, **kwargs)
    except (BattenbergException, CookiecutterException) as error:
        raise click.ClickException from error


@main.command()
@click.argument('extra_context', nargs=-1, callback=validate_extra_context)
@click.option(
    '-c', '--checkout',
    help='branch, tag or commit to checkout',
    default='master'
)
@click.option(
    '--no-input', is_flag=True,
    help='Do not prompt for parameters and only use cookiecutter.json '
         'file content',
)
@click.pass_context
def upgrade(ctx, **kwargs):
    try:
        battenberg = Battenberg(open_repository(ctx.obj['target']), ctx.obj['context_file'])
        battenberg.upgrade(**kwargs)
    except (BattenbergException, CookiecutterException) as error:
        raise click.ClickException from error
