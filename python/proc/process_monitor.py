#!/usr/local/bin/python3

import datetime
import os
import signal
import socket
import subprocess
import sys
import threading
import time
import traceback

from optparse import OptionParser
from http.server import BaseHTTPRequestHandler, HTTPServer
from queue import Empty, Queue
from socketserver import ThreadingMixIn

from lib.LogFile import LogFile
from lib.net import socketConnect, socketRecv, socketSend

#CLUSTER
LOCATION = "localhost"
PROC_MASTER = {}

#PARAMS
PYTHONPATH = os.environ['PYTHONPATH']
PYTHON = "/usr/loca/bin/python"

PROC_RETRY = 5
PROC_REFRESH = 5
PROC_POLL = 30
PROC_PORT = 9063
PROC_DIR = PYTHONPATH+'/proc'
PROC_LOGS = PROC_DIR+'/logs'
PROC_JOBS = PROC_DIR+"/jobs"
PROC_HTTP_PORT = 8000
PROC_LOG_STORAGE_DAYS = 45

#PYUTILS
def sendEmail(*args):
    pass

def iif(x, y = True, z = False):
    if x:
        return y
    else:
        return z

def ior(x, *y):
    if x:
        return x
    elif y:
        return ior(*y)
    else:
        return x

S_STATUSERROR = 0
S_WAITING = 1
S_RUNNING = 2
S_FAILED = 3
S_SUCCEEDED = 4
S_UNRUNNABLE = 5
S_CANCELED = 6
S_SUSPENDED = 7
S_BLOCKED = 8
S_MANUAL = 9
S_DETACHED = 10
S_ERROR = 11

STATUS_MAP = {
    S_STATUSERROR: "StatusError",
    S_WAITING: "Waiting",
    S_RUNNING: "Running",
    S_FAILED: "Failed",
    S_SUCCEEDED: "Succeeded",
    S_UNRUNNABLE: "Unrunnable",
    S_CANCELED: "Canceled",
    S_SUSPENDED: "Suspended",
    S_BLOCKED: "Blocked",
    S_MANUAL: "Manual",
    S_DETACHED: "Detached",
    S_ERROR: "Error"
}
LINK_COLORMAP = {
    S_CANCELED: "green",
    S_MANUAL: "green",
    S_BLOCKED: "red",
    S_SUSPENDED: "red",
    S_UNRUNNABLE: "red",
}

T_DEFAULT = 0
T_PROCLIST = 1
T_NEWHOST = 2
T_POLL = 3
T_LAUNCH = 4
T_RESTART = 5
T_KILL = 6
T_CANCEL = 7
T_SUSPEND = 8
T_INIT = 9
T_SIGNAL = 10
T_APPROVE = 11
T_SUSPEND_DEPS = 12

I_LOGO = "/prcm.png"
I_BLANK = "/blank.png"
I_CANCEL = "/cancel.png"
I_KILL = "/kill.png"
I_RESTART = "/restart.png"
I_SUSPEND = "/suspend.png"
I_LOG = "/log.png"
I_INVINCIBLE = "/invincible.png"
I_APPROVE = "/approve.png"

REFRESH_MS = 5000

class ThreadedHTTPServer(ThreadingMixIn, HTTPServer):
    pass

