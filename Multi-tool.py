import os, sys, time, random, requests, json, socket, subprocess, threading, datetime, base64, re, shutil
from pystyle import Colors, Colorate, Center
from concurrent.futures import ThreadPoolExecutor
from urllib.parse import quote
 
# ──────────────────────────────────────────────────────────────────────────────
#  CONFIG
# ──────────────────────────────────────────────────────────────────────────────
CONFIG = {
    "proxy":         None,
    "log_enabled":   True,
    "retry_count":   3,
    "retry_delay":   1.5,
    "timeout":       10,
    "tokens":        [],
    "request_delay": 0.3,   # global delay between requests
    "theme":         "blue", # blue / red / green / purple
    "session_file":  "session.json",
}
LOG_DIR = "logs"
os.makedirs(LOG_DIR, exist_ok=True)
 
# ──────────────────────────────────────────────────────────────────────────────
#  COLORS
# ──────────────────────────────────────────────────────────────────────────────
BLUE       = (5,   20,  200)
CYAN       = (0,   220, 255)
WHITE      = (255, 255, 255)
DARK_BLUE  = (5,   10,  120)
RED        = (220, 30,  30 )
DARK_RED   = (80,  0,   0  )
PURPLE     = (120, 0,   200)
MAGENTA    = (255, 0,   200)
GREEN      = (0,   200, 80 )
DARK_GREEN = (0,   60,  20 )
GOLD       = (255, 215, 0  )
ORANGE     = (255, 140, 0  )
TEAL       = (0,   180, 150)
DARK_TEAL  = (0,   60,  50 )
 
THEME_COLORS = {
    "blue":   Colors.blue_to_cyan,
    "red":    Colors.red_to_white,
    "green":  Colors.green_to_cyan,
    "purple": Colors.purple_to_blue,
}
 
THEME = {
    "main":    Colors.blue_to_cyan,
    "osint":   Colors.blue_to_cyan,
    "server":  Colors.red_to_white,
    "account": Colors.white_to_blue,
    "network": Colors.green_to_cyan,
    "misc":    Colors.purple_to_blue,
    "settings":Colors.cyan_to_blue,
    "multi":   Colors.cyan_to_blue,
    "crypto":  Colors.green_to_cyan,
    "webhack": Colors.red_to_white,
    "invite":  Colors.purple_to_blue,
    "reaction":Colors.blue_to_cyan,
    "purge":   Colors.red_to_white,
}
 
INPUT_GRAD = {
    "main":    (BLUE,      CYAN   ),
    "osint":   (DARK_BLUE, CYAN   ),
    "server":  (DARK_RED,  RED    ),
    "account": (PURPLE,    WHITE  ),
    "network": (DARK_GREEN,GREEN  ),
    "misc":    (PURPLE,    MAGENTA),
    "settings":(BLUE,      WHITE  ),
    "multi":   (DARK_BLUE, CYAN   ),
    "crypto":  (DARK_GREEN,GOLD   ),
    "webhack": (DARK_RED,  ORANGE ),
    "invite":  (PURPLE,    CYAN   ),
    "reaction":(DARK_BLUE, MAGENTA),
    "purge":   (DARK_RED,  RED    ),
}
 
PULSE = {
    "main":    [(0,50,200),(0,100,255),(0,180,255),(0,220,255),(0,180,255),(0,100,255)],
    "osint":   [(0,20,120),(0,60,200),(0,140,255),(0,200,255),(0,140,255),(0,60,200)],
    "server":  [(80,0,0),(160,10,10),(220,30,30),(255,80,80),(220,30,30),(160,10,10)],
    "account": [(60,0,140),(100,0,200),(160,0,255),(200,100,255),(160,0,255),(100,0,200)],
    "network": [(0,40,20),(0,100,40),(0,180,80),(0,220,100),(0,180,80),(0,100,40)],
    "misc":    [(80,0,140),(140,0,200),(200,0,255),(255,0,200),(200,0,255),(140,0,200)],
    "settings":[(0,50,150),(0,120,200),(0,180,240),(0,220,255),(0,180,240),(0,120,200)],
    "multi":   [(0,30,100),(0,80,180),(0,150,240),(0,220,255),(0,150,240),(0,80,180)],
    "crypto":  [(0,80,20),(0,140,40),(0,200,80),(200,180,0),(0,200,80),(0,140,40)],
    "webhack": [(80,20,0),(160,50,0),(220,100,0),(255,140,0),(220,100,0),(160,50,0)],
    "invite":  [(60,0,120),(100,0,180),(150,0,240),(180,100,255),(150,0,240),(100,0,180)],
    "reaction":[(0,20,120),(40,0,180),(100,0,220),(160,0,255),(100,0,220),(40,0,180)],
    "purge":   [(80,0,0),(160,10,10),(220,30,30),(255,80,80),(220,30,30),(160,10,10)],
}
 
TITLE   = "[ DISCORD MULTI TOOL ]"
VERSION = "v6.0"
HANDLE  = "by ACC/sqlzsa, https://discord.gg/unCRmtjSM."
 
# ──────────────────────────────────────────────────────────────────────────────
#  ASCII ART
# ──────────────────────────────────────────────────────────────────────────────
ASCII_MAIN = """\
      ..      ..                        ..
   ..OOOO..  ..OO..                ..OOOO..
 ..OO....OO....OO....            ..OO....OO..
..OO......OO..OO..OO..  ..    ..OO......OO..OO..
..OO..  ..OOOOOO..OO....OO....OO..  ..OOOO....OO..
..OO....OOOO..OOOOOO....OO....OO....OOOO..OOOO..OO..
  ..OOOO..  ..OOOO....OOOOOOOOOO....OO....OO..OOOO..
          ..OO..    ..OO..  ..OO..  ..OOOOOO....OO..
        ..OO....  ..OO..      ..OO....OO..OO..OO..
      ..OO..OO....OO..          ..OOOOOO....OOOO..
    ..OO..  ..OOOO..              ..OOOO....OO..
  ..OO..      ..                    ..OOOOOO..
..OO..                                ..OO..
..                                      .."""
 
ASCII_OSINT   = "  ___  ___ ___ _  _ _____\n / _ \\/ __|_ _| \\| |_   _|\n| (_) \\__ \\| || .` | | |\n \\___/|___/___|_|\\_| |_|\n  [ intelligence tools ]"
ASCII_SERVER  = "  ____  ___ _____   _____ ___\n / ___|| __|  __ \\ / / __| _ \\\n \\__ \\| _||    \\ V /| _||   /\n |___/|___|___| \\_/ |___|_|_\\\n   [ server operations ]"
ASCII_ACCOUNT = "  _   ___ ___ ___  _   _ _  _ _____\n /_\\ / __/ __/ _ \\| | | | \\| |_   _|\n/ _ \\ (_| (_| (_) | |_| | .` | | |\n/_/ \\_\\___\\___\\___/ \\___/|_|\\_| |_|\n       [ account manager ]"
ASCII_NETWORK = "  _  _ ___ _____      ___  ___ _  __\n | \\| | __|_   _|    / _ \\| __| |/ /\n | .` | _|  | |     | (_) | _|| ' <\n |_|\\_|___| |_|      \\___/|___|_|\\_\\\n       [ network recon ]"
ASCII_MISC    = "  __  __ ___ ___  ___\n |  \\/  |_ _/ __|/ __|\n | |\\/| || |\\__ \\ (__\n |_|  |_|___|___/\\___|\n   [ miscellaneous ]"
ASCII_MULTI   = "  __  __ _   _ _  _____ ___ ___  _  _____ _  _\n |  \\/  | | | | ||_   _|_ _|_ _|| |/ / _ | \\| |\n | |\\/| | |_| | |__| |  | | | | | ' | (_) | .` |\n |_|  |_|\\___/|____|_| |___|___||_|\\_\\___/|_|\\_|\n       [ multi token operations ]"
ASCII_CRYPTO  = "   ____ ____  __   ______  _____ ___\n  / ___| __ \\|  \\ / /  _ \\|_   _/ _ \\\n | |   |    /| |\\ V /| |_) | | || | | |\n | |___| |\\ \\| | | | |  __/  | || |_| |\n  \\____|_| \\_|_| |_| |_|     |_| \\___/\n       [ crypto tools ]"
ASCII_WEBHACK = "  _    _ ___ ___   _  _   _   ___ _  __\n | |  | | __| _ ) | || | /_\\ / __| |/ /\n | |__| | _|| _ \\ | __ |/ _ \\ (__| ' <\n |____|_|___|___/ |_||_/_/ \\_\\___|_|\\_\\\n      [ web hacking tools ]"
ASCII_INVITE  = "  ___ _  ___   _____ _____ ___\n |_ _| \\| \\ \\ / /_ _|_   _| __|\n  | || .` |\\ V / | |  | | | _|\n |___|_|\\_| \\_/ |___| |_| |___|\n   [ invite manager ]"
ASCII_REACTION= "  ___ ___   _   ___ _____ ___ ___  _  _\n | _ \\ __| /_\\ / __|_   _|_ _/ _ \\| \\| |\n |   / _| / _ \\ (__  | |  | | (_) | .` |\n |_|_\\___/_/ \\_\\___| |_| |___\\___/|_|\\_|\n     [ reaction tools ]"
ASCII_SETTINGS= "  ___ ___ _____ _____ ___ _  _  ___  ___\n / __| __|_   _|_   _|_ _| \\| |/ __/ __|\n \\__ \\ _|  | |   | |  | || .` | (_ \\__ \\\n |___/___|  |_|   |_| |___|_|\\_|\\___|___/\n       [ configuration ]"
ASCII_PURGE   = "  ___ _   _ ___ ___ ___\n | _ \\ | | | _ \\ __| __|\n |  _/ |_| |   / _|| _|\n |_|  \\___/|_|_\\___|___|\n  [ message purger ]"
 
SECTION_ASCII = {
    "main":    ASCII_MAIN,    "osint":   ASCII_OSINT,
    "server":  ASCII_SERVER,  "account": ASCII_ACCOUNT,
    "network": ASCII_NETWORK, "misc":    ASCII_MISC,
    "multi":   ASCII_MULTI,   "crypto":  ASCII_CRYPTO,
    "webhack": ASCII_WEBHACK, "invite":  ASCII_INVITE,
    "reaction":ASCII_REACTION,"settings":ASCII_SETTINGS,
    "purge":   ASCII_PURGE,
}
 
# ──────────────────────────────────────────────────────────────────────────────
#  LOGGING
# ──────────────────────────────────────────────────────────────────────────────
_log_lines = []
def log(text): _log_lines.append(f"[{datetime.datetime.now().strftime('%H:%M:%S')}] {text}")
def save_log(tag="result"):
    if not CONFIG["log_enabled"] or not _log_lines: return
    fname = os.path.join(LOG_DIR, f"{tag}_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.txt")
    with open(fname,"w",encoding="utf-8") as f:
        f.write(f"ACC Discord Multi Tool {VERSION}\n{datetime.datetime.now()}\n{'─'*60}\n")
        f.write("\n".join(_log_lines))
    _log_lines.clear()
    success(f"Saved → {fname}")
 
def save_session():
    try:
        with open(CONFIG["session_file"],"w") as f:
            json.dump({"proxy":CONFIG["proxy"],"log_enabled":CONFIG["log_enabled"],
                       "retry_count":CONFIG["retry_count"],"request_delay":CONFIG["request_delay"],
                       "theme":CONFIG["theme"]}, f, indent=2)
        success(f"Session saved → {CONFIG['session_file']}")
    except Exception as e: error(f"Could not save session: {e}")
 
def load_session():
    try:
        if os.path.exists(CONFIG["session_file"]):
            with open(CONFIG["session_file"]) as f: data=json.load(f)
            for k,v in data.items():
                if k in CONFIG: CONFIG[k]=v
            success(f"Session loaded from {CONFIG['session_file']}")
    except Exception as e: error(f"Could not load session: {e}")
 
# ──────────────────────────────────────────────────────────────────────────────
#  HTTP
# ──────────────────────────────────────────────────────────────────────────────
def _proxies():
    return {"http":CONFIG["proxy"],"https":CONFIG["proxy"]} if CONFIG["proxy"] else None
 
def req(method, url, **kwargs):
    kwargs.setdefault("timeout", CONFIG["timeout"])
    if CONFIG["proxy"]: kwargs["proxies"] = _proxies()
    for attempt in range(CONFIG["retry_count"]):
        try:
            r = requests.request(method, url, **kwargs)
            if r.status_code == 429:
                wait = float(r.headers.get("Retry-After", CONFIG["retry_delay"]))
                info(f"Rate limited — waiting {wait:.1f}s"); time.sleep(wait); continue
            return r
        except requests.exceptions.ProxyError:
            error("Proxy error"); return None
        except requests.exceptions.ConnectionError:
            if attempt < CONFIG["retry_count"]-1:
                info(f"Retrying ({attempt+1}/{CONFIG['retry_count']})..."); time.sleep(CONFIG["retry_delay"])
        except Exception as e:
            error(f"Request error: {e}"); return None
    error("All retries failed"); return None
 
# ──────────────────────────────────────────────────────────────────────────────
#  CORE UTILS
# ──────────────────────────────────────────────────────────────────────────────
def clear(): os.system('cls' if os.name=='nt' else 'clear')
def rgb(r,g,b): return f"\033[38;2;{r};{g};{b}m"
RESET = "\033[0m"
 
def term_width():
    try: return shutil.get_terminal_size().columns
    except: return 80
 
def grad_print(text, start, end, newline=True):
    n=max(len(text),1); r,g,b=float(start[0]),float(start[1]),float(start[2])
    dr=(end[0]-start[0])/n; dg=(end[1]-start[1])/n; db=(end[2]-start[2])/n
    for ch in text:
        sys.stdout.write(f"{rgb(int(r),int(g),int(b))}{ch}{RESET}"); r+=dr; g+=dg; b+=db
    sys.stdout.flush()
    if newline: print()
 
def grad_type(text, start, end, delay=0.022):
    n=max(len(text),1); r,g,b=float(start[0]),float(start[1]),float(start[2])
    dr=(end[0]-start[0])/n; dg=(end[1]-start[1])/n; db=(end[2]-start[2])/n
    for ch in text:
        sys.stdout.write(f"{rgb(int(r),int(g),int(b))}{ch}{RESET}")
        sys.stdout.flush(); r+=dr; g+=dg; b+=db; time.sleep(delay)
    print()
 
