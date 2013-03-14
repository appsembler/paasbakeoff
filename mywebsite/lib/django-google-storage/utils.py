from django.utils.encoding import force_unicode


def safe_join(base, *paths):
    """
    A version of django.utils._os.safe_join for S3 paths.

    Joins one or more path components to the base path component intelligently.
    Returns a normalized version of the final path.

    The final path must be located inside of the base path component (otherwise
    a ValueError is raised).

    Paths outside the base path indicate a possible security sensitive operation.
    """
    from urlparse import urljoin
    base_path = force_unicode(base)
    paths = map(lambda p: force_unicode(p), paths)
    final_path = urljoin(base_path + ("/" if not base_path.endswith("/") else ""), *paths)
    # Ensure final_path starts with base_path and that the next character after
    # the final path is '/' (or nothing, in which case final_path must be
    # equal to base_path).
    base_path_len = len(base_path)
    if not final_path.startswith(base_path) or final_path[base_path_len:base_path_len + 1] not in ('', '/'):
        raise ValueError('the joined path is located outside of the base path'
                         ' component')
    return final_path