class ClientRequestHandler(BaseHTTPRequestHandler):
    def setup(self):
        BaseHTTPRequestHandler.setup(self)
        self.request.settimeout(60)

    def format_cell(self, s, stk = -1):
        if stk < 0:
            sts = ""
        else:
            sts = " class=\"%s\"" % STATUS_MAP[stk].lower()
        return "<td%s><tt class=\"atomic\">&nbsp;%s&nbsp;</tt></td>" % (sts, s)

    def bold(self, s):
        return "<b>%s</b>" % s

    def table(self, s):
        return "<table>%s</table>" % s

    def link(self, ln, s, st = ""):
        return "<a class=\"%s\" href=\"%s\">%s</a>" % (
            LINK_COLORMAP.get(st, "black"),
            ln,
            s
        )

    def image(self, alt, src):
        return "<img src=\"%s\" width=12 height=12 alt=\"%s\">" % (src, alt)

    def input(self, name, value, src):
        if self.js:
            return "<acronym title=\"%s\">" % name \
                + "<a href=\"javascript:postdata('%s.%s', %s);\">" % (
                    name,
                    value,
                    REFRESH_MS
                ) + "<img src=\"%s\" width=12 height=12 alt=\"%s\">" % (
                    src,
                    ("%s" % name)[:2]
                ) + "</img></a></acronym>"
        else:
            return "<acronym title=\"%s\"><input type=\"image\" " % name \
                + ("name=\"%s.%s\" width=12 height=12 src=\"%s\" "
                + "alt=\"%s\"></acronym>") % (
                name,
                value,
                src,
                ("%s" % name)[:2]
            )

    def format_entry(self, d):
        content = ""
        for (k, v) in sorted(d.items()):
            vv = v
            if k in ("Depends", "Required By"):
                vv = " ".join([self.link(x, x) for x in sorted(vv)])
            elif "Status" == k:
                vv = v[:]
                if S_RUNNING == vv[0]:
                    vv = "Running %s:%s" % tuple(vv[1:3])
                else:
                    vv = STATUS_MAP[vv[0]]
            content += "<tr>%s%s</tr>\n" % (
                self.format_cell(k),
                self.format_cell(vv)
            )
        return self.table(content)

    def format_process_list(self, allProcesses, allHosts, doneProcesses, js):
        t1 = ""
        nag = []
        for (proc, v) in sorted(allProcesses.items()):
            st = v.get("Status", [S_STATUSERROR])
            sa = v.get("StartAfter", "")
            data = iif(sa, "%s " % self.bold(sa), "")
            prefix = iif(
                st[0] in (S_RUNNING, S_FAILED, S_ERROR, S_SUCCEEDED),
                self.link(
                    "%s/%s.log" % (iif(js, "", "/ns"), proc),
                    self.image("lg", I_LOG)
                ),
                self.image("--", I_BLANK)
            )
            data = "%s&nbsp;%s" % (prefix, data)
            data += " ".join(sorted(v.get("Depends", set([])) - doneProcesses))
            try:
                if st[0] == S_RUNNING:
                    invincible = "Invincible" in allProcesses[proc] \
                        and allProcesses[proc]["Invincible"]
                    host = allProcesses[proc]["HostClass"]
                    status = "%s%s&nbsp;%s:%s" % (
                        iif(
                            host in allHosts and not invincible,
                            self.input("kill", proc, I_KILL),
                            self.image("--", I_BLANK)
                        ),
                        iif(
                            invincible,
                            self.image("in", I_INVINCIBLE),
                            iif(
                                host in allHosts,
                                self.input("restart", proc, I_RESTART),
                                self.image("--", I_BLANK)
                            )
                        ),
                        st[1],
                        st[2]
                    )
                elif st[0] == S_FAILED:
                    if v.get("Nag", 0):
                        nag.append(proc)
                    status = "%s%s&nbsp;%s" % (
                        self.input("cancel", proc, I_CANCEL),
                        self.input("restart", proc, I_RESTART),
                        STATUS_MAP[st[0]]
                    )
                elif st[0] == S_DETACHED:
                    if v.get("Nag", 0):
                        nag.append(proc)
                    status = "%s%s&nbsp;%s" % (
                        self.input("cancel", proc, I_CANCEL),
                        self.image("--", I_BLANK),
                        STATUS_MAP[st[0]]
                    )
                elif st[0] == S_SUCCEEDED:
                    status = "%s%s&nbsp;%s" % (
                        self.image("--", I_BLANK),
                        self.input("restart", proc, I_RESTART),
                        STATUS_MAP[st[0]]
                    )
                elif st[0] == S_CANCELED:
                    status = "%s%s&nbsp;%s" % (
                        self.image("--", I_BLANK),
                        self.input("suspend", proc, I_SUSPEND),
                        STATUS_MAP[st[0]]
                    )
                elif st[0] == S_SUSPENDED:
                    status = "%s%s&nbsp;%s" % (
                        self.input("cancel", proc, I_CANCEL),
                        self.input("restart", proc, I_RESTART),
                        STATUS_MAP[st[0]]
                    )
                elif st[0] == S_MANUAL:
                    status = "%s%s&nbsp;%s" % (
                        self.input("cancel", proc, I_CANCEL),
                        self.input("approve", proc, I_APPROVE),
                        STATUS_MAP[st[0]]
                    )
                elif st[0] in (S_WAITING, S_UNRUNNABLE, S_BLOCKED, S_ERROR):
                    status = "%s%s&nbsp;%s" % (
                        self.input("cancel", proc, I_CANCEL),
                        self.input("suspend", proc, I_SUSPEND),
                        STATUS_MAP[st[0]]
                    )
                else:
                    status = "%s%s&nbsp;%s" % (
                        self.image("--", I_BLANK),
                        self.image("--", I_BLANK),
                        STATUS_MAP[st[0]]
                    )
                if st[0] in (S_RUNNING, S_CANCELED, S_MANUAL):
                    data = "%s&nbsp;%s" % (
                        prefix,
                        str(list(reversed(st))[0].time())
                    )
                elif st[0] in (S_FAILED, S_SUCCEEDED, S_ERROR):
                    data = "%s&nbsp;%s" % (prefix, "&nbsp;".join([str(x.time()) for x in st[1:]]))
                elif S_DETACHED == st[0]:
                    data = "%s&nbsp;%s" % (prefix, "%s&nbsp;%s" % (
                        str(st[1].time()),
                        st[2]
                    ))
            except AttributeError as e:
                data = "STATUS FORMAT ERROR: " + e.__str__()
            t1 += "<tr>%s%s%s</tr>\n" % (
                self.format_cell(
                    self.link(
                        "%s/proc/%s" % (iif(js, "", "/ns"), proc),
                        proc,
                        st[0]
                    ),
                    st[0]
                ),
                self.format_cell(status, st[0]),
                self.format_cell(data, st[0])
            )
        return "%s\n%s%s" % (
            self.table(t1),
            iif(
                nag,
                "<!-- NAGIOS_STATUS_CRITICAL %s -->\n" % ",".join(nag),
                "<!-- NAGIOS_STATUS_OK -->\n"
            ),
            "<p><tt>registered hosts: %s</tt></p>" % \
                " ".join(sorted(allHosts.keys()))
        )

    def generate_header(self, title, ts, args={}):
        if "t" in args:
            del args["t"]
        header = """
<!doctype html public "-//W3C//DTD HTML 4.01//EN"
    "http://www.w3.org/TR/html4/strict.dtd">
<html>
<head>
<title>%(title)s</title>
<meta http-equiv="Content-Type" content="text/html; charset=utf-8">
<meta http-equiv="Content-Style-Type" content="text/css">
%(auto_meta)s<link rel="stylesheet" type="text/css" href="/style.css">
%(js)s</head>
%%s
</html>
"""[1:] % {
            "title"     : title,
            "js"        : iif(
                            self.js,
                            "<script type=\"text/javascript\" " \
                                + "src=\"/webutils.js\"></script>\n\n",
                            ""
                        ),
            "auto_meta" : iif(
                            self.js,
                            "",
                            "<meta http-equiv=\"refresh\" " \
                                + "content=\"%s;url=%s\">\n" \
                                % (PROC_REFRESH, self.path),
                        )
        }
        return header

    def generate_output(
        self,
        title,
        content,
        bottom,
        ts,
        link=False,
        internal=False,
        args={},
        refresh=False
    ):
        links = [self.link("%s/restart" % iif(self.js, "", "/ns"), "restart")]
        if not self.js:
            links.append(self.link("/ns/autorefresh", "autorefresh"))
        path = iif(
            args,
            "/internal/?"+"&".join(["=".join(x) for x in list(args.items())])+"&",
            "/internal/?"
        )
        body = iif(
            internal or not self.js or not refresh,
            """
<body>
<img src=\"%(logo)s\" />
<h1>%(title)s</h1>
<p><tt>current time: <b>%(time)s</b></tt></p>
<form action="" method="post">
%(content)s
</form>
%(auto_link)s
<p><tt>%(bottom)s</tt></p>
</body>
</html>
"""[1:] % {
            "logo"      : I_LOGO,
            "time"      : self.lg.localTime(),
            "title"     : title,
            "content"   : content,
            "bottom"    : bottom,
            "auto_link" : iif(
                            link,
                            "<p><tt>%s</tt></p>" % iif(
                                self.autorefresh and not self.js,
                                self.link("/ns/", "autorefresh stop"),
                                " ".join(links)
                            ),
                            ""
                        ),
            },
            "<body onload=\"javascript:init(%s);\">" % REFRESH_MS \
                + "<div id=\"internal\"></div></body>",
        )
        if internal and refresh:
            return body
        else:
            return self.generate_header(
                title,
                ts,
                args=args
            ) % body

    def process(self):
        data = ""
        url = self.path.split("?")
        path = url[0]
        internal = False
        self.js = True
        if path.startswith("/ns"):
            self.js = False
            path = path[3:]
        elif path.startswith("/internal"):
            internal = True
            path = path[9:]
        ts = datetime.datetime.now()
        homelink = iif(
            self.js,
            self.link("/", "home"),
            self.link("/ns/", "home")
        )
        if (
            path.endswith(".css") or
            path.endswith(".png") or
            path.endswith(".js")
        ):
            try:
                k = 'rb' if path.endswith('.png') else 'r'
                with open("%s%s" % (PROC_DIR, path), k) as f:
                    data = f.read()
                if path.endswith(".css"):
                    mtype = "text/css"
                if path.endswith(".js"):
                    mtype = "application/javascript"
                if path.endswith(".png"):
                    #self.send_header("ETag", "0-0-0-0")
                    mtype = "image/png"
                self.send_response(200)
                self.send_header("Content-type", mtype)
            except Exception as e:
                self.lg.warn(e)
                self.lg.warn(
                    "unexpected request: %s" % sys.exc_info()[0]
                )
                data = "404 File Not Found"
                self.send_response(404)
                self.send_header("Content-type", "text/plain")
        elif path.endswith(".log"):
            try:
                self.server.wq.put(
                    (T_PROCLIST, ""),
                    timeout=PROC_RETRY
                )
                (t, allProcesses, allHosts, doneProcesses) = (
                    self.server.rq.get(timeout=PROC_RETRY))
                proc = path[1:-4]
                host = allProcesses[proc]["HostClass"]
                data = obtainLogFile(host, proc)
                self.send_response(200)
                self.send_header("Content-type", "text/plain")
            except:
                data = "404 File Not Found\n\r\n\r%s" % str(sys.exc_info())
                self.send_response(404)
                self.send_header("Content-type", "text/plain")
        elif path.startswith("/reload/"):
            try:
                self.server.wq.put(
                    (T_PROCLIST, ""),
                    timeout=PROC_RETRY
                )
                (
                    t,
                    allProcesses,
                    allHosts,
                    doneProcesses
                ) = self.server.rq.get(timeout=PROC_RETRY)
                proc = path[8:]
                self.lg.info('reloading proc %s'%proc)
                reload = loadSingleProcess(
                    proc,
                    self.lg,
                ).get(proc, {})
                excludeStatus = lambda x: x != "Status"
                for (k, v) in filter(excludeStatus, list(reload.items())):
                    allProcesses[proc][k] = v
                for k in filter(
                    excludeStatus,
                    set(allProcesses[proc].keys()) - set(reload.keys())
                ):
                    self.lg.warn(
                        "removing key %s from allProcesses[%s]" % (k, proc)
                    )
                    del allProcesses[proc][k]
                self.send_response(303)
                self.send_header("Location", "/proc/%s" % proc)
            except:
                data = "404 File Not Found\n\r\n\r%s" % str(sys.exc_info())
                self.send_response(404)
                self.send_header("Content-type", "text/plain")
        elif path in ("/", "/autorefresh"):
            self.lg.info("<-- HTTP-GET %s %s" % (
                self.path,
                self.client_address[0]
            ))
            try:
                o = self.server.wq.put(
                    (T_PROCLIST, ""),
                    timeout=PROC_RETRY
                )
            except Full:
                self.lg.error("queue is full")
                return ""
            try:
                (
                    t,
                    allProcesses,
                    allHosts,
                    doneProcesses
                ) = self.server.rq.get(timeout=PROC_RETRY)
            except Empty:
                self.lg.error("queue is empty")
                return ""
            data = self.generate_output(
                "Process Monitor: tee hub",
                self.format_process_list(
                    allProcesses,
                    allHosts,
                    doneProcesses,
                    self.js
                ),
                '(c) PRCM',
                ts,
                link = True,
                internal = internal,
                refresh = True
            )
            self.send_response(200)
            self.send_header("Content-type", "text/html")
        elif path == "/restart":
            self.lg.info("<-- HTTP-GET %s %s" % (
                self.path,
                self.client_address[0]
            ))
            data = self.generate_output(
                "Restarting Server",
                self.table((
                    "<tr><td>Please wait several seconds, and "
                    "then click the link below.</td></tr>"
                )),
                homelink,
                ts,
            )
            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            self.wfile.write(data.encode())
            self.server.wq.put((T_INIT, ""))
            return ""
        elif path.startswith("/proc/"):
            try:
                self.lg.info("<-- HTTP-GET %s %s" % (
                    self.path,
                    self.client_address[0]
                ))
                self.server.wq.put(
                    (T_PROCLIST, ""),
                    timeout=PROC_RETRY
                )
                (
                    t,
                    allProcesses,
                    allHosts,
                    doneProcesses
                ) = self.server.rq.get(timeout=PROC_RETRY)
                path = path[6:]
                immdeps = []
                alldeps = []
                for p in sorted(allProcesses.keys()):
                    if path in dependencies(allProcesses, p):
                        alldeps.append(p)
                    if path in allProcesses.get(p, {}).get("Depends", []):
                        immdeps.append(p)
                if path in allProcesses:
                    statusmap = [(
                            dep,
                            allProcesses.get(dep, {}).get("Status", [0])[0]
                        ) for dep in alldeps]
                    this_status = allProcesses.get(path, {}).get(
                        "Status",
                        [0]
                    )[0]
                    may_succeed = [dep_status3[0] for dep_status3 in [dep_status for dep_status in statusmap if dep_status[1] in (
                                S_CANCELED,
                                S_RUNNING,
                                S_SUCCEEDED,
                                S_BLOCKED,
                                S_UNRUNNABLE,
                            )]]
                    if may_succeed and this_status in (
                        S_FAILED,
                        S_SUSPENDED,
                        S_MANUAL
                    ):
                        actlink = "&nbsp;<span class=\"blackborder\">" \
                            + "%s&nbsp;suspend-deps</span>" % self.input(
                            "suspend-deps",
                            path,
                            I_SUSPEND
                        )
                    else:
                        actlink = ""
                    display_status = dict(list(allProcesses[path].items())[:])
                    if immdeps:
                        display_status["Required By"] = immdeps
                    data = self.generate_output(
                        path,
                        self.format_entry(display_status),
                        "%s&nbsp;%s&nbsp;%s%s" % (
                            self.link(
                                "%s/%s.log" % (iif(self.js, "", "/ns"), path),
                                "log"
                            ),
                            self.link(
                                "%s/reload/%s" % (
                                    iif(self.js, "", "/ns"),
                                    path
                                ),
                                "reload"
                            ),
                            homelink,
                            actlink
                        ),
                        ts
                    )
                    self.send_response(200)
                    self.send_header("Content-type", "text/html")
                else:
                    data = "404 File Not Found"
                    self.send_response(404)
                    self.send_header("Content-type", "text/plain")
            except:
                data = "404 File Not Found"
                self.send_response(404)
                self.send_header("Content-type", "text/plain")
        else:
            self.lg.info("<-- HTTP-GET %s %s" % (
                self.path,
                self.client_address[0]
            ))
            self.server.wq.put((T_DEFAULT, path))
            self.send_response(404)
            self.send_header("Content-type", "text/html")
        return data

    def do_GET(self):
        self.autorefresh = (self.path == "/ns/autorefresh")
        self.lg = self.server.lg
        if self.server.se.is_set():
            self.send_response(404)
            self.send_header("Content-type", "text/html")
            self.wfile.write('')
            return
        data = self.process()
        self.send_header("Content-Length", len(data))
        self.end_headers()
        if type(data) is bytes:
            self.wfile.write(data)
        elif type(data) is str:
            self.wfile.write(data.encode())
        else:
            self.lg.warn(data)
        return

    def do_POST(self):
        self.lg = self.server.lg
        self.autorefresh = (self.path == "/ns/autorefresh")
        self.lg.info("<-- HTTP-POST %s %s" % (
            self.path,
            self.client_address[0]
        ))
        length = int(self.headers.get('Content-Length',10))
        data = self.rfile.read(length)
        if self.path in ("/", "/ns/", "/ns/autorefresh"):
            commands = []
            for line in data.decode().split("&"):
                commands.append(tuple((
                    lambda x: (x[0], x[1]))(*[line.split(".")])))
            for (k, v) in sorted(set(commands)):
                self.lg.warn(str(k)+" "+str(v))
                if k == "restart":
                    self.server.wq.put((T_RESTART, v))
                elif k == "cancel":
                    self.server.wq.put((T_CANCEL, v))
                elif k == "kill":
                    self.server.wq.put((T_KILL, v))
                elif k == "suspend":
                    self.server.wq.put((T_SUSPEND, v))
                elif k == "approve":
                    self.server.wq.put((T_APPROVE, v))
                elif k == "suspend-deps":
                    self.server.wq.put((T_SUSPEND_DEPS, v))
            self.server.wq.put((T_PROCLIST, ""))
            (t, allProcesses, allHosts, doneProcesses) = self.server.rq.get(
                timeout=PROC_RETRY
            )
            data = self.process()
        else:
            self.server.wq.put((T_DEFAULT, self.path))
            self.send_response(404)
            self.send_header("Content-type", "text/html")

        self.send_header("Content-Length", len(data))
        self.end_headers()
        self.wfile.write(data.encode())
        return

    def log_request(self, code='-', size='-'):
        pass

