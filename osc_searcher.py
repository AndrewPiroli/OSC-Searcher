# SPDX-License-Identifier: BSD-3-Clause

import json
import os
import dataclasses
import pathlib
import requests
import rapidfuzz
from time import time
from typing import List, Tuple, Union

@dataclasses.dataclass(frozen=True)
class OSCPackage:
    display_name: str
    long_description: str
    internal_name: str
    short_description: str
    category: str
    coder: str
    contributors: str
    package_type: str
    rating: str
    shop_title_id: str
    release_date: str
    controllers: str
    downloads: str
    extra_directories: list
    extracted: str
    icon_url: str
    updated: str
    version: str
    zip_size: str
    zip_url: str
    shop_title_version: str

api_base = "https://api.oscwii.org/v2/"
api_host = "primary"
api_all_pkgs_endpoint = "/packages"

friendly_url_base = "https://oscwii.org/library/app/"

cache_file = pathlib.Path(".") / "cache.json"
# max cache age in seconds - 8 hours
cache_max_age = 60 * 60 * 8

def search(query: str, haystack: List[OSCPackage], limit: int = 5) -> List[Tuple[int, OSCPackage]]:
    assert limit > -1, "Cannot set limit below 0"
    results = list()
    for candidate in haystack:
        match_display_name = rapidfuzz.fuzz.partial_ratio(query, candidate.display_name)
        match_descr = rapidfuzz.fuzz.partial_ratio(query, candidate.long_description)
        best_match = match_descr if match_descr > match_display_name else match_display_name
        results.append((best_match, candidate))
    results.sort(key= lambda x: x[0], reverse=True)
    if limit == 0:
        return results
    else:
        return results[0:limit]

def try_read_cache() -> Union[None, List]:
    print("Checking package cache.")
    try:
        cache_stat = os.stat(cache_file)
        if cache_stat.st_mtime < int(time()) - cache_max_age:
            print("Cache too old.")
            return None
        with open(cache_file, "r") as cache_fp:
            print("Loaded cached package list.")
            return json.load(cache_fp)
    except FileNotFoundError:
        print("No package cache found.")
        return None
    except Exception:
        print("Error reading cache.")
        return None


if __name__ == "__main__":
    if not __debug__:
        print("I use a bunch of asserts, you probably shouldn't run the script like this.....")
        import sys
        sys.exit(1)
    package_list = try_read_cache()
    if package_list is None:
        print("Downloading package list from OSC.")
        r = requests.get(f"{api_base}{api_host}{api_all_pkgs_endpoint}")
        assert 200 <= r.status_code < 300, "Recieved error response from API"
        package_list: List = r.json()
        del r
        assert isinstance(package_list, list), "Unexpected response from API"
        try:
            with open(cache_file, "w+") as cache_fp:
                json.dump(package_list, cache_fp)
        except Exception:
            print("Failed to save package list to cache!")
    packages = list()
    for package in package_list:
        try:
            packages.append(OSCPackage(**package))
        except Exception as e:
            pass
    del package_list
    assert len(packages) > 0, "No packages available!"
    search_str = input("Enter search query: ")
    search_result = search(search_str, packages)
    for idx, result in enumerate(search_result):
        pkg: OSCPackage = result[1]
        print(f"{idx + 1}: {pkg.display_name} | {pkg.long_description} | Link: {friendly_url_base}{pkg.internal_name} | match %: {result[0]}")