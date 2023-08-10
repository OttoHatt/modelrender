import subprocess, os, sys
from pathlib import Path


def render(fIn, fOut, template_path, blender_path):
    scriptPath = os.path.abspath("blender/blenderScript.py")
    cmd = [
        blender_path,
        template_path,
        "--background",
        "--python",
        scriptPath,
        "--",
        "--in={}".format(fIn),
        "--out={}".format(fOut),
    ]
    subprocess.Popen(cmd).wait()


def findBlender() -> str | None:
    # TODO: Attempt to locate Blender from the registry.
    # See: "HKEY_CURRENT_USER\SOFTWARE\Classes\Applications\blender.exe\shell\open\command".

    attempts = [
        # Favour steam, will be auto-updated.
        r"C:\Program Files (x86)\Steam\steamapps\common\Blender\blender.exe",
        # TODO: Uhhh...
        r"C:\Program Files\Blender Foundation\Blender 4.0\blender.exe",
        r"C:\Program Files\Blender Foundation\Blender 3.6\blender.exe",
        r"C:\Program Files\Blender Foundation\Blender 3.5\blender.exe",
        r"C:\Program Files\Blender Foundation\Blender 3.4\blender.exe",
        r"C:\Program Files\Blender Foundation\Blender 3.3\blender.exe",
        r"C:\Program Files\Blender Foundation\Blender 3.2\blender.exe",
        r"C:\Program Files\Blender Foundation\Blender 3.1\blender.exe",
        r"C:\Program Files\Blender Foundation\Blender 3.0\blender.exe",
    ]
    return next((p for p in attempts if Path(p).exists()), None)


if __name__ == "__main__":
    blenderPath = findBlender()
    if not blenderPath:
        print("Couldn't locate Blender.")
        sys.exit(1)

    render(
        template_path=os.path.abspath(sys.argv[1]),
        fIn=os.path.abspath(sys.argv[2]),
        fOut=os.path.abspath(sys.argv[3]),
        blender_path=blenderPath,
    )