class DaemonThread(threading.Thread):

    def __init__(self, queue, lg,stopevent):
        self.queue = queue
        self.stopevent=stopevent
        self.lg = lg
        try:
            ts = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            ts.close()
            self.lg.info("closing existing socket")
        except:
            pass
        self.s = [
            socket.socket(socket.AF_INET, socket.SOCK_STREAM),
            ("", PROC_PORT)
        ]
        self.ss = None
        threading.Thread.__init__(self)

    def run(self):
        self.lg.info("starting daemon thread")
        bound = 0
        while not bound:
            try:
                self.ss, peer = self.s
                self.ss.bind(peer)
                bound = 1
            except socket.error as e:
                self.lg.warn("socket.error %s" % e.__str__())
                time.sleep(PROC_RETRY)
        self.lg.info("bound to %s:%s" % peer)
        self.ss.listen(1)
        id = 0
        while not self.stopevent.is_set():
            try:
                (client, addr) = self.ss.accept()
                self.lg.info("new connection from %s" % str(addr))
                client.settimeout(PROC_RETRY)
                self.queue.put([client, None])
            except:
                self.lg.warn("daemon thread socket accept failed")
        self.lg.info('daemonthread done')

class DispatchThread(threading.Thread):
    def __init__(self, wq, rq, loc, lg,stopevent):
        self.dt = None
        self.rq = rq
        self.wq = wq
        self.loc = loc
        self.lg = lg
        self.stopevent=stopevent
        threading.Thread.__init__(self)

    def run(self):
        self.lg.info("starting dispatch thread")

        self.dq = Queue()
        self.dt = DaemonThread(self.dq, self.lg, self.stopevent)
        self.dt.setDaemon(1)
        self.dt.start()
        self.date = datetime.date.today()

        while not self.stopevent.is_set():
            try:
                s = self.dq.get(timeout = PROC_RETRY)
                if not s:
                    self.lg.warn("queue error in dispatch thread")
                args = socketRecv(s)
                (t, host) = args[:2]
                if len(args) > 2:
                    children = args[2]
                else:
                    children = set()
                self.lg.info("dispatch children %s" % str(children))
                self.wq.put((T_NEWHOST, (host, s, children)))
                socketSend(
                    s,
                    [T_DEFAULT, self.loc, self.date],
                    timeout = PROC_RETRY
                )
                socketRecv(s)
            except Empty:
                pass
            except Exception as e:
                self.lg.warn("dispatch error: "+str(e))
        self.lg.info('DispatchThread Done')

