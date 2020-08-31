#!/usr/bin/env python
# -*- coding: utf-8 -*-


import os


def invoke_and_join(functions, *args, **kwargs):
    return [result for f in functions for result in f(*args, **kwargs)]


def trim_indent(s):
    return os.linesep.join(s.lstrip() for s in s.splitlines())
