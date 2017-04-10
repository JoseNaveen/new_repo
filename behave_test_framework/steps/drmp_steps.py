#!/usr/bin/python

from behave import *
from pyMMI import MMI
from testcase1 import DRMP_Test1

@given('Valid "{NOIP}"')
def step_impl(context,NOIP):
    context.test=DRMP_Test1(NOIP)


@then('System Options "{b}" "{a}"')
def step_impl(context,a,b):
    if b=='Enable' and a=='DRMP':
        context.test.enable_drmp()
