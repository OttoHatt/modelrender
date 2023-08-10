from pathlib import Path
import requests, urllib3, json, dotenv, time, sys

env = dotenv.dotenv_values(".env")


def dumpOk(response: requests.Response) -> bool:
    if not response.ok:
        print(response.status_code, response.json(), response.text)
    return response.ok


def uploadImage(image: Path) -> str | None:
    # TODO: Find a way to embed a unique code - i.e. 'UNIX_TIME_START' - per batch.

    # https://github.com/treeben77/rblx-open-cloud/blob/10b2322d193aea198357752c3a7d78f166766e68/rblxopencloud/creator.py#L86
    body, contentType = urllib3.encode_multipart_formdata(
        {
            "request": json.dumps(
                {
                    "assetType": "Image",
                    "displayName": "Rendered Icon",  # If the asset name gets moderated, the upload will always fail. Use something generic.
                    "description": "Auto-generated icon.",
                    "creationContext": {"creator": {"groupId": env["GROUP-ID"]}},
                }
            ),
            "fileContent": (image.name, image.read_bytes(), "image/png"),
        }
    )

    # Upload.
    response = requests.post(
        "https://apis.roblox.com/assets/v1/assets",
        headers={
            "x-api-key": env["OPEN-CLOUD-KEY"] or "",
            "content-type": contentType,
        },
        data=body,
    )
    if not dumpOk(response):
        return

    # Grab operation. Needed for later requests.
    return response.json()["path"]


def getAssetIdFromOperationPath(operationPath: str) -> str | None:
    # Uploaded images are basically never available immediately.
    # Probably depends on the speed of your internet connection.
    time.sleep(1)

    # Sometimes retrieval tasks get stuck? Not even rate limited, just broken.
    # Try a number of times, then return an error code. Buildsystem will start over on this upload next time we run it.
    for attemptId in range(0, 3):
        response = requests.get(
            f"https://apis.roblox.com/assets/v1/{operationPath}",
            headers={
                "x-api-key": env["OPEN-CLOUD-KEY"] or "",
            },
        )
        if not dumpOk(response):
            return

        responseJson = response.json()

        if "done" in responseJson:
            return responseJson["response"]["assetId"]
        else:
            print(
                f"Failed to get assetId for '{operationPath}' on attempt {attemptId}. Response: '{responseJson}'"
            )
            # We've probably been rate limited. Back off.
            time.sleep(10)
    # Exhausted our retries. Sad.
    print(f"Rate limited on uploading. Try again later.")


if __name__ == "__main__":
    assert env
    assert "OPEN-CLOUD-KEY" in env
    assert "GROUP-ID" in env

    fIn = Path(sys.argv[1])
    fOut = Path(sys.argv[2])

    # Upload.
    operationPath = uploadImage(fIn)
    if not operationPath:
        print(f"Failed to upload '{fOut.stem}'!")
        sys.exit(1)

    # AssetId.
    assetId = getAssetIdFromOperationPath(operationPath)
    if not assetId:
        print(f"Failed to retrieve AssetId for '{fOut.stem}'!")
        sys.exit(1)

    # Save for collection.
    with fOut.open("w") as writer:
        writer.write("rbxassetid://" + assetId)
    print(f"Successfully uploaded '{fIn.stem}'! AssetId: '{assetId}'.")
