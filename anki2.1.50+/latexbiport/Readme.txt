Class hierarchy (see anki/importing):
-------------------------------------

ForeignNote  (noteimp.py)

Importer     (base.py)
 |
 |
NoteImporter (noteimp.py)
- def: run(self)
       self.importNotes(self.foreignNotes)
- def: importNotes(self, notes)
       ... heart of the importing machinary ...
 |                              |
 |                              |
TextImporter (csvfile.py)      LatexImporter  (lateximport.py)
- openFile(self)               - openFile(self)
- foreignNotes(self)           - foreignNotes(self)


As indicated, the class LatexImporter is derived from the class NoteImporter. 
Much of its code is copied verbatim from TextImporter.  However, the methods 
openFile(self) and foreignNotes(self) have been severely modified.
 

Code executing order at run-time (see aqt/importing.py):
-------------------------------------------------------

    . openFile() is called as soon as the user has chosen a file to import.
      In more detail, we have the following call order:
      onImport() --calls--> importFile(file)
                 --calls--> importer = importer(.., file)
                            importer.open()
		 --calls--> importer.cacheFile()
		 --calls--> importer.openFile()

    . Then the ImportDialog (aqt/importing.py) is shown, 
      in which the user may specify which deck to import into etc.
	
    . When the user clicks "Import":
      doImport() --calls--> (Note)importer.run()
                 --calls--> (Text|Latex|..)importer.foreignNotes()

In TextImporter, openFile() only checks that the file format is understood.
No further processing of the file takes place at this stage.

In LatexImporter, openFilen() already does all the processing required,
because it needs to work out the maximum number of fields of the notes
to be imported.
foreignNotes() later only returns a ready-made list of foreignNote's.


