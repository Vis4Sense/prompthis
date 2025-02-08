"""
handle user login
"""

import os
import pandas as pd


def match_username_with_userid(
    username: str,
    dir: str = './outputs',
    filename: str = 'users.csv'
) -> int:
    """match username with userid"""
    filepath = os.path.join(dir, filename)

    df = pd.read_csv(filepath)
    result = df[df["username"] == username]["userid"].values

    if len(result) > 0:
        return int(result[0])
    else:
        userid = df.shape[0]
        new_user = {"username": username, "userid": userid}
        df = pd.concat([df, pd.DataFrame([new_user])], ignore_index=True)
        df.to_csv(filepath, index=False)
        return userid