def obtainLogFile(host, proc):
    tfile = "%s/%s.log" % (PROC_LOGS, proc)
    command = (
        'scp',
        'scp',
        "%s:%s" % ({
            'davids-Mac-mini': '192.168.0.2',
            'davids-macbook-pro': '192.168.0.12',
        }.get(host, host), tfile),
        tfile
    )
    os.spawnlp(os.P_WAIT, *command)
    with open(tfile) as fh:
        data = fh.read()
    return data

def tokenize(contents, f, lg):
    d = {}
    candidates = set([
        "Command",
        "Depends",
        "HostClass",
        "Invincible",
        "StartAfter",
        "Nag",
        "Notify",
        "Signal",
        "SignalAfter",
        "Manual",
        "Days"
    ])
    for line in contents:
        try:
            if line.startswith("#"):
                continue
            if not line.lstrip():
                continue
            tag = None
            for c in candidates:
                if line.startswith("%s: " % c):
                    tag = c
                    pre = line[len(c)+1:].strip()
                    break
            if tag in ("StartAfter", "SignalAfter"):
                s = datetime.time(*list(map(int, pre.split(":"))))
            elif "Depends" == tag:
                s = set(pre.split(" "))
                s.discard('')
            elif "Invincible" == tag:
                s = int(pre)
            elif "Signal" == tag:
                s = signal.__dict__[pre]
            else:
                s = pre
            assert tag
            d[tag] = s
        except Exception as e:
            lg.warn(line)
            lg.warn(e)
            lg.warn("parse error in %s" % f)
    if "Depends" not in d and "StartAfter" not in d:
        raise Exception("missing both \"Depends\" and \"StartAfter\" fields ")
    if "Command" not in d:
        d["Command"] = "true"
    return d

