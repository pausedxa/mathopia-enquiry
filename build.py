"""Builds index.html (the GitHub Pages copy of the enquiry form) from ../enquiry-form/Form.html.

The only change: the form sends its answers to the Apps Script web app with fetch
instead of google.script.run, because this page is not served by Apps Script.
Run after editing Form.html, then commit and push this folder.
"""
from pathlib import Path

HERE = Path(__file__).parent
EXEC_URL = "https://script.google.com/macros/s/AKfycbwMy5tLxgPnKNDTSRrwBeD2zvGDiTlKKb4bnhyw2pVPI5h5u_xWUPFIgyxddmdbdNd-QQ/exec"

OLD = """    google.script.run
      .withSuccessHandler(function () {
        document.getElementById('app').classList.add('sent');
        window.scrollTo(0, 0);
      })
      .withFailureHandler(function () {
        btn.disabled = false;
        btn.textContent = 'Send enquiry';
        err.textContent = "Sorry, that didn't go through. Please try again, or message us on WhatsApp.";
      })
      .submitEnquiry(f);"""

NEW = """    // text/plain keeps this a simple request, so the browser sends no preflight
    fetch('%s', { method: 'POST', headers: { 'Content-Type': 'text/plain;charset=utf-8' }, body: JSON.stringify(f) })
      .then(function (r) { return r.json(); })
      .then(function (res) {
        if (!res.ok) throw new Error(res.error);
        document.getElementById('app').classList.add('sent');
        window.scrollTo(0, 0);
      })
      .catch(function () {
        btn.disabled = false;
        btn.textContent = 'Send enquiry';
        err.textContent = "Sorry, that didn't go through. Please try again, or message us on WhatsApp.";
      });""" % EXEC_URL

src = (HERE.parent / "enquiry-form" / "Form.html").read_text()
assert src.count(OLD) == 1, "Form.html's send code changed; update build.py"
page = src.replace(OLD, NEW)
if "<title>" not in page:
    page = page.replace("<head>", "<head>\n<title>Join Mathopia</title>", 1)
if 'name="viewport"' not in page:
    page = page.replace("<head>", '<head>\n<meta name="viewport" content="width=device-width, initial-scale=1">', 1)
(HERE / "index.html").write_text(page)
print("index.html written")
