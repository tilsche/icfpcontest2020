import sys

import click
import requests

import numpy
import pandas
import scipy

print("click", click.__version__)
print("np", numpy.__version__)
print("scipy", scipy.__version__)
print("pandas", pandas.__version__)


def main():
    server_url = sys.argv[1]
    player_key = sys.argv[2]
    print("ServerUrl: %s; PlayerKey: %s" % (server_url, player_key))

    res = requests.post(server_url, data=player_key)
    if res.status_code != 200:
        print("Unexpected server response:")
        print("HTTP code:", res.status_code)
        print("Response body:", res.text)
        exit(2)
    print("Server response:", res.text)


if __name__ == "__main__":
    main()