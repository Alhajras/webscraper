import requests


def extract_disallow_lines_from_url(url):
    """
    Used to extract the Disallow urls from the Robots.txt file
    """
    if url == "" or url is None:
        return []
    disallow_lines = []
    try:
        response = requests.get(url)
        if response.status_code == 200:
            file_content = response.text

            for line in file_content.split("\n"):
                if "Disallow" in line:
                    disallow_lines.append(line.replace("Disallow:", "").strip())

        else:
            print(f"Failed to retrieve file. Status code: {response.status_code}")

    except requests.exceptions.RequestException as e:
        print(f"Error occurred: {str(e)}")

    return disallow_lines
