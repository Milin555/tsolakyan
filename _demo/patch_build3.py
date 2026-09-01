"""Windows holds a directory open if any shell has it as its working directory,
so rmtree() on the demo root fails even when every file inside is free. Clear
the contents and reuse the directory instead of deleting it.
"""
import io, ast

P = "_demo/build_demos.py"
c = io.open(P, encoding="utf-8").read()

c = c.replace('''    if os.path.exists(dst):
        shutil.rmtree(dst)
    os.makedirs(OUT_ROOT, exist_ok=True)
    shutil.copytree(src, dst, ignore=ignore)''',
'''    os.makedirs(OUT_ROOT, exist_ok=True)
    clear_dir(dst)
    shutil.copytree(src, dst, ignore=ignore, dirs_exist_ok=True)''')

c = c.replace('''def build_replacements(''',
'''def clear_dir(path):
    """Empty a directory without removing it.

    On Windows the directory itself stays locked while any process has it as a
    working directory, so rmtree() raises even though the contents are free.
    Preserve .git so a redeploy keeps the repo's history and remote.
    """
    if not os.path.isdir(path):
        os.makedirs(path, exist_ok=True)
        return
    for name in os.listdir(path):
        if name == ".git":
            continue
        p = os.path.join(path, name)
        try:
            if os.path.isdir(p) and not os.path.islink(p):
                shutil.rmtree(p)
            else:
                os.remove(p)
        except OSError:
            pass


def build_replacements(''', 1)

io.open(P, "w", encoding="utf-8").write(c)
ast.parse(c)
print("patched, parses OK")
print(("  ok    " if "def clear_dir" in c else "  MISS  ") + "clear_dir")
print(("  ok    " if "dirs_exist_ok=True" in c else "  MISS  ") + "dirs_exist_ok")