def loadSingleProcess(f, lg):
    # TODO: do this from the db?
    try:
        fn = "%s/%s" % (PROC_JOBS, f)
        with open(fn) as fh:
            contents = [x.strip("\n") for x in fh.readlines()]
        fn = fn[len(PROC_JOBS)+1:]
    except Exception as e:
        lg.warn("failed to load process: %s\n%s" % (
            e.__str__(),
            traceback.format_exc(200)
        ))
    try:
        return dict([(fn, tokenize(contents, f, lg))])
    except Exception as e:
        lg.warn("parse error processing %s: %s" % (fn, e.__str__()))
        return {}

def obtainProcesses(lg):
    allProcesses = {}
    for (root, dirs, files) in os.walk(PROC_JOBS):
        for f in files:
            allProcesses.update(loadSingleProcess(f, lg))
    return allProcesses

def dependencies(allProcesses, proc, exclude=set(), restrict=False):
    direct = allProcesses.get(proc, {}).get("Depends", set()) - exclude
    exclude = set()
    if restrict:
        for dep in direct:
            if allProcesses.get(dep, {}).get("Status", [0])[0] \
                in (S_SUCCEEDED, S_CANCELED):
                exclude.add(dep)
    direct = direct - exclude
    deps = set()
    for dep in direct:
        deps |= dependencies(
            allProcesses,
            dep,
            exclude | direct,
            restrict=restrict
        )
    return deps | direct

def handleLaunchAck(allProcesses, allHosts, proc, host, requestTimestamp, args, rt, dt, lg):
    lg.info("received launch ack")
    if len(args) > 2:
        children = args[2]
    else:
        children = set()
    lg.info("core sorted children %s %s" % ( host, str(children) ))

    (instruction, data) = args[:2]
    (timestamp, pid) = data
    if timestamp != requestTimestamp:
        updateStatus(allProcesses, proc, [S_ERROR, rt, rt], lg)
        raise Exception("Launch req/ack mismatch for %s on %s. PID: %s." % (proc, host, pid))
    if allProcesses[proc]["Status"] == S_RUNNING:
        updateStatus(allProcesses, proc, [S_ERROR, allProcesses[proc]["Status"][4], rt], lg)
        raise Exception("Duplicate launch ack for %s on %s. PID: %s." % (proc, host, pid))
    elif pid < 0:
        updateStatus(
            allProcesses,
            proc,
            [S_FAILED, rt, rt],
            lg
        )
    else:
        updateStatus(
            allProcesses,
            proc,
            [
                S_RUNNING,
                host,
                pid,
                allProcesses[proc].get("SignalAfter", datetime.time.max) < rt.time(),
                rt
            ],
            lg
        )

def handleUpdates(allProcesses, allHosts, host, procReverseMap, doneProcesses, args, rt, dt, lg):
    (t, updates) = args[:2]
    if not hasattr(updates, '__iter__'):
        lg.warn('non-iterable %s passed instead of updates list' % str(updates))
        return
    if len(args) > 2:
        children = args[2]
    else:
        children = set()
    lg.info("core periodic children %s %s" % (
        host,
        str(children)
    ))
    if updates:
        lg.info("updates on %s: %s" % (host, str(updates)))
    for (pid, status) in updates:
        try:
            if status < 0:
                status = S_FAILED
            proc = procReverseMap[host][pid]
            try:
                ort = allProcesses[proc]["Status"][-1]
            except:
                ort = datetime.time.min
            if status == S_RUNNING:
                updateStatus(
                    allProcesses,
                    proc,
                    [S_RUNNING, host, pid, allProcesses[proc].get("SignalAfter", datetime.time.max) < rt.time(), rt],
                    lg
                )
            else:
                updateStatus(
                    allProcesses,
                    proc,
                    [status, ort, rt],
                    lg
                )
            lg.info("Updated status of %s on %s to %s." % (proc, host, STATUS_MAP[status]))
            if status in (S_SUCCEEDED, S_CANCELED):
                try:
                    doneProcesses \
                        |= set([procReverseMap[host][pid]])
                except KeyError as e:
                    lg.error("Bad host or PID: %s\n%s" % (e.__str__(), traceback.format_exc(200)))
            if status in (S_FAILED, S_ERROR) \
                and "Notify" in allProcesses[proc]:
                try:
                    data = obtainLogFile(host, proc)
                    sendEmail(
                        "Process Daemon <procd@phasecap.com>",
                        allProcesses[proc]["Notify"].split(
                            ","
                        ),
                        "process %s %s on %s" % (
                            proc,
                            STATUS_MAP[status],
                            host
                        ),
                        "\n".join(data.split("\n")[-50:])
                    )
                except Exception as e:
                    lg.warn(
                        "email failed: %s" % e.__str__()
                    )
        except Exception as e:
            lg.warn("status overwritten: %s\n%s" % (
                e.__str__(),
                traceback.format_exc(200)
            ))

def updateStatus(allProcesses, proc, s, lg):
    lg.info("updating status of %s to %s" % (proc, s))
    allProcesses[proc]["Status"] = s
    return 0

def kill_proc(req, allProcesses, allHosts, rt, dt, lg):
    lg.info("killing: %s" % req)
    st = allProcesses[req]["Status"]
    if req in allProcesses:
        f = 1
        if S_RUNNING == st[0]:
            (host, pid, sigStatus, startTime) = st[1:]
            lg.info("request to kill %s:%s" % (host, pid))
            if host in allHosts:
                socketSend(
                    allHosts[host],
                    (T_KILL, pid),
                    retry = False,
                    timeout = PROC_RETRY,
                    lg = lg
                )
                response = socketRecv(allHosts[host], lg = lg)
                if (not response) or response[1] != 0:
                    f = 0
        if f:
            try:
                ort = allProcesses[req]["Status"][-1]
                assert type(ort) in [datetime.time, datetime.datetime]
            except:
                ort = datetime.time.min
            return updateStatus(
                allProcesses,
                req,
                [S_FAILED, ort, rt],
                lg
            )
    return 1

