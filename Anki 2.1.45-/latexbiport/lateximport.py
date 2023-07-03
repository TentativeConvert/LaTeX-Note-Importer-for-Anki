# -*- coding: utf-8 -*-
# import the "show info" tool from utils.py
from aqt.utils import showInfo

import anki.importing as importing
from anki.importing.noteimp import ForeignNote
from anki.importing.noteimp import NoteImporter
import operator
import re

from aqt import mw
from aqt.qt import *
from aqt.importing import ImportDialog
from anki.hooks import wrap


# GUI:
def hideAllowHTML(self):
    if type(self.importer) == LatexImporter:
        self.frm.allowHTML.hide()
ImportDialog.setupMappingFrame = wrap(ImportDialog.setupMappingFrame, hideAllowHTML)


# MEAT:
class LatexImporter(NoteImporter):
    
    needMapper = True
    needDelimiter = False
    # allowHTML always True (assignments have no affect):
    allowHTML = property(lambda self: True, lambda self,value: 0, lambda self: 0, "allowHTML, always returns True")
  
    def __init__(self, *args):
        # excerpt from TextImporter (csvfile.py)
        NoteImporter.__init__(self, *args)
        self.fileobj = None
        # preamble and postamble are saved in the following variables,
        # but they are not actually processed by the current version
        # of LatexImporter:
        self.preamble = ""
        self.postamble = ""
        # noteList will contain all ForeignNotes that have been imported:
        self.noteList = []
        # the log will be built from a list of warnings and a list
        # of text passages that have been ignored
        self.log = []
        self.rubbishList = []
        self.warningList = []
    
    def fields(self):
        # exact copy from TextImporter (csvfile.py)
        "Number of fields."
        self.open()
        return self.numFields
    
    def open(self):
        # exact copy from TextImporter (csvfile.py)
        "Parse the top line and determine the pattern and number of fields."
        self.cacheFile()

    def cacheFile(self):
        # exact copy from TextImporter (csvfile.py)
        "Read file into self.lines if not already there."
        if not self.fileobj:
            self.openFile()
    
    def openFile(self):
        # modified from TextImporter (csvfile.py)
        self.dialect = None
        self.fileobj = open(self.file, "rb")
        self.processFile(str(self.fileobj.read(), "utf-8"))

    def foreignNotes(self):
        # modified from TextImporter (csvfile.py)
        return self.noteList

    def textToHtml(self, text):
        "Replace line breaks, <, > and & by HTML equivalents"
        htmldict = [[r"&", r"&amp;"],
                    [r"<", r"&lt;"],
                    [r">", r"&gt;"]]
        for v in htmldict:
            text = text.replace(v[0], v[1])
        # order of replacements matters --
        # line breaks need to be replaced last!
        text = text.replace("\n", r"<br>")
        return text

    def ignore(self, value, ignored):
        if re.search("\S", value) != None:
            ignored.append(value.strip())

    # parsing functions for different parts of the latex document
    # 1. parsing functions for different field types/tags
    def process_plain(self, value, note):
        value = self.textToHtml(value)
        note.fields.append(value)

    def process_latex(self, value, note):
        value = value.strip()
        if value != "":
            value = r"[latex]" + value + r"[/latex]"
        value = self.textToHtml(value)
        note.fields.append(value)

    def process_tags(self, value, note):
        note.tags.extend(value.split())

    # Klammer-zu-suche:
    def findClosingBrace(self, string):
        "return position of } matching invisible { at beginning of string"
        l = 1  # parenthization level
        p = 0
        while p < len(string) and l > 0:
            if string[p] == "\\":
                p += 1  # skip a character
            elif string[p] == "{":
                l += 1
            elif string[p] == "}":
                l -= 1
            elif string[p] == "%":
                jump = string[p:].find("\n")  # jump to end of line
                if jump == -1: break
                else: p += jump
            p += 1  # loop
        if l == 0:  # matching "}" found
            return (p-1, p)
        else:
            self.warningList.append("\nWARNING: } expected at the end of the following string.\n")
            self.warningList.append(string + "\n")
            return None

    def findCommand(self, string, command, arg=None, warning=False):
        if arg == None:
            pattern = r"\\" + command + r"(?![a-z])"
        elif arg == "?":
            pattern = r"\\" + command + r"\s*{"
        else:
            pattern = r"\\" + command + r"\s*{" + arg + r"}"
        p = 0
        mo = None
        while p < len(string):
            mo = re.match(pattern, string[p:])
            if mo: break
            if string[p] == "\\":
                p += 1  # skip a character
            elif string[p] == "%":
                jump = string[p:].find("\n")  # jump to end of line
                if jump == -1: break
                else: p += jump
            p += 1  # loop
        if mo:
            return (p + mo.start(), p + mo.end())
        else:
            if warning == True:
                self.warningList.append("\nWARNING: The environment containing the following string seems to be corrupted.\n")
                self.warningList.append(string + "\n")
            return None

    def findIter(self, string, findfun):
        poslist = []
        pos = (0, 0)
        while True:
            adpos = findfun(string[pos[1]:])
            if adpos == None:
                break
            if adpos[1] == adpos[0]:
                # This really shouldn't happen, I just want to make sure
                # I don't land in an infinite loop
                self.warningList.append("\nERROR: An error occurred while parsing the following string. Import may have failed.\n")
                self.warningList.append(string + "\n")
                break
            pos = (pos[1] + adpos[0], pos[1] + adpos[1])
            poslist.append(pos)
        return poslist

    def cutIntoPieces(self, string, cList):
        """returns a list of the strings before and in between all sections
        marked by the commands in cList, and a list of all sections"""
        triples = [(ao[0], ao[1], cList.index(command))
                   for command in cList
                   for ao in self.findIter(string, command['beginfun'])]
        triples.sort()
        Begins = [p[0] for p in triples] + [len(string)]
        intBegins = [p[1] for p in triples]
        commandIndices = [p[2] for p in triples]

        returnList = []
        i, prevEnd = 0, 0
        while i < len(intBegins):
            ci = commandIndices[i]
            preString = string[prevEnd:Begins[i]]
            intString = string[intBegins[i]:Begins[i+1]]
            ends = cList[ci]['endfun'](intString)
            if ends == None:
                valueString = intString
                prevEnd = Begins[i+1]
            else:
                valueString = intString[:ends[0]]
                prevEnd = intBegins[i] + ends[1]
            returnList.append((preString, valueString, ci))
            i += 1
        return returnList, string[prevEnd:]

    def processFile(self, fileString):
        docCommands = [{'beginfun': lambda string: self.findCommand(string, r"begin", r"document"),
                        'endfun': lambda string: self.findCommand(string, r"end", r"document", warning=True),
                        'process': lambda string: self.processDocument(string)}]
        pieces, post = self.cutIntoPieces(fileString, docCommands)
        # may return several documents if file was written like that,
        # but I'll ignore all except the first,
        # just like any latex interpreter would
        if pieces:
            self.preamble, document, ci = pieces[0]
        else:
            self.log = ["\nWARNING: Unable to determine document environment. Interpreted the whole file as document environment instead.\n"]
            self.preamble = ""
            document = fileString
            ci = 0  # unsure about this line; added [2021-02-27] as a hotfix without understanding what ci is
        self.preamble = self.preamble + "\\begin{document}"
        self.postamble = "\\end{document}" + post
        self.processDocument(document)
        # make all notes same length and
        # add tags as extra field at the very end
        # (Adding tags as field is necessary for tags to be "update-able":
        #  when updating a note via import, the core ANKI importer
        #  does not check whether tags have changed unless they are
        #  imported as an additional field.)
        self.numFields = max([len(note.fields) for note in self.noteList]) + 1
        # (+1 for tag-field)
        for note in self.noteList:
            note.fields = note.fields + [""]*(self.numFields-1-len(note.fields)) + [" ".join(note.tags)]
            note.tags = []
        # clean up rubbishList & provide feedback
        self.rubbishList = [s.strip() for s in self.rubbishList if re.search("\S", s) != None]
        self.log = self.log + self.warningList
        if len(self.rubbishList) > 0:
                self.log = self.log + [str(len(self.rubbishList)) + " lines have been ignored – they occurred in between notes or in between fields.\n"]

    def processDocument(self, document):
        globalTags = []
        noteCommands = [{'beginfun': lambda string: self.findCommand(string, r"begin", r"note"),
                         'endfun': lambda string: self.findCommand(string, r"end", r"note", warning=True),
                         'process': lambda string: self.processNote(string, globalTags)}]
        pieces, post = self.cutIntoPieces(document, noteCommands)
        for pre, value, ci in pieces:
            globalTags = self.processInterNoteText(pre, globalTags)
            noteCommands[ci]['process'](value)
             
    def processNote(self, noteString, globalTags):
        newNote = ForeignNote()
        newNote.tags.extend(globalTags)
        fieldCommands = [{'beginfun': lambda string: self.findCommand(string, r"field"),
                          'endfun': lambda string: self.findCommand(string, r"endfield"),
                          'process': lambda string: self.processLatexField(string, newNote)},
                         {'beginfun': lambda string: self.findCommand(string, r"begin", r"field"),
                          'endfun': lambda string: self.findCommand(string, r"end", r"field", warning=True),
                          'process': lambda string: self.processLatexField(string, newNote)},
                         {'beginfun': lambda string: self.findCommand(string, r"xfield", r"?"),
                          'endfun': self.findClosingBrace,
                          'process': lambda string: self.processLatexField(string, newNote)},
                         {'beginfun': lambda string: self.findCommand(string, r"plain"),
                          'endfun': lambda string: self.findCommand(string, r"endplain"),
                          'process': lambda string: self.processPlainField(string, newNote)},
                         {'beginfun': lambda string: self.findCommand(string, r"begin", r"plain"),
                          'endfun': lambda string: self.findCommand(string, r"end", r"plain", warning=True),
                          'process': lambda string: self.processPlainField(string, newNote)},
                         {'beginfun': lambda string: self.findCommand(string, r"xplain", r"?"),
                          'endfun': self.findClosingBrace,
                          'process': lambda string: self.processPlainField(string, newNote)},
                         {'beginfun': lambda string: self.findCommand(string, r"tags", r"?"),
                          'endfun': self.findClosingBrace,
                          'process': lambda string: self.processTags(string, newNote)}
                         ]
        pieces, post = self.cutIntoPieces(noteString, fieldCommands)
        for pre, value, ci in pieces:
            self.rubbishList.append(pre)
            fieldCommands[ci]['process'](value)
        self.rubbishList.append(post)
        self.noteList.append(newNote)

    def processInterNoteText(self, string, globalTags):
        tagCommands = [{'beginfun': lambda string: self.findCommand(string, r"tags", "?"),
                        'endfun': self.findClosingBrace,
                        'process': None}
                       ]
        pieces, post = self.cutIntoPieces(string, tagCommands)
        self.rubbishList.extend([pre for pre, value, ci in pieces] + [post])
        tags = [tag for pre, value, ci in pieces for tag in value.split() if tag != ""]
        if len(tags) > 0:
            return tags
        else:
            return globalTags

    def processTags(self, string, note):
        tags = [tag for tag in string.split() if tag != ""]
        note.tags.extend(tags)
 
    def processLatexField(self, string, note):
        if string.strip() != "":
            # string = re.sub(r"^[ \t]*", "", string, flags=re.MULTILINE)
            # see note below
            string = self.textToHtml(string)
            string = r"[latex]" + string + r"[/latex]"
        note.fields.append(string)
        
    def processPlainField(self, string, note):
        string = string.strip()
        string = re.sub(r"^[ \t]*", "", string, flags=re.MULTILINE)
        # see note below
        string = self.textToHtml(string)
        note.fields.append(string)

        
### This line worked up to version 2.1.44:
#        importing.Importers = importing.Importers + ((_("Latex Notes (*.tex)"), LatexImporter),)
### This is the replacement suggested by Kelciour:
def myImporters(col, _old):
    ret = _old(col)
    ret += ((_("Latex Notes (*.tex)"), LatexImporter),)
    return ret

importing.importers = wrap(importing.importers, myImporters, "around")
###

# note:
# The command
#     string = re.sub(r"^[ \t]*","",string,flags = re.MULTILINE)
# removes all whitespace at the beginning of each line of the
# (possibly-multiline) string.  However, I no longer understand
# why I should do this.  In the normal Anki editor, such leading
# whitespace does not show up in any case.  When importing
# verbatim-environments, deleting whitespace causes problems.
