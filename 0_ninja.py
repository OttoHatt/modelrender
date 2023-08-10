from pathlib import Path

CONTENT_PATH = Path("content/")
# Links to images within an OBJ's material. We want to re-render if one changes.
# These are the tags Roblox exports right now. There are others in common use, notably for PBR.
# If support is added for exports, this will need to be updated.
MTL_TAGS = ["map_Ka", "map_Kd", "map_d"]


def getMtlDependencies(deps: list[Path], mtl: Path):
    with open(mtl) as mtl_file:
        for line in mtl_file:
            for tag in MTL_TAGS:
                if line.startswith(tag):
                    img_path = CONTENT_PATH / line.removeprefix(tag).strip()
                    deps.append(img_path)
                    break


def getObjDependencies(deps: list[Path], obj: Path):
    # .obj files depend on at least 1 material file.
    # We assume just 1 here.
    with open(obj) as obj_file:
        for line in obj_file:
            if line.startswith("mtllib"):
                lib_path = CONTENT_PATH / line.removeprefix("mtllib").strip()
                deps.append(lib_path)
                getMtlDependencies(deps, lib_path)
                # Assume only one .mtl per obj.
                return


def path_str(x: Path):
    # Posix format for concistency.
    # Changing path delimiters will invoke a rebuild.
    return str(x).replace("\\", "/")


with open("build.ninja", "w") as out:
    out.write("blenderfile = template.blend\n")
    # Only one render at a time, blender needs as many cores as possible.
    out.write("rule render_icon\n")
    out.write("  command = py 1_render.py $blenderfile $in $out\n")
    out.write("  pool = console\n")
    # Downscale doesn't have a pool, can run whenever.
    out.write("rule render_downscale\n")
    out.write("  command = py 2_downscale.py $in $out\n")
    # Only one render upload at a time, to prevent rate limiting.
    out.write("pool render_upload_pool\n")
    out.write("  depth = 1\n")
    out.write("rule render_upload\n")
    out.write("  command = py 3_upload.py $in $out\n")
    out.write("  pool = render_upload_pool\n")
    # Collection only runs once.
    out.write("rule render_collect\n")
    out.write("  command = py 4_collect.py $in $out\n")
    out.write("  pool = console\n")
    #
    # Render icons
    #
    for x in CONTENT_PATH.glob("*.obj"):
        out.write(f"build out/staging/{x.stem}.png: render_icon {path_str(x)}")
        deps = list[Path]()
        getObjDependencies(deps, x)
        if len(deps) > 0:
            out.write(" | ")
        for dep in deps:
            out.write(path_str(dep))
            out.write(" ")
        out.write("\n")
    #
    # Downscale renders.
    # (render high so we have lots of pixels to work with in screen-space composited effects)
    # (if we render at a low-res first, we'll get blocky outlines)
    #
    for x in CONTENT_PATH.glob("*.obj"):
        out.write(
            f"build out/downscaled/{x.stem}.png: render_downscale out/staging/{x.stem}.png\n"
        )
    #
    # Upload, save AssetId
    #
    for x in CONTENT_PATH.glob("*.obj"):
        out.write(
            f"build out/upload/{x.stem}.txt: render_upload out/downscaled/{x.stem}.png\n"
        )
    #
    # Collect all AssetIds at 'out.json'
    # Import into your game with Rojo.
    #
    out.write(f"build out/out.json: render_collect")
    for x in CONTENT_PATH.glob("*.obj"):
        out.write(f" out/upload/{x.stem}.txt")
    out.write("\n")

    out.write("\n")