def core(allProcesses, allHosts, wrq, wwq, srq, swq, dt, httpd, ddt, lg):
    poll = dt
    sortedProcesses = sorted(allProcesses.items())
    doneProcesses = set([])
    for (proc, v) in sortedProcesses:
        if v["Status"][0] in (S_SUCCEEDED, S_CANCELED):
            doneProcesses |= set([proc])
    while 1:
        rt = datetime.datetime(*time.localtime()[:6])
        lg.info("rt heartbeat %s poll %s" % (rt, poll))

        try:
            (t, req) = wrq.get(timeout = PROC_RETRY)
            lg.info("received request %s" % req)
            if t in (
                T_RESTART,
                T_CANCEL,
                T_KILL,
                T_SUSPEND,
                T_LAUNCH,
                T_SUSPEND_DEPS
            ):
                st = allProcesses[req]["Status"]
                host = allProcesses[req]["HostClass"]
            if T_PROCLIST == t:
                lg.info("sending process list")
                wwq.put((T_PROCLIST, allProcesses, allHosts, doneProcesses))
            elif T_RESTART == t:
                lg.info("restarting: %s" % req)
                if req in allProcesses:
                    f = 1
                    if S_RUNNING == st[0]:
                        (host, pid, sigStatus, startTime) = st[1:]
                        lg.info("request to kill %s:%s" % (host, pid))
                        if host in allHosts:
                            socketSend(
                                allHosts[host],
                                (T_KILL, pid),
                                retry = False,
                                timeout = PROC_RETRY,
                                lg = lg
                            )
                            response = socketRecv(allHosts[host], lg = lg)
                            if (not response) or response[1] != 0:
                                f = 0
                    if f:
                        updateStatus(
                            allProcesses,
                            req,
                            [iif(
                                host in allHosts,
                                S_WAITING,
                                S_UNRUNNABLE
                            )],
                            lg
                        )
                        doneProcesses -= set([req])
            elif T_CANCEL == t:
                lg.info("canceling: %s" % req)
                if req in allProcesses:
                    f = 1
                    if S_RUNNING == st[0]:
                        (host, pid, sigStatus, startTime) = st[1:]
                        lg.info("request to kill %s:%s" % (host, pid))
                        if host in allHosts:
                            socketSend(
                                allHosts[host],
                                (T_KILL, pid),
                                retry = False,
                                timeout = PROC_RETRY,
                                lg = lg
                            )
                            if (not response) or response[1] != 0:
                                f = 0
                    if f:
                        updateStatus(
                            allProcesses,
                            req,
                            [S_CANCELED, rt],
                            lg
                        )
                        doneProcesses |= set([req])
            elif T_KILL == t:
                killResponse = kill_proc(req, allProcesses, allHosts, rt, dt, lg)
                if killResponse:
                    lg.error("Failed to kill %s." % req)
                else:
                    lg.info("Kill succeeded: %s" % req)
            elif T_SUSPEND == t:
                lg.info("suspending: %s" % req)
                if req in allProcesses:
                    updateStatus(
                        allProcesses,
                        req,
                        [S_SUSPENDED, rt],
                        lg
                    )
                    doneProcesses -= set([req])
            elif T_APPROVE == t:
                lg.info("approved: %s" % req)
                if req in allProcesses \
                    and allProcesses[req]["Status"][0] == S_MANUAL:
                    updateStatus(
                        allProcesses,
                        req,
                        [S_MANUAL, 0, rt],
                        lg
                    )
            elif T_SUSPEND_DEPS == t and st[0] in (S_FAILED, S_SUSPENDED, S_MANUAL):
                lg.info("suspending deps of: %s" % req)
                alldeps = []
                for p in sorted(allProcesses.keys()):
                    if req in dependencies(allProcesses, p):
                        alldeps.append(p)
                statusmap = [(
                        dep,
                        allProcesses.get(dep, {}).get("Status", [0])[0]
                    ) for dep in alldeps]
                running = [dep_status4[0] for dep_status4 in [dep_status1 for dep_status1 in statusmap if dep_status1[1] == S_RUNNING]]
                if running:
                    lg.info("killing running deps: %s" % ",".join(running))
                    for dep in running:
                        if allProcesses.get(dep, {}).get("Invincible"):
                            lg.info("%s is invincible" % dep)
                        else:
                            kill_proc(dep, allProcesses, allHosts, rt, dt, lg)
                may_run = [dep_status5[0] for dep_status5 in [dep_status2 for dep_status2 in statusmap if dep_status2[1] in (
                            S_CANCELED,
                            S_SUCCEEDED,
                            S_BLOCKED,
                            S_UNRUNNABLE
                        )]]
                if may_run:
                    lg.info("suspending other deps: %s" % ",".join(may_run))
                    for dep in may_run:
                        if dep in allProcesses:
                            updateStatus(
                                allProcesses,
                                dep,
                                [S_SUSPENDED, rt],
                                lg
                            )
                            doneProcesses -= set([dep])
                if running or may_run:
                    lg.info("restarting deps: %s" % ",".join(running+may_run))
                    for dep in running+may_run:
                        if dep in allProcesses:
                            updateStatus(
                                allProcesses,
                                dep,
                                [S_UNRUNNABLE, rt],
                                lg
                            )
                            doneProcesses -= set([dep])
            elif T_INIT == t:
                httpd.server_close()
                lg.info(' '.join(sys.argv))
                os.execv(PYTHON, [PYTHON]+sys.argv)
                sys.exit(0)
            else:
                lg.info("received %s" % req)
        except Empty:
            pass

        try:
            lg.info("obtaining status updates")
            (t, req) = srq.get(timeout = 0)
            if T_NEWHOST == t:
                (host, s) = req[:2]
                if type(host) is str:
                    if len(req) > 2:
                        children = req[2]
                    else:
                        children = set()
                    lg.info(
                        "core status children %s %s" % (host, str(children))
                    )
                    allHosts[host] = s
                    for (proc, v) in sortedProcesses:
                        if S_UNRUNNABLE == v["Status"][0] and host == v["HostClass"]:
                            updateStatus(
                                allProcesses,
                                proc,
                                [S_WAITING],
                                lg
                            )
                        elif S_DETACHED == v["Status"][0] and host == v["HostClass"]:
                            (host, spid) = v["Status"][2].split(":")
                            pid = int(spid)
                            lg.info("pid %s children %s" % (
                                pid,
                                ",".join(map(str, sorted(children)))
                            ))
                            if pid in children:
                                updateStatus(
                                    allProcesses,
                                    proc,
                                    [S_RUNNING, host, pid, 0, v["Status"][1]],
                                    lg
                                )
                            else:
                                if type(v["Status"][1]) in [datetime.time, datetime.datetime]:
                                    ort = v["Status"][1]
                                else:
                                    ort = datetime.time.min
                                updateStatus(
                                    allProcesses,
                                    proc,
                                    [S_FAILED, ort, rt],
                                    lg
                                )
                    lg.info("registered new host: %s" % host)
                else:
                    lg.warn("unexpected message type: slow host?")
            else:
                lg.warn("received unexpected message type from dispatcher")
        except Empty:
            pass

        if rt - poll > datetime.timedelta(0, PROC_POLL):
            lg.info("periodic procedures")
            if rt.date() > dt.date():
                lg.info("midnight: terminating")
                return
            poll = rt
            procReverseMap = {}
            for (proc, v) in sortedProcesses:
                if S_RUNNING == v["Status"][0]:
                    (st, host, pid, sigStatus, startTime) = v["Status"]
                    if type(pid) is not int:
                        lg.warn("non-int PID for process %s: %s" % (proc, pid))
                        updateStatus(allProcesses, proc, [S_ERROR, startTime, rt], lg)
                        continue
                    if host not in procReverseMap:
                        procReverseMap[host] = {}
                    procReverseMap[host][pid] = proc
            for (host, s) in list(allHosts.items()):
                f = 0
                try:
                    socketSend(
                        s,
                        [T_POLL],
                        retry = False,
                        timeout = PROC_RETRY,
                        lg = lg
                    )
                    args = socketRecv(s, lg = lg)
                    (t, p) = args[:2]
                    if type(p) is list:
                        handleUpdates(allProcesses, allHosts, host, procReverseMap, doneProcesses, args, rt, dt, lg)
                    elif type(p) is tuple:
                        lg.warn("Got launch ack instead of status update from %s: %s" \
                            % (host, args[1]))
                        raise Exception("Launch ack/status update mismatch.")
                    else:
                        lg.warn(
                            "bad data from %s: %s" % (host, args[1])
                        )
                        raise Exception("ill-formed status update from %s: %s" % (host, p))

                except Exception as e:
                    lg.warn("poll error: %s\n%s" % (
                        e.__str__(),
                        traceback.format_exc(200)
                    ))
                    try:
                        s[0].close()
                    except Exception as e:
                        lg.warn("failed to close socket: %s" % e.__str__())
                    f = 1
                if f:
                    lg.info("host disconnected: %s" % host)
                    del allHosts[host]
                    detached_set = {}
                    for (proc, v) in sortedProcesses:
                        if host == v["HostClass"]:
                            if S_WAITING == v["Status"][0]:
                                updateStatus(
                                    allProcesses,
                                    proc,
                                    [S_UNRUNNABLE],
                                    lg
                                )
                            elif S_RUNNING == v["Status"][0]:
                                hostport = "%s:%s" % tuple(v["Status"][1:3])
                                detached_set[proc] = hostport
                                try:
                                    ort = v["Status"][-1]
                                except:
                                    ort = datetime.time.min
                                updateStatus(
                                    allProcesses,
                                    proc,
                                    [S_DETACHED, rt, hostport],
                                    lg
                                )
                    if detached_set:
                        notifyees = set()
                        for proc in list(detached_set.keys()):
                            notifyees |= set(filter(
                                bool,
                                [x.strip() for x in allProcesses[proc].get(
                                        "Notify",
                                        ""
                                    ).split(",")]
                            ))
                        try:
                            sendEmail(
                                "Process Daemon <procd@phasecap.com>",
                                sorted(notifyees),
                                "host %s detached" % host,
                                "processes affected:\n\n%s" % "\n".join(["%s:%s" % (k_v[0], k_v[1]) for k_v in sorted(detached_set.items())])
                            )
                        except Exception as e:
                            lg.warn(
                                "email failed: %s" % e.__str__()
                            )

        lg.info("regular process checks")
        for (proc, v) in sortedProcesses:
            if (
                v["Status"][0] in (S_WAITING, S_MANUAL) \
                and v.get("StartAfter", datetime.time.min) < rt.time() \
                and not v.get("Depends", set([])) - doneProcesses
            ):
                host = v["HostClass"]
                lg.info("ready to launch: %s" % proc)
                if host in allHosts:
                    if v.get("Manual", 0) and not v["Status"][0] == S_MANUAL:
                        updateStatus(
                            allProcesses,
                            proc,
                            [S_MANUAL, 1, rt],
                            lg
                        )
                        continue
                    if v["Status"][0] == S_MANUAL and v["Status"][1] > 0 \
                            and rt > v["Status"][2]+datetime.timedelta(
                                0,
                                60*int(v.get("Manual", 0))
                            ):
                        updateStatus(
                            allProcesses,
                            proc,
                            [S_MANUAL, -1, v["Status"][2]],
                            lg
                        )
                        if v.get("Notify"):
                            try:
                                sendEmail(
                                    "Process Daemon <procd@phasecap.com>",
                                    v["Notify"].split(","),
                                    "process %s is awaiting intervention" % proc,
                                    ""
                                )
                            except Exception as e:
                                lg.error( "email failed: %s" % e.__str__() )
                    if v["Status"][0] == S_MANUAL and v["Status"][1]:
                        continue
                    s = allHosts[host]
                    timestamp = datetime.datetime.now().isoformat()
                    socketSend(
                        s,
                        [T_LAUNCH, [proc, v, timestamp]],
                        retry = False,
                        timeout = PROC_RETRY,
                        lg = lg
                    )
                    try:
                        lg.info("sent launch request")
                        args = socketRecv(s, lg = lg)
                        (t, p) = args[:2]
                        if type(p) is tuple:
                            handleLaunchAck(allProcesses, allHosts, proc, host, timestamp, args, rt, dt, lg)
                        elif type(p) is list:
                            handleUpdates(allProcesses, allHosts, host, procReverseMap, doneProcesses, args, rt, dt, lg)
                            lg.warn("Got status update instead of launch ack for %s on %s: %s" \
                                % (proc, host, args[1]))
                            raise Exception("Launch ack/status update mismatch.")
                        else:
                            lg.warn(
                                "bad data from %s: %s" % (host, p)
                            )
                            raise Exception("ill-formed launch ack for %s: %s" % (proc, p))

                    except Exception as e:
                        updateStatus(allProcesses, proc, [S_ERROR, rt, rt], lg)
                        lg.error("launch failed: %s\n%s" % (
                            e.__str__(),
                            traceback.format_exc(200)
                        ))
                        try:
                            data = obtainLogFile(host, proc)
                            sendEmail(
                                "Process Daemon <procd@phasecap.com>",
                                allProcesses[proc]["Notify"].split(","),
                                "%s launch failed: possible ERROR on %s" % (
                                    proc,
                                    host
                                ),
                                "\n".join(data.split("\n")[-50:])
                            )
                        except Exception as e:
                            lg.error("email failed: %s" % e.__str__() )

            if (
                S_RUNNING == v["Status"][0] \
                and v.get("SignalAfter", datetime.time.max) < rt.time() \
                and not v["Status"][3]
            ):
                (host, pid, sigStatus, startTime) = v["Status"][1:]
                if host in allHosts:
                    s = allHosts[host]
                    socketSend(
                        s,
                        [T_SIGNAL, [pid, v.get("Signal", signal.SIGTERM)]],
                        retry = False,
                        timeout = PROC_RETRY,
                        lg = lg
                    )
                    try:
                        args = socketRecv(s, lg = lg) or socketRecv(s, lg = lg)
                        (t, p) = args[:2]
                        if len(args) > 2:
                            children = args[2]
                        else:
                            children = set()
                        lg.info("core signal children %s %s" % (
                            host,
                            str(children)
                        ))
                        updateStatus(
                            allProcesses,
                            proc,
                            [S_RUNNING, host, pid, 1, rt],
                            lg
                        )
                    except TypeError as e:
                        lg.warn(
                            "bad data from %s: %s" % (host, e.__str__())
                        )
                    except Exception as e:
                        lg.warn("signal failed: %s\n%s" % (
                            e.__str__(),
                            traceback.format_exc(200)
                        ))

