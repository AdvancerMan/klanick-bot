def invoke_and_join(functions, *args, **kwargs):
    return [result for f in functions for result in f(*args, **kwargs)]
