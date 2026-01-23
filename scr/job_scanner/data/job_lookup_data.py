from typing import Optional, Union

def job_lookup_data(data_type: int = 0) -> Optional[Union[frozenset[str],tuple[str],tuple[str],frozenset[str]]]:
    """
    This is a set of data that the script will use
    when I need to update things or compare data in different
    parts.

    Args:
        data_type (int): The type of data to return when called
                         0 = None
                         1 = set of keywords that represent job
                             titles
                         2 = Agents to use for spoofing accessing
                             web traffic
                         3 = decompose tags found in HTML websites to
                             remove traffic if not needed to help with
                             parsing out data
                         4 = this is the ignore keyword system for words
                             that I see that are red flags to kill the add

    Return:
        data_retrieved (None): the data that is being returned
        job_title_keywords (frozenset): this is all the keywords for job titles I am looking for
        user_agents (tuple): this is the user agent used to look like fake traffic on the website
        decompose_tags (tuples): this is the different type of headers to decompress from for tags
    """
    # job title key names
    if data_type == 1:
        job_title_keywords = frozenset({
            "animator",
            "techartist", # Tech Artist
            "rigger",
            "gameplayanimator", # Gameplay Animator
            "3danimator", # 3D Animator
            "technicalanimator" # Technical Animator
        })
        return job_title_keywords
    # agents to spoof connection to webpages for scraping
    elif data_type == 2:
        user_agents = (
            # Chrome – Windows
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/121.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/119.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/118.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/117.0.0.0 Safari/537.36",
            # Chrome – macOS
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 13_6) AppleWebKit/537.36 Chrome/121.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 13_5) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 13_4) AppleWebKit/537.36 Chrome/119.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 12_6) AppleWebKit/537.36 Chrome/118.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 12_5) AppleWebKit/537.36 Chrome/117.0.0.0 Safari/537.36",
            # Chrome – Linux
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/121.0.0.0 Safari/537.36",
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36",
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/119.0.0.0 Safari/537.36",
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/118.0.0.0 Safari/537.36",
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/117.0.0.0 Safari/537.36",
            # Firefox – Windows
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:122.0) Gecko/20100101 Firefox/122.0",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:120.0) Gecko/20100101 Firefox/120.0",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:119.0) Gecko/20100101 Firefox/119.0",
            # Firefox – macOS
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 13.6; rv:122.0) Gecko/20100101 Firefox/122.0",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 13.5; rv:121.0) Gecko/20100101 Firefox/121.0",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 12.6; rv:120.0) Gecko/20100101 Firefox/120.0",
            # Firefox – Linux
            "Mozilla/5.0 (X11; Linux x86_64; rv:122.0) Gecko/20100101 Firefox/122.0",
            "Mozilla/5.0 (X11; Linux x86_64; rv:121.0) Gecko/20100101 Firefox/121.0",
            "Mozilla/5.0 (X11; Linux x86_64; rv:120.0) Gecko/20100101 Firefox/120.0",
            # Safari – macOS
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 13_6) AppleWebKit/605.1.15 Version/17.1 Safari/605.1.15",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 13_5) AppleWebKit/605.1.15 Version/16.6 Safari/605.1.15",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 13_4) AppleWebKit/605.1.15 Version/16.5 Safari/605.1.15",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 12_6) AppleWebKit/605.1.15 Version/16.4 Safari/605.1.15",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 12_5) AppleWebKit/605.1.15 Version/16.3 Safari/605.1.15",
        )
        return user_agents
    # tags to decompose between on websites
    elif data_type == 3:
        decompose_tags = (
            # Layout / noise
            "script",
            "style",
            "noscript",
            "header",
            "footer",
            "nav",
            "aside",
            "iframe",
            "form",
            "input",
            "button",
            "select",
            "option",
            "embed",
            "object",
            "canvas",
            "map",
            "area",
            "base",
            "link",
            "meta",
            # Rare / obsolete
            "applet",
            "acronym",
            "basefont",
            "big",
            "center",
            "font",
            "strike",
            "menu",
            "dir",
            "wbr",
            "bdi",
            "bdo",
            "ruby",
            "rt",
            "rp",
        )
        return decompose_tags
    elif data_type == 4:
        ignore_key_words = frozenset(
            {
                # Software flags
                "adobe after effects",
                "toon boom",
                "photoshop",
                # Wrong Job Names
                "illustrator",
                # Seniority mismatch
                "intern",
                "internship",
                "junior",
                "graduate",
                "student",
                "entry level",
                "entry-level",
                "trainee",
                "apprentice",
                # Teaching / mentoring
                "teacher",
                "lecturer",
                "instructor",
                "professor",
                "teaching assistant",
                # Non-production roles
                "recruiter",
                "talent acquisition",
                "hr",
                "human resources",
                "sales",
                "marketing",
                "social media manager",
                "community manager",
                # Volunteer / unpaid
                "volunteer",
                "unpaid",
                "pro bono",
                # Non-relevant animation usage
                "animation tester",
                "qa",
                "quality assurance",
                "motion capture technician",
                "mocap operator",
                # Red flags
                "crypto",
                "nft",
                "web3",
            }
        )
        return ignore_key_words
    return None