def master(dt, proc_table, log_to_file=True):
    lg = LogFile(PROC_LOGS+"/master.log" if log_to_file else None)
    ret = 0
    try:
        (srq, swq) = (Queue(), Queue())
        se = threading.Event()
        ddt = DispatchThread(srq, swq, proc_table, lg,se)
        ddt.setDaemon(1)
        ddt.start()

        ClientRequestHandler.protocol_version = "HTTP/1.1"
        while 1:
            try:
                httpd = ThreadedHTTPServer(
                    ("", PROC_HTTP_PORT),
                    ClientRequestHandler
                )
                break
            except Exception as e:
                time.sleep(PROC_RETRY)
                lg.warn(e.__str__())
        (wrq, wwq) = (Queue(), Queue())
        httpd.lg = lg
        httpd.se = se
        httpd.rq = wwq
        httpd.wq = wrq
        httpd.dt = dt
        httpd.proc_table = proc_table

        sa = httpd.socket.getsockname()
        lg.info("serving HTTP on %s:%s" % (sa[0], sa[1]))
        allProcesses = obtainProcesses(lg)

        server = threading.Thread(target = httpd.serve_forever)
        server.setDaemon(True)
        server.start()
        lg.info("RunDate "+dt.isoformat())
        for proc in list(allProcesses.keys()):
            lg.info("Checking {0} {1}".format(proc, allProcesses[proc]))
            allProcesses[proc]["Status"] = [S_UNRUNNABLE]
            lg.info("Checked {0} {1}".format(proc, allProcesses[proc]))
        lg.info("successfully initialized status")
        core(allProcesses, {}, wrq, wwq, srq, swq, dt, httpd, ddt, lg)
        lg.info("successfully completed a core run")
        se.set()
        httpd.server_close()
        httpd.shutdown()
    except KeyboardInterrupt:
        try:
            httpd.server_close()
        except:
            raise
        lg.info("process aborted")
        ret = 0
    except Exception as e:
        lg.error("fatal: %s\n%s" % (e.__str__(), traceback.format_exc(200)))
        ret = -1
    return ret

