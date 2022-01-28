from re import compile

URL = "https://scholar.google.com/citations?view_op=view_org&hl=ru&org=7538668628685604268"
LAST_20_URL = 'https://scholar.google.com/citations?view_op=view_org&hl=ru&org=7538668628685604268&before_author=oIVz_wIAAAAJ&astart=460'
HEADERS = {"user-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) "
                         "Chrome/84.0.4147.135 Safari/537.36 OPR/70.0.3728.154",
           "accept": "*/*"}
HOST = "https://scholar.google.com"
PATTERN = compile(r"^window.location='(.+)'$")