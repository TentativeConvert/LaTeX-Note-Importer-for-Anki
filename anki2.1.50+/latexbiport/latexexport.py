# -*- coding: utf-8 -*-
# import the main window object (mw) from ankiqt
from aqt import mw
# import the "show info" tool from utils.py
from aqt.utils import showInfo
# import all of the Qt GUI library
from aqt.qt import *
from anki.exporting import *
from anki.hooks import addHook


class LatexNoteExporter(Exporter):

    key = _("Notes in Latex")
    ext = ".tex"

    def __init__(self, col):
        Exporter.__init__(self, col)
        self.includeID = True
        self.includeTags = True

    def replaceLineBreaks(self,text):
        "Replace html-line breaks by plain-text line breaks"
        #remove plain-text line breaks (most probobly there aren't any to begin with)
        text = text.replace("\n","")
        #convert some html
        htmldict = {r"<br>":"\n",
                    r"<br />":"\n",
                    r"<div>":"\n",
                    r"</div>":"",
                    r"&nbsp;":r" "}
        for k, v in htmldict.items():
            text = text.replace(k, v)
        return text
    
    def stripNewLines(self,text):
        "Remove newlines at beginning and end of text, and replace double blank lines by single blank lines"
        text = re.sub("\n\s*\n+","\n\n",text).strip()
        #the following is superfluous as its done automatically by strip()
        #while len(text) > 0 and text[1] == "\n":     
        #    text = text[1:].strip()
        #while len(text) > 0 and text[-1] == "\n":     
        #    text = text[:-1].strip()
        return text
    
    def htmlToLatex(self, text):
        "Remove [latex], [/latex] and html"
        #convert some html
        htmldict = {r"&amp;":r"&",
                    r"&lt;":r"<",
                    r"&gt;":r">"}
        for k, v in htmldict.items():
            text = text.replace(k, v)
        #remove all remaining html
        text = re.sub("<[^<]+?>", "", text)
        #remove latex marks and any surrounding line breaks
        text = re.sub("\n*\[latex\]","",text)
        text = re.sub("\[/latex\]\n*","",text)
        return text


    def doExport(self, file):
        cardIds = self.cardIds()
        data = []
        model = mw.col.getCard(cardIds[0]).model()
        for id, flds, tags in self.col.db.execute("""
 select guid, flds, tags from notes
 where id in
 (select nid from cards
 where cards.id in %s)""" % ids2str(cardIds)):
            latexnote = []
            TAB = "    "
            latexnote.append(r"\begin{note}")
            # fields
            for f in splitFields(flds):
                newf = self.replaceLineBreaks(f)
                if newf.find("[latex]") != -1:
                    #treat as latex field
                    newf = self.htmlToLatex(newf)
                    if newf.find("\n") == -1:
                        #field consists of a single line
                        latexnote.append(TAB + r"\xfield{" + newf + "}") 
                    else:
                        newf = self.stripNewLines(newf)
                        newf = TAB + TAB + newf.replace("\n","\n" + TAB + TAB)
                        latexnote.append(TAB + r"\begin{field}" + "\n" + newf + "\n" + TAB + r"\end{field}")
                else:
                    #treat as plain-text field
                    if newf.find("\n") == -1:
                        #field consists of a single line
                        latexnote.append(TAB + r"\xplain{" + newf + "}") 
                    else:
                        newf = self.stripNewLines(newf)
                        newf = TAB + TAB + newf.replace("\n","\n" + TAB + TAB)
                        latexnote.append(TAB + r"\begin{plain}" + "\n" + newf + "\n" + TAB + r"\end{plain}")
            #remove empty fields at the end of the note:
            while latexnote[-1] == TAB + r"\xplain{}":
                latexnote.pop()
            # tags
            if self.includeTags:
                cleantag = tags.strip()
                if cleantag != "":
                    latexnote.append(TAB + r"\tags{" + tags.strip() + r"}")
            latexnote.append(r"\end{note}" + "\n")
            data.append("\n".join(latexnote))
        self.count = len(data)
        #preamble =r"""# -- I've decided that this should be placed in model["latexPre"] by the user
        #\newenvironment{note}{}{\begin{center}\rule{\textwidth}{2pt}\end{center}}
        #\newenvironment{field}{}{\begin{center}\rule{\textwidth}{0.4pt}\end{center}}
        #\newcommand*{\tags}[1]{\paragraph{tags: }#1}"""
        out = "% -*- coding: utf-8 -*-\n" + model["latexPre"] + "\n" + "\n".join(data) + "\n" + model["latexPost"]
        file.write(out.encode("utf-8"))
        
def addLatexExporterToList(exps):
    exps.append((LatexNoteExporter.key + " (*" + LatexNoteExporter.ext + r")", LatexNoteExporter))

addHook("exportersList", addLatexExporterToList);