def slave(dt, master, master_host, log_to_file=True):
    loc = ""
    rundate = datetime.date.today()
    hostname = socket.gethostname().split(".")[0]
    lg = LogFile(PROC_LOGS+"/slave.log" if log_to_file else None)
    s = socketConnect(
        (
            ior(master_host, PROC_MASTER.get(master, master)),
            PROC_PORT
        ),
        lg,
        retry = True,
        timeout = PROC_RETRY
    )
    data = hostname
    children = set()
    while 1:
        rt = datetime.datetime(*time.localtime()[:6])
        try:
            if rt.date() > dt.date():
                lg.info("midnight: terminating")
                for sp in sorted(children):
                    os.kill(sp.pid, signal.SIGTERM)
                break
            socketSend(
                s,
                [T_DEFAULT, data, sorted([x.pid for x in children])],
                timeout = PROC_RETRY
            )
            req = socketRecv(s)
            if not req:
                lg.info("reconnecting")
                data = hostname
            elif T_DEFAULT == req[0]:
                lg.info("received ack")

                if len(req) > 1:
                    loc = req[1]
                    try:
                        rundate = req[2]
                    except:
                        lg.warn("transitional")
                else:
                    loc = LOCATION
                data = None

            elif T_LAUNCH == req[0]:
                try:
                    (proc, v, requestTimestamp) = req[1]
                    lg.info("launching %s" % v["Command"])
                    command = v["Command"].split()
                    os.chdir(PYTHONPATH)
                    with open(
                        "%s/%s.log" % (PROC_LOGS, proc),
                        "w"
                    ) as fh:
                        sys.stdout = fh
                        env = os.environ
                        env.update({"LOCATION": loc, "RUNDATE": str(rundate), })

                        sp = subprocess.Popen(
                            command,
                            stdout = fh,
                            stderr = fh,
                            env = env
                        )
                        data = (requestTimestamp, sp.pid)
                        if data[1] > 0:
                            children |= set([sp])
                except Exception as e:
                    lg.warn("request failed: %s" % e.__str__())
                    data = (requestTimestamp, -1) 
            elif T_POLL == req[0]:
                lg.info("children: %s" % ",".join(
                    [str(x.pid) for x in children]
                ))
                data = []
                for sp in children.copy():
                    try:
                        rc = sp.poll()
                        if rc is not None:
                            lg.info("process %s returned %s" % (sp.pid, rc))
                            data.append((
                                sp.pid,
                                iif(rc, S_FAILED, S_SUCCEEDED)
                            ))
                            children.remove(sp)
                    except Exception as e:
                        children.remove(sp)
                        data.append((sp.pid, -1))
                        lg.warn("pid vanished: %s %s" % (pid, e.__str__()))
            elif T_KILL == req[0]:
                pid = req[1]
                try:
                    os.kill(pid, signal.SIGTERM)
                    children.remove(
                        filter( lambda x: x.pid==pid, children )[0]
                    )
                    lg.info("successfully killed %s" % pid)
                    data = 0 
                except Exception as e:
                    lg.warn("failed to kill %s: %s" % (pid, e.__str__()))
                    data = 1 
            elif T_SIGNAL == req[0]:
                (pid, sig) = req[1]
                try:
                    os.kill(pid, sig)
                    lg.info("successfully signaled %s" % pid)
                except Exception as e:
                    lg.warn("failed to kill %s: %s" % (pid, e.__str__()))
            elif T_RESTART == req[0]:
                pass 
        except KeyboardInterrupt:
            lg.info("process aborted")
            break
    return

def main(args):
    dt = datetime.datetime.now()
    p = OptionParser()
    p.add_option(
        "-m",
        "--master",
        dest = "master",
        default = LOCATION,
    )
    p.add_option(
        "-s",
        "--slave",
        action = "store_true",
        dest = "slave",
        default = False,
    )
    p.add_option(
        "-l",
        "--log_to_file",
        action = "store_false",
        dest = "log_to_file",
        default = True,
    )
    p.add_option(
        "-H",
        "--master-host",
        dest = "master_host",
        default = LOCATION,
    )
    (o, a) = p.parse_args(args)
    if o.slave:
        try:
            return slave(dt, o.master, o.master_host, o.log_to_file)
        except:
            os.kill(os.getpid(), signal.SIGTERM)
            time.sleep(10)
            return -1
    else:
        return master(dt, o.master, o.log_to_file)

if __name__ == '__main__':
    sys.exit(main(sys.argv))