def grad_input(prompt, start, end):
    grad_print(prompt, start, end, newline=False)
    sys.stdout.write(rgb(*start)); sys.stdout.flush()
    val=input(); sys.stdout.write(RESET); return val
 
def success(msg):
    grad_print(f"  ✓ {msg}", GREEN, DARK_GREEN); log(f"[OK] {msg}")
def error(msg):
    grad_print(f"  ✗ {msg}", RED, DARK_RED); log(f"[ERR] {msg}")
def info(msg, start=CYAN, end=WHITE):
    grad_print(f"  » {msg}", start, end); log(f"[INFO] {msg}")
def warn(msg):
    grad_print(f"  ⚠ {msg}", ORANGE, GOLD); log(f"[WARN] {msg}")
 
def wait_enter(theme="main"):
    s,e=INPUT_GRAD[theme]; print()
    grad_type("  Press Enter to go back...", e, WHITE, delay=0.012)
    sys.stdout.write(rgb(*s)); input(); sys.stdout.write(RESET)
 
def box_print(lines, start, end):
    tw=min(term_width()-6, 80); safe=[l[:tw-4] for l in lines]
    W=min(max((len(l) for l in safe),default=10)+4, tw)
    grad_print(f"  ╔{'═'*W}╗", start, end)
    for line in safe:
        grad_print(f"  ║  {line+' '*(W-2-len(line))}║", start, end); log(line)
    grad_print(f"  ╚{'═'*W}╝", start, end)
 
def calc_account_age(uid):
    try:
        ts=((int(uid)>>22)+1420070400000)/1000; cr=datetime.datetime.fromtimestamp(ts)
        days=(datetime.datetime.now()-cr).days
        return f"{cr.strftime('%Y-%m-%d')} ({days//365}y {(days%365)//30}m ago)"
    except: return "Unknown"
 
