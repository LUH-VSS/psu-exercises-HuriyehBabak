def double_dispatch(self, prefix, object, *args, ignore_missing=False, **kwargs):
    for cls in type(object).__mro__:
        method_name = prefix + cls.__name__
        method = getattr(self, method_name, None)
        if method:  # Method found. Call it!
            return method(object, *args, **kwargs)

    if not ignore_missing:
        raise RuntimeError("Double Dispatch: could not find {}-method for {}".format(prefix, type(object)))
