import sys, pathlib, difflib, json, bs4

src_html = pathlib.Path(sys.argv[1]).read_text(encoding="utf-8")
out_dir  = pathlib.Path(sys.argv[2])
out_dir.mkdir(parents=True, exist_ok=True)

soup = bs4.BeautifulSoup(src_html, "html.parser")

# 1) select elements to be revealed frame by frame
#    here we use all tags inside .box as an example, you can filter by yourself:
targets = []
for box in soup.select("div.box"):
    for node in box.descendants:
        if isinstance(node, bs4.Tag):
            # you can filter out wrapper / script / style etc. as needed
            if node.name in {"script", "style"}:
                continue
            targets.append(node)

total = len(targets)
print(f"Total nodes to be revealed: {total}")

manifest, prev_lines = [], []

for idx, node in enumerate(targets, 1):
    step_soup = bs4.BeautifulSoup(src_html, "html.parser")

    # second pass: hide elements that are not yet shown
    shown_ids = set()        # use id() to identify same node
    for j, n in enumerate(
        step_soup.select("div.box *")    # * = all descendants
    ):
        if isinstance(n, bs4.Tag) and id(n) in shown_ids:
            # already processed (prevent duplicate)
            continue
        if j + 1 > idx:                   # not yet shown elements
            style = n.get("style", "")
            # ensure no duplicate style
            if "opacity" not in style:
                style = (
                    "opacity:0;transition:opacity .35s ease-out;" + style
                )
            n["style"] = style
        shown_ids.add(id(n))

    # 3) write file
    fname = f"{idx:04d}.html"
    (out_dir / fname).write_text(str(step_soup), encoding="utf-8")

    diff = "" if not prev_lines else "\n".join(
        difflib.unified_diff(prev_lines, str(step_soup).splitlines(), lineterm="")
    )
    manifest.append(
        {"file": fname, "caption": f"Elements: {idx}/{total}", "diff": diff}
    )
    prev_lines = str(step_soup).splitlines()

# 4) write manifest
(out_dir / "manifest.json").write_text(
    json.dumps(manifest, ensure_ascii=False, indent=2)
)
print("Finished", out_dir.resolve())