def nitro_label(n): return {0:"None",1:"Nitro Classic",2:"Nitro",3:"Nitro Basic"}.get(n,"Unknown")
def _dh(t): return {"Authorization":t,"Content-Type":"application/json","User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
def _validate_token(token):
    r=req("GET","https://discord.com/api/v9/users/@me",headers=_dh(token))
    if r and r.status_code==200:
        d=r.json(); success(f"Valid — {d['username']}#{d.get('discriminator','0')}"); return True
    error("Invalid token"); return False
 
# ──────────────────────────────────────────────────────────────────────────────
#  ANIMATIONS
# ──────────────────────────────────────────────────────────────────────────────
def spinner(label, duration, start=BLUE, end=CYAN):
    frames=['⠋','⠙','⠹','⠸','⠼','⠴','⠦','⠧','⠇','⠏']
    t_end=time.time()+duration; i=0
    while time.time()<t_end:
        sys.stdout.write(f"\r  {rgb(*start)}{frames[i%len(frames)]}{RESET} ")
        grad_print(label,start,end,newline=False); sys.stdout.flush(); time.sleep(0.08); i+=1
    sys.stdout.write(f"\r  {rgb(*end)}✓{RESET} "); grad_print(label,start,end)
 
def loading_bar(label, duration, start=BLUE, end=CYAN):
    BAR=30
    for i in range(BAR+1):
        t=i/BAR; r=int(start[0]+(end[0]-start[0])*t); g=int(start[1]+(end[1]-start[1])*t); b=int(start[2]+(end[2]-start[2])*t)
        sys.stdout.write(f"\r  {rgb(r,g,b)}{label} [{'█'*i+'░'*(BAR-i)}] {int(t*100)}%{RESET}")
        sys.stdout.flush(); time.sleep(duration/BAR)
    print()
 
def flash_text(text, start, end, times=3):
    for _ in range(times):
        sys.stdout.write("\r  "); grad_print(text,start,end,newline=False); time.sleep(0.18)
        sys.stdout.write(f"\r  {' '*len(text)}"); sys.stdout.flush(); time.sleep(0.1)
    sys.stdout.write("\r  "); grad_print(text,start,end)
 
def glitch_print(text, start, end, times=7):
    gc='▓▒░█▄▀■□▪▫#@!?$%&'
    for _ in range(times):
        g=''.join(random.choice(gc) if random.random()<0.35 else c for c in text)
        sys.stdout.write("\r"); grad_print(g,start,end,newline=False); sys.stdout.flush(); time.sleep(0.06)
    sys.stdout.write("\r"); grad_print(text,start,end)
 
def matrix_rain(duration=2.0):
    cols=term_width(); rows=20
    chars="ｦｧｨｩｪｫｬｭｮｯｰｱｲｳｴｵｶｷｸｹｺｻｼｽｾｿﾀﾁﾂﾃﾄﾅﾆﾇﾈﾉﾊﾋﾌﾍﾎﾏﾐﾑﾒﾓﾔﾕﾖﾗﾘﾙﾚﾛﾜﾝ0123456789ABCDEF"
    drops=[random.randint(-rows,0) for _ in range(cols//2)]
    t_end=time.time()+duration; sys.stdout.write("\033[?25l")
    while time.time()<t_end:
        lines=[[' ']*(cols//2) for _ in range(rows)]
        for col,drop in enumerate(drops):
            for r in range(rows):
                row=drop-r
                if 0<=row<rows:
                    g_val=int(255*(1-r/rows))
                    lines[row][col]=f"\033[38;2;0;{g_val};0m{random.choice(chars)}\033[0m"
            drops[col]=(drop+1)%(rows+random.randint(5,15))
        clear()
        for row in lines: sys.stdout.write(''.join(row)+'\n')
        sys.stdout.flush(); time.sleep(0.05)
    sys.stdout.write("\033[?25m")
 
def wipe_transition(theme="main"):
    s,e=INPUT_GRAD[theme]; tw=term_width()
    for i in range(0,tw,4):
        t=i/tw; r=int(s[0]+(e[0]-s[0])*t); g=int(s[1]+(e[1]-s[1])*t); b=int(s[2]+(e[2]-s[2])*t)
        sys.stdout.write(f"\r{rgb(r,g,b)}{'█'*i}{RESET}"); sys.stdout.flush(); time.sleep(0.003)
    sys.stdout.write(f"\r{' '*tw}\r"); sys.stdout.flush()
 
# ──────────────────────────────────────────────────────────────────────────────
#  HEADER + MENU
# ──────────────────────────────────────────────────────────────────────────────
def print_header(theme="main", animate=False):
    clear()
    col=THEME.get(theme, Colors.blue_to_cyan)
    for line in SECTION_ASCII.get(theme, ASCII_MAIN).split('\n'):
        print(Colorate.Horizontal(col, line, 1))
        if animate: time.sleep(0.020)
    print()
    s,e=INPUT_GRAD.get(theme, INPUT_GRAD["main"])
    grad_print(Center.XCenter(f"{TITLE}  {VERSION}"), s, e)
    tags=[]
    if CONFIG["proxy"]: tags.append("[PROXY: ON]")
    if CONFIG["tokens"]: tags.append(f"[TOKENS: {len(CONFIG['tokens'])}]")
    if CONFIG["request_delay"]>0: tags.append(f"[DELAY: {CONFIG['request_delay']}s]")
    if tags: grad_print(Center.XCenter("  ".join(tags)), GOLD, ORANGE)
    grad_print(Center.XCenter(HANDLE), e, WHITE)
    print()
 
def print_menu(title, options, theme="main", desc=None):
    wipe_transition(theme); print_header(theme)
    s,e=INPUT_GRAD.get(theme, INPUT_GRAD["main"])
    tw=min(term_width()-6,70); W=tw
    top_label=f"─[ {title} ]"; top_line=f"  ┌{top_label}{'─'*max(0,W-len(top_label)-1)}┐"
    pulse_colors=PULSE.get(theme, PULSE["main"])
    for col in pulse_colors[:3]:
        sys.stdout.write(f"\r{rgb(*col)}{top_line}{RESET}"); sys.stdout.flush(); time.sleep(0.06)
    print(f"\r{rgb(*s)}{top_line}{RESET}")
    if desc:
        grad_print(f"  │  {desc[:W-4]:<{W-3}}│", e, s)
        grad_print(f"  ├{'─'*W}┤", s, e)
    for key,label in options:
        grad_print(f"  │  {f'[{key}] {label}'[:W-5]:<{W-3}}│", s, e)
    bot_line=f"  └{'─'*W}┘"
    for col in pulse_colors[:3]:
        sys.stdout.write(f"\r{rgb(*col)}{bot_line}{RESET}"); sys.stdout.flush(); time.sleep(0.06)
    print(f"\r{rgb(*s)}{bot_line}{RESET}"); print()
 
# ──────────────────────────────────────────────────────────────────────────────
#  BOOT
# ──────────────────────────────────────────────────────────────────────────────
def boot():
    clear(); load_session(); matrix_rain(2.0)
    print_header("main", animate=True); time.sleep(0.1)
    glitch_print(Center.XCenter("INITIALIZING SYSTEM..."), DARK_BLUE, CYAN); print()
    spinner("Loading OSINT modules",       0.5, BLUE,       CYAN   )
    spinner("Loading account modules",     0.4, DARK_BLUE,  BLUE   )
    spinner("Loading server modules",      0.4, BLUE,       CYAN   )
    spinner("Loading network modules",     0.4, DARK_GREEN, GREEN  )
    spinner("Loading crypto modules",      0.4, DARK_GREEN, GOLD   )
    spinner("Loading web hack modules",    0.4, DARK_RED,   ORANGE )
    spinner("Loading multi-token engine",  0.4, DARK_BLUE,  CYAN   )
    spinner("All systems ready",           0.3, CYAN,       WHITE  )
    print(); flash_text("[ SYSTEM ONLINE ]", CYAN, WHITE, times=4); time.sleep(0.3)
 
# ──────────────────────────────────────────────────────────────────────────────
#  OSINT MODULE
# ──────────────────────────────────────────────────────────────────────────────
def osint_self():
    token=grad_input("  Token: ",DARK_BLUE,CYAN); h=_dh(token)
    r=req("GET","https://discord.com/api/v9/users/@me",headers=h)
    if not r or r.status_code!=200: error("Invalid token"); return
    d=r.json()
    gr=req("GET","https://discord.com/api/v9/users/@me/guilds",headers=h)
    sc=len(gr.json()) if gr and gr.status_code==200 else "?"
    flags=d.get('public_flags',0)
    bm={1:"Staff",2:"Partner",4:"HypeSquad Events",8:"Bug Hunter L1",64:"Bravery",
        128:"Brilliance",256:"Balance",512:"Early Supporter",16384:"Bug Hunter L2",
        131072:"Verified Bot Dev",4194304:"Active Dev"}
    badges=[n for bit,n in bm.items() if flags&bit] or ["None"]
    box_print([
        f"Username : {d['username']}#{d.get('discriminator','0')}",
        f"ID       : {d['id']}",
        f"Email    : {d.get('email','Hidden')}",
        f"Phone    : {d.get('phone','Hidden')}",
        f"MFA      : {d.get('mfa_enabled',False)}",
        f"Verified : {d.get('verified',False)}",
        f"Nitro    : {nitro_label(d.get('premium_type',0))}",
        f"Locale   : {d.get('locale','?')}",
        f"Servers  : {sc}",
        f"Badges   : {', '.join(badges)}",
        f"Created  : {calc_account_age(d['id'])}",
    ],DARK_BLUE,CYAN); save_log("osint_self")
 
def osint_user_id():
    uid=grad_input("  User ID: ",DARK_BLUE,CYAN)
    r=req("GET",f"https://discord.com/api/v9/users/{uid}")
    if not r or r.status_code!=200: error("Not found"); return
    d=r.json(); flags=d.get('public_flags',0)
    bm={1:"Staff",2:"Partner",4:"HypeSquad Events",8:"Bug Hunter L1",64:"Bravery",
        128:"Brilliance",256:"Balance",512:"Early Supporter",16384:"Bug Hunter L2",
        131072:"Verified Bot Dev",4194304:"Active Dev"}
    badges=[n for bit,n in bm.items() if flags&bit] or ["None"]
    box_print([
        f"Username : {d['username']}#{d.get('discriminator','0')}",
        f"ID       : {d['id']}",
        f"Bot      : {d.get('bot',False)}",
        f"Avatar   : {'Yes' if d.get('avatar') else 'No'}",
        f"Banner   : {'Yes' if d.get('banner') else 'No'}",
        f"Badges   : {', '.join(badges)}",
        f"Created  : {calc_account_age(d['id'])}",
        f"Token Age: {calc_account_age(d['id'])}",
    ],DARK_BLUE,CYAN)
    if d.get('avatar'):
        ext="gif" if d['avatar'].startswith("a_") else "png"
        info(f"Avatar: https://cdn.discordapp.com/avatars/{uid}/{d['avatar']}.{ext}?size=1024")
    if d.get('banner'):
        ext="gif" if d['banner'].startswith("a_") else "png"
        info(f"Banner: https://cdn.discordapp.com/banners/{uid}/{d['banner']}.{ext}?size=1024")
    save_log("osint_user")
 
def osint_server():
    gid=grad_input("  Server ID: ",DARK_BLUE,CYAN); token=grad_input("  Token: ",DARK_BLUE,CYAN)
    r=req("GET",f"https://discord.com/api/v9/guilds/{gid}?with_counts=true",headers=_dh(token))
    if not r or r.status_code!=200: error(f"Failed ({r.status_code if r else 'no response'})"); return
    d=r.json()
    box_print([
        f"Name        : {d.get('name','?')}",
        f"ID          : {d.get('id','?')}",
        f"Owner ID    : {d.get('owner_id','?')}",
        f"Members     : {d.get('approximate_member_count','?')}",
        f"Online      : {d.get('approximate_presence_count','?')}",
        f"Boost Level : {d.get('premium_tier','?')}",
        f"Boosts      : {d.get('premium_subscription_count','?')}",
        f"Verification: {d.get('verification_level','?')}",
        f"NSFW Level  : {d.get('nsfw_level','?')}",
        f"Features    : {', '.join(d.get('features',[])[:4]) or 'None'}",
    ],DARK_BLUE,CYAN)
    ch_r=req("GET",f"https://discord.com/api/v9/guilds/{gid}/channels",headers=_dh(token))
    if ch_r and ch_r.status_code==200:
        chs=ch_r.json()
        info(f"Channels: {len([c for c in chs if c['type']==0])} text | {len([c for c in chs if c['type']==2])} voice | {len([c for c in chs if c['type']==4])} categories")
    save_log("osint_server")
 
def osint_invite():
    code=grad_input("  Invite (code or link): ",DARK_BLUE,CYAN); code=code.split("/")[-1].strip()
    r=req("GET",f"https://discord.com/api/v9/invites/{code}?with_counts=true")
    if not r or r.status_code!=200: error("Invalid invite"); return
    d=r.json()
    box_print([
        f"Server   : {d['guild']['name']}",
        f"Server ID: {d['guild']['id']}",
        f"Channel  : #{d['channel']['name']}",
        f"Inviter  : {d.get('inviter',{}).get('username','Unknown')}",
        f"Uses     : {d.get('uses',0)} / {d.get('max_uses',0) or '∞'}",
        f"Expires  : {d.get('expires_at','Never')}",
        f"Members  : {d.get('approximate_member_count','?')}",
        f"Online   : {d.get('approximate_presence_count','?')}",
    ],DARK_BLUE,CYAN); save_log("invite_info")
 
def osint_avatar():
    uid=grad_input("  User ID: ",DARK_BLUE,CYAN); size=grad_input("  Size [1024]: ",DARK_BLUE,CYAN) or "1024"
    r=req("GET",f"https://discord.com/api/v9/users/{uid}")
    if not r or r.status_code!=200: error("Not found"); return
    d=r.json()
    if d.get('avatar'):
        ext="gif" if d['avatar'].startswith("a_") else "png"
        url=f"https://cdn.discordapp.com/avatars/{uid}/{d['avatar']}.{ext}?size={size}"
        success(f"Avatar URL: {url}")
        dl=grad_input("  Download to file? [y/N]: ",DARK_BLUE,CYAN)
        if dl.lower()=='y':
            try:
                img=requests.get(url,timeout=10); fname=f"avatar_{uid}.{ext}"
                with open(fname,'wb') as f: f.write(img.content)
                success(f"Saved → {fname}")
            except Exception as e: error(f"Download failed: {e}")
    else: info("No custom avatar")
 
def osint_banner():
    uid=grad_input("  User ID: ",DARK_BLUE,CYAN)
    r=req("GET",f"https://discord.com/api/v9/users/{uid}")
    if not r or r.status_code!=200: error("Not found"); return
    d=r.json()
    if d.get('banner'):
        ext="gif" if d['banner'].startswith("a_") else "png"
        success(f"https://cdn.discordapp.com/banners/{uid}/{d['banner']}.{ext}?size=1024")
    else: info("No banner")
 
def osint_token_check():
    token=grad_input("  Token: ",DARK_BLUE,CYAN)
    r=req("GET","https://discord.com/api/v9/users/@me",headers=_dh(token))
    if r and r.status_code==200:
        d=r.json()
        ts_part=token.split('.')[0] if '.' in token else token
        try:
            uid=base64.b64decode(ts_part+'==').decode('utf-8',errors='ignore')
            age=calc_account_age(uid)
        except: age="Unknown"
        success(f"VALID — {d['username']}#{d.get('discriminator','0')} | {nitro_label(d.get('premium_type',0))} | Age: {age}")
    else: error(f"INVALID — {r.status_code if r else 'no response'}")
 
def osint_badges():
    uid=grad_input("  User ID: ",DARK_BLUE,CYAN)
    r=req("GET",f"https://discord.com/api/v9/users/{uid}")
    if not r or r.status_code!=200: error("Not found"); return
    flags=r.json().get('public_flags',0)
    bm={1:"Discord Staff",2:"Partnered Server Owner",4:"HypeSquad Events",
        8:"Bug Hunter L1",64:"HypeSquad Bravery",128:"HypeSquad Brilliance",
        256:"HypeSquad Balance",512:"Early Supporter",16384:"Bug Hunter L2",
        131072:"Verified Bot Developer",4194304:"Active Developer"}
    badges=[n for bit,n in bm.items() if flags&bit]
    if badges:
        for b in badges: grad_print(f"    ● {b}",CYAN,WHITE); log(f"Badge: {b}")
    else: info("No public badges")
 
def osint_username_search():
    username=grad_input("  Username: ",DARK_BLUE,CYAN)
    platforms={
        "GitHub":   f"https://github.com/{username}",
        "Twitter/X":f"https://x.com/{username}",
        "Instagram":f"https://www.instagram.com/{username}",
        "TikTok":   f"https://www.tiktok.com/@{username}",
        "Reddit":   f"https://www.reddit.com/user/{username}",
        "Twitch":   f"https://www.twitch.tv/{username}",
        "YouTube":  f"https://www.youtube.com/@{username}",
        "Steam":    f"https://steamcommunity.com/id/{username}",
        "Roblox":   f"https://www.roblox.com/user.aspx?username={username}",
        "Replit":   f"https://replit.com/@{username}",
        "Pastebin": f"https://pastebin.com/u/{username}",
        "LinkedIn": f"https://www.linkedin.com/in/{username}",
        "Medium":   f"https://medium.com/@{username}",
        "Dev.to":   f"https://dev.to/{username}",
        "Keybase":  f"https://keybase.io/{username}",
        "HackerNews":f"https://news.ycombinator.com/user?id={username}",
    }
    info(f"Searching '{username}' across {len(platforms)} platforms..."); print(); found=[]
    for plat,url in platforms.items():
        try:
            resp=requests.get(url,timeout=6,allow_redirects=True,headers={"User-Agent":"Mozilla/5.0"})
            if resp.status_code==200 and "not found" not in resp.text.lower()[:400]:
                success(f"{plat:<14} {url}"); found.append(f"{plat}: {url}")
            else: grad_print(f"  ✗ {plat:<14} not found",RED,DARK_RED)
        except: warn(f"{plat:<14} timeout")
        time.sleep(0.15)
    print(); info(f"Found on {len(found)}/{len(platforms)} platforms"); save_log(f"username_{username}")
 
def osint_phone():
    phone=grad_input("  Phone (E.164 e.g. +14155552671): ",DARK_BLUE,CYAN)
    cc_map={"+1":"USA/Canada","+44":"UK","+49":"Germany","+33":"France","+61":"Australia",
            "+91":"India","+86":"China","+7":"Russia","+34":"Spain","+39":"Italy",
            "+55":"Brazil","+52":"Mexico","+81":"Japan","+82":"South Korea","+31":"Netherlands"}
    country="Unknown"
    for code,name in sorted(cc_map.items(),key=lambda x:-len(x[0])):
        if phone.startswith(code): country=name; break
    box_print([
        f"Number  : {phone}",
        f"Country : {country}",
        f"Format  : {phone}",
    ],DARK_BLUE,CYAN)
    info(f"Truecaller → https://www.truecaller.com/search/gb/{phone.lstrip('+')} ",DARK_BLUE,CYAN)
    info(f'Google dork → "{phone}"',DARK_BLUE,CYAN)
 
def osint_domain():
    domain=grad_input("  Domain: ",DARK_BLUE,CYAN)
    spinner("WHOIS lookup",0.8,DARK_BLUE,CYAN)
    try:
        whois_raw=subprocess.run(f"whois {domain}",shell=True,capture_output=True,text=True,timeout=10).stdout
        whois_lines=[l for l in whois_raw.splitlines() if any(k in l.lower() for k in ['registrar','created','expir','name server','status'])][:10]
    except: whois_lines=["WHOIS unavailable"]
    box_print(whois_lines,DARK_BLUE,CYAN)
    spinner("Certificate transparency",0.7,DARK_BLUE,CYAN)
    try:
        r=requests.get(f"https://crt.sh/?q=%.{domain}&output=json",timeout=10)
        if r.status_code==200:
            subs=sorted(set(c['name_value'].replace('*.','').strip() for c in r.json() if domain in c.get('name_value','')))[:20]
            info(f"Found {len(subs)} subdomains via cert logs:")
            for sub in subs: grad_print(f"    ◆ {sub}",DARK_BLUE,CYAN)
    except: warn("crt.sh unavailable")
    info(f"Wayback → https://web.archive.org/web/*/{domain}",DARK_BLUE,CYAN)
    save_log(f"domain_{domain}")
 
def osint_email_permutations():
    fn=grad_input("  First name: ",DARK_BLUE,CYAN).lower()
    ln=grad_input("  Last name: ",DARK_BLUE,CYAN).lower()
    domain=grad_input("  Domain: ",DARK_BLUE,CYAN)
    patterns=[f"{fn}@{domain}",f"{ln}@{domain}",f"{fn}.{ln}@{domain}",f"{ln}.{fn}@{domain}",
              f"{fn}{ln}@{domain}",f"{fn[0]}{ln}@{domain}",f"{fn}{ln[0]}@{domain}",
              f"{fn[0]}.{ln}@{domain}",f"{fn}_{ln}@{domain}",f"{ln}_{fn}@{domain}",
              f"{fn[0]}_{ln}@{domain}",f"{ln[0]}.{fn}@{domain}"]
    info(f"Email permutations for {fn} {ln} @ {domain}:")
    for p in patterns: grad_print(f"    ✉  {p}",DARK_BLUE,CYAN); log(p)
    save_log("email_perms")
 
def osint_breach_links():
    target=grad_input("  Email/username/domain: ",DARK_BLUE,CYAN); enc=quote(target)
    resources=[
        ("HaveIBeenPwned",f"https://haveibeenpwned.com/account/{enc}"),
        ("DeHashed",      f"https://www.dehashed.com/search?query={enc}"),
        ("LeakCheck",     f"https://leakcheck.io/search?query={enc}"),
        ("IntelX",        f"https://intelx.io/?s={enc}"),
        ("Pastebin Search",f"https://psbdmp.ws/search/{enc}"),
        ("Google Pastes", f'https://google.com/search?q="{enc}"+site:pastebin.com'),
        ("Breach Directory","https://breachdirectory.org/"),
        ("Scatteredsecrets","https://scatteredsecrets.com/"),
    ]
    box_print([f"[{i+1:02}] {l:<18} {u[:50]}" for i,(l,u) in enumerate(resources)],DARK_BLUE,CYAN)
    warn("Always ensure authorization before querying breach data.")
 
def osint_ip_reputation():
    ip=grad_input("  IP address: ",DARK_BLUE,CYAN)
    spinner("Fetching IP intelligence",1.0,DARK_BLUE,CYAN)
    try:
        r=req("GET",f"http://ip-api.com/json/{ip}?fields=66846719")
        if not r: return
        d=r.json()
        if d.get('status')=='success':
            box_print([
                f"IP        : {d.get('query','?')}",
                f"Country   : {d.get('country','?')} ({d.get('countryCode','?')})",
                f"City      : {d.get('city','?')}",
                f"ISP       : {d.get('isp','?')}",
                f"Org       : {d.get('org','?')}",
                f"AS        : {d.get('as','?')}",
                f"Mobile    : {d.get('mobile',False)}",
                f"Proxy/VPN : {d.get('proxy',False)}",
                f"Hosting   : {d.get('hosting',False)}",
                f"Timezone  : {d.get('timezone','?')}",
            ],DARK_BLUE,CYAN)
            info(f"Maps → https://maps.google.com/?q={d['lat']},{d['lon']}",DARK_BLUE,CYAN)
        else: error("Lookup failed")
    except Exception as e: error(f"Error: {e}")
 
def osint_snowflake():
    sf=grad_input("  Snowflake ID: ",DARK_BLUE,CYAN)
    try:
        ts=((int(sf)>>22)+1420070400000)/1000; dt=datetime.datetime.fromtimestamp(ts)
        box_print([
            f"Created   : {dt.strftime('%Y-%m-%d %H:%M:%S')}",
            f"Unix      : {int(ts)}",
            f"Age       : {calc_account_age(sf)}",
            f"Worker ID : {(int(sf)&0x3E0000)>>17}",
            f"Process   : {(int(sf)&0x1F000)>>12}",
            f"Increment : {int(sf)&0xFFF}",
        ],DARK_BLUE,CYAN)
    except Exception as e: error(f"Error: {e}")
 
def osint_token_decode():
    token=grad_input("  Token: ",DARK_BLUE,CYAN)
    try:
        decoded=base64.b64decode(token.split('.')[0]+'==').decode('utf-8',errors='ignore')
        info(f"User ID : {decoded}"); info(f"Created : {calc_account_age(decoded)}")
    except Exception as e: error(f"Error: {e}")
 
def osint_vanity_check():
    vanity=grad_input("  Vanity URL (slug only): ",DARK_BLUE,CYAN).strip().lower()
    r=req("GET",f"https://discord.com/api/v9/invites/{vanity}")
    if r and r.status_code==200:
        d=r.json(); error(f"TAKEN — {d['guild']['name']} ({d['guild']['id']})")
    elif r and r.status_code==404: success(f"AVAILABLE — discord.gg/{vanity} is free!")
    else: warn(f"Unknown status: {r.status_code if r else 'no response'}")
 
# ──────────────────────────────────────────────────────────────────────────────
#  SERVER MODULE
# ──────────────────────────────────────────────────────────────────────────────
def server_channels():
    gid = grad_input("  Server ID: ", DARK_RED, RED)
    token = grad_input("  Token: ", DARK_RED, RED)

    r = req("GET", f"https://discord.com/api/v9/guilds/{gid}/channels", headers=_dh(token))
    if not r or r.status_code != 200:
        error("Failed")
        return

    tm = {
        0: "Text",
        2: "Voice",
        4: "Category",
        5: "Announcement",
        13: "Stage",
        15: "Forum"
    }

    for c in sorted(r.json(), key=lambda x: x.get("position", 0)):
        ctype = c.get("type", "?")
        label = tm.get(ctype, f"T{ctype}")
        line = f"    [{label:12}] #{c.get('name', '?')} — {c.get('id', '?')}"
        grad_print(line, DARK_RED, RED)
        log(line)

    save_log("channels")
 
def server_roles():
    gid=grad_input("  Server ID: ",DARK_RED,RED); token=grad_input("  Token: ",DARK_RED,RED)
    r=req("GET",f"https://discord.com/api/v9/guilds/{gid}/roles",headers=_dh(token))
    if not r or r.status_code!=200: error("Failed"); return
    for role in sorted(r.json(),key=lambda x:-x.get('position',0)):
        line=f"    {role.get('name','?'):<20} #{role.get('color',0):06X}  ID:{role.get('id','?')}"
        grad_print(line,DARK_RED,RED); log(line)
    save_log("roles")
 
def server_members():
    gid=grad_input("  Server ID: ",DARK_RED,RED); token=grad_input("  Token: ",DARK_RED,RED)
    limit=int(grad_input("  How many members [100]: ",DARK_RED,RED) or "100")
    r=req("GET",f"https://discord.com/api/v9/guilds/{gid}/members?limit={min(limit,1000)}",headers=_dh(token))
    if not r or r.status_code!=200: error(f"Failed: {r.status_code if r else 'no response'}"); return
    members=r.json(); info(f"Fetched {len(members)} members:")
    for m in members:
        u=m.get('user',{}); roles=m.get('roles',[])
        nick=m.get('nick') or u.get('username','?')
        line=f"    {nick:<24} {u.get('id','?')} roles:{len(roles)}"
        grad_print(line,DARK_RED,RED); log(line)
    save_log(f"members_{gid}")
 
def server_emojis():
    gid=grad_input("  Server ID: ",DARK_RED,RED); token=grad_input("  Token: ",DARK_RED,RED)
    r=req("GET",f"https://discord.com/api/v9/guilds/{gid}/emojis",headers=_dh(token))
    if not r or r.status_code!=200: error("Failed"); return
    for e in r.json():
        grad_print(f"    :{e['name']}: — https://cdn.discordapp.com/emojis/{e['id']}.{'gif' if e.get('animated') else 'png'}",DARK_RED,RED)
 
def server_stickers():
    gid=grad_input("  Server ID: ",DARK_RED,RED); token=grad_input("  Token: ",DARK_RED,RED)
    r=req("GET",f"https://discord.com/api/v9/guilds/{gid}/stickers",headers=_dh(token))
    if not r or r.status_code!=200: error("Failed"); return
    for s in r.json():
        grad_print(f"    {s.get('name','?')} — https://cdn.discordapp.com/stickers/{s['id']}.png",DARK_RED,RED)
 
def server_export():
    gid=grad_input("  Server ID: ",DARK_RED,RED); token=grad_input("  Token: ",DARK_RED,RED); h=_dh(token)
    loading_bar("Fetching server data",1.5,DARK_RED,RED); data={}
    r=req("GET",f"https://discord.com/api/v9/guilds/{gid}?with_counts=true",headers=h)
    if not r or r.status_code!=200: error("Failed"); return
    data["guild"]=r.json()
    for endpoint,key in [("channels","channels"),("roles","roles"),("emojis","emojis"),("stickers","stickers")]:
        rr=req("GET",f"https://discord.com/api/v9/guilds/{gid}/{endpoint}",headers=h)
        data[key]=rr.json() if rr and rr.status_code==200 else []
        spinner(f"Fetched {key}",0.3,DARK_RED,RED)
    fname=os.path.join(LOG_DIR,f"server_export_{gid}_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.json")
    with open(fname,"w",encoding="utf-8") as f: json.dump(data,f,indent=2,ensure_ascii=False)
    success(f"Exported → {fname}")
 
def server_read_messages():
    ch_id=grad_input("  Channel ID: ",DARK_RED,RED); token=grad_input("  Token: ",DARK_RED,RED)
    limit=int(grad_input("  How many messages [20]: ",DARK_RED,RED) or "20")
    r=req("GET",f"https://discord.com/api/v9/channels/{ch_id}/messages?limit={min(limit,100)}",headers=_dh(token))
    if not r or r.status_code!=200: error(f"Failed: {r.status_code if r else 'no response'}"); return
    msgs=r.json(); info(f"Last {len(msgs)} messages:"); print()
    for msg in reversed(msgs):
        author=f"{msg['author']['username']}#{msg['author'].get('discriminator','0')}"
        content=msg.get('content','[embed/attachment]')[:80]; ts=msg.get('timestamp','')[:10]
        line=f"  [{ts}] {author}: {content}"
        grad_print(line,DARK_RED,RED); log(line)
    save_log(f"messages_{ch_id}")
 
def server_search_messages():
    ch_id=grad_input("  Channel ID: ",DARK_RED,RED); token=grad_input("  Token: ",DARK_RED,RED)
    keyword=grad_input("  Keyword to search: ",DARK_RED,RED)
    r=req("GET",f"https://discord.com/api/v9/channels/{ch_id}/messages?limit=100",headers=_dh(token))
    if not r or r.status_code!=200: error("Failed"); return
    msgs=r.json(); results=[m for m in msgs if keyword.lower() in m.get('content','').lower()]
    info(f"Found {len(results)} messages containing '{keyword}':")
    for msg in results:
        author=f"{msg['author']['username']}#{msg['author'].get('discriminator','0')}"
        grad_print(f"    [{msg.get('timestamp','')[:10]}] {author}: {msg.get('content','')[:100]}",DARK_RED,RED)
 
def server_analytics():
    ch_id=grad_input("  Channel ID: ",DARK_RED,RED); token=grad_input("  Token: ",DARK_RED,RED)
    r=req("GET",f"https://discord.com/api/v9/channels/{ch_id}/messages?limit=100",headers=_dh(token))
    if not r or r.status_code!=200: error("Failed"); return
    msgs=r.json(); authors={}
    for msg in msgs:
        u=f"{msg['author']['username']}#{msg['author'].get('discriminator','0')}"
        authors[u]=authors.get(u,0)+1
    sorted_authors=sorted(authors.items(),key=lambda x:-x[1])
    info(f"Top {min(10,len(sorted_authors))} most active users (last 100 msgs):")
    for i,(author,count) in enumerate(sorted_authors[:10]):
        bar='█'*min(count,30); grad_print(f"    {i+1:2}. {author:<30} {bar} {count}",DARK_RED,RED)
 
def webhook_info():
    url=grad_input("  Webhook URL: ",DARK_RED,RED); r=req("GET",url)
    if not r or r.status_code!=200: error("Invalid"); return
    d=r.json()
    box_print([f"Name:{d.get('name','?')}",f"Channel:{d.get('channel_id','?')}",f"Guild:{d.get('guild_id','?')}"],DARK_RED,RED)
 
def webhook_send():
    url=grad_input("  URL: ",DARK_RED,RED); name=grad_input("  Username [blank=default]: ",DARK_RED,RED) or None
    msg=grad_input("  Message: ",DARK_RED,RED); data={"content":msg}
    if name: data["username"]=name
    r=req("POST",url,json=data)
    success("Sent") if r and r.status_code==204 else error(f"Failed: {r.status_code if r else 'no response'}")
 
def webhook_spam():
    url=grad_input("  URL: ",DARK_RED,RED); msg=grad_input("  Message: ",DARK_RED,RED)
    count=int(grad_input("  Count: ",DARK_RED,RED) or "10"); delay_s=float(grad_input("  Delay [0.2]: ",DARK_RED,RED) or "0.2")
    sent=0
    for i in range(count):
        r=req("POST",url,json={"content":msg})
        if r and r.status_code==204: sent+=1
        sys.stdout.write(f"\r  {rgb(*DARK_RED)}Sent {sent}/{count}{RESET}"); sys.stdout.flush()
        if delay_s>0: time.sleep(delay_s)
    print(); success(f"Done — {sent}/{count}")
 
def webhook_embed():
    url=grad_input("  URL: ",DARK_RED,RED); title=grad_input("  Title: ",DARK_RED,RED)
    desc=grad_input("  Description: ",DARK_RED,RED); color=grad_input("  Color hex [8000ff]: ",DARK_RED,RED) or "8000ff"
    foot=grad_input("  Footer [blank=none]: ",DARK_RED,RED) or None
    embed={"title":title,"description":desc,"color":int(color,16)}
    if foot: embed["footer"]={"text":foot}
    r=req("POST",url,json={"embeds":[embed]})
    success("Sent") if r and r.status_code==204 else error(f"Failed: {r.status_code if r else 'no response'}")
 
def webhook_delete():
    url=grad_input("  URL: ",DARK_RED,RED)
    if grad_input("  Type YES: ",DARK_RED,RED).upper()!="YES": info("Cancelled"); return
    r=req("DELETE",url)
    success("Deleted") if r and r.status_code==204 else error(f"Failed: {r.status_code if r else 'no response'}")
 
# ──────────────────────────────────────────────────────────────────────────────
#  PURGE MODULE
# ──────────────────────────────────────────────────────────────────────────────
def purge_own_messages():
    token=grad_input("  Token: ",DARK_RED,RED); ch_id=grad_input("  Channel ID: ",DARK_RED,RED)
    if not _validate_token(token): return
    h=_dh(token)
    me_r=req("GET","https://discord.com/api/v9/users/@me",headers=h)
    if not me_r or me_r.status_code!=200: error("Failed to get user info"); return
    my_id=me_r.json()['id']; deleted=0
    warn("This will delete your messages one by one. Type YES to confirm.")
    if grad_input("  Confirm: ",DARK_RED,RED).upper()!="YES": info("Cancelled"); return
    while True:
        r=req("GET",f"https://discord.com/api/v9/channels/{ch_id}/messages?limit=100",headers=h)
        if not r or r.status_code!=200: break
        msgs=[m for m in r.json() if m['author']['id']==my_id]
        if not msgs: break
        for msg in msgs:
            rr=req("DELETE",f"https://discord.com/api/v9/channels/{ch_id}/messages/{msg['id']}",headers=h)
            if rr and rr.status_code==204: deleted+=1
            sys.stdout.write(f"\r  {rgb(*DARK_RED)}Deleted {deleted} messages{RESET}"); sys.stdout.flush()
            time.sleep(0.7)  # avoid rate limits
    print(); success(f"Deleted {deleted} messages")
 
def purge_bulk_delete():
    token=grad_input("  Token (needs Manage Messages): ",DARK_RED,RED); ch_id=grad_input("  Channel ID: ",DARK_RED,RED)
    count=int(grad_input("  Messages to delete [100]: ",DARK_RED,RED) or "100")
    warn("Requires Manage Messages permission. Type YES to confirm.")
    if grad_input("  Confirm: ",DARK_RED,RED).upper()!="YES": info("Cancelled"); return
    h=_dh(token); deleted=0
    while deleted < count:
        r=req("GET",f"https://discord.com/api/v9/channels/{ch_id}/messages?limit=100",headers=h)
        if not r or r.status_code!=200: break
        msgs=r.json()
        if not msgs: break
        ids=[m['id'] for m in msgs[:min(100,count-deleted)]]
        if len(ids)==1:
            rr=req("DELETE",f"https://discord.com/api/v9/channels/{ch_id}/messages/{ids[0]}",headers=h)
            if rr and rr.status_code==204: deleted+=1
        else:
            rr=req("POST",f"https://discord.com/api/v9/channels/{ch_id}/messages/bulk-delete",headers=h,json={"messages":ids})
            if rr and rr.status_code==204: deleted+=len(ids)
        sys.stdout.write(f"\r  {rgb(*DARK_RED)}Deleted {deleted}/{count} messages{RESET}"); sys.stdout.flush()
        time.sleep(1.0)
    print(); success(f"Deleted {deleted} messages")
 
# ──────────────────────────────────────────────────────────────────────────────
#  INVITE MODULE
# ──────────────────────────────────────────────────────────────────────────────
def invite_create():
    token=grad_input("  Token: ",PURPLE,CYAN); ch_id=grad_input("  Channel ID: ",PURPLE,CYAN)
    max_age=int(grad_input("  Max age seconds [86400=1day, 0=forever]: ",PURPLE,CYAN) or "86400")
    max_uses=int(grad_input("  Max uses [0=unlimited]: ",PURPLE,CYAN) or "0")
    temp=grad_input("  Temporary? [y/n]: ",PURPLE,CYAN).lower()=="y"
    r=req("POST",f"https://discord.com/api/v9/channels/{ch_id}/invites",headers=_dh(token),
          json={"max_age":max_age,"max_uses":max_uses,"temporary":temp})
    if r and r.status_code==200: success(f"Created: https://discord.gg/{r.json().get('code','?')}")
    else: error(f"Failed: {r.status_code if r else 'no response'}")
 
def invite_info():
    code=grad_input("  Invite code: ",PURPLE,CYAN); code=code.split("/")[-1].strip()
    r=req("GET",f"https://discord.com/api/v9/invites/{code}?with_counts=true")
    if not r or r.status_code!=200: error("Invalid"); return
    d=r.json()
    box_print([
        f"Server  : {d['guild']['name']}",
        f"Channel : #{d['channel']['name']}",
        f"Uses    : {d.get('uses',0)} / {d.get('max_uses',0) or '∞'}",
        f"Inviter : {d.get('inviter',{}).get('username','Unknown')}",
        f"Expires : {d.get('expires_at','Never')}",
        f"Members : {d.get('approximate_member_count','?')}",
    ],PURPLE,CYAN)
 
def invite_list_server():
    token=grad_input("  Token: ",PURPLE,CYAN); gid=grad_input("  Server ID: ",PURPLE,CYAN)
    r=req("GET",f"https://discord.com/api/v9/guilds/{gid}/invites",headers=_dh(token))
    if not r or r.status_code!=200: error(f"Failed: {r.status_code if r else 'no response'}"); return
    invites=r.json(); info(f"Found {len(invites)} invites:")
    for inv in invites:
        code=inv.get('code','?'); uses=inv.get('uses',0); max_u=inv.get('max_uses',0) or '∞'
        inviter=inv.get('inviter',{}).get('username','?')
        line=f"    discord.gg/{code:<12} uses:{uses}/{max_u}  by:{inviter}"
        grad_print(line,PURPLE,CYAN); log(line)
    save_log("invites")
 
def invite_delete():
    token=grad_input("  Token: ",PURPLE,CYAN); code=grad_input("  Invite code: ",PURPLE,CYAN)
    code=code.split("/")[-1].strip()
    r=req("DELETE",f"https://discord.com/api/v9/invites/{code}",headers=_dh(token))
    success("Deleted") if r and r.status_code==200 else error(f"Failed: {r.status_code if r else 'no response'}")
 
# ──────────────────────────────────────────────────────────────────────────────
#  REACTION MODULE
# ──────────────────────────────────────────────────────────────────────────────
def reaction_add():
    token=grad_input("  Token: ",DARK_BLUE,MAGENTA); ch_id=grad_input("  Channel ID: ",DARK_BLUE,MAGENTA)
    msg_id=grad_input("  Message ID: ",DARK_BLUE,MAGENTA); emoji=grad_input("  Emoji (👍 or name:id): ",DARK_BLUE,MAGENTA)
    r=req("PUT",f"https://discord.com/api/v9/channels/{ch_id}/messages/{msg_id}/reactions/{quote(emoji)}/@me",headers=_dh(token))
    success("Reaction added") if r and r.status_code==204 else error(f"Failed: {r.status_code if r else 'no response'}")
 
def reaction_remove():
    token=grad_input("  Token: ",DARK_BLUE,MAGENTA); ch_id=grad_input("  Channel ID: ",DARK_BLUE,MAGENTA)
    msg_id=grad_input("  Message ID: ",DARK_BLUE,MAGENTA); emoji=grad_input("  Emoji: ",DARK_BLUE,MAGENTA)
    r=req("DELETE",f"https://discord.com/api/v9/channels/{ch_id}/messages/{msg_id}/reactions/{quote(emoji)}/@me",headers=_dh(token))
    success("Removed") if r and r.status_code==204 else error(f"Failed: {r.status_code if r else 'no response'}")
 
def reaction_list():
    token=grad_input("  Token: ",DARK_BLUE,MAGENTA); ch_id=grad_input("  Channel ID: ",DARK_BLUE,MAGENTA)
    msg_id=grad_input("  Message ID: ",DARK_BLUE,MAGENTA); emoji=grad_input("  Emoji: ",DARK_BLUE,MAGENTA)
    r=req("GET",f"https://discord.com/api/v9/channels/{ch_id}/messages/{msg_id}/reactions/{quote(emoji)}",headers=_dh(token))
    if not r or r.status_code!=200: error(f"Failed: {r.status_code if r else 'no response'}"); return
    users=r.json(); info(f"{len(users)} users reacted with {emoji}:")
    for u in users: grad_print(f"    {u.get('username','?')}#{u.get('discriminator','0')} — {u.get('id','?')}",DARK_BLUE,MAGENTA)
 
def reaction_mass():
    token=grad_input("  Token: ",DARK_BLUE,MAGENTA); ch_id=grad_input("  Channel ID: ",DARK_BLUE,MAGENTA)
    msg_id=grad_input("  Message ID: ",DARK_BLUE,MAGENTA)
    emojis_raw=grad_input("  Emojis (comma separated 👍,❤️,😂): ",DARK_BLUE,MAGENTA)
    emojis=[e.strip() for e in emojis_raw.split(",") if e.strip()]
    for emoji in emojis:
        r=req("PUT",f"https://discord.com/api/v9/channels/{ch_id}/messages/{msg_id}/reactions/{quote(emoji)}/@me",headers=_dh(token))
        success(f"Added {emoji}") if r and r.status_code==204 else error(f"Failed {emoji}")
        time.sleep(0.5)
 
# ──────────────────────────────────────────────────────────────────────────────
#  CRYPTO MODULE
# ──────────────────────────────────────────────────────────────────────────────
def crypto_eth():
    address=grad_input("  ETH Address (0x...): ",DARK_GREEN,GOLD)
    try:
        r=requests.get(f"https://api.blockcypher.com/v1/eth/main/addrs/{address}/balance",timeout=10)
        if r.status_code==200:
            d=r.json()
            box_print([f"Address:{address[:20]}...",f"Balance:{d.get('balance',0)/1e18:.6f} ETH",
                       f"Total Received:{d.get('total_received',0)/1e18:.6f} ETH",f"Tx Count:{d.get('n_tx',0)}"],DARK_GREEN,GOLD)
        else: error(f"Failed: {r.status_code}")
    except Exception as e: error(f"Error: {e}")
 
def crypto_btc():
    address=grad_input("  BTC Address: ",DARK_GREEN,GOLD)
    try:
        r=requests.get(f"https://api.blockcypher.com/v1/btc/main/addrs/{address}/balance",timeout=10)
        if r.status_code==200:
            d=r.json()
            box_print([f"Address:{address[:20]}...",f"Balance:{d.get('balance',0)/1e8:.8f} BTC",
                       f"Total:{d.get('total_received',0)/1e8:.8f} BTC",f"Txs:{d.get('n_tx',0)}"],DARK_GREEN,GOLD)
        else: error(f"Failed: {r.status_code}")
    except Exception as e: error(f"Error: {e}")
 
def crypto_price():
    coin=grad_input("  Coin (bitcoin, ethereum, etc): ",DARK_GREEN,GOLD).lower()
    try:
        r=requests.get(f"https://api.coingecko.com/api/v3/simple/price?ids={coin}&vs_currencies=usd,eur,gbp",timeout=10)
        if r.status_code==200:
            d=r.json().get(coin,{})
            if d: box_print([f"Coin:{coin.upper()}",f"USD:${d.get('usd','?')}",f"EUR:€{d.get('eur','?')}",f"GBP:£{d.get('gbp','?')}"],DARK_GREEN,GOLD)
            else: error("Coin not found")
        else: error(f"API error: {r.status_code}")
    except Exception as e: error(f"Error: {e}")
 
def crypto_tx():
    tx=grad_input("  TX Hash: ",DARK_GREEN,GOLD); chain=grad_input("  Chain [eth/btc]: ",DARK_GREEN,GOLD).lower() or "eth"
    endpoint={"eth":"eth/main","btc":"btc/main"}.get(chain,"eth/main")
    try:
        r=requests.get(f"https://api.blockcypher.com/v1/{endpoint}/txs/{tx}",timeout=10)
        if r.status_code==200:
            d=r.json()
            box_print([f"Hash:{d.get('hash','?')[:30]}...",f"Block:{d.get('block_height','unconfirmed')}",
                       f"Confirmations:{d.get('confirmations',0)}",f"Total:{d.get('total',0)/1e8:.8f}",
                       f"Fees:{d.get('fees',0)/1e8:.8f}"],DARK_GREEN,GOLD)
        else: error(f"Failed: {r.status_code}")
    except Exception as e: error(f"Error: {e}")
 
def crypto_wallet_history():
    address=grad_input("  ETH Address: ",DARK_GREEN,GOLD)
    try:
        r=requests.get(f"https://api.blockcypher.com/v1/eth/main/addrs/{address}",timeout=10)
        if r.status_code==200:
            txs=r.json().get('txrefs',[]); info(f"Last {min(10,len(txs))} txs:")
            for tx in txs[:10]:
                val=tx.get('value',0)/1e18; line=f"    {tx.get('tx_hash','?')[:20]}... {val:.4f} ETH"
                grad_print(line,DARK_GREEN,GOLD); log(line)
        else: error(f"Failed: {r.status_code}")
    except Exception as e: error(f"Error: {e}")
 
# ──────────────────────────────────────────────────────────────────────────────
#  WEB HACKING MODULE
# ──────────────────────────────────────────────────────────────────────────────
def webhack_headers():
    url=grad_input("  URL: ",DARK_RED,ORANGE)
    try:
        r=requests.get(url,timeout=8,allow_redirects=True,headers={"User-Agent":"Mozilla/5.0"})
        info(f"Status: {r.status_code}")
        security_headers={"Strict-Transport-Security":"HSTS","Content-Security-Policy":"CSP",
                          "X-Frame-Options":"Clickjacking","X-Content-Type-Options":"MIME sniff",
                          "X-XSS-Protection":"XSS","Referrer-Policy":"Referrer",
                          "Permissions-Policy":"Permissions","Access-Control-Allow-Origin":"CORS"}
        grad_print("  ┌─[ SECURITY HEADERS ]──────────────────────────────┐",DARK_RED,ORANGE)
        for header,label in security_headers.items():
            val=r.headers.get(header)
            if val: grad_print(f"  │  ✓ {label:<18} {str(val)[:40]:<40}│",GREEN,TEAL)
            else:   grad_print(f"  │  ✗ {label:<18} {'MISSING':<40}│",RED,DARK_RED)
        grad_print("  └────────────────────────────────────────────────────┘",DARK_RED,ORANGE)
        print(); grad_print("  All Headers:",DARK_RED,ORANGE)
        for k,v in r.headers.items(): grad_print(f"    {k}: {v[:60]}",DARK_RED,ORANGE)
        save_log(f"headers_{url[:20].replace('/','_')}")
    except Exception as e: error(f"Error: {e}")
 
def webhack_subdomain():
    domain=grad_input("  Domain: ",DARK_RED,ORANGE)
    wordlist=["www","mail","ftp","admin","api","dev","test","stage","app","blog","shop","cdn",
              "static","media","portal","vpn","smtp","pop","imap","ns1","ns2","mx","webmail",
              "remote","login","secure","dashboard","git","jenkins","jira","grafana","kibana"]
    info(f"Testing {len(wordlist)} subdomains...")
    found=[]
    def check(sub):
        host=f"{sub}.{domain}"
        try: ip=socket.gethostbyname(host); return host,ip
        except: return None,None
    with ThreadPoolExecutor(max_workers=20) as ex:
        for host,ip in ex.map(check,wordlist):
            if host: found.append(host); success(f"{host} → {ip}")
    info(f"Found {len(found)} subdomains"); save_log(f"subdomains_{domain}")
 
def webhack_dir_scan():
    url=grad_input("  Base URL: ",DARK_RED,ORANGE).rstrip("/")
    paths=["admin","login","dashboard","api","config","backup","test","dev","robots.txt","sitemap.xml",
           ".env","wp-admin","wp-login.php","phpmyadmin","index.php","admin.php","console","shell",
           "api/v1","api/v2","swagger","docs","health","status","metrics","debug",".htaccess",
           "backup.zip","db.sql","config.php","web.config","phpinfo.php","info.php","server-status"]
    info(f"Scanning {len(paths)} paths..."); found=[]
    status_colors={200:(GREEN,DARK_GREEN),301:(GOLD,ORANGE),302:(GOLD,ORANGE),401:(ORANGE,GOLD),403:(ORANGE,GOLD),500:(RED,DARK_RED)}
    def check(path):
        try:
            r=requests.get(f"{url}/{path}",timeout=5,allow_redirects=False,headers={"User-Agent":"Mozilla/5.0"})
            return path,r.status_code
        except: return path,None
    with ThreadPoolExecutor(max_workers=20) as ex:
        for path,code in ex.map(check,paths):
            if code and code!=404:
                found.append((path,code)); col=status_colors.get(code,(CYAN,WHITE))
                grad_print(f"    [{code}] /{path}",*col)
    info(f"Found {len(found)} interesting paths"); save_log(f"dirscan_{url[:20].replace('/','_')}")
 
def webhack_ssl():
    host=grad_input("  Host (no https://): ",DARK_RED,ORANGE)
    try:
        import ssl; ctx=ssl.create_default_context()
        with ctx.wrap_socket(socket.socket(),server_hostname=host) as s:
            s.settimeout(8); s.connect((host,443)); cert=s.getpeercert(); cipher=s.cipher()
        subject=dict(x[0] for x in cert['subject']); issuer=dict(x[0] for x in cert['issuer'])
        box_print([
            f"Subject    : {subject.get('commonName','?')}",
            f"Issuer     : {issuer.get('organizationName','?')}",
            f"Valid From : {cert.get('notBefore','?')}",
            f"Valid Until: {cert.get('notAfter','?')}",
            f"Cipher     : {cipher[0]}",
            f"TLS Version: {cipher[1]}",
        ],DARK_RED,ORANGE)
        sans=cert.get('subjectAltName',[])
        if sans: info(f"SANs ({len(sans)}):"); [grad_print(f"    {t}: {v}",DARK_RED,ORANGE) for t,v in sans[:10]]
    except Exception as e: error(f"Error: {e}")
 
def webhack_whois():
    domain=grad_input("  Domain: ",DARK_RED,ORANGE)
    result=subprocess.run(f"whois {domain}",shell=True,capture_output=True,text=True)
    for line in result.stdout.splitlines()[:50]: grad_print(f"  {line}",DARK_RED,ORANGE)
    save_log(f"whois_{domain}")
 
def webhack_port_scan():
    host=grad_input("  Host: ",DARK_RED,ORANGE)
    common_ports=[21,22,23,25,53,80,110,143,443,445,3306,3389,5432,5900,6379,8080,8443,27017]
    svc={21:"FTP",22:"SSH",23:"Telnet",25:"SMTP",53:"DNS",80:"HTTP",110:"POP3",143:"IMAP",
         443:"HTTPS",445:"SMB",3306:"MySQL",3389:"RDP",5432:"PostgreSQL",5900:"VNC",
         6379:"Redis",8080:"HTTP-Alt",8443:"HTTPS-Alt",27017:"MongoDB"}
    def scan(port):
        try: s=socket.socket(); s.settimeout(0.8); s.connect((host,port)); s.close(); return port
        except: return None
    with ThreadPoolExecutor(max_workers=30) as ex:
        for port in ex.map(scan,common_ports):
            if port: success(f"Port {port:5} OPEN  [{svc.get(port,'unknown')}]")
 
def webhack_tech_detect():
    url=grad_input("  URL: ",DARK_RED,ORANGE)
    try:
        r=requests.get(url,timeout=10,headers={"User-Agent":"Mozilla/5.0"})
        headers=r.headers; body=r.text[:8000].lower(); detected=[]
        srv=headers.get('Server',''); xpb=headers.get('X-Powered-By','')
        if srv: detected.append(f"Server      : {srv}")
        if xpb: detected.append(f"Powered-By  : {xpb}")
        if 'wp-content' in body or 'wp-json' in body: detected.append("CMS         : WordPress")
        if 'drupal' in body: detected.append("CMS         : Drupal")
        if 'joomla' in body: detected.append("CMS         : Joomla")
        if 'laravel' in body or 'csrf-token' in body: detected.append("Framework   : Laravel")
        if 'django' in body or 'csrfmiddlewaretoken' in body: detected.append("Framework   : Django")
        if '_next/static' in body: detected.append("Framework   : Next.js")
        if 'reactdom' in body or '__react' in body: detected.append("Frontend    : React")
        if 'angular' in body or 'ng-version' in body: detected.append("Frontend    : Angular")
        if 'vue' in body: detected.append("Frontend    : Vue.js")
        if any(h in headers for h in ['CF-RAY','CF-Cache-Status']): detected.append("CDN/WAF     : Cloudflare")
        if 'X-Sucuri-ID' in headers: detected.append("WAF         : Sucuri")
        if 'bootstrap' in body: detected.append("CSS         : Bootstrap")
        if 'jquery' in body: detected.append("JS          : jQuery")
        box_print([f"Target: {url}",""] + (detected or ["Nothing detected"]),DARK_RED,ORANGE)
    except Exception as e: error(f"Error: {e}")
 
def webhack_param_fuzzer():
    url=grad_input("  URL with FUZZ placeholder: ",DARK_RED,ORANGE)
    payloads=["<script>alert(1)</script>","'","\" OR 1=1--","../../../etc/passwd",
              "{{7*7}}","${7*7}","http://127.0.0.1/","http://169.254.169.254/",
              "<img src=x onerror=alert(1)>","<svg onload=alert(1)>","1; DROP TABLE users--",
              "1' AND SLEEP(5)--","file:///etc/passwd","%0d%0aHeader: injected"]
    if "FUZZ" not in url: error("URL must contain FUZZ"); return
    info(f"Fuzzing {len(payloads)} payloads..."); interesting=[]
    for i,payload in enumerate(payloads):
        test_url=url.replace("FUZZ",quote(payload))
        try:
            r=requests.get(test_url,timeout=6,headers={"User-Agent":"Mozilla/5.0"})
            reflected=payload.lower() in r.text.lower()
            sys.stdout.write(f"\r  [{i+1}/{len(payloads)}] {r.status_code} reflected={reflected} {payload[:30]:<30}")
            sys.stdout.flush()
            if reflected or r.status_code in (500,501,502,503): interesting.append((payload,r.status_code,reflected))
        except: pass
        time.sleep(0.1)
    print()
    if interesting:
        warn(f"Interesting findings ({len(interesting)}):")
        for payload,code,refl in interesting: grad_print(f"    [HTTP {code}] reflected={refl} → {payload[:80]}",ORANGE,GOLD)
    else: info("No interesting responses")
 
def webhack_cors():
    url=grad_input("  URL: ",DARK_RED,ORANGE)
    origins=["https://evil.com","null","https://attacker.com","http://localhost"]
    info(f"Testing CORS on {url}...")
    for origin in origins:
        try:
            r=requests.get(url,timeout=8,headers={"Origin":origin,"User-Agent":"Mozilla/5.0"})
            acao=r.headers.get("Access-Control-Allow-Origin",""); acac=r.headers.get("Access-Control-Allow-Credentials","")
            if acao:
                if acao=="*": warn(f"Wildcard CORS * (origin: {origin})")
                elif origin in acao: warn(f"Reflects origin: {origin} — credentials: {acac}")
                else: info(f"ACAO: {acao} (origin: {origin})")
            else: grad_print(f"  No ACAO header for {origin}",GREY,DARK_GREY) if GREY else None
        except Exception as e: error(f"Error ({origin}): {e}")
 
def webhack_waf_detect():
    url=grad_input("  URL: ",DARK_RED,ORANGE)
    payloads=["'","<script>","../","1 OR 1=1"]
    waf_signatures={"Cloudflare":["cloudflare","cf-ray"],"AWS WAF":["aws","x-amzn"],"ModSecurity":["mod_security","modsec"],"Sucuri":["sucuri","x-sucuri"],"Imperva":["imperva","incapsula"]}
    detected=set()
    for payload in payloads:
        try:
            r=requests.get(f"{url}?q={quote(payload)}",timeout=8,headers={"User-Agent":"Mozilla/5.0"})
            text=r.text.lower(); hdrs=str(r.headers).lower()
            for waf,sigs in waf_signatures.items():
                if any(s.lower() in text or s.lower() in hdrs for s in sigs): detected.add(waf)
        except: pass
        time.sleep(0.2)
    if detected:
        for waf in detected: warn(f"Possible WAF: {waf}")
    else: info("No WAF detected (or transparent)")
 
def webhack_http_methods():
    url=grad_input("  URL: ",DARK_RED,ORANGE)
    methods=["GET","POST","PUT","DELETE","PATCH","OPTIONS","HEAD","TRACE","CONNECT"]
    info(f"Testing HTTP methods on {url}...")
    for method in methods:
        try:
            r=requests.request(method,url,timeout=6,headers={"User-Agent":"Mozilla/5.0"})
            col=(GREEN,DARK_GREEN) if r.status_code in(200,201) else (ORANGE,GOLD) if r.status_code in(301,302,405) else (RED,DARK_RED)
            grad_print(f"    {method:<10} [{r.status_code}]",*col)
            if method=="TRACE" and "TRACE" in r.text: warn("TRACE enabled — XST vulnerability possible")
        except Exception as e: grad_print(f"    {method:<10} error",DARK_RED,RED)
        time.sleep(0.2)
 
# ──────────────────────────────────────────────────────────────────────────────
#  ACCOUNT MODULE
# ──────────────────────────────────────────────────────────────────────────────
def account_info():
    token=grad_input("  Token: ",PURPLE,WHITE); h=_dh(token)
    r=req("GET","https://discord.com/api/v9/users/@me",headers=h)
    if not r or r.status_code!=200: error("Invalid token"); return
    d=r.json()
    billing=req("GET","https://discord.com/api/v9/users/@me/billing/payment-sources",headers=h)
    has_billing=billing and billing.status_code==200 and len(billing.json())>0
    box_print([
        f"Username : {d['username']}#{d.get('discriminator','0')}",
        f"ID       : {d['id']}",
        f"Email    : {d.get('email','Hidden')}",
        f"Phone    : {d.get('phone','Hidden')}",
        f"MFA      : {d.get('mfa_enabled',False)}",
        f"Verified : {d.get('verified',False)}",
        f"Nitro    : {nitro_label(d.get('premium_type',0))}",
        f"Billing  : {'Yes ✓' if has_billing else 'No'}",
        f"Created  : {calc_account_age(d['id'])}",
    ],PURPLE,WHITE); save_log("account_info")
 
def account_friends():
    token=grad_input("  Token: ",PURPLE,WHITE)
    r=req("GET","https://discord.com/api/v9/users/@me/relationships",headers=_dh(token))
    if not r or r.status_code!=200: error("Invalid token"); return
    tm={1:"Friend",2:"Blocked",3:"Incoming",4:"Outgoing"}; friends=r.json()
    info(f"Found {len(friends)} relationships:")
    for f in friends:
        u=f.get('user',{}); t=tm.get(f.get('type',1),"?")
        line=f"    [{t:8}] {u.get('username','?')}#{u.get('discriminator','0')} — {u.get('id','?')}"
        grad_print(line,PURPLE,WHITE); log(line)
    save_log("friends")
 
def account_servers():
    token=grad_input("  Token: ",PURPLE,WHITE)
    r=req("GET","https://discord.com/api/v9/users/@me/guilds",headers=_dh(token))
    if not r or r.status_code!=200: error("Invalid token"); return
    guilds=r.json(); info(f"In {len(guilds)} servers:")
    for g in guilds:
        crown="👑" if g.get('owner') else "  "
        line=f"    {crown} {g.get('name','?'):<28} {g.get('id','?')}"
        grad_print(line,PURPLE,WHITE); log(line)
    save_log("servers")
 
def account_status():
    token=grad_input("  Token: ",PURPLE,WHITE)
    if not _validate_token(token): return
    info("online / idle / dnd / invisible")
    status=grad_input("  Status: ",PURPLE,WHITE).lower()
    if status not in ("online","idle","dnd","invisible"): error("Invalid"); return
    r=req("PATCH","https://discord.com/api/v9/users/@me/settings",headers=_dh(token),json={"status":status})
    success("Status updated") if r and r.status_code==200 else error(f"Failed: {r.status_code if r else 'no response'}")
 
def account_custom_status():
    token=grad_input("  Token: ",PURPLE,WHITE)
    if not _validate_token(token): return
    text=grad_input("  Status text: ",PURPLE,WHITE); emoji=grad_input("  Emoji [blank=none]: ",PURPLE,WHITE) or None
    data={"custom_status":{"text":text}}
    if emoji: data["custom_status"]["emoji_name"]=emoji
    r=req("PATCH","https://discord.com/api/v9/users/@me/settings",headers=_dh(token),json=data)
    success("Set") if r and r.status_code==200 else error(f"Failed: {r.status_code if r else 'no response'}")
 
def account_username():
    token=grad_input("  Token: ",PURPLE,WHITE)
    if not _validate_token(token): return
    name=grad_input("  New username: ",PURPLE,WHITE); pwd=grad_input("  Password: ",PURPLE,WHITE)
    r=req("PATCH","https://discord.com/api/v9/users/@me",headers=_dh(token),json={"username":name,"password":pwd})
    success("Changed") if r and r.status_code==200 else error(f"Failed: {r.json().get('message','?') if r else 'no response'}")
 
def account_bio():
    token=grad_input("  Token: ",PURPLE,WHITE)
    if not _validate_token(token): return
    bio=grad_input("  New bio: ",PURPLE,WHITE)
    r=req("PATCH","https://discord.com/api/v9/users/@me/profile",headers=_dh(token),json={"bio":bio})
    success("Updated") if r and r.status_code==200 else error(f"Failed: {r.status_code if r else 'no response'}")
 
def account_hypesquad():
    token=grad_input("  Token: ",PURPLE,WHITE)
    if not _validate_token(token): return
    info("1=Bravery  2=Brilliance  3=Balance"); h=grad_input("  Choice: ",PURPLE,WHITE)
    if h not in ("1","2","3"): error("Invalid"); return
    r=req("POST","https://discord.com/api/v9/hypesquad/online",headers=_dh(token),json={"house_id":int(h)})
    success("Changed") if r and r.status_code==204 else error(f"Failed: {r.status_code if r else 'no response'}")
 
def account_friend_add():
    token=grad_input("  Token: ",PURPLE,WHITE)
    if not _validate_token(token): return
    username=grad_input("  Username (without #): ",PURPLE,WHITE)
    r=req("POST","https://discord.com/api/v9/users/@me/relationships",headers=_dh(token),json={"username":username,"discriminator":None})
    success("Friend request sent") if r and r.status_code==204 else error(f"Failed: {r.status_code if r else 'no response'} — {r.text[:100] if r else ''}")
 
def account_block_user():
    token=grad_input("  Token: ",PURPLE,WHITE); uid=grad_input("  User ID to block: ",PURPLE,WHITE)
    r=req("PUT",f"https://discord.com/api/v9/users/@me/relationships/{uid}",headers=_dh(token),json={"type":2})
    success("User blocked") if r and r.status_code==204 else error(f"Failed: {r.status_code if r else 'no response'}")
 
def account_unblock_user():
    token=grad_input("  Token: ",PURPLE,WHITE); uid=grad_input("  User ID to unblock: ",PURPLE,WHITE)
    r=req("DELETE",f"https://discord.com/api/v9/users/@me/relationships/{uid}",headers=_dh(token))
    success("User unblocked") if r and r.status_code==204 else error(f"Failed: {r.status_code if r else 'no response'}")
 
def account_group_dm():
    token=grad_input("  Token: ",PURPLE,WHITE)
    if not _validate_token(token): return
    raw=grad_input("  User IDs (comma separated): ",PURPLE,WHITE)
    recipients=[uid.strip() for uid in raw.split(",") if uid.strip()]
    r=req("POST","https://discord.com/api/v9/users/@me/channels",headers=_dh(token),json={"recipients":recipients})
    if r and r.status_code==200:
        ch=r.json(); success(f"Group DM created — ID: {ch.get('id','?')}")
    else: error(f"Failed: {r.status_code if r else 'no response'}")
 
def account_mass_dm():
    token=grad_input("  Token: ",PURPLE,WHITE)
    if not _validate_token(token): return
    msg=grad_input("  Message: ",PURPLE,WHITE); delay_s=float(grad_input("  Delay [0.5]: ",PURPLE,WHITE) or "0.5")
    h=_dh(token); r=req("GET","https://discord.com/api/v9/users/@me/channels",headers=h)
    if not r or r.status_code!=200: error("Failed"); return
    channels=r.json(); sent=0
    for ch in channels:
        rr=req("POST",f"https://discord.com/api/v9/channels/{ch['id']}/messages",headers=h,json={"content":msg})
        if rr and rr.status_code==200: sent+=1
        sys.stdout.write(f"\r  {rgb(*PURPLE)}Sent {sent}/{len(channels)}{RESET}"); sys.stdout.flush()
        time.sleep(delay_s)
    print(); success(f"Sent to {sent}/{len(channels)}")
 
def account_leave_all():
    token=grad_input("  Token: ",PURPLE,WHITE)
    if not _validate_token(token): return
    if grad_input("  Type YES to leave ALL: ",PURPLE,WHITE).upper()!="YES": info("Cancelled"); return
    h=_dh(token); r=req("GET","https://discord.com/api/v9/users/@me/guilds",headers=h)
    if not r or r.status_code!=200: error("Failed"); return
    guilds=r.json(); left=0
    for g in guilds:
        rr=req("DELETE",f"https://discord.com/api/v9/users/@me/guilds/{g['id']}",headers=h)
        if rr and rr.status_code==204: left+=1
        sys.stdout.write(f"\r  {rgb(*PURPLE)}Left {left}/{len(guilds)}{RESET}"); sys.stdout.flush(); time.sleep(0.35)
    print(); success(f"Left {left} servers")
 
def account_remove_friends():
    token=grad_input("  Token: ",PURPLE,WHITE)
    if not _validate_token(token): return
    if grad_input("  Type YES to remove ALL: ",PURPLE,WHITE).upper()!="YES": info("Cancelled"); return
    h=_dh(token); r=req("GET","https://discord.com/api/v9/users/@me/relationships",headers=h)
    if not r or r.status_code!=200: error("Failed"); return
    friends=[f for f in r.json() if f.get('type')==1]; removed=0
    for f in friends:
        rr=req("DELETE",f"https://discord.com/api/v9/users/@me/relationships/{f['id']}",headers=h)
        if rr and rr.status_code in(200,204): removed+=1
        sys.stdout.write(f"\r  {rgb(*PURPLE)}Removed {removed}/{len(friends)}{RESET}"); sys.stdout.flush(); time.sleep(0.35)
    print(); success(f"Removed {removed} friends")
 
def account_dm_history():
    token=grad_input("  Token: ",PURPLE,WHITE); h=_dh(token)
    r=req("GET","https://discord.com/api/v9/users/@me/channels",headers=h)
    if not r or r.status_code!=200: error("Failed"); return
    for ch in r.json():
        recips=ch.get('recipients',[{}]); name=recips[0].get('username','?') if recips else 'Group DM'
        line=f"    {name:<24} — channel {ch.get('id','?')}"
        grad_print(line,PURPLE,WHITE); log(line)
    save_log("dm_history")
 
# ──────────────────────────────────────────────────────────────────────────────
#  NETWORK MODULE
# ──────────────────────────────────────────────────────────────────────────────
def net_ip():
    ip=grad_input("  IP: ",DARK_GREEN,GREEN); r=req("GET",f"http://ip-api.com/json/{ip}?fields=66846719")
    if not r or r.status_code!=200: error("API error"); return
    d=r.json()
    if d.get('status')!='success': error("Lookup failed"); return
    box_print([f"IP:{d.get('query','?')}",f"Country:{d.get('country','?')} ({d.get('countryCode','?')})",
               f"City:{d.get('city','?')}",f"ISP:{d.get('isp','?')}",f"Org:{d.get('org','?')}",
               f"Timezone:{d.get('timezone','?')}",f"Proxy/VPN:{d.get('proxy',False)}",f"Hosting:{d.get('hosting',False)}"],DARK_GREEN,GREEN)
    info(f"Maps: https://maps.google.com/?q={d['lat']},{d['lon']}"); save_log(f"ip_{ip.replace('.','_')}")
 
def net_myip():
    r=req("GET","http://ip-api.com/json/?fields=66846719")
    if not r: error("Failed"); return
    d=r.json()
    box_print([f"Your IP:{d.get('query','?')}",f"Country:{d.get('country','?')}",f"City:{d.get('city','?')}",
               f"ISP:{d.get('isp','?')}",f"VPN:{d.get('proxy',False)}"],DARK_GREEN,GREEN)
 
def net_ports():
    host=grad_input("  Host: ",DARK_GREEN,GREEN); ports=grad_input("  Ports (80,443 or 1-1000): ",DARK_GREEN,GREEN)
    if '-' in ports:
        s,e=map(int,ports.split('-')); port_list=list(range(s,e+1))
    else: port_list=[int(p.strip()) for p in ports.split(',') if p.strip()]
    svc={21:"FTP",22:"SSH",23:"Telnet",25:"SMTP",53:"DNS",80:"HTTP",443:"HTTPS",3306:"MySQL",3389:"RDP"}
    open_p=[]
    def scan(port):
        try: s=socket.socket(); s.settimeout(0.5); s.connect((host,port)); s.close(); return port
        except: return None
    with ThreadPoolExecutor(max_workers=100) as ex:
        for p in ex.map(scan,port_list):
            if p: open_p.append(p); success(f"Port {p:5} OPEN  [{svc.get(p,'unknown')}]")
    info(f"Open: {open_p}" if open_p else "No open ports")
 
def net_ping():
    host=grad_input("  Host: ",DARK_GREEN,GREEN)
    cmd=f"ping -n 4 {host}" if os.name=='nt' else f"ping -c 4 {host}"
    result=subprocess.run(cmd,shell=True,capture_output=True,text=True)
    for line in result.stdout.splitlines(): grad_print(f"  {line}",DARK_GREEN,GREEN)
 
def net_trace():
    host=grad_input("  Host: ",DARK_GREEN,GREEN)
    cmd=f"tracert {host}" if os.name=='nt' else f"traceroute {host}"
    result=subprocess.run(cmd,shell=True,capture_output=True,text=True)
    for line in result.stdout.splitlines()[:30]: grad_print(f"  {line}",DARK_GREEN,GREEN)
 
def net_dns():
    domain=grad_input("  Domain: ",DARK_GREEN,GREEN)
    try:
        ip=socket.gethostbyname(domain); info(f"A: {domain} → {ip}")
        try: info(f"Reverse: {socket.gethostbyaddr(ip)[0]}")
        except: pass
    except Exception as e: error(f"Error: {e}")
 
def net_whois():
    domain=grad_input("  Domain: ",DARK_GREEN,GREEN)
    result=subprocess.run(f"whois {domain}",shell=True,capture_output=True,text=True)
    for line in result.stdout.splitlines()[:40]: grad_print(f"  {line}",DARK_GREEN,GREEN)
 
def net_sweep():
    net=grad_input("  Network (e.g. 192.168.1): ",DARK_GREEN,GREEN); info(f"Sweeping {net}.1-254...")
    active=[]
    def ping(i):
        h=f"{net}.{i}"; cmd=f"ping -n 1 -w 200 {h} > nul 2>&1" if os.name=='nt' else f"ping -c 1 -W 1 {h} > /dev/null 2>&1"
        return h if os.system(cmd)==0 else None
    with ThreadPoolExecutor(max_workers=50) as ex:
        for h in ex.map(ping,range(1,255)):
            if h: active.append(h); success(f"{h} online")
    info(f"Found {len(active)} active hosts"); save_log("sweep")
 
def net_http_headers():
    url=grad_input("  URL: ",DARK_GREEN,GREEN)
    try:
        r=requests.head(url,timeout=8,allow_redirects=True,headers={"User-Agent":"Mozilla/5.0"})
        info(f"Status: {r.status_code}"); info(f"Final URL: {r.url}")
        for k,v in r.headers.items(): grad_print(f"    {k}: {v[:60]}",DARK_GREEN,GREEN)
    except Exception as e: error(f"Error: {e}")
 
def net_service_fingerprint():
    host=grad_input("  Host: ",DARK_GREEN,GREEN); port=int(grad_input("  Port: ",DARK_GREEN,GREEN) or "80")
    try:
        s=socket.socket(); s.settimeout(5); s.connect((host,port))
        if port in (80,8080,443): s.send(b"HEAD / HTTP/1.0\r\nHost: "+host.encode()+b"\r\n\r\n")
        else: s.send(b"\r\n")
        data=s.recv(512); banner=data.decode('utf-8',errors='replace').strip(); s.close()
        for line in banner.splitlines()[:15]: grad_print(f"  {line}",DARK_GREEN,GREEN)
    except Exception as e: error(f"Error: {e}")
 
# ──────────────────────────────────────────────────────────────────────────────
#  MULTI TOKEN
# ──────────────────────────────────────────────────────────────────────────────
def multi_load():
    path=grad_input("  Tokens file: ",DARK_BLUE,CYAN)
    try:
        with open(path) as f: tokens=[l.strip() for l in f if l.strip()]
        CONFIG["tokens"]=tokens; success(f"Loaded {len(tokens)} tokens")
    except Exception as e: error(f"Error: {e}")
 
def multi_check():
    if not CONFIG["tokens"]: error("No tokens loaded"); return
    valid=[]; invalid=[]
    for i,token in enumerate(CONFIG["tokens"]):
        r=req("GET","https://discord.com/api/v9/users/@me",headers=_dh(token))
        if r and r.status_code==200:
            d=r.json(); valid.append(token)
            success(f"[{i+1}] {d['username']}#{d.get('discriminator','0')} | {nitro_label(d.get('premium_type',0))}")
        else: invalid.append(token); error(f"[{i+1}] Invalid")
        time.sleep(CONFIG["request_delay"])
    info(f"Valid: {len(valid)} | Invalid: {len(invalid)}")
    if valid:
        fname=os.path.join(LOG_DIR,f"valid_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.txt")
        with open(fname,"w") as f: f.write("\n".join(valid))
        success(f"Saved → {fname}")
 
def multi_info():
    if not CONFIG["tokens"]: error("No tokens"); return
    for i,t in enumerate(CONFIG["tokens"]):
        r=req("GET","https://discord.com/api/v9/users/@me",headers=_dh(t))
        if r and r.status_code==200:
            d=r.json(); info(f"[{i+1}] {d['username']}#{d.get('discriminator','0')} | {d['id']} | {nitro_label(d.get('premium_type',0))}")
        else: error(f"[{i+1}] Invalid")
        time.sleep(CONFIG["request_delay"])
    save_log("multi_info")
 
def multi_mass_status():
    if not CONFIG["tokens"]: error("No tokens"); return
    info("online/idle/dnd/invisible"); status=grad_input("  Status: ",DARK_BLUE,CYAN).lower()
    if status not in ("online","idle","dnd","invisible"): error("Invalid"); return
    done=0
    for t in CONFIG["tokens"]:
        r=req("PATCH","https://discord.com/api/v9/users/@me/settings",headers=_dh(t),json={"status":status})
        if r and r.status_code==200: done+=1
        time.sleep(CONFIG["request_delay"])
    success(f"Done on {done}/{len(CONFIG['tokens'])}")
 
def multi_mass_custom_status():
    if not CONFIG["tokens"]: error("No tokens"); return
    text=grad_input("  Status text: ",DARK_BLUE,CYAN); emoji=grad_input("  Emoji [blank=none]: ",DARK_BLUE,CYAN) or None
    done=0
    for t in CONFIG["tokens"]:
        data={"custom_status":{"text":text}}
        if emoji: data["custom_status"]["emoji_name"]=emoji
        r=req("PATCH","https://discord.com/api/v9/users/@me/settings",headers=_dh(t),json=data)
        if r and r.status_code==200: done+=1
        time.sleep(CONFIG["request_delay"])
    success(f"Done on {done}/{len(CONFIG['tokens'])}")
 
def multi_mass_bio():
    if not CONFIG["tokens"]: error("No tokens"); return
    bio=grad_input("  Bio: ",DARK_BLUE,CYAN); done=0
    for t in CONFIG["tokens"]:
        r=req("PATCH","https://discord.com/api/v9/users/@me/profile",headers=_dh(t),json={"bio":bio})
        if r and r.status_code==200: done+=1
        time.sleep(CONFIG["request_delay"])
    success(f"Done on {done}/{len(CONFIG['tokens'])}")
 
def multi_mass_remove_friends():
    if not CONFIG["tokens"]: error("No tokens"); return
    if grad_input("  Type YES to remove ALL friends on ALL tokens: ",DARK_BLUE,CYAN).upper()!="YES": info("Cancelled"); return
    for i,t in enumerate(CONFIG["tokens"]):
        r=req("GET","https://discord.com/api/v9/users/@me/relationships",headers=_dh(t))
        if not r or r.status_code!=200: continue
        friends=[f for f in r.json() if f.get('type')==1]
        for f in friends:
            req("DELETE",f"https://discord.com/api/v9/users/@me/relationships/{f['id']}",headers=_dh(t))
            time.sleep(0.35)
        success(f"[{i+1}] Removed {len(friends)} friends")
 
def multi_export_info():
    if not CONFIG["tokens"]: error("No tokens"); return
    fname=os.path.join(LOG_DIR,f"multi_export_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.txt")
    results=[]
    for i,t in enumerate(CONFIG["tokens"]):
        r=req("GET","https://discord.com/api/v9/users/@me",headers=_dh(t))
        if r and r.status_code==200:
            d=r.json()
            line=f"{d['username']}#{d.get('discriminator','0')} | {d['id']} | {nitro_label(d.get('premium_type',0))} | {t}"
            results.append(line); success(f"[{i+1}] {line[:60]}")
        else: results.append(f"INVALID | {t}"); error(f"[{i+1}] Invalid")
        time.sleep(CONFIG["request_delay"])
    with open(fname,"w") as f: f.write("\n".join(results))
    success(f"Exported {len(results)} tokens → {fname}")
 
def multi_clear():
    CONFIG["tokens"]=[]; success("Cleared")
 
# ──────────────────────────────────────────────────────────────────────────────
#  MISC MODULE
# ──────────────────────────────────────────────────────────────────────────────
def misc_nitro():
    code=grad_input("  Code: ",PURPLE,MAGENTA)
    r=req("GET",f"https://discord.com/api/v9/entitlements/gift-codes/{code}?with_subscription_plan=true")
    if r and r.status_code==200: success(f"VALID — {r.json().get('subscription_plan',{}).get('name','?')}")
    else: error(f"Invalid — {r.status_code if r else 'no response'}")
 
def misc_mass_nitro():
    path=grad_input("  File path: ",PURPLE,MAGENTA)
    try:
        with open(path) as f: codes=[l.strip() for l in f if l.strip()]
        valid=[]
        for i,code in enumerate(codes):
            r=req("GET",f"https://discord.com/api/v9/entitlements/gift-codes/{code}")
            if r and r.status_code==200: success(f"[{i+1}] VALID — {code}"); valid.append(code)
            else: error(f"[{i+1}] invalid")
            time.sleep(0.3)
        info(f"Valid: {len(valid)}/{len(codes)}")
        if valid:
            fname=os.path.join(LOG_DIR,f"nitro_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.txt")
            with open(fname,"w") as f: f.write("\n".join(valid))
            success(f"Saved → {fname}")
    except Exception as e: error(f"Error: {e}")
 
def misc_dm():
    token=grad_input("  Token: ",PURPLE,MAGENTA); uid=grad_input("  User ID: ",PURPLE,MAGENTA); h=_dh(token)
    r=req("POST","https://discord.com/api/v9/users/@me/channels",headers=h,json={"recipient_id":uid})
    if not r or r.status_code!=200: error(f"Failed: {r.status_code if r else 'no response'}"); return
    ch=r.json().get('id'); success(f"DM opened — {ch}")
    msg=grad_input("  Message [blank=skip]: ",PURPLE,MAGENTA)
    if msg:
        rr=req("POST",f"https://discord.com/api/v9/channels/{ch}/messages",headers=h,json={"content":msg})
        success("Sent") if rr and rr.status_code==200 else error("Failed")
 
def misc_snowflake():
    sf=grad_input("  Snowflake: ",PURPLE,MAGENTA)
    try:
        ts=((int(sf)>>22)+1420070400000)/1000; dt=datetime.datetime.fromtimestamp(ts)
        box_print([f"Created:{dt.strftime('%Y-%m-%d %H:%M:%S')}",f"Unix:{int(ts)}",f"Age:{calc_account_age(sf)}"],PURPLE,MAGENTA)
    except Exception as e: error(f"Error: {e}")
 
def misc_token_decode():
    token=grad_input("  Token: ",PURPLE,MAGENTA)
    try:
        decoded=base64.b64decode(token.split('.')[0]+'==').decode('utf-8',errors='ignore')
        info(f"User ID: {decoded}"); info(f"Created: {calc_account_age(decoded)}")
    except Exception as e: error(f"Error: {e}")
 
def misc_token_age():
    token=grad_input("  Token: ",PURPLE,MAGENTA)
    try:
        uid=base64.b64decode(token.split('.')[0]+'==').decode('utf-8',errors='ignore')
        ts=((int(uid)>>22)+1420070400000)/1000; dt=datetime.datetime.fromtimestamp(ts)
        days=(datetime.datetime.now()-dt).days
        box_print([f"User ID  : {uid}",f"Created  : {dt.strftime('%Y-%m-%d %H:%M:%S')}",
                   f"Age      : {days} days ({days//365}y {(days%365)//30}m)"],PURPLE,MAGENTA)
    except Exception as e: error(f"Error: {e}")
 
def misc_cdn_download():
    url=grad_input("  Discord CDN URL: ",PURPLE,MAGENTA)
    if "cdn.discordapp.com" not in url and "media.discordapp.net" not in url:
        warn("URL doesn't look like a Discord CDN link, continuing anyway...")
    try:
        r=requests.get(url,timeout=15); fname=url.split("/")[-1].split("?")[0] or "download"
        with open(fname,'wb') as f: f.write(r.content)
        success(f"Downloaded {len(r.content)} bytes → {fname}")
    except Exception as e: error(f"Error: {e}")
 
# ──────────────────────────────────────────────────────────────────────────────
#  SETTINGS MODULE
# ──────────────────────────────────────────────────────────────────────────────
def settings_proxy():
    info(f"Current: {CONFIG['proxy'] or 'None'}")
    val=grad_input("  Proxy [blank=disable]: ",BLUE,WHITE)
    CONFIG["proxy"]=val.strip() or None; success(f"Proxy: {CONFIG['proxy'] or 'disabled'}")
 
def settings_log():
    CONFIG["log_enabled"]=not CONFIG["log_enabled"]
    success(f"Logging {'enabled' if CONFIG['log_enabled'] else 'disabled'}")
 
def settings_retry():
    val=grad_input(f"  Retry count [{CONFIG['retry_count']}]: ",BLUE,WHITE)
    try: CONFIG["retry_count"]=int(val); success(f"Set to {CONFIG['retry_count']}")
    except: error("Invalid")
 
def settings_delay():
    val=grad_input(f"  Request delay seconds [{CONFIG['request_delay']}]: ",BLUE,WHITE)
    try: CONFIG["request_delay"]=float(val); success(f"Set to {CONFIG['request_delay']}s")
    except: error("Invalid")
 
def settings_theme():
    info("Themes: blue / red / green / purple")
    t=grad_input("  Theme: ",BLUE,WHITE).lower()
    if t in THEME_COLORS:
        CONFIG["theme"]=t; THEME["main"]=THEME_COLORS[t]
        success(f"Theme set to {t} — restart for full effect")
    else: error("Invalid theme")
 
def settings_save_session():
    save_session()
 
def settings_about():
    clear(); print_header("settings")
    s,e=INPUT_GRAD["settings"]
    for line in [f"  {TITLE}  {VERSION}","",
                 "  built this for fun, tired of tools that are",
                 "  broken or locked behind sketchy paywalls.",
                 "  this one just works.","",
                 "  osint / server / account / network / purge",
                 "  crypto / webhack / invite / reaction",
                 "  multi-token / misc","",
                 "  logs auto-saved to ./logs/",
                 "  proxy + retry + delay built in",
                 "  session saves between runs","",
                 f"  — {HANDLE}"]:
        grad_type(line,s,e,delay=0.007)
    print()
 
# ──────────────────────────────────────────────────────────────────────────────
#  SCREENS
# ──────────────────────────────────────────────────────────────────────────────
def _run(fns, choice, theme):
    if choice in fns:
        print(); fns[choice](); wait_enter(theme)
 
def screen_osint():
    while True:
        print_menu("OSINT TOOLS",[
            ("1","Self Lookup"),         ("2","User by ID"),
            ("3","Server Info"),         ("4","Invite Resolver"),
            ("5","Avatar Grabber"),      ("6","Banner Grabber"),
            ("7","Badge Checker"),       ("8","Token Validator"),
            ("9","Username Search"),     ("10","Token Decoder"),
            ("11","Snowflake Info"),     ("12","Phone OSINT"),
            ("13","Domain OSINT"),       ("14","Email Permutations"),
            ("15","Breach Links"),       ("16","IP Reputation"),
            ("17","Vanity URL Checker"), ("0","Back"),
        ],"osint","Discord intelligence & recon")
        c=grad_input("  >> ",*INPUT_GRAD["osint"])
        if c=="0": break
        _run({"1":osint_self,"2":osint_user_id,"3":osint_server,"4":osint_invite,
              "5":osint_avatar,"6":osint_banner,"7":osint_badges,"8":osint_token_check,
              "9":osint_username_search,"10":osint_token_decode,"11":osint_snowflake,
              "12":osint_phone,"13":osint_domain,"14":osint_email_permutations,
              "15":osint_breach_links,"16":osint_ip_reputation,"17":osint_vanity_check},c,"osint")
 
def screen_server():
    while True:
        print_menu("SERVER TOOLS",[
            ("1","Channel List"),      ("2","Role List"),
            ("3","Member List"),       ("4","Emoji List"),
            ("5","Sticker List"),      ("6","Read Messages"),
            ("7","Search Messages"),   ("8","Server Analytics"),
            ("9","Server Export"),     ("10","Webhook Info"),
            ("11","Webhook Send"),     ("12","Webhook Spam"),
            ("13","Webhook Embed"),    ("14","Webhook Delete"),
            ("0","Back"),
        ],"server","Server management & tools")
        c=grad_input("  >> ",*INPUT_GRAD["server"])
        if c=="0": break
        _run({"1":server_channels,"2":server_roles,"3":server_members,"4":server_emojis,
              "5":server_stickers,"6":server_read_messages,"7":server_search_messages,
              "8":server_analytics,"9":server_export,"10":webhook_info,"11":webhook_send,
              "12":webhook_spam,"13":webhook_embed,"14":webhook_delete},c,"server")
 
def screen_account():
    while True:
        print_menu("ACCOUNT TOOLS",[
            ("1","Token Info"),          ("2","Friend List"),
            ("3","Server List"),         ("4","DM History"),
            ("5","Change Status"),       ("6","Custom Status"),
            ("7","Change Username"),     ("8","Change Bio"),
            ("9","HypeSquad"),           ("10","Add Friend"),
            ("11","Block User"),         ("12","Unblock User"),
            ("13","Create Group DM"),    ("14","Mass DM"),
            ("15","Leave All Servers"),  ("16","Remove All Friends"),
            ("0","Back"),
        ],"account","Account management tools")
        c=grad_input("  >> ",*INPUT_GRAD["account"])
        if c=="0": break
        _run({"1":account_info,"2":account_friends,"3":account_servers,"4":account_dm_history,
              "5":account_status,"6":account_custom_status,"7":account_username,
              "8":account_bio,"9":account_hypesquad,"10":account_friend_add,
              "11":account_block_user,"12":account_unblock_user,"13":account_group_dm,
              "14":account_mass_dm,"15":account_leave_all,"16":account_remove_friends},c,"account")
 
def screen_network():
    while True:
        print_menu("NETWORK TOOLS",[
            ("1","IP Lookup"),           ("2","My IP"),
            ("3","Port Scanner"),        ("4","Ping"),
            ("5","Traceroute"),          ("6","DNS Lookup"),
            ("7","Whois"),               ("8","Ping Sweep"),
            ("9","HTTP Headers"),        ("10","Service Fingerprint"),
            ("0","Back"),
        ],"network","Network recon & diagnostics")
        c=grad_input("  >> ",*INPUT_GRAD["network"])
        if c=="0": break
        _run({"1":net_ip,"2":net_myip,"3":net_ports,"4":net_ping,"5":net_trace,
              "6":net_dns,"7":net_whois,"8":net_sweep,"9":net_http_headers,
              "10":net_service_fingerprint},c,"network")
 
def screen_purge():
    while True:
        print_menu("PURGE TOOLS",[
            ("1","Delete My Messages (safe, slow)"),
            ("2","Bulk Delete (Manage Messages perm)"),
            ("0","Back"),
        ],"purge","Message purging tools")
        c=grad_input("  >> ",*INPUT_GRAD["purge"])
        if c=="0": break
        _run({"1":purge_own_messages,"2":purge_bulk_delete},c,"purge")
 
def screen_crypto():
    while True:
        print_menu("CRYPTO TOOLS",[
            ("1","ETH Balance"),    ("2","BTC Balance"),
            ("3","TX Lookup"),      ("4","Coin Price"),
            ("5","Wallet History"), ("0","Back"),
        ],"crypto","Blockchain & crypto tools")
        c=grad_input("  >> ",*INPUT_GRAD["crypto"])
        if c=="0": break
        _run({"1":crypto_eth,"2":crypto_btc,"3":crypto_tx,"4":crypto_price,"5":crypto_wallet_history},c,"crypto")
 
def screen_webhack():
    while True:
        print_menu("WEB HACKING",[
            ("1","Security Headers Audit"),  ("2","Subdomain Finder"),
            ("3","Directory Scanner"),       ("4","SSL Certificate Info"),
            ("5","Whois Lookup"),            ("6","Port Scan (common)"),
            ("7","Tech Stack Detector"),     ("8","Parameter Fuzzer"),
            ("9","CORS Check"),              ("10","WAF Detector"),
            ("11","HTTP Method Tester"),     ("0","Back"),
        ],"webhack","Web recon & security tools")
        c=grad_input("  >> ",*INPUT_GRAD["webhack"])
        if c=="0": break
        _run({"1":webhack_headers,"2":webhack_subdomain,"3":webhack_dir_scan,"4":webhack_ssl,
              "5":webhack_whois,"6":webhack_port_scan,"7":webhack_tech_detect,
              "8":webhack_param_fuzzer,"9":webhack_cors,"10":webhack_waf_detect,
              "11":webhack_http_methods},c,"webhack")
 
def screen_invite():
    while True:
        print_menu("INVITE MANAGER",[
            ("1","Create Invite"),       ("2","Invite Info"),
            ("3","List Server Invites"), ("4","Delete Invite"),
            ("0","Back"),
        ],"invite","Invite link management")
        c=grad_input("  >> ",*INPUT_GRAD["invite"])
        if c=="0": break
        _run({"1":invite_create,"2":invite_info,"3":invite_list_server,"4":invite_delete},c,"invite")
 
def screen_reaction():
    while True:
        print_menu("REACTION TOOLS",[
            ("1","Add Reaction"),   ("2","Remove Reaction"),
            ("3","List Reactions"), ("4","Mass React"),
            ("0","Back"),
        ],"reaction","Message reaction tools")
        c=grad_input("  >> ",*INPUT_GRAD["reaction"])
        if c=="0": break
        _run({"1":reaction_add,"2":reaction_remove,"3":reaction_list,"4":reaction_mass},c,"reaction")
 
def screen_multi():
    while True:
        loaded=len(CONFIG["tokens"])
        print_menu("MULTI TOKEN",[
            ("1",f"Load Tokens File  [{loaded} loaded]"),
            ("2","Check All Tokens"),
            ("3","Info All Tokens"),
            ("4","Mass Status Change"),
            ("5","Mass Custom Status"),
            ("6","Mass Bio Change"),
            ("7","Mass Remove Friends"),
            ("8","Export All Info to File"),
            ("9","Clear Tokens"),
            ("0","Back"),
        ],"multi","Run operations across multiple tokens")
        c=grad_input("  >> ",*INPUT_GRAD["multi"])
        if c=="0": break
        _run({"1":multi_load,"2":multi_check,"3":multi_info,"4":multi_mass_status,
              "5":multi_mass_custom_status,"6":multi_mass_bio,"7":multi_mass_remove_friends,
              "8":multi_export_info,"9":multi_clear},c,"multi")
 
def screen_misc():
    while True:
        print_menu("MISC TOOLS",[
            ("1","Nitro Checker"),      ("2","Mass Nitro Checker"),
            ("3","Open DM + Send"),     ("4","Snowflake → Time"),
            ("5","Token Decoder"),      ("6","Token Age Calculator"),
            ("7","CDN Image Download"), ("0","Back"),
        ],"misc","Miscellaneous utilities")
        c=grad_input("  >> ",*INPUT_GRAD["misc"])
        if c=="0": break
        _run({"1":misc_nitro,"2":misc_mass_nitro,"3":misc_dm,"4":misc_snowflake,
              "5":misc_token_decode,"6":misc_token_age,"7":misc_cdn_download},c,"misc")
 
def screen_settings():
    while True:
        print_menu("SETTINGS",[
            ("1",f"Set Proxy              [{'ON' if CONFIG['proxy'] else 'OFF'}]"),
            ("2",f"Toggle Logging         [{'ON' if CONFIG['log_enabled'] else 'OFF'}]"),
            ("3",f"Set Retry Count        [{CONFIG['retry_count']}]"),
            ("4",f"Set Request Delay      [{CONFIG['request_delay']}s]"),
            ("5",f"Set Theme              [{CONFIG['theme']}]"),
            ("6","Save Session Config"),
            ("7","About"),
            ("8","Clear Console"),
            ("0","Back"),
        ],"settings")
        c=grad_input("  >> ",BLUE,WHITE)
        if c=="0": break
        elif c=="1": settings_proxy()
        elif c=="2": settings_log()
        elif c=="3": settings_retry()
        elif c=="4": settings_delay()
        elif c=="5": settings_theme()
        elif c=="6": settings_save_session()
        elif c=="7": settings_about(); wait_enter("settings")
        elif c=="8": clear(); print_header("settings")
 
# ──────────────────────────────────────────────────────────────────────────────
#  MAIN MENU
# ──────────────────────────────────────────────────────────────────────────────
def main_menu():
    while True:
        print_menu("MAIN MENU",[
            ("1","OSINT Tools"),
            ("2","Server Tools"),
            ("3","Account Tools"),
            ("4","Network Tools"),
            ("5","Purge Tools"),
            ("6","Crypto Tools"),
            ("7","Web Hacking"),
            ("8","Invite Manager"),
            ("9","Reaction Tools"),
            ("10","Multi Token"),
            ("11","Misc Tools"),
            ("12","Settings"),
            ("0","Exit"),
        ],"main")
        c=grad_input("  >> ",BLUE,CYAN)
        if   c=="1":  screen_osint()
        elif c=="2":  screen_server()
        elif c=="3":  screen_account()
        elif c=="4":  screen_network()
        elif c=="5":  screen_purge()
        elif c=="6":  screen_crypto()
        elif c=="7":  screen_webhack()
        elif c=="8":  screen_invite()
        elif c=="9":  screen_reaction()
        elif c=="10": screen_multi()
        elif c=="11": screen_misc()
        elif c=="12": screen_settings()
        elif c=="0":
            clear(); glitch_print(Center.XCenter("DISCONNECTING..."),CYAN,DARK_BLUE)
            time.sleep(0.3); grad_type(Center.XCenter("goodbye."),CYAN,DARK_BLUE,delay=0.05)
            print(); time.sleep(0.5); break
 
# ──────────────────────────────────────────────────────────────────────────────
GREY = (120, 120, 120); DARK_GREY = (40, 40, 40)
 
if __name__=="__main__":
    try: boot(); main_menu()
    except KeyboardInterrupt:
        clear(); grad_type(Center.XCenter("Interrupted."),BLUE,CYAN,delay=0.02); print